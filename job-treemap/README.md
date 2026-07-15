# job-treemap — 多国 AI 暴露职业树图（独立站）

一套**自包含、可独立部署**的静态站点，用 squarified treemap 展示各国职业的 **AI 自动化暴露度**：
方块面积 = 就业人数（workforce），颜色 = AI 暴露度 0–10（绿低→红高）。

复刻自外部项目:
 [0xtreme/aus-jobs](https://github.com/0xtreme/aus-jobs) ,
 [karpathy/jobs](https://github.com/karpathy/jobs) ,
 [madeye.github.io/jobs](https://madeye.github.io/jobs/)
 的模板思路，
**与主站（`site/` 的 Astro 应用）完全独立**，本目录就是为「**单独域名部署**」准备的。

覆盖 **12 国**：AU · US · UK · CA · NZ · JP · DE · FR · ES · IT · NL · IE。

---

## 目录结构

```
job-treemap/
├── build.py         # 构建脚本：读主站数据 -> 生成 dist/
├── template.html    # 唯一共享模板（内联 CSS/JS，含 __CONFIG__ 占位符）
├── dist/            # 构建产物（可直接部署，见下）
│   ├── index.html          # 总览页：带国家下拉切换器
│   ├── favicon.svg
│   ├── data/{cc}.json      # 总览页按国懒加载的数据（fetch）
│   └── {cc}/               # 每国一个「独立可部署」的单国站
│       ├── index.html      #   自包含页面（模板注入该国 __CONFIG__）
│       ├── data.json       #   该国数据
│       └── favicon.svg
└── dist.zip         # dist 的打包快照（便于传输；不确定是否最新时请重新构建）
```

- **模板只有一份**（`template.html`），所有页面都是它 + 不同的 `__CONFIG__`（JSON）注入而成。
- 所有资源路径均为**相对路径**（`data/{cc}.json`、`data.json`、`./favicon.svg`），
  故可部署在**域名根目录或任意子路径**，无需改代码。

---

## 数据来源

`build.py` 读取主站导出的 v2 数据（**唯一数据源**，本目录不自采数据）：

- `../site/src/data/occupations_v2.json` — 职业数据（英文母本 v2 管线导出）
- `../site/src/data/categories_v2.json` — 分类 slug

字段映射（`build_record()`）：

| 树图字段 | 来自 occupations_v2.json |
|---|---|
| `title` | `name_en`（回退 `slug`） |
| `jobs`（面积） | `workforce_size` |
| `exposure`（颜色，0–10 整数） | `ai.automation_exposure`（四舍五入取整、裁剪 0–10） |
| `pay` | `avg_salary` |
| `exposure_rationale` | `ai.verdict_zh` |
| `aioe_pct` | `ai.aioe_pct` |
| `category` | `category` → `categories_v2.json` 的 slug |
| `anzsco` | `occ_code`（各国为 ANZSCO/SOC/NOC/ISCO/JSCO 等） |

> 各国页脚的「Data sources」文字是 `build.py` 里 `COUNTRY_META` 的**署名引用**（如 AU=JSA/ABS、US=BLS/O*NET…）。
> 底层数值来自 `occupations_v2.json`，其本身按主站管线混合了官方数据与 LLM 估算（部分国家的薪资/就业量为估算，详见主站文档）。

各国货币符号也在 `COUNTRY_META` 中按国切换；未列入 `COUNTRY_META` 的国家（如 CH 占位）会被跳过。

---

## 构建

```bash
# Windows（本项目 Python）
E:\run\Python3.13\python.exe job-treemap/build.py

# 或在任意 python3 环境
python job-treemap/build.py
```

- 无第三方依赖（仅标准库）。
- 前置条件：`../site/src/data/occupations_v2.json` 已是最新（由主站的 `export_site_data_v2` 生成）。
  若主站数据更新了，**先重新导出主站数据，再跑本脚本**。
- 产物全部写入 `dist/`（脚本会覆盖同名文件）。

本地预览（**必须走 HTTP**，`fetch` 不支持 `file://`）：

```bash
cd job-treemap/dist && python -m http.server 8080
# 总览页  http://localhost:8080/
# 单国站  http://localhost:8080/US/
```

---

## 部署（单独域名）

产物是**纯静态文件**，任何静态托管都可（Nginx / Apache / 对象存储+CDN / Netlify / GitHub Pages…）。
只需保证以 **HTTP(S)** 提供（因为要 `fetch` 数据 JSON）。

### 方案 A：整站（推荐，带国家切换）
把整个 `dist/` 作为该域名的 webroot。访客在总览页用下拉切换国家（懒加载 `data/{cc}.json`），
各国单页 `/{cc}/` 也可直接访问。

### 方案 B：仅单国
只部署 `dist/{cc}/`（如 `dist/US/`）即可，该目录**自包含**，无需其它文件。

### Nginx 示例

```nginx
server {
    listen 80;
    server_name treemap.example.com;                 # 你的独立域名
    root /var/www/job-treemap;                        # = dist/ 的内容
    index index.html;

    location / { try_files $uri $uri/ =404; }

    # data.json / data/*.json 用短缓存，页面/图标可长缓存（可选）
    location ~* \.json$   { add_header Cache-Control "public, max-age=3600"; }
    location = /favicon.svg { add_header Cache-Control "public, max-age=604800"; }
}
```

### 上传示例

```bash
# 构建后同步 dist/ 到服务器 webroot
rsync -avz --delete job-treemap/dist/ user@host:/var/www/job-treemap/
# 或用打包快照
scp job-treemap/dist.zip user@host:/tmp/ && ssh user@host 'unzip -o /tmp/dist.zip -d /var/www/job-treemap'
```

> 主站另有一套线上 dist 部署脚本（`scripts/deploy_dist.{sh,ps1}`、`docs/deploy-dist-over-ssh.md`），
> 那是给**主站 Astro dist** 用的，与本目录无关；本站请按上面的方式独立部署到自己的域名。

---

## 更新流程小结

1. 主站数据有变 → 重新导出 `occupations_v2.json`。
2. `python job-treemap/build.py` 重建 `dist/`。
3. `rsync` / `scp` 同步 `dist/` 到独立域名的 webroot。
