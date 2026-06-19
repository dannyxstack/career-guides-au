import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 静态站（SSG）。职业详情/列表/精选对比都在构建期生成。
// 站点 URL 用于 sitemap / canonical / hreflang，部署时务必改成真实域名。
export default defineConfig({
  site: 'https://example.com',
  output: 'static',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  integrations: [sitemap()],
});
