# aijobrisk-go 部署文档

Go SSR 版 aijobrisk。**纯标准库 + 单一第三方依赖**（`go-sql-driver/mysql`，仅投票 API 用），无 Web 框架、无 ORM。
单进程、**单端口**同时提供：站点页面 + `/api` 投票 + `sitemap/robots` + `/static` 静态资源。

## 架构要点

- **运行时读数据**：数据（`data/` 约 358MB JSON）在启动时读入内存，**不打进二进制**。
  因此构建**无需 16GB 内存**（区别于 Astro 版）；启动约 **1.9s**；常驻 **RSS ~694MB**（6 语言翻译英文键重复占大头）。
- **投票 DB 懒连接**：`sql.Open` 启动时不拨号，首个投票请求才连 MySQL。
  连不上则投票降级（`GET /api/polls` 返空票、`POST` 503），**页面照常渲染**——"MySQL 挂了站不挂"。
- **语言前缀路由**：显示语言在 URL 第一级（`/fr/...`），英文裸路径无前缀；国家在末级。

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
  data/                # 数据 JSON（~358MB，含 occupations_v2.json / outline-paths.json / translations-v2/ 等）
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
| `POLLS_CORS_ORIGINS` | — | 允许跨域来源；**同端口同源部署可留空（免 CORS）** |
| `POLLS_RATE_MAX` | `20` | 限流：窗口内最大请求数 |
| `POLLS_RATE_WINDOW` | `60` | 限流窗口秒数 |
| `PUBLIC_POLLS_API` | `/api` | 投票组件请求的 API 基址；**同源部署留空即用 `/api`**，仅独立子域时设为完整地址 |
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

## 资源小结

| 项 | 值 |
|---|---|
| 构建内存 | 常规（数据不打进 bundle，无需 16GB） |
| 启动时间 | ~1.9s（加载 6578 职业 / 4861 slug） |
| 常驻内存 | RSS ~694MB |
| 依赖 | Go 标准库 + `go-sql-driver/mysql`（仅投票） |
| MySQL | 可选；挂掉仅影响投票，页面照常 |
