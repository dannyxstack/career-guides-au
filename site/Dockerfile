# syntax=docker/dockerfile:1

# ---------- Build stage ----------
# 纯静态 Astro SSG：数据 JSON 已落盘在 src/data/，构建期不需要连 MySQL。
FROM node:20-alpine AS build
WORKDIR /app

# 真实域名经 --build-arg 注入；sitemap/canonical/hreflang 依赖它。
ARG SITE_URL=https://example.com

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# 把 astro.config.mjs 的占位域名替换为真实域名后再构建。
RUN sed -i "s#https://example.com#${SITE_URL}#g" astro.config.mjs \
    && npm run build

# ---------- Runtime stage ----------
FROM nginx:1.27-alpine AS runtime
# 自定义站点配置（监听 8080、目录式路由、gzip、缓存、安全头）。
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
