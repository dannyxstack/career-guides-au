# aijobrisk-go 部署文档

Go SSR 版 aijobrisk。**纯标准库 + 单一第三方依赖**（`go-sql-driver/mysql`，仅投票 API 用），无 Web 框架、无 ORM。
单进程、**单端口**同时提供：站点页面 + `/api` 投票 + `sitemap/robots` + `/static` 静态资源。

## 架构要点

- **运行时读数据**：数据（`data/` 约 600MB JSON）在启动时读入内存，**不打进二进制**。
  因此构建**无需 16GB 内存**（区别于 Astro 版）；启动约 **3.9s**；常驻 **RSS ~866MB**
  （4 个显示语言的翻译占大头——`translations-v2/` 单目录就 414MB）。
- **投票 DB 懒连接**：`sql.Open` 启动时不拨号，首个投票请求才连 MySQL。
  连不上则投票降级（`GET /api/polls` 返空票、`POST` 503），**页面照常渲染**——"MySQL 挂了站不挂"。
- **语言前缀路由**：显示语言在 URL 第一级（`/fr/...`），英文裸路径无前缀；国家在末级。
- **显示语言现状**（2026-09-09）：`en` / `es` / `fr` / `zh-Hans` 对外开放（nav 下拉 + hreflang + 可索引）；
  `ja` 翻译仅 59.6%，**入口暂时隐藏**（`i18n.hiddenDisplay`）——URL 仍可访问、译文照常渲染，
  但不进 nav / hreflang / sitemap 且整页 noindex，补齐后从该 map 移除即可。
  `de` / `pt` / `ko` 已退役（`i18n.RetiredLocales`），`/de/*`、`/pt/*`、`/ko/*` 301 回英文对应页。
  **`data/translations-v2/` 只导出显示语言**：`loadTranslations()` 按 `i18n.DisplayLocales` 过滤，
  其余语言即使存在也不载入；`scripts/export_go_translations.py` 亦拒绝导出非显示语言。

## 一、构建

需 **Go 1.24+**。**在目标服务器（Linux）上构建**，产出静态二进制：

```bash
cd aijobrisk-go
CGO_ENABLED=0 go build -ldflags="-s -w" -trimpath -o aijobrisk .
```

- `-ldflags="-s -w" -trimpath`：去符号/调试信息与本地路径，减小体积。
- `CGO_ENABLED=0`：纯静态，便于跨发行版部署。
- 交叉编译（本地打 Linux 包）：`GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -ldflags="-s -w" -trimpath -o aijobrisk .`

> ⚠️ **Windows 本地构建坑**：Windows Defender / 火绒会把新构建的 Go `.exe` 当启发式误报（`HEUR:VirTool/Obfuscator.*`）隔离。
> 本机验证改用 `go run .`；正式构建在 Linux 服务器上做，或给输出目录加杀软信任区。Linux 无此问题。

## 二、需要部署的文件

二进制运行时依赖同目录（或由环境变量指定）的三个目录 + 可选 `.env`：

```
/opt/aijobrisk-go/
  aijobrisk            # 二进制
  data/                # 数据 JSON（~600MB，含 occupations_v2.json / outline-paths.json / translations-v2/ 等）
  templates/           # *.html 模板
  static/              # app.css / logo.svg
  .env                 # 环境变量（含 MYSQL_*，权限 600）
```

用 rsync 上传（示例）：

```bash
rsync -avz --delete aijobrisk-go/data aijobrisk-go/templates aijobrisk-go/static \
  aijobrisk user@server:/opt/aijobrisk-go/
```

## 三、环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `HOST` | `127.0.0.1` | 监听地址（配合 nginx 反代，绑本地即可） |
| `PORT` | `4332` | 监听端口 |
| `AIJOBRISK_SITE` | `https://aijobrisk.com` | 站点绝对根（canonical / hreflang / og 用） |
| `AIJOBRISK_DATA` | `data` | 数据目录（相对进程 CWD；建议设绝对路径或用 systemd `WorkingDirectory`） |
| `AIJOBRISK_TEMPLATES` | `templates` | 模板目录 |
| `AIJOBRISK_STATIC` | `static` | 静态目录 |
| **投票（可选）** | | 不配则投票功能自动降级 |
| `MYSQL_HOST`/`MYSQL_PORT`/`MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE`/`MYSQL_CHARSET` | — | 投票库连接 |
| `POLLS_IP_SALT` | — | IP 哈希软去重的盐（生产必设） |
| `POLLS_TURNSTILE_SECRET` | — | Cloudflare Turnstile 密钥（可选人机校验） |
| `POLLS_CLIENT_IP_HEADER` | — | 可信的客户端 IP 头。**挂 CDN 后必设**（Cloudflare 填 `CF-Connecting-IP`）：设了就只认该头，忽略可伪造的 `X-Forwarded-For`；留空则沿用 XFF 首段（单层 nginx 反代）。详见 `docs/analytics-setup.md` |
| `POLLS_CORS_ORIGINS` | — | 允许跨域来源；**同端口同源部署可留空（免 CORS）** |
| `POLLS_RATE_MAX` | `20` | 限流：窗口内最大请求数 |
| `POLLS_RATE_WINDOW` | `60` | 限流窗口秒数 |
| `PUBLIC_POLLS_API` | `/api` | 投票组件请求的 API 基址；**同源部署留空即用 `/api`**，仅独立子域时设为完整地址 |
| `AIJOBRISK_RELOAD_TOKEN` | — | 博客热重载接口 `POST /internal/reload-blog` 的 token（≥32 字符）；不设则接口整体 404。仅接受本机直连，经 nginx/CF 转发的请求一律拒绝。见 §八 |
| `AIJOBRISK_BLOG_DIR` | `data/blog` | 博客数据目录。线上指向 `ops/blog-pull.sh` 维护的独立镜像，**不与代码目录共用** |
| `AIJOBRISK_BLOG_STATIC_DIR` | `static/blog` | 博客头图目录（同上，指向镜像） |
| `AIJOBRISK_ENV` | — | 指向 `.env` 文件路径（否则自动找 `.env`/`../.env`/`../../.env`） |

`.env` 示例（放 `/opt/aijobrisk-go/.env`，`chmod 600`）：

```dotenv
HOST=127.0.0.1
PORT=4332
AIJOBRISK_SITE=https://aijobrisk.com
AIJOBRISK_DATA=/opt/aijobrisk-go/data
AIJOBRISK_TEMPLATES=/opt/aijobrisk-go/templates
AIJOBRISK_STATIC=/opt/aijobrisk-go/static
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=aijobrisk_polls
MYSQL_PASSWORD=__set_me__
MYSQL_DATABASE=career_contents
MYSQL_CHARSET=utf8mb4
POLLS_IP_SALT=__random_long_string__
POLLS_RATE_MAX=20
POLLS_RATE_WINDOW=60
```

## 四、投票数据库（可选）

投票用 `poll_votes` / `poll_agg` / `poll_agg_num` 三张表。首次建表：

```bash
python -m scripts.seed_polls_schema      # 在主仓库根目录运行
```

**生产建议用最小权限账号**（只对 `poll_*` 表 DML，不给建表/其他表权限）：

```sql
CREATE USER 'aijobrisk_polls'@'127.0.0.1' IDENTIFIED BY '__set_me__';
GRANT SELECT, INSERT, UPDATE ON career_contents.poll_votes    TO 'aijobrisk_polls'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE ON career_contents.poll_agg      TO 'aijobrisk_polls'@'127.0.0.1';
GRANT SELECT, INSERT, UPDATE ON career_contents.poll_agg_num  TO 'aijobrisk_polls'@'127.0.0.1';
FLUSH PRIVILEGES;
```

投票 API 端点（同端口同源）：`GET /api/polls`、`POST /api/polls/vote`、`GET /api/health`。

> 可选：若要把投票 API 拆成独立子域/进程，用 `go build -o pollsapi ./cmd/pollsapi`（默认端口 `POLLS_PORT=8790`），
> 并给前端设 `PUBLIC_POLLS_API` 指向该子域（此时需配 `POLLS_CORS_ORIGINS`）。默认单端口同源无需这么做。

## 五、systemd 服务

`/etc/systemd/system/aijobrisk-go.service`：

```ini
[Unit]
Description=aijobrisk-go SSR
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/aijobrisk-go
EnvironmentFile=/opt/aijobrisk-go/.env
ExecStart=/opt/aijobrisk-go/aijobrisk
Restart=on-failure
RestartSec=3
# 加固
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now aijobrisk-go
sudo systemctl status aijobrisk-go
journalctl -u aijobrisk-go -f          # 看启动日志：loaded N occupations / [serve] ...
```

健康检查：`curl -s http://127.0.0.1:4332/api/health`。

## 六、nginx 反代 + TLS

```nginx
server {
    listen 443 ssl http2;
    server_name aijobrisk.com www.aijobrisk.com;

    ssl_certificate     /etc/letsencrypt/live/aijobrisk.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aijobrisk.com/privkey.pem;

    # 静态资源交给 Go（已内置 /static 与 /logo.svg），也可在此加长缓存头
    location /static/ {
        proxy_pass http://127.0.0.1:4332;
        proxy_cache_valid 200 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    location / {
        proxy_pass http://127.0.0.1:4332;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}

server {
    listen 80;
    server_name aijobrisk.com www.aijobrisk.com;
    return 301 https://$host$request_uri;
}
```

TLS 证书用 certbot：`sudo certbot --nginx -d aijobrisk.com -d www.aijobrisk.com`。

## 七、更新与回滚

- **只更新数据**（重新导出 `data/`）：rsync 覆盖 `data/` 后 `systemctl restart aijobrisk-go`（重载入内存，~2s）。
- **更新代码**：服务器上 `git pull` → 重新 `go build` → `systemctl restart`。构建产物可先输出到临时名，验证后原子替换（`mv`）再重启，便于回滚。
- **验证**：`curl -sI https://aijobrisk.com/` 看 200；`/job-risk-map` 看风险图；`/api/health` 看投票健康。

## 八、Blog 无人值守定时发布

> 全自动：**没有人工审稿，也不需要手动部署**。选题来自人工维护的 `scripts/blog_topics.txt`，
> 写作、排期、发布全部自动化；用**自动质量闸门**替代人工审稿，不过闸的稿子不发布。
> 节奏遵循 `docs/blog-plan.md` §8.3：**每周 1 篇**，并始终保留 2 周的已排期存货。

### 8.1 链路

```
GitHub Actions（每天 02:17 UTC，.github/workflows/blog-autopublish.yml）
  └─ draft_blog --ensure-queue 2 --cadence-days 7
       队列里已排期、未到发布日的文章不足 2 篇才起草；够了就什么都不做（不产生 commit）
       每篇：DeepSeek（deepseek-chat）→ 质量闸门 → 不过则重试，最多 3 次
       发布日 = 上一篇之后 +7 天；断更过久则从今天起补发
  └─ build_blog.py  烘焙（未来日期的文章也烘进 index.json）
  └─ commit + push 到 main

服务器 cron（每 10 分钟，ops/blog-pull.sh）
  └─ 独立稀疏镜像 git fetch → 有新提交才继续
  └─ 防误删检查（index.json 文章数骤降 >50% 或坏 JSON → 拒绝）
  └─ reset 镜像 → POST /internal/reload-blog → Go 热重载（不重启、不停服）

Go（internal/data/blog.go）
  └─ 按「UTC 今天」在运行时过滤：未到发布日的文章在列表 / 详情 / 标签 / RSS /
     sitemap / 职业·行业·国家页反向内链里**全部不可见**，到日子自动出现
```

**定时发布的关键**：日期过滤在 Go 运行时做，不在烘焙时做——一次烘焙、一次同步，
文章到日子自己上线，发布当天不需要任何动作。

### 8.2 质量闸门（替代人工审稿，`scripts/draft_blog.py` 的 `quality_gate`）

| 检查 | 不通过的处理 |
|---|---|
| 正文 600–2500 词 | 重试 |
| 至少 2 个 `##` 小节；正文不得有 H1 | 重试 |
| 标题 10–70 字符，有导语 | 重试 |
| 无占位 / 拒答文本（as an AI、lorem ipsum、[insert…、TODO…） | 重试 |
| 分析文正文**不含外链**（无人审稿时编造的「来源链接」最伤可信度） | 重试 |
| 百分比数字 ≤ 8 个（prompt 要求避免无法核实的精确统计） | 重试 |
| 至少 1 条有效的职业内链（blog 的价值约八成在内链，见 blog-plan §0） | 重试 |

只卡**新生成**的稿子，不进烘焙——早期种子文章只有 ~300 词，放进烘焙会被下架。

### 8.3 一次性配置

按顺序做。**第 1 步必须最先**：旧二进制不认识定时过滤，会把未来日期的文章立刻展示出来。

1. **部署新二进制**（含定时过滤 + 重载接口）：服务器 `git pull` → `build.sh` → `restart.sh`。
2. **建博客镜像**（服务器上，需能 `git clone` 仓库——只读 deploy key 即可）：
   ```bash
   bash /opt/career-guides-au/ops/blog-pull.sh --init git@github.com:dannyxstack/career-guides-au.git
   ```
   它会打印三行环境变量，追加到 `/opt/career-guides-au/aijobrisk-go/.env`，然后 `systemctl restart aijobrisk-go`。
   启动日志应出现 `[blog] … dir=/opt/aijobrisk-blog-mirror/… reload-endpoint=true`。
3. **挂 cron**（每 10 分钟；无新提交时静默退出，不刷日志）：
   ```cron
   */10 * * * * /usr/bin/flock -n /tmp/blog-pull.lock bash /opt/career-guides-au/ops/blog-pull.sh >> /var/log/blog-pull.log 2>&1
   ```
4. **GitHub**：Settings → Secrets and variables → Actions → 新建 `DEEPSEEK_API_KEY`。
   若 main 开了分支保护，需允许 `github-actions[bot]` 直接推送。
5. **试跑**：Actions → blog-autopublish → Run workflow。之后每天自动跑。

### 8.4 日常需要关心的只有两件事

- **选题池**：用完会**停止发布并报错**（退出码 3），不会循环复用选题造出近似重复的文章。
  届时往 `scripts/blog_topics.txt` 补选题即可（2026-10 时剩 13 个，约够 3 个月）。
- **失败邮件**：起草失败或选题池耗尽时 Actions 标红，GitHub 会给仓库所有者发邮件。
  单日失败不影响读者——队列里还有 2 周存货，第二天会自动重试。

### 8.5 撤稿 / 手动干预

| 要做的事 | 怎么做 |
|---|---|
| 撤下某篇 | 把它 front-matter 的 `status` 改成 `draft` → 跑 `build_blog.py` → commit + push；10 分钟内下线 |
| 手动插一篇 | `draft_blog --topic "…" --publish-on 2026-11-11` → `build_blog.py` → commit + push |
| 暂停自动发布 | Actions 页面 Disable workflow（已排期的仍会按日上线；要一起停就把它们改成 draft） |
| 立刻同步（不等 cron） | 服务器上 `bash /opt/career-guides-au/ops/blog-pull.sh` |
| 查看队列 | 重载接口 / 启动日志里的 `visible / scheduled / next` |

**博客只走 git 这一条路**：`upload-data.sh` 已排除 `blog/`，服务器上 Go 读的是镜像目录。
不要再往线上 `data/blog` 直接 rsync。

### 8.6 风险与取舍（无人审稿）

`docs/blog-plan.md` §8 列过两类风险：事实错误直接上线，以及 Google 对「批量自动生成内容」的打击。
当前的缓解：选题由人工把关；低频（每周 1 篇，不是批量灌）；质量闸门拦截编造外链、过量统计数字、
拒答文本和无内链的稿子；撤稿 10 分钟内生效。**闸门拦不住「看起来合理但错误」的论断**——
这是去掉人工审稿换来的代价。

## 资源小结

| 项 | 值 |
|---|---|
| 构建内存 | 常规（数据不打进 bundle，无需 16GB） |
| 启动时间 | ~3.9s（加载 20,946 职业 / 4,491 slug） |
| 常驻内存 | RSS ~866MB |
| `data/` 体积 | ~600MB（其中 `translations-v2/` 414MB） |
| 依赖 | Go 标准库 + `go-sql-driver/mysql`（仅投票） |
| MySQL | 可选；挂掉仅影响投票，页面照常 |
