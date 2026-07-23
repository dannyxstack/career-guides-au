import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 静态站（SSG）。职业详情/列表/精选对比都在构建期生成。
// 站点 URL 用于 sitemap / canonical / hreflang，部署时务必改成真实域名。
export default defineConfig({
  site: 'https://aijobrisk.com',
  output: 'static',
  trailingSlash: 'ignore',
  // 组件作用域 CSS 外置为共享文件（不逐页内联 ~4KB），大幅缩减 128k 页的 dist 体积。
  build: { format: 'directory', inlineStylesheets: 'never' },
  integrations: [sitemap({
    filter: (page) => !page.includes('/risk-map/') && !page.endsWith('.json'),
  })],
});
