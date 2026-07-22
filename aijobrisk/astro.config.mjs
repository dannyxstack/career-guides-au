import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

// aijobrisk.com — SSR 站（按需服务端渲染）。数据层与 site 独立（全部复制）。
// 设计：aijobrisk-design/deepseek 蓝系主题（theme.css）。英文单语，缺译回退英文母本。
export default defineConfig({
  site: 'https://aijobrisk.com',
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  trailingSlash: 'ignore',
  // 语言在第一级：英文裸 URL，其余 /{lang}/ 前缀。由 src/middleware.ts 剥前缀并回写 locals.locale，
  // rewrite 到无前缀路径复用同一套页面（无需复制文件）。语言码 = FAQ「2030」译文可切换集。
  // 见 RULES.md「aijobrisk.com 路由规约」。
});
