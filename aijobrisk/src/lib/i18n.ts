// aijobrisk SSR 站的显示语言 + 路由前缀（语言第一级、国家最后一级）。
// 见 RULES.md「aijobrisk.com（aijobrisk/ SSR 站）路由规约」。
//
// 说明：显示语言（URL 前缀）共 8 种 = FAQ「2030」译文覆盖集。其中 ko/zh-Hans 在
// data.ts 的 Locale 联合类型里没有对应母本，故内容层（tr/strings/name/countryName）回退到
// contentLocale（英文兜底）；仅 FAQ 问句等已有对应译文的内容按显示语言切换。
// fr 已有完整引用集译文（translations-v2/fr.*），content 直接映射到 'fr'；但旧 UI 字典
// ui_i18n.json 无 fr，故 about/methodology 的 strings() 及 AU sourcesBody 仍英文兜底。
import type { Locale } from './data';

export type Display = 'en' | 'es' | 'fr' | 'de' | 'pt' | 'ja' | 'zh-Hans' | 'ko';

export interface DisplayInfo { code: Display; label: string; content: Locale; hreflang: string }

// nav 语言下拉的顺序与展示名。content = 供 tr()/strings() 使用的数据层 Locale。
export const DISPLAY_LOCALES: DisplayInfo[] = [
  { code: 'en',      label: 'English',  content: 'en',    hreflang: 'en' },
  { code: 'es',      label: 'Español',  content: 'es',    hreflang: 'es' },
  { code: 'fr',      label: 'Français', content: 'fr',    hreflang: 'fr' },
  { code: 'de',      label: 'Deutsch',  content: 'de',    hreflang: 'de' },
  { code: 'pt',      label: 'Português',content: 'pt',    hreflang: 'pt' },
  { code: 'ja',      label: '日本語',    content: 'ja',    hreflang: 'ja' },
  { code: 'zh-Hans', label: '简体中文',  content: 'zh-CN', hreflang: 'zh-Hans' },
  { code: 'ko',      label: '한국어',     content: 'en',    hreflang: 'ko' },
];

export const DISPLAY_CODES = DISPLAY_LOCALES.map((d) => d.code);
const NON_EN = new Set(DISPLAY_CODES.filter((c) => c !== 'en'));
const INFO = new Map(DISPLAY_LOCALES.map((d) => [d.code, d]));

export function isDisplay(x: string | null | undefined): x is Display {
  return !!x && DISPLAY_CODES.includes(x as Display);
}

// 数据层 Locale（供 tr/strings/name/countryName），fr/ko→en、zh-Hans→zh-CN。
export function contentLocale(d: Display): Locale {
  return INFO.get(d)?.content ?? 'en';
}

// 从 Astro 解析当前显示语言：优先 middleware 写入的 locals.locale（已剥前缀并 rewrite），
// 再看 currentLocale，最后用 URL 首段兜底。
export function pageLocale(astro: { locals?: any; currentLocale?: string; url: URL }): Display {
  const l = astro.locals?.locale;
  if (isDisplay(l)) return l;
  const c = astro.currentLocale;
  if (isDisplay(c)) return c;
  const seg = astro.url.pathname.split('/').filter(Boolean)[0];
  return isDisplay(seg) ? seg : 'en';
}

// 给英文裸路径加语言前缀（en 不加）。path 以 '/' 开头。
export function withL(d: Display, path: string): string {
  return d === 'en' ? path : `/${d}${path === '/' ? '' : path}`;
}

// 去掉 pathname 的语言前缀 → 英文裸路径（供语言下拉为当前页构造各语言 URL）。
export function stripLocale(pathname: string): string {
  const parts = pathname.split('/');
  if (parts[1] && NON_EN.has(parts[1] as Display)) {
    const rest = '/' + parts.slice(2).join('/');
    return rest === '/' ? '/' : rest.replace(/\/$/, '');
  }
  return pathname;
}

// —— 语言前缀 + 国家末级的链接构造 ——
export const hrefJob = (d: Display, slug: string, country?: string) =>
  withL(d, country ? `/jobs/${slug}/${country}` : `/jobs/${slug}`);
export const hrefIndustries = (d: Display, country?: string) =>
  withL(d, country ? `/industries/${country}` : '/industries');
export const hrefIndustry = (d: Display, sector: string, country?: string) =>
  withL(d, country ? `/industry/${sector}/${country}` : `/industry/${sector}`);
export const hrefRankings = (d: Display, country?: string) =>
  withL(d, country ? `/rankings/${country}` : '/rankings');
export const hrefBoard = (d: Display, board: string, country?: string) =>
  withL(d, country ? `/rankings/${board}/${country}` : `/rankings/${board}`);
export const hrefCompare = (d: Display, pair?: string) =>
  withL(d, pair ? `/compare/${pair}` : '/compare');
export const hrefMap = (d: Display, country?: string) =>
  withL(d, country ? `/job-risk-map/${country}` : '/job-risk-map');
export const hrefSearch = (d: Display) => withL(d, '/search');
export const hrefAbout = (d: Display) => withL(d, '/about');
export const hrefMethodology = (d: Display) => withL(d, '/methodology');
export const hrefHome = (d: Display) => withL(d, '/');
