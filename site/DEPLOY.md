# 部署说明 · career-guides 静态站

纯静态 Astro 站（SSG）。构建产物 = `dist/` 静态文件，运行时由 nginx 托管，**容器只暴露 8080**，TLS / 域名由线上已有的反向代理负责。

> 数据 JSON（`src/data/translations.json` 等）已随仓库提供，构建期**不连 MySQL**。
> 若数据有更新，需先在开发机跑 `python -m scripts.export_site_data` 重新导出再提交，然后才构建镜像。

## 文件
- `Dockerfile` — 多阶段：`node:20` 构建 → `nginx:1.27-alpine` 托管。
- `nginx.conf` — 监听 8080，目录式路由、gzip、缓存、安全头。
- `docker-compose.yml` — 构建 + 运行，默认仅绑定 `127.0.0.1:8080`。
- `.dockerignore` — 排除 node_modules/dist。

## 一、在生产机部署（compose 方式）

```bash
# 1. 取代码（含已导出的 src/data/*.json）
cd /opt/career-guides-au/site

# 2. 设置真实域名（sitemap/canonical/hreflang 依赖）
echo 'SITE_URL=https://你的真实域名' > .env

# 3. 构建并启动（首次或更新后）
docker compose up -d --build

# 4. 验证
curl -I http://127.0.0.1:8080/
docker compose ps
```

更新内容后重新部署：`git pull && docker compose up -d --build`

## 二、纯 docker 命令方式（不用 compose）

```bash
docker build --build-arg SITE_URL=https://你的真实域名 -t career-guides-site:latest .
docker run -d --name career-guides-site --restart unless-stopped \
  -p 127.0.0.1:8080:8080 career-guides-site:latest
```

## 三、前置反向代理接入

容器监听 `127.0.0.1:8080`。在已有代理里把站点域名 upstream 指向它即可。

nginx 示例（代理已管 TLS）：
```nginx
server {
    server_name 你的真实域名;
    # ... listen 443 ssl + 证书 ...
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Caddy 示例：
```
你的真实域名 {
    reverse_proxy 127.0.0.1:8080
}
```

## 注意
- **域名必须正确**：`SITE_URL` 不传则回退占位 `https://example.com`，会导致 sitemap/canonical/hreflang 出错。
- 若代理跑在另一台机/容器网络，把 `docker-compose.yml` 的 `127.0.0.1:8080:8080` 改成 `8080:8080`，并在防火墙限制来源。
- 镜像不可变：内容更新必须重新 build（静态站无运行时数据源）。
