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
