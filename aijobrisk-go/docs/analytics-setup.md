# aijobrisk.com 访问统计接入方案

> 目标：拿到 **Requests / UV / PV**，以及其中的 **bot（爬虫）占比**。要求免费、尽量不动业务代码。
> 现状（2026-09-09）：站点**无任何埋点**；域名直接解析到源站 `207.57.133.99`，**未挂 CDN**；
> Go 侧**无访问日志中间件**（只有 boot 日志），唯一的请求记录是服务器上的 nginx access log。

---

## 0. 选型结论（先读这段）

**JS 埋点看不到 bot。** GA4 / Plausible / Umami / Clarity 都是浏览器端 beacon，爬虫不执行 JS，
它们统计到的天然就是「已过滤掉 bot 的人类流量」——分母里根本没有 bot，**永远算不出占比**。

要看 bot 占比只有两条路：**服务端日志分析** 或 **CDN 边缘统计**。

| 方案 | Requests | UV/PV | bot 占比 | 成本 | 改代码 |
|---|:--:|:--:|:--:|---|:--:|
| **① Cloudflare 免费版**（DNS 代理） | ✅ | ✅ | ✅ 粗粒度 | 免费 | 零 |
| **② GoAccess**（读 nginx log 自建） | ✅ | ⚠️ IP+UA 估算 | ✅ 可按 UA 拆到具体爬虫 | 免费 | 零 |
| ③ Go 统计中间件 | ✅ | ⚠️ 估算 | ✅ 规则自定义 | 免费 | 要 |
| GA4 / Plausible / Umami | ❌ | ✅ | ❌ | 免费 | 要 |

**采用 ①+② 双层**：CF 给面板化的全局请求量与 human/bot 划分（零维护），
GoAccess 补 CF 的两个短板——**原始日志级别的 UA 细节**和**长期留存**（CF 免费版分析数据只留约 30 天）。
两者都不需要动 Go 业务代码。③ 作为可选加分项见 §5。

**不想迁 NS** → 只上 ②，需求能满足约 90%，只是 UV 是估算值。

---

## 1. 前置：Go 侧改动（已完成）

`internal/pollsapi/api.go` 的 `clientIP()` 原本只读 `X-Forwarded-For` 首段。挂 CDN 后这条链路会变，
且该头**客户端可伪造**（nginx 用 `proxy_add_x_forwarded_for`，会把客户端自带的 XFF 保留在首位），
伪造头能刷出无限个限流桶、绕过投票的 IP 软去重。

已改为：

- 新增环境变量 **`POLLS_CLIENT_IP_HEADER`**。设了就**只认该头**（挂 CF 时填 `CF-Connecting-IP`，
  该头由 CF 边缘覆写，客户端伪造不了）；留空则沿用 XFF 首段，行为与改动前一致。
- 取到的值**必须是合法 IP**（`net.ParseIP` 校验），否则回退 `RemoteAddr`。
- `RemoteAddr` 改用 `net.SplitHostPort` 拆分，顺带修掉 IPv6 被解析成 `[2001:db8::1]`（带方括号）的问题。

上 CF 后，`/opt/aijobrisk-go/.env` 加一行、重启即可：

```dotenv
POLLS_CLIENT_IP_HEADER=CF-Connecting-IP
```

> ⚠️ **顺序很重要**：这一行要等 CF 代理**真正生效之后**再加。CF 没生效时该头不存在，
> 所有请求会一起回退到 `RemoteAddr`（= nginx 的 127.0.0.1），投票去重会全站塌成同一个桶。

---

## 2. 第一层：Cloudflare 免费版

### 2.1 接入步骤

1. **注册并添加站点**：CF Dashboard → Add a site → `aijobrisk.com` → 选 **Free** 方案。
   CF 会扫描现有 DNS 记录，**逐条核对不要漏**（尤其 MX、TXT/SPF、以及其它域名指向本机的记录）。
2. **迁 NS**：到域名注册商把 NS 改成 CF 给的两个。生效通常几分钟到 24 小时。
3. **开橙云**：`aijobrisk.com` 和 `www` 的 A 记录（`207.57.133.99`）设为 **Proxied（橙色云）**。
   只有橙云的流量才会经过 CF，也才有统计。
4. **SSL/TLS 模式选 `Full (strict)`**。源站已有 certbot 签发的 Let's Encrypt 证书，满足 strict 要求。
   **不要选 Flexible**（CF→源站变明文，且会引发重定向循环）。
5. **确认 certbot 续期不被打断**：`http-01` 挑战走 `/.well-known/acme-challenge/`，橙云下仍可通过，
   但保险起见给该路径加一条 Cache Rule 设为 Bypass，或改用 DNS-01。续期时留意一次即可。

### 2.2 缓存规则（本站是 SSR，务必配）

CF 默认**不缓存 HTML**，所以开箱即安全。要注意的是：

- **绝对不要开 "Cache Everything"**。本站页面按语言前缀 + 国家末段渲染，
  一旦缓存 HTML，多语言/多国家页面会互相串。
- 加一条 Cache Rule：**`/api/*` → Bypass cache**（保护投票 API）。
- `/static/*` 让它缓存：nginx 已经回了 `Cache-Control: public, max-age=604800`，CF 会自动遵守，
  无需额外配置。想更激进可再加一条 Cache Rule 把 Edge TTL 拉长。

### 2.3 让 nginx 记录真实 IP（这一步决定 GoAccess 的 UV 准不准）

挂 CF 后 nginx 看到的 `$remote_addr` 变成 CF 边缘 IP，**access log 里所有请求会长得像同一个访客**，
GoAccess 的 UV 直接废掉。必须配 real_ip：

```nginx
# /etc/nginx/conf.d/cloudflare-realip.conf
# CF IP 段来自 https://www.cloudflare.com/ips-v4 与 /ips-v6，会变更，建议每月刷新
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
# … 其余段照抄官方列表 …
set_real_ip_from 2400:cb00::/32;
# … IPv6 段同理 …
real_ip_header CF-Connecting-IP;
```

生效后 `$remote_addr` 即真实客户端 IP，access log 与 GoAccess 统计恢复正常。
（`CF-Connecting-IP` 头本身仍会原样透传给 Go，不影响 §1 的配置。）

自动刷新 CF IP 段（每月一次 cron）：

```bash
{ curl -s https://www.cloudflare.com/ips-v4; curl -s https://www.cloudflare.com/ips-v6; } | sed 's|^|set_real_ip_from |; s|$|;|' > /etc/nginx/conf.d/cloudflare-realip.conf && echo 'real_ip_header CF-Connecting-IP;' >> /etc/nginx/conf.d/cloudflare-realip.conf && nginx -t && systemctl reload nginx
```

### 2.4 防绕过：只放行 CF 回源

不做这一步，别人直连 `207.57.133.99` 就绕过了 CF（统计缺失 + 防护失效 + 源站 IP 暴露）。
**只限制 80/443，务必不要动 SSH 的 62828 端口**：

```bash
ufw allow 62828/tcp && for ip in $(curl -s https://www.cloudflare.com/ips-v4; curl -s https://www.cloudflare.com/ips-v6); do ufw allow from $ip to any port 443 proto tcp; ufw allow from $ip to any port 80 proto tcp; done
```

> 建议在**另开一个 SSH 会话**的情况下操作，避免把自己关在门外。

### 2.5 在哪看数据

- **Analytics & Logs → Traffic**：Requests、Unique Visitors、Page Views、Top paths、Top countries。
- **Security → Analytics**：按 bot score 划分的 human / automated 流量占比。

> **期望管理**：免费版给的是**粗粒度**的 human vs bot 划分。
> 「GPTBot 抓了多少、Googlebot 抓了多少」这种按爬虫逐个拆的 Bot Analytics 属于付费功能——
> 那个维度用第二层的 GoAccess 拿（§3.4）。免费版数据保留期也短（约 30 天），
> 长期留存同样靠 GoAccess。开通后自己在面板上确认一次粒度是否够用。

---

## 3. 第二层：GoAccess（自建日志分析）

### 3.1 安装与日志格式

```bash
apt-get install -y goaccess
```

确认 nginx access log 用的是 `combined` 格式（默认即是，**必须带 User-Agent**，否则无法识别爬虫）：

```bash
grep -r "access_log\|log_format" /etc/nginx/nginx.conf /etc/nginx/sites-enabled/
```

### 3.2 生成实时 HTML 报表

```bash
goaccess /var/log/nginx/access.log --log-format=COMBINED --persist --restore --db-path=/var/lib/goaccess -o /var/www/stats/index.html --real-time-html
```

- `--persist --restore --db-path=` 把统计**落盘累计**，日志轮转后历史不丢——这是长期留存的关键。
- `--real-time-html` 会起一个 WebSocket 持续刷新；只要静态报表的话去掉该参数、挂 cron 定时跑即可。

### 3.3 报表页必须加保护

报表页会暴露站点全部 URL 和流量结构，**不能裸奔**：

```nginx
location /stats/ {
    auth_basic "stats";
    auth_basic_user_file /etc/nginx/.htpasswd;   # htpasswd -c 创建
    add_header X-Robots-Tag "noindex, nofollow" always;
    alias /var/www/stats/;
}
```

用 `htpasswd -c /etc/nginx/.htpasswd <user>` 创建账号。另外记得 `/stats/` 不要进 sitemap。

### 3.4 看 bot 占比

跑两遍、对比总量，就得到干净的人机拆分：

```bash
goaccess /var/log/nginx/access.log --log-format=COMBINED --crawlers-only -o /var/www/stats/bots.html
```

```bash
goaccess /var/log/nginx/access.log --log-format=COMBINED --ignore-crawlers -o /var/www/stats/humans.html
```

> ⚠️ **GoAccess 自带的爬虫列表偏旧，多半认不出 AI 爬虫**（GPTBot / ClaudeBot / PerplexityBot /
> Bytespider / CCBot 等）。这些会被误算进「真人」，对一个 AI 主题站是致命误差。
> 解决办法是复制一份 `browsers.list` 自定义、把它们加进 `Crawlers` 分组，
> 之后所有 goaccess 命令都带上 `--browsers-file=/etc/goaccess/browsers.custom.list`：

```bash
cp /etc/goaccess/browsers.list /etc/goaccess/browsers.custom.list && printf '%s\n' 'GPTBot,Crawlers' 'OAI-SearchBot,Crawlers' 'ChatGPT-User,Crawlers' 'ClaudeBot,Crawlers' 'Claude-Web,Crawlers' 'anthropic-ai,Crawlers' 'PerplexityBot,Crawlers' 'Bytespider,Crawlers' 'CCBot,Crawlers' 'Google-Extended,Crawlers' 'Applebot-Extended,Crawlers' 'meta-externalagent,Crawlers' >> /etc/goaccess/browsers.custom.list
```

先看看实际都有谁在抓，再决定这个清单还要补什么：

```bash
awk -F'"' '{print $6}' /var/log/nginx/access.log | grep -iE 'bot|crawler|spider|gpt|claude|perplexity|bytespider|ccbot' | sort | uniq -c | sort -rn | head -30
```

### 3.5 日志轮转

`logrotate` 默认按天切、留 14 天。GoAccess 开了 `--persist` 后历史统计不受影响，
但**原始日志**只剩两周。若要保留更久，调 `/etc/logrotate.d/nginx` 的 `rotate` 值并确认磁盘够用。

---

## 4. 验证清单

上线后逐条过：

- [ ] `curl -sI https://aijobrisk.com/` 返回 200，响应头里有 `cf-ray`（说明走了 CF）
- [ ] `curl -sI https://aijobrisk.com/static/app.css` 有 `cf-cache-status: HIT`（缓存生效）
- [ ] `curl -sI https://aijobrisk.com/api/health` 正常，且 `cf-cache-status: BYPASS` 或 `DYNAMIC`
- [ ] 页面投票能正常提交（验证 `POLLS_CLIENT_IP_HEADER` 配对了）
- [ ] `tail -f /var/log/nginx/access.log` 里 IP 是**真实访客 IP**，不是 CF 边缘 IP（real_ip 生效）
- [ ] 连续快速投票会触发 429（限流桶正常，没有因为 IP 全塌成一个而误伤或失效）
- [ ] 直连 `curl -sI --resolve aijobrisk.com:443:207.57.133.99 https://aijobrisk.com/` **超时**（防绕过生效）
- [ ] `/stats/` 需要密码，且返回 `X-Robots-Tag: noindex`
- [ ] 多语言页面抽查：`/es/jobs/...`、`/zh-Hans/jobs/...` 内容没串（缓存规则没配错）

---

## 5. 可选第三层：Go 中间件按 UA 分类

CF 免费版给不了「**哪些职业页被哪个 AI 爬虫抓**」，GoAccess 只能给个大概。
真要做细，可在 `internal/web/server.go` 的 `Router()` 外面包一层中间件：按 UA 正则分类、
按 path 计数，内存聚合后定期 flush 到已有的 MySQL（投票库）。纯标准库即可，不破坏架构约束。

价值点：这个站的主题就是 AI 取代工作，**AI 爬虫的抓取分布本身既是 GEO（生成式引擎优化）效果信号，
也是现成的 blog 选题素材**。

但属于加分项——**建议先把 ①② 跑起来看到真实数据，再决定要不要做**，避免过度设计。

---

## 6. 回滚

- **CF**：把 DNS 记录从 Proxied 改回 DNS only（灰云），流量立刻绕开 CF；彻底回滚则把 NS 改回注册商。
  回滚前记得**先移除 `.env` 里的 `POLLS_CLIENT_IP_HEADER`** 并重启，
  否则该头消失会导致 IP 全塌成 nginx 本地地址。
- **防火墙**：`ufw status numbered` + `ufw delete <n>` 逐条删掉 CF 段放行规则。
- **GoAccess**：纯旁路，删掉 `/stats/` 的 nginx location 和 cron 即可，对站点零影响。
