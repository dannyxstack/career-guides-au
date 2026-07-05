# 社区投票功能 · 架构与部署

给静态站外挂的动态层：用户对职业投票（当前 2 个：AI 替代概率 5 档、是否转行 3 档），
无需注册，跨国家共享（按 slug），展示分布 + 大众平均。通用引擎，加投票只改配置。

## 组成
| 文件 | 作用 |
|---|---|
| `site/src/data/polls.json` | **投票定义单一真相源**（前端与 API 共用）。加投票=加一项 |
| `site/src/lib/polls.ts` | 前端读取定义 + 本地化/平均折算 helper |
| `site/src/components/PollBlock.astro` | 职业页 widget：SSR 题目/选项 + 客户端拉实时/提交 |
| `scripts/seed_polls_schema.py` | 建 3 张表：`poll_votes` / `poll_agg` / `poll_agg_num` |
| `api/polls_api.py` | FastAPI：`GET /api/polls`、`POST /api/polls/vote`、`GET /api/health` |
| `scripts/export_site_data.py` | 构建期把 `poll_agg` 按 slug 烘进 `occupations.json`（`o.polls`）|

数据流：静态页 SSR（烘焙聚合首屏）→ 客户端 `GET` 拉实时 + `POST` 投票 → 写 `poll_votes` +
重算 `poll_agg` → 下次 build 烘焙更新。**跨国共享**：`occ_key = slug`，同名岗各国聚到一处。

## 键与规则
- `occ_key` = 职业 slug（locale/国家无关）。
- 一浏览器一票：`(poll_code, occ_key, client_token)` 唯一，`client_token` 存 localStorage，upsert=可改票。
- 防刷：`ip_hash`(sha256(ip+salt)) 限流 + Turnstile（可选）+ 选项白名单校验 + 参数化 SQL。

## 本地开发
```bash
# 1) 建表（一次）
python -m scripts.seed_polls_schema
# 2) 起 API（默认 CORS 放行 4399/4321，未配 Turnstile=跳过校验）
POLLS_CORS_ORIGINS="http://localhost:4399" \
  python -m uvicorn api.polls_api:app --port 8790
# 3) 前端默认指向 http://localhost:8790/api（PollBlock 里的 API_BASE 默认值），直接 npm run dev 即可
```

## 生产部署
1. **DB 最小权限账号**：只对 `poll_votes/poll_agg/poll_agg_num` 有 SELECT/INSERT/UPDATE/DELETE。
   API 用这个账号（另配一份 .env 或环境变量），不要用能读职业数据的账号。
2. **常驻服务**（systemd 示例）：
   ```ini
   [Service]
   Environment=POLLS_IP_SALT=<随机长串>
   Environment=POLLS_TURNSTILE_SECRET=<Cloudflare Turnstile secret>
   Environment=POLLS_CORS_ORIGINS=https://aicareergraph.com
   Environment=MYSQL_HOST=... MYSQL_USER=<最小权限账号> ...
   ExecStart=/path/python -m uvicorn api.polls_api:app --host 127.0.0.1 --port 8790
   Restart=always
   ```
3. **反代**（nginx）：`api.aicareergraph.com` → `127.0.0.1:8790`，配 TLS。
4. **构建环境变量**：build 时设 `PUBLIC_POLLS_API=https://api.aicareergraph.com/api`
   （否则烘进静态页的是 localhost 默认值）。
5. **前端 Turnstile**（可选但推荐）：在 PollBlock 加 Turnstile widget，把 token 随 POST 带上；
   API 端设了 `POLLS_TURNSTILE_SECRET` 即自动校验。

## 加一个新投票
只改 `site/src/data/polls.json` 加一项（`code`/`q`/`options`；概率型每项带 `mid` 才有大众平均），
下次 build 生效。**表、API、widget 都不用动。** 未来若要滑块型（数值），用 `type:"slider"` +
`answer_num`（`poll_agg_num` 已预留）。

## 运维注意
- API 每请求开一条 DB 连接（`get_cursor`）；量大再加连接池。
- 内存限流是单实例的；多实例部署需换 Redis。
- `poll_agg` 仅供构建期烘焙；`GET` 始终读 `poll_votes` 实时值，不依赖 agg。
