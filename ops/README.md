# ops/ —— 服务器运维脚本

放本机/服务器层面的运维脚本。与站点代码无关的、跨域名共用的东西放这里
（`aijobrisk-go/` 下的 `build.sh` / `restart.sh` / `upload-data.sh` 是该站专属的部署脚本，不要混）。

---

## nginx-log-rotate.sh

nginx 日志按天切割 + 自动清理过期归档。面向 **aaPanel（宝塔）** 的目录布局：
日志在 `/www/wwwlogs/{domain}.log`，nginx 在 `/www/server/nginx/`。

本机三个站的日志都在同一目录，所以脚本按目录批量处理，不用逐个域名配置：

```
/www/wwwlogs/aijobrisk.com.log         aijobrisk.com.error.log
/www/wwwlogs/aijobriskmap.com.log      aijobriskmap.com.error.log
/www/wwwlogs/ismyjobaiproof.com.log    ismyjobaiproof.com.error.log
```

### 它做什么

1. **切割**：把 `{LOG_DIR}/*.log` 移到 `{ARCHIVE_DIR}/{name}-YYYYMMDD.log`。空日志跳过。
2. **让 nginx 重开日志**：`kill -USR1 <pid>` → `nginx -s reopen` → `systemctl reload nginx`，依次兜底。
3. **压缩**：等 2 秒让 nginx 切到新 fd，再 `gzip -9`。
4. **清理**：删除归档目录里超过 `KEEP_DAYS`（默认 30）天的 `*-YYYYMMDD.log.gz`。

> ⚠️ **第 2 步不能省。** nginx 持有日志文件的 fd，文件被 `mv` 走之后它仍然往旧 inode 写，
> 新建的 `access.log` 会一直是 0 字节。网上很多"一行 mv + find -delete"的切割脚本都漏了这步，
> 结果是日志静默丢失、几周后才发现。脚本里 reopen 三种方式全失败时会**退出码 2 并告警**，
> 不会假装成功。

### 用法

```bash
./nginx-log-rotate.sh                 # 默认：/www/wwwlogs，保留 30 天
./nginx-log-rotate.sh --dry-run       # 只打印会做什么，不动任何文件
./nginx-log-rotate.sh --keep 60       # 保留 60 天
./nginx-log-rotate.sh --log-dir /www/wwwlogs --archive-dir /www/wwwlogs/rotated
```

也可用环境变量：`LOG_DIR` / `ARCHIVE_DIR` / `KEEP_DAYS` / `NGINX_BIN` / `NGINX_PID`。

退出码：`0` 成功｜`1` 参数或环境错误｜`2` nginx reopen 失败（日志已移走，需人工介入）。

### 安装

```bash
install -m 755 ops/nginx-log-rotate.sh /usr/local/bin/nginx-log-rotate.sh
```

**先跑一次 dry-run 确认路径对**（aaPanel 版本不同，nginx 路径可能有出入）：

```bash
/usr/local/bin/nginx-log-rotate.sh --dry-run
```

挂 cron，每天 00:05，`flock` 防重入，日志留档：

```cron
5 0 * * * /usr/bin/flock -n /tmp/nginx-log-rotate.lock /usr/local/bin/nginx-log-rotate.sh >> /var/log/nginx-log-rotate.log 2>&1
```

也可以用 aaPanel 的「计划任务 → Shell 脚本」，内容填上面那行（不含 cron 时间部分）。

### ⚠️ 先关掉 aaPanel 自带的日志切割

aaPanel 面板里「网站 → 设置 → 配置修改」旁边通常有**日志切割**功能，
计划任务里也可能已经存在一条自动创建的切割任务。**两套机制同时跑会互相打架**
（一天被切两次、归档命名不一致、GoAccess 统计出现断层）。装本脚本前先去
「计划任务」列表确认，把 aaPanel 自建的那条**停用或删除**，只保留一套。

### 与 GoAccess 的关系

`docs/analytics-setup.md`（在 `aijobrisk-go/docs/`）里的 GoAccess 用了
`--persist --restore --db-path=`，统计**落盘累计**，所以日志被切割、被删除都不影响历史数据。
但原始日志只保留 30 天——要留更久就调 `--keep`，注意磁盘。

### 为什么不用 logrotate

logrotate 是更标准的选择，本机也可以用。没走它的原因：aaPanel 的 nginx 是自编译的
（`/www/server/nginx`），面板升级时偶尔会重写自己的 logrotate 配置；而且这个脚本能
`--dry-run`、退出码能区分"reopen 失败"这种需要人工介入的情况，排查更直接。

如果你更想用 logrotate，等价配置是：

```
/www/wwwlogs/*.log {
    daily
    rotate 30
    missingok
    notifempty
    compress
    delaycompress
    dateext
    sharedscripts
    postrotate
        [ -f /www/server/nginx/logs/nginx.pid ] && kill -USR1 $(cat /www/server/nginx/logs/nginx.pid)
    endscript
}
```

（放 `/etc/logrotate.d/nginx-aapanel`，同样要先关掉 aaPanel 自带的切割。）

---

## blog-pull.sh

服务器端博客同步：拉取 GitHub Actions 自动发布的文章（`.github/workflows/blog-autopublish.yml`），
热重载到运行中的站点。完整链路、一次性配置与撤稿方法见 `aijobrisk-go/deployment.md` §八。

**为什么用独立镜像，而不是在线上代码目录里 `git pull`**：

- 线上目录拉到新模板 / Go 源码后，进程一旦重启就会变成「旧二进制 + 新模板」，渲染报错。
- `data/blog`、`static/blog` 在仓库里是被跟踪的，往线上目录写文件会让你下次部署代码时 `git pull` 冲突。

所以镜像只稀疏检出 `aijobrisk-go/data/blog` 与 `aijobrisk-go/static/blog`，
Go 通过 `AIJOBRISK_BLOG_DIR` / `AIJOBRISK_BLOG_STATIC_DIR` 直接读镜像。

```bash
bash ops/blog-pull.sh --init git@github.com:OWNER/REPO.git   # 一次性
bash ops/blog-pull.sh                                        # cron：每 10 分钟
```

```cron
*/10 * * * * /usr/bin/flock -n /tmp/blog-pull.lock bash /opt/career-guides-au/ops/blog-pull.sh >> /var/log/blog-pull.log 2>&1
```

| 退出码 | 含义 | 处理 |
|---|---|---|
| 0 | 成功，或没有新提交（静默） | — |
| 1 | 环境 / 配置错误 | 看报错 |
| 2 | 文件已同步，但重载接口失败 | 多半是旧二进制或 token 不一致；部署新二进制后 `systemctl restart aijobrisk-go` |
| 4 | 防误删拒绝：新 `index.json` 文章数骤降 >50%，或不是合法 JSON | 确认是有意的大批撤稿后用 `--force` |

安全措施：只对带 `.git/aijobrisk-blog-mirror` 标记的目录执行 `reset --hard`（防止误指到线上仓库抹掉改动）；
调用重载接口时 `--noproxy '*'`（服务器设了 `http_proxy` 时 curl 会把 127.0.0.1 也送去代理）。

---

## pull.sh（本地用）

GitHub Actions 的博客 bot 每天可能往 `main` 推提交，本地同步时用它代替 `git pull`。在 Git Bash 里运行：

```bash
bash ops/pull.sh            # 拉取并 rebase
bash ops/pull.sh --dry-run  # 只看远端有哪些新提交
```

和直接 `git pull` 的区别：用 rebase 不产生 merge 提交（本地未推送的提交接到最新 main 后面，之后直接 push）；
工作区有改动时自动暂存再放回；出冲突自动回滚到拉取前；远端新文件和本地未跟踪文件同名时先停下，不覆盖。

| 退出码 | 含义 |
|---|---|
| 0 | 成功，或已是最新 |
| 1 | 环境问题：不在仓库 / 不在 main / 有进行中的 rebase 或 merge / fetch 失败 |
| 2 | 有冲突，已自动回滚，本地和拉取前完全一样 |
| 3 | 远端新增文件会覆盖本地未跟踪的同名文件，未拉取 |
| 4 | 已拉取，但本地未提交的改动放回时冲突，改动在 stash 里（`git stash pop` 取回） |
