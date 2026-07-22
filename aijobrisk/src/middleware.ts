// 语言前缀路由：/{lang}/... 剥掉前缀，记到 locals.locale，rewrite 到无前缀路径复用同一套页面。
// 英文裸 URL 不经此分支。语言码见 lib/i18n.ts（= FAQ「2030」译文可切换集）。
import { defineMiddleware } from 'astro:middleware';

const LOCALES = new Set(['es', 'fr', 'de', 'pt', 'ja', 'zh-Hans', 'ko']);

export const onRequest = defineMiddleware((context, next) => {
  const seg = context.url.pathname.split('/')[1];
  if (LOCALES.has(seg)) {
    (context.locals as any).locale = seg;
    const rest = context.url.pathname.slice(seg.length + 1) || '/';
    return context.rewrite(rest + context.url.search);
  }
  return next();
});
