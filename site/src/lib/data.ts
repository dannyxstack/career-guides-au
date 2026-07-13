// 站点数据层：消费 Python 导出的 occupations_v2.json（英文母本 v2 管线，DB 为唯一数据源）。
// 过渡期：v2 JSON 沿用旧键名（i18n['zh-CN'] / *_zh 装英文母本），故前端零改动，仅换数据源 + tr 母本。
import data from '../data/occupations_v2.json';
import cats from '../data/categories_v2.json';
// 翻译记忆按语言 + 分片加载：每 locale 拆 N 片到 data/translations-v2/{loc}.{i}.json
// （单文件 9 语言 ~195MB 超 GitHub 100MB 上限；按 locale 拆后 th 仍达 ~51MB 触发 50MB 软警告，
//  故再按 md5(源串)%N 分片，各片 <7MB，随 FR/ES 翻译增长仍有充足余量。分片由 export_site_data_v2.py 生成）
import uiI18n from '../data/ui_i18n.json';

export type Locale = 'zh-CN' | 'zh-Hant' | 'en' | 'es' | 'pt' | 'vi' | 'th' | 'ms' | 'id' | 'ja' | 'de' | 'it' | 'nl';
export const COUNTRIES = ['AU', 'NZ', 'CA', 'US', 'UK', 'DE', 'FR', 'ES', 'IT', 'NL', 'IE'] as const;
export const LOCALES: Locale[] = ['zh-CN', 'zh-Hant', 'en', 'es', 'pt', 'vi', 'th', 'ms', 'id', 'ja', 'de', 'it', 'nl'];
export const DEFAULT = { country: 'AU', locale: 'zh-CN' as Locale };
// 国家 -> 本币代码（薪资/费用展示用）
export const CURRENCY: Record<string, string> = { AU: 'AUD', NZ: 'NZD', CA: 'CAD', US: 'USD', UK: 'GBP', DE: 'EUR', FR: 'EUR', ES: 'EUR', IT: 'EUR', NL: 'EUR', IE: 'EUR' };
// 国家显示名（国家切换器用）
export const COUNTRY_NAME: Record<string, { 'zh-CN': string; en: string }> = {
  AU: { 'zh-CN': '澳大利亚', en: 'Australia' },
  NZ: { 'zh-CN': '新西兰', en: 'New Zealand' },
  CA: { 'zh-CN': '加拿大', en: 'Canada' },
  US: { 'zh-CN': '美国', en: 'United States' },
  UK: { 'zh-CN': '英国', en: 'United Kingdom' },
  DE: { 'zh-CN': '德国', en: 'Germany' },
  FR: { 'zh-CN': '法国', en: 'France' },
  ES: { 'zh-CN': '西班牙', en: 'Spain' },
  IT: { 'zh-CN': '意大利', en: 'Italy' },
  NL: { 'zh-CN': '荷兰', en: 'Netherlands' },
  IE: { 'zh-CN': '爱尔兰', en: 'Ireland' },
};
export const countryName = (cc: string, locale: Locale) =>
  COUNTRY_NAME[cc]?.[locale === 'zh-CN' ? 'zh-CN' : 'en'] || cc;

// 国旗：全站唯一来源，统一用内联 SVG（带 xmlns，含 class="flagsvg" 供 CSS 控制尺寸）。
// 规则：所有国旗必须用 SVG 或静态图片渲染，禁止使用 emoji 国旗（Windows 等平台无区域指示符字形）。
export const COUNTRY_FLAG: Record<string, string> = {
  AU: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#00247D"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#CF142B" stroke-width="3"/><rect x="25" width="10" height="30" fill="#fff"/><rect y="10" width="60" height="10" fill="#fff"/><rect x="27" width="6" height="30" fill="#CF142B"/><rect y="12" width="60" height="6" fill="#CF142B"/><circle cx="30" cy="46" r="4.5" fill="#fff"/><circle cx="95" cy="13" r="2.6" fill="#fff"/><circle cx="106" cy="26" r="2.6" fill="#fff"/><circle cx="90" cy="36" r="2.6" fill="#fff"/><circle cx="101" cy="46" r="2.6" fill="#fff"/><circle cx="86" cy="49" r="1.7" fill="#fff"/></svg>',
  CA: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><rect width="30" height="60" fill="#D52B1E"/><rect x="90" width="30" height="60" fill="#D52B1E"/><path d="M60,11 l4,9 9,-2 -4,8 5,3 -8,4 1,6 -8,-2 -8,2 1,-6 -8,-4 5,-3 -4,-8 9,2 z" fill="#D52B1E"/></svg>',
  NZ: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#00247D"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#CF142B" stroke-width="3"/><rect x="25" width="10" height="30" fill="#fff"/><rect y="10" width="60" height="10" fill="#fff"/><rect x="27" width="6" height="30" fill="#CF142B"/><rect y="12" width="60" height="6" fill="#CF142B"/><circle cx="100" cy="13" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="108" cy="31" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="91" cy="35" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/><circle cx="100" cy="49" r="3" fill="#CF142B" stroke="#fff" stroke-width="1"/></svg>',
  US: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#fff"/><g fill="#B22234"><rect width="120" height="4.62"/><rect y="9.23" width="120" height="4.62"/><rect y="18.46" width="120" height="4.62"/><rect y="27.69" width="120" height="4.62"/><rect y="36.92" width="120" height="4.62"/><rect y="46.15" width="120" height="4.62"/><rect y="55.38" width="120" height="4.62"/></g><rect width="48" height="32.31" fill="#3C3B6E"/><g fill="#fff"><circle cx="6" cy="5" r="1.4"/><circle cx="16" cy="5" r="1.4"/><circle cx="26" cy="5" r="1.4"/><circle cx="36" cy="5" r="1.4"/><circle cx="11" cy="11" r="1.4"/><circle cx="21" cy="11" r="1.4"/><circle cx="31" cy="11" r="1.4"/><circle cx="41" cy="11" r="1.4"/><circle cx="6" cy="17" r="1.4"/><circle cx="16" cy="17" r="1.4"/><circle cx="26" cy="17" r="1.4"/><circle cx="36" cy="17" r="1.4"/><circle cx="11" cy="23" r="1.4"/><circle cx="21" cy="23" r="1.4"/><circle cx="31" cy="23" r="1.4"/><circle cx="41" cy="23" r="1.4"/><circle cx="6" cy="29" r="1.4"/><circle cx="16" cy="29" r="1.4"/><circle cx="26" cy="29" r="1.4"/><circle cx="36" cy="29" r="1.4"/></g></svg>',
  UK: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><clipPath id="ukc"><rect width="120" height="60"/></clipPath><g clip-path="url(#ukc)"><rect width="120" height="60" fill="#012169"/><path d="M0,0 L120,60 M120,0 L0,60" stroke="#fff" stroke-width="12"/><path d="M0,0 L120,60 M120,0 L0,60" stroke="#C8102E" stroke-width="8" clip-path="url(#ukc)"/><rect x="50" width="20" height="60" fill="#fff"/><rect y="20" width="120" height="20" fill="#fff"/><rect x="54" width="12" height="60" fill="#C8102E"/><rect y="24" width="120" height="12" fill="#C8102E"/></g></svg>',
  DE: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="20" fill="#000"/><rect y="20" width="120" height="20" fill="#DD0000"/><rect y="40" width="120" height="20" fill="#FFCE00"/></svg>',
  FR: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#0055A4"/><rect x="40" width="40" height="60" fill="#fff"/><rect x="80" width="40" height="60" fill="#EF4135"/></svg>',
  ES: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="60" fill="#AA151B"/><rect y="15" width="120" height="30" fill="#F1BF00"/></svg>',
  IT: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#008C45"/><rect x="40" width="40" height="60" fill="#F4F5F0"/><rect x="80" width="40" height="60" fill="#CD212A"/></svg>',
  NL: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="120" height="20" fill="#AE1C28"/><rect y="20" width="120" height="20" fill="#fff"/><rect y="40" width="120" height="20" fill="#21468B"/></svg>',
  IE: '<svg class="flagsvg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"><rect width="40" height="60" fill="#169B62"/><rect x="40" width="40" height="60" fill="#fff"/><rect x="80" width="40" height="60" fill="#FF883E"/></svg>',
};
// 标题/SEO 用的简称（中文用习惯简称「澳洲」；其余语言用全称）
const COUNTRY_TITLE_ZH: Record<string, string> = { AU: '澳洲', NZ: '新西兰', CA: '加拿大', US: '美国', UK: '英国', DE: '德国', FR: '法国', ES: '西班牙', IT: '意大利', NL: '荷兰', IE: '爱尔兰' };
export const countryTitleName = (cc: string, locale: Locale) =>
  locale === 'zh-CN' ? (COUNTRY_TITLE_ZH[cc] || cc) : (COUNTRY_NAME[cc]?.en || cc);

// 澳洲移民/职业数据的权威来源链接（用于「关于」页数据来源说明）
export const AU_SOURCE_LINKS: { label: { 'zh-CN': string; en: string }; url: string }[] = [
  { label: { 'zh-CN': '澳洲内政部 · 核心技能职业清单（CSOL，PDF）', en: 'Dept of Home Affairs · Core Skills Occupation List (CSOL, PDF)' },
    url: 'https://immi.homeaffairs.gov.au/Documents/core-sol.pdf' },
  { label: { 'zh-CN': '澳洲内政部 · 技术职业清单总览', en: 'Dept of Home Affairs · Skilled occupation lists' },
    url: 'https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list' },
  { label: { 'zh-CN': '澳洲内政部 · 偏远地区指定移民协议（DAMA）', en: 'Dept of Home Affairs · Designated Area Migration Agreements (DAMA)' },
    url: 'https://immi.homeaffairs.gov.au/visas/employing-and-sponsoring-someone/sponsoring-workers/nominating-a-position/labour-agreements/designated-area-migration-agreements' },
  { label: { 'zh-CN': 'Jobs and Skills Australia（就业与技能署）', en: 'Jobs and Skills Australia (JSA)' },
    url: 'https://www.jobsandskills.gov.au/' },
  { label: { 'zh-CN': '澳洲统计局 · ANZSCO 职业分类', en: 'ABS · ANZSCO occupation classification' },
    url: 'https://www.abs.gov.au/statistics/classifications/anzsco-australian-and-new-zealand-standard-classification-occupations' },
];
export const currencyOf = (country: string) => CURRENCY[country] || 'AUD';

// 翻译记忆解析：中文母本 → 目标语言（回退 en → 原文）。按 locale 分片加载后合并。
// Vite eager glob 收集全部分片，从文件名 `{loc}.{i}.json` 解析 locale 合并成整表。
const TM_BY_LOCALE: Partial<Record<Locale, Record<string, string>>> = {};
{
  const shards = import.meta.glob('../data/translations-v2/*.json', { eager: true }) as
    Record<string, { default: Record<string, string> }>;
  for (const [path, mod] of Object.entries(shards)) {
    const m = path.match(/\/([a-zA-Z-]+)\.\d+\.json$/);
    if (!m) continue;
    const loc = m[1] as Locale;
    (TM_BY_LOCALE[loc] ??= {});
    Object.assign(TM_BY_LOCALE[loc]!, mod.default);
  }
}
export function tr(s: string | null | undefined, locale: Locale): string {
  if (!s) return s || '';
  if (locale === 'en') return s;  // 英文为母本，源串即英文
  const k = s.trim();
  return TM_BY_LOCALE[locale]?.[k] || s;  // 缺译回退英文母本
}
// 是否存在该源串的译文（英文母本恒为真），用于决定走 tr() 还是回退到 curated 英文文案
const hasTr = (s: string, locale: Locale): boolean => {
  if (locale === 'en') return true;
  return !!TM_BY_LOCALE[locale]?.[s.trim()];
};

export interface Occ {
  id: number; country: string; occ_code: string; occ_code_type: string;
  anzsco_code: string; category: string; currency?: string; is_migration: number; is_public_servant?: boolean; shortage_listed: boolean;
  workforce_size: number | null; slug: string; name_en: string; growth_areas?: string[];
  training_zh: string;
  i18n: Record<string, { name: string; summary: string; forecast_note: string; trend_summary: string }>;
  salaries: { label: string; min: number | null; max: number | null; note: string | null }[];
  ratings: { dimension: string; stars: number | null }[];
  overall_score: number | null;
  avg_salary?: number | null;  // 官方平均薪资（年薪，本币），来自 occupation_salaries band='mean'
  // ↓ 懒加载详情字段（occ-detail/{cc}.json，经 occFull() 合并；lean 对象里为 undefined）
  visa?: { subclass: string; name: string; desc: string; min_score?: number | null; score_asof?: string | null }[];
  education: { stage: string; duration: string; cost_min: number | null; cost_max: number | null; cost_note: string | null }[];
  qualifications?: { name: string; issuer: string | null; note: string | null; mandatory: boolean }[];
  suitability?: { fit: string[]; unfit: string[] };
  faqs?: { type: string; question: string; answer: string }[];
  ai?: {
    verdict_type: 'compressed' | 'amplified' | 'mixed';
    verdict_zh: string; entry_narrowing_zh?: string;
    replaced_zh?: string[]; augmented_zh?: string[]; moat_zh?: string[]; skills_zh?: string[];
    upgrade_path_zh?: string | null;
    adjacent?: { slug: string; name_en: string; category: string }[];
    cluster?: string | null;
    automation_exposure?: number | null; human_moat?: number | null;
    entry_risk?: number | null; ai_upside?: number | null;
    // 学术 AI Exposure 指数（Felten 等 AIOE）：aioe_pct=百分位(0-100，越高越暴露)，aioe_soc=映射到的美国SOC码，aioe_method=direct/crosswalk
    aioe_score?: number | null; aioe_pct?: number | null;
    aioe_soc?: string | null; aioe_method?: string | null;
    disruptors?: any[];  // 懒加载详情
  } | null;
}

export const occupations = (data as any).occupations as Occ[];

// ── 详情懒加载：重字段（visa/faqs/qualifications/suitability/growth_areas/ai 文案）拆到
//    occ-detail/{cc}.json，按国一次性加载并缓存。详情页/对比页用 occFull(o) 取合并后的完整对象。──
const _detailGlob = import.meta.glob('../data/occ-detail-v2/*.json') as Record<string, () => Promise<{ default: Record<string, any> }>>;
const _detailCache: Record<string, Record<string, any>> = {};
export async function loadDetail(country: string): Promise<Record<string, any>> {
  if (!_detailCache[country]) {
    const loader = _detailGlob[`../data/occ-detail-v2/${country}.json`];
    _detailCache[country] = loader ? (await loader()).default : {};
  }
  return _detailCache[country];
}
/** 合并 lean 对象与其懒加载详情，返回含全部字段的完整 Occ（详情页/对比页用）。 */
export async function occFull(o: Occ): Promise<Occ> {
  const d = (await loadDetail(o.country))[o.id];
  if (!d) return o;
  return { ...o, ...d, ai: o.ai ? { ...o.ai, ...(d.ai || {}) } : (d.ai ?? o.ai) };
}
export const categories = (cats as any).categories as string[];
export const categorySlug = (cats as any).category_slug as Record<string, string>;
export const slugToCategory: Record<string, string> =
  Object.fromEntries(Object.entries(categorySlug).map(([k, v]) => [v, k]));

export const catSlug = (c: string) => categorySlug[c];
// 按国家取职业（country 省略时为全部，兼容旧调用）
export const occByCountry = (country?: string) =>
  country ? occupations.filter((o) => o.country === country) : occupations;
// 该国实际拥有的分类（用于首页分类 chip）
export const categoriesFor = (country: string) =>
  categories.filter((c) => occupations.some((o) => o.country === country && o.category === c));
export const byCategory = (c: string, country?: string) =>
  occByCountry(country).filter((o) => o.category === c);
export const getBySlug = (slug: string, country?: string) =>
  occByCountry(country).find((o) => o.slug === slug);

// 跨国「同一职业」：按规范化英文名精确匹配其它国家的同名职业（安全、零误链）。
// 各国职业分类体系不同（ANZSCO/NOC/SOC/KldB），仅同名才关联；无同名则不展示。
// 用于在职业页「移民」板块给出「移民到其它国家」的入口（每国取一个）。
const normName = (s: string) => s.trim().toLowerCase();
export function sameOccAbroad(o: Occ): Occ[] {
  const key = normName(o.name_en);
  const seen = new Set<string>();
  const out: Occ[] = [];
  for (const x of occupations) {
    if (x.country === o.country || normName(x.name_en) !== key || seen.has(x.country)) continue;
    seen.add(x.country);
    out.push(x);
  }
  return out;
}

// —— /jobs 一级聚合：按 slug 归一「同一职业跨国」——
// slug 全站一致映射到同一职业（已验证：仅 3 个 slug 因标点差异对应 2 个 name_en，仍是同一职业），
// 故 slug 可安全作为全球主键。每组按 COUNTRIES 顺序排列，Tab 稳定。
const _jobGroups: Map<string, Occ[]> = (() => {
  const m = new Map<string, Occ[]>();
  for (const o of occupations) {
    const a = m.get(o.slug);
    if (a) a.push(o); else m.set(o.slug, [o]);
  }
  const order = new Map(COUNTRIES.map((c, i) => [c as string, i]));
  for (const a of m.values())
    a.sort((x, y) => (order.get(x.country) ?? 99) - (order.get(y.country) ?? 99));
  return m;
})();
export const JOB_SLUGS: string[] = [..._jobGroups.keys()];
// 职业页多语言矩阵生成的语言：全 11 语言全覆盖（en 为默认=裸 URL，其余用 /{locale}/ 前缀）。
export const JOBS_LOCALES: Locale[] = ['en', 'zh-CN', 'zh-Hant', 'es', 'pt', 'vi', 'th', 'ms', 'id', 'ja', 'de', 'it', 'nl'];
// 全量渲染职业详情页的语言（优先语种）。其余 JOBS_LOCALES 只出 noindex 轻量桩页（canonical→英文），
// URL 仍有效、hreflang 不断链，但不生成完整重型页面，大幅缩减 dist。
export const FULL_JOB_LOCALES: Locale[] = ['en', 'zh-CN', 'zh-Hant', 'ja', 'es', 'pt'];
export const isFullJobLocale = (l: Locale) => FULL_JOB_LOCALES.includes(l);
// 干净分类前缀 URL：en 裸 /{cat}/{slug}[/{cc}]，其余 /{locale}/{cat}/{slug}[/{cc}]。
// 分类段取该 slug 代表副本（rep=首国）的分类，全站唯一（同 slug 跨国用同一分类段）。
export function jobHref(locale: Locale, slug: string, country?: string): string {
  const g = _jobGroups.get(slug);
  const cat = g ? catSlug(g[0].category) : '';
  const base = country ? `/${cat}/${slug}/${country}` : `/${cat}/${slug}`;
  return locale === 'en' ? base : `/${locale}${base}`;
}
// hreflang alternates（含全部 JOBS_LOCALES）；x-default 由页面单独指向英文裸 URL
export function jobAlternates(slug: string, country?: string): { locale: string; href: string }[] {
  return JOBS_LOCALES.map((l) => ({ locale: l, href: jobHref(l, slug, country) }));
}
export interface JobGroup { slug: string; rep: Occ; countries: Occ[] }
// 取某 slug 的全球聚合：rep 供全球 AI/名称（AI 块跨国一致），countries 为各国数据
export function jobBySlug(slug: string): JobGroup | null {
  const a = _jobGroups.get(slug);
  if (!a || a.length === 0) return null;
  return { slug, rep: a[0], countries: a };
}

export function name(o: Occ, locale: Locale) {
  const zh = o.i18n['zh-CN']?.name;
  return (zh ? tr(zh, locale) : '') || o.i18n['zh-CN']?.name || o.name_en;
}
export function summary(o: Occ, locale: Locale) {
  return tr(o.i18n['zh-CN']?.summary, locale) || '';
}

// 评分维度多语言标签
export const DIM_LABEL: Record<string, Partial<Record<Locale, string>>> = {
  learning_difficulty: { 'zh-CN': '学习难度', en: 'Learning' },
  learning_duration: { 'zh-CN': '学习周期', en: 'Duration' },
  certification_difficulty: { 'zh-CN': '考证难度', en: 'Certification' },
  job_demand: { 'zh-CN': '职位需求', en: 'Demand' },
  competition: { 'zh-CN': '竞争度', en: 'Competition' },
  work_intensity: { 'zh-CN': '工作强度', en: 'Intensity' },
  income_level: { 'zh-CN': '收入水平', en: 'Income' },
  future_prospect: { 'zh-CN': '发展前景', en: 'Prospects' },
  ai_risk: { 'zh-CN': 'AI替代风险', en: 'AI Risk' },
  pr_friendliness: { 'zh-CN': '移民友好度', en: 'PR Friendly' },
  pr_difficulty: { 'zh-CN': '移民难度', en: 'PR Difficulty' },
};
// AI 替代工具：类型 / 替代程度 标签（仅 zh-CN/en 母本，其余回退 en）
const DIS_TYPE: Record<string, Partial<Record<Locale, string>>> = {
  tool: { 'zh-CN': '工具', en: 'Tool' },
  platform: { 'zh-CN': '平台', en: 'Platform' },
  product: { 'zh-CN': '产品', en: 'Product' },
  model: { 'zh-CN': '模型', en: 'Model' },
  research: { 'zh-CN': '研究', en: 'Research' },
  news: { 'zh-CN': '新闻', en: 'News' },
};
const DIS_LEVEL: Record<string, Partial<Record<Locale, string>>> = {
  partial: { 'zh-CN': '部分替代', en: 'Partial' },
  major: { 'zh-CN': '大幅替代', en: 'Major' },
  full: { 'zh-CN': '几乎完全替代', en: 'Near-full' },
};
export const disType = (k: string, locale: Locale) => DIS_TYPE[k]?.[locale] || DIS_TYPE[k]?.['en'] || k;
export const disLevel = (k: string, locale: Locale) => DIS_LEVEL[k]?.[locale] || DIS_LEVEL[k]?.['en'] || k;

const UI_I18N = uiI18n as Record<string, { ui?: Record<string, string>; dim?: Record<string, string>; dimdesc?: Record<string, string> }>;
export const dimLabel = (dim: string, locale: Locale) =>
  DIM_LABEL[dim]?.[locale] || UI_I18N[locale]?.dim?.[dim] || DIM_LABEL[dim]?.['en'] || dim;

// 维度优势/劣势释义（含极性方向）：解释该维度评分高/低意味着什么
export const DIM_DESC: Record<string, Partial<Record<Locale, string>>> = {
  income_level: { 'zh-CN': '越高越好：薪资天花板与议价空间更大', en: 'Higher is better: greater pay ceiling and bargaining power' },
  job_demand: { 'zh-CN': '越高越好：岗位更多、更易就业', en: 'Higher is better: more openings, easier to find work' },
  future_prospect: { 'zh-CN': '越高越好：行业增长与晋升空间更好', en: 'Higher is better: stronger industry growth and advancement' },
  pr_friendliness: { 'zh-CN': '越高越好：技术移民路径更顺畅', en: 'Higher is better: smoother skilled-migration pathway' },
  ai_risk: { 'zh-CN': '越低越好：不易被自动化取代', en: 'Lower is better: less likely to be automated' },
  competition: { 'zh-CN': '越低越好：求职/晋升对手更少', en: 'Lower is better: fewer rivals for jobs and promotion' },
  work_intensity: { 'zh-CN': '越低越好：体力/加班压力更小', en: 'Lower is better: less physical strain and overtime' },
  learning_difficulty: { 'zh-CN': '越低越好：入门更轻松', en: 'Lower is better: easier to get started' },
  learning_duration: { 'zh-CN': '越短越好：更快入行', en: 'Shorter is better: faster entry to the field' },
  certification_difficulty: { 'zh-CN': '越低越好：资质更易取得', en: 'Lower is better: qualifications easier to obtain' },
  pr_difficulty: { 'zh-CN': '越低越好：移民门槛/排队更少', en: 'Lower is better: fewer migration hurdles and shorter queues' },
};
export const dimDesc = (dim: string, locale: Locale) =>
  DIM_DESC[dim]?.[locale] || UI_I18N[locale]?.dimdesc?.[dim] || DIM_DESC[dim]?.['en'] || '';

// UI 文案（仅 zh-CN/en 为母本；其余语言经 strings() 回退到 en）
export const UI: Record<string, Record<string, string>> = {
  'zh-CN': {
    siteTitle: 'AI Career Graph', tagline: 'AI 时代职业图谱与职业规划 · 不卖课只讲数据',
    homeMetaDesc: 'AI Career Graph 用职业图谱分析 AI 时代的工作风险、薪资、移民路径、入门难度和未来技能，帮助你判断哪些职业会被压缩，哪些会被 AI 放大。',
    agMetaDesc: '查看 AI 时代职业图谱：按自动化风险、人类护城河、执照责任、现场依赖和人际信任，把职业分成高替代、AI增强、强执照、强现场等类型。',
    salary: '薪资范围', ratings: '职业评分', overall: '综合评分', education: '教育路径',
    overallTip: '综合评分 = 各评分维度的平均分（10 分制）；负向维度（AI 替代风险、竞争、学习难度等）按反向计入，分数越高代表整体越好。评分为综合公开来源的估算，定期更新，仅供参考。',
    visaCode: '职业分类代码',
    qualifications: '从业资质', visa: '移民路径', visaToSuffix: '（前往{c}）', migrateOther: '把这个职业移民到其它国家',
    suitability: '适合 / 不适合', faq: '常见问题',
    compare: '职业对比', nonMig: '非技术移民职业（不在技术移民清单上）', fit: '适合', unfit: '不适合',
    experience: '经验阶段', annual: '年薪', cost: '费用', code: '职业代码', backHome: '← 全部职业',
    growth: '职业前景', growthKw: '增长方向 / 热词', compareTitle: '对比', vs: 'vs', winner: '更优', note: '估算数据，仅供参考',
    sources: '数据来源', sourcesBody: '本页薪资为综合 Seek、Indeed、Glassdoor、ERI SalaryExpert 等招聘平台公开区间的估算；就业与需求预测引用 Jobs and Skills Australia（JSA）及澳洲统计局（ABS）；签证与移民信息以澳大利亚内政部（Department of Home Affairs）最新职业清单及相关评估机构为准。数据仅供参考，请以官方最新发布为准。',
    seniorPay: '资深薪资', training: '培训周期',
    heroValue: '按薪资、PR 移民路径、培训时长、职位需求与「被 AI 替代风险」来探索职业。',
    ctaBrowse: '浏览全部职业', ctaCompare: '对比两个职业',
    searchPh: '搜索职业…', sortBy: '排序', allCareers: '全部职业',
    fPR: '可技术移民', fHigh: '高薪', fShort: '短培训', noResult: '没有匹配的职业',
    sortOverall: '综合评分', sortPay: '资深薪资', sortTrain: '培训时长', sortPR: 'PR 友好度',
    secMigration: '最适合移民', secIncome: '高收入职业', secFast: '最快入行', secCats: '职业大类',
    migOcc: '技术移民职业', migRestrictedOcc: '受限移民职业（仅雇主担保/DAMA）',
    migRestrictedNote: '本职业不在独立技术移民清单（189/190/491）上，无法直接申请普通技术移民；但可通过雇主担保（482/494）、偏远地区指定协议（DAMA）或劳务协议等通道移民——通道与名额受限，以 Department of Home Affairs 最新规定及 CSOL 清单为准。',
    byDim: '逐项对比', dimension: '维度',
    stage: '阶段', period: '周期', qualification: '资质', issuer: '发证机构',
    mandatory: '必备', optional: '可选', visaCol: '签证', descCol: '说明',
    nonMigVisa: '签证路径需按具体职责匹配对应 ANZSCO，以 Department of Home Affairs 最新职业清单及相关评估机构结果为准。',
    inviteCutoff: '{asof} 竞争性获邀约 {n} 分（参考）',
    aiTitle: 'AI 时代：{name}会怎样', aiVerdict: 'AI 时代风险结论',
    aiReplaced: 'AI 会接管/替代/消除的任务', aiAugmented: 'AI 会增强的任务', aiMoat: '人类护城河',
    aiEntry: '入门岗位是否变窄', aiSkills: '未来 5 年建议补的技能',
    aiUpgrade: 'AI 时代升级路线', aiAdjacent: '风险高时可考虑的相邻职业',
    aiDisrupt: '已经在替代这个职业的 AI（工具 / 产品 / 研究 / 新闻）', aiDisruptAlso: '也影响：',
    navHome: '首页', navAbout: '关于', navGraph: 'AI 图谱', navRisk: 'AI 风险地图',
    agTitle: 'AI 职业图谱：哪些工作会被压缩，哪些会被放大？',
    agSubtitle: '我们按任务可自动化程度、执照责任、现场操作、人际信任和监管责任，把职业分成 6 类。',
    agMatrix: '图谱视图（二维矩阵）', agAxisX: 'AI 可自动化程度（低 → 高）', agAxisY: '人类责任 / 现场依赖（低 → 高）',
    agQuadTL: '最稳', agQuadTR: 'AI 增强型', agQuadBL: '传统稳定 · 增长有限', agQuadBR: '高风险压缩区',
    agCore: '核心判断', agAction: '行动建议', agRepJobs: '代表职业',
    agWhy: '为什么这类受 AI 影响', agFit: '适合的人', agUnfit: '不适合的人',
    agActionIn: '已入行：下一步补什么', agActionOut: '还没入行：是否值得进入', agPivot: '推荐转向',
    agScores: '四项评分（1-5）', agAuto: 'AI 自动化程度', agMoat: '人类护城河', agEntry: '入门压缩', agUpside: 'AI 放大',
    agMyPos: '{name}在 AI 图谱中的位置', agViewGraph: '查看完整 AI 职业图谱 →',
    navRank: '职业榜单',
    rkHubTitle: 'AI 时代职业榜单', rkHubSub: '不同的人关心不同的问题：怕被替代、想移民、想高薪、想快速入行。我们按多个维度给出榜单，而不是一个总榜。',
    rkViewFull: '查看完整榜单 →', rkRank: '排名', rkReason: '推荐理由', rkRelated: '相关榜单',
    rkWhyHeader: '榜单解释', rkAiRisk: 'AI 风险', rkGrowth: '未来增长', rkPay: '高级薪资', rkPr: 'PR 友好',
    rkAll: '完整榜单', rkSrcTitle: '数据来源与方法',
    rkMethod: '榜单排名由各职业的评分维度（AI 替代风险、职位需求、PR 友好度等）与「AI 图谱」四项评分（自动化程度、人类护城河、入门压缩、AI 放大）按公开规则的排序公式自动计算，并非人工指定。评分与薪资为综合公开数据的估算，定期更新，仅供参考，具体以官方最新发布为准。',
    homeRkTitle: 'AI 时代职业榜单', homeRkBody: '怕被替代？想移民？想高薪？想快速入行？我们按不同维度给出 8 个榜单，帮你找到适合自己的方向。',
    homeAgTitle: 'AI 时代职业图谱',
    homeAgBody: '不是所有职业都会被 AI 取代。更准确地说，AI 会重写每个职业的任务结构：有些岗位被压缩，有些被放大，有些因为执照、现场操作、照护关系和公共责任而更稳。我们把职业分成 6 类，帮你判断：现在的工作风险在哪里，未来 5 年该补什么技能，以及可以转向哪些更稳的职业。',
    vCompressed: '被自动化压缩', vAmplified: '被 AI 放大能力', vMixed: '喜忧参半',
    winnerNote: '"更优"按维度极性判断（负向维度如 AI 风险 / 竞争 / 难度越低越好）。',
    // —— 全球首页（/[locale]/） ——
    hLead: '在 AI 时代规划你的职业。',
    hHeadline: 'AI 正在重塑全球 {n} 职业：你的工作还在安全区吗？',
    hSub: '探索 AI 如何改变各国的工作：自动化风险、人类护城河、薪资、移民路径、榜单与未来职业路线。',
    hCtaSearch: '搜索职业', hCtaCountry: '选择国家', hCtaMap: '探索 AI 职业图谱',
    hSearchPh: '输入职业或国家，查 AI 替代风险',
    hSearchHint: '在 {n} 个职业中全局搜索 —— 结果按国家标注。',
    hPickCountry: '选择国家', hCountryMeta: '{n} 个职业 · 薪资 · 移民 · AI 风险', hEnter: '进入{name} →',
    hCapH: '你可以做什么',
    hCap1T: 'AI 职业图谱', hCap1B: '看清哪些职业被压缩、被放大、受执照保护或受人际信任保护。',
    hCap2T: '职业榜单', hCap2B: '找出低 AI 风险、高增长、移民友好、高薪与快速入行的职业。',
    hCap3T: '职业对比', hCap3B: '从薪资、AI 风险、培训时长、移民路径和未来前景对比两个职业。',
    hCap4T: '各国职业指南', hCap4B: '按国家了解本地薪资、执照、移民与就业市场状况。',
    hMethodH: '我们的方法', hMethodB: '我们综合公开的劳动力市场数据、职业分类、薪资区间、移民路径和 AI 时代任务分析。我们的目标不是完美预测未来，而是帮助人们提出更好的职业问题。',
    // —— 热门职业搜索板块 ——
    hHotH: '热门职业搜索', hHotB: '大家都在查这些职业的 AI 风险与前景',
    // —— 首页滚动播报（构建期预生成，占位符 {name}/{cat}/{pct}/{n}/{a}{b}{c}）——
    hTk1: '{cat} 领域 AI 暴露最高的职业：{a}、{b}、{c}',
    hTk2: '预计未来 5 年，{name} 被 AI 替代的概率约 {pct}%',
    hTk6: '{name} 的 AI 暴露度为 {pct}/100',
    hTk4: '{n} 位「{name}」从业者考虑转行（来自访客投票）',
    hTk5: '{n} 人认为「{name}」被 AI 替代的风险约 {pct}%（来自访客投票）',
    hWhoH: '适合谁',
    hWho1: '正在选专业的学生', hWho2: '对比职业路径的移民申请人', hWho3: '担心被 AI 替代的从业者',
    hWho4: '寻找更稳路径的转行者', hWho5: '帮孩子规划未来工作的父母',
    hQH: '人们常问的问题',
    hQ1T: 'AI 会影响我的职业吗？', hQ1B: '在 AI 职业图谱上逐项查看你的工作是被压缩、被放大还是受保护。', hQ1Go: '查看 AI 图谱 →',
    hQ2T: '哪些工作更稳？', hQ2B: '在榜单中浏览低 AI 风险、高增长和移民友好的职业。', hQ2Go: '查看榜单 →',
    hQ3T: 'AI 时代我该学什么？', hQ3B: '搜索你的职业，查看未来技能、AI 时代升级路线和更稳的相邻职业。', hQ3Go: '搜索职业 →',
    hBottomCountry: '选择你的国家', hBottomRank: '探索 AI 职业榜单', hBottomSearch: '搜索你的职业',
    hFoot: 'AI Career Graph · AI 时代数据驱动的职业指南 · 仅为估算，请始终核对官方来源。',
    // —— /jobs 职业聚合页 ——
    jLead: '下方是全球通用的 AI 影响分析；选择一个国家可查看当地薪资、执照与移民数据。',
    jByCountry: '按国家查看本地数据', jWork: '从业人口', jAvail: '可用国家',
    jAioeT: 'AI 暴露指数（学术 · AIOE）', jAioeD: '暴露程度高于约 {pct}% 的职业（百分位，越高越易受 AI 影响）',
    jTitleG: 'AI 替代风险、被 AI 取代的部分与人类护城河', jTitleC: 'AI 风险、薪资、移民与职业路线',
    jClassic: '打开{c}完整旧版详情页',
    // —— 首页搜索结果（客户端）——
    hSrNoResults: '未找到相关职业。', hSrAvailIn: '可查看国家：',
    hSrAiAugmented: 'AI 增强型', hSrAiLowRisk: '低 AI 替代风险', hSrAiHigherExp: '较高 AI 暴露', hSrAiMixed: 'AI 影响不一',
    hSrMigFriendly: '移民友好', hSrMigRestricted: '受限移民',
    // —— 全球「关于」页（/[locale]/about/） ——
    abTitle: '关于 AI Career Graph',
    abLead: 'AI Career Graph 是一个面向 AI 时代的职业图谱项目——它不止于描述职业，更帮助你判断哪些职业会被 AI 压缩、哪些会被放大、未来 5 年该补什么，以及可以转向哪些更稳的职业。',
    abS1h: '我们是谁',
    abS1: 'AI Career Graph 是一个面向 AI 时代的职业图谱项目，帮助学生、转行者、移民申请人和在职专业人士理解各国不同职业的风险、机会与转型路径。',
    abS2h: '我们要解决的问题',
    abS2a: '我们不只是问"AI 会不会取代这份工作"——而是拆解职业内部哪些任务会被自动化、哪些会被放大、哪些能力仍然需要人。',
    abS2b: '我们把职业分成 6 类（AI 高暴露 / AI 增强 / 执照型 / 现场型 / 人际信任型 / 受监管型），并逐项标注：AI 会接管的任务、AI 会增强的任务、人类护城河、入门是否变窄、AI 时代升级路线，以及风险高时可转向的相邻职业。',
    abS3h: '我们如何分析职业',
    abS3a: '每个职业按多个维度评分：AI 自动化风险、人类护城河、入门压缩、AI 放大潜力、薪资、需求、执照与移民友好度。',
    abS3b: 'AI 职业图谱把职业可视化在二维矩阵上（自动化暴露 × 人类责任/现场依赖）。AI 时代榜单按这些维度给出多个榜单，由透明、可复现的公式自动计算，而非人工指定。',
    abS7h: '11 个评分维度',
    abS7lead: '每个职业按以下 11 个维度评分（10 分制，详情页以星星展示）。维度分正向或负向：正向越高越好，负向越低越好。综合评分在反转负向维度后取平均。',
    abS4h: '数据来源与方法',
    abS4a: '我们汇总公开数据：招聘平台薪资区间、官方职业分类（如澳新的 ANZSCO、加拿大的 NOC、美国和英国的 SOC、德国的 KldB、法国的 ROME、西班牙的 CNO）、移民主管机构的职业清单和就业机构的需求预测，并在其上构建评分模型。',
    abS4b: '所有薪资、评分和移民细节均为估算、仅供参考，并定期更新——请始终以最新官方来源为准。',
    abS5h: '我们不做什么',
    abS5: '我们不卖课，也不提供移民、法律或财务建议，更不保证就业或签证结果。所有内容仅供参考。',
    abS6h: '接下来',
    abS6: '我们从澳大利亚起步，已扩展到加拿大、新西兰和美国，并持续完善每个国家的 AI 时代分析与职业路径数据。',
    abCountrySrcH: '各国数据来源',
    abCountrySrcNote: '薪资、执照和移民细节因国家而异，遵循各国官方来源。完整来源链接见各国指南：',
    abCountryGuide: '— 国家指南 →',
    filterCountries: '国家：', colCountry: '国家',
  },
  en: {
    siteTitle: 'AI Career Graph', tagline: 'AI-era career map & planning · data, not courses',
    homeMetaDesc: 'AI Career Graph maps careers by automation risk, human moat, salary, migration pathways and future skills, helping you plan work in the AI era.',
    agMetaDesc: 'Explore the AI-era career map: occupations grouped by automation risk, human moat, licensing accountability, on-site dependence and human trust — from high-replacement to AI-augmented, licensed and on-site clusters.',
    salary: 'Salary', ratings: 'Ratings', overall: 'Overall', education: 'Education Path',
    overallTip: 'Overall score = the average of all rating dimensions (out of 10); negative dimensions (AI risk, competition, learning difficulty, etc.) are counted inversely, so a higher score means better overall. Scores are estimates aggregated from public sources, updated periodically and indicative only.',
    visaCode: 'Occupation classification code',
    qualifications: 'Qualifications', visa: 'Migration', visaToSuffix: ' (to {c})', migrateOther: 'Migrate this occupation to other countries',
    suitability: 'Who it fits', faq: 'FAQ',
    compare: 'Compare', nonMig: 'Not a skilled migration occupation', fit: 'Fits', unfit: 'Not for',
    experience: 'Experience', annual: 'Annual', cost: 'Cost', code: 'Occupation code', backHome: '← All occupations',
    growth: 'Career outlook', growthKw: 'Growth areas', compareTitle: 'Compare', vs: 'vs', winner: 'Higher', note: 'Estimated data, indicative only',
    sources: 'Data sources', sourcesBody: 'Salary ranges are estimates aggregated from public listings on Seek, Indeed, Glassdoor and ERI SalaryExpert; employment and demand forecasts cite Jobs and Skills Australia (JSA) and the Australian Bureau of Statistics (ABS); visa and migration details follow the latest occupation lists from the Department of Home Affairs and the relevant assessing authorities. Figures are indicative only — always refer to the latest official sources.',
    seniorPay: 'Senior pay', training: 'Training',
    heroValue: 'Explore careers by salary, PR pathway, training time, job demand, and AI replacement risk.',
    ctaBrowse: 'Browse careers', ctaCompare: 'Compare two careers',
    searchPh: 'Search occupation…', sortBy: 'Sort', allCareers: 'All careers',
    fPR: 'PR pathway', fHigh: 'High salary', fShort: 'Short training', noResult: 'No matching occupations',
    sortOverall: 'Overall score', sortPay: 'Senior pay', sortTrain: 'Training time', sortPR: 'PR friendly',
    secMigration: 'Best for migration', secIncome: 'Best high-income careers', secFast: 'Fastest entry careers', secCats: 'Categories',
    migOcc: 'Skilled migration occupation', migRestrictedOcc: 'Restricted migration (employer-sponsored / DAMA only)',
    migRestrictedNote: 'This occupation is not on the independent skilled migration lists (189/190/491), so standard points-tested migration is not available; however migration is possible via employer sponsorship (482/494), Designated Area Migration Agreements (DAMA) or labour agreements — pathways and places are limited. Refer to the latest Department of Home Affairs rules and the CSOL.',
    byDim: 'By dimension', dimension: 'Dimension',
    stage: 'Stage', period: 'Duration', qualification: 'Qualification', issuer: 'Issuer',
    mandatory: 'Required', optional: 'Optional', visaCol: 'Visa', descCol: 'Details',
    nonMigVisa: 'Visa pathways depend on matching the specific duties to the correct ANZSCO; refer to the latest Department of Home Affairs occupation lists and the relevant assessing authorities.',
    inviteCutoff: '~{n} pts competitive cut-off ({asof}, indicative)',
    aiTitle: 'In the AI era: what happens to {name}', aiVerdict: 'AI-era verdict',
    aiReplaced: 'Tasks AI will take over or replace', aiAugmented: 'Tasks AI will augment', aiMoat: 'Human moat',
    aiEntry: 'Entry-level outlook', aiSkills: 'Skills to build (next 5 years)',
    aiUpgrade: 'How to level up in the AI era', aiAdjacent: 'Adjacent careers if risk is high',
    aiDisrupt: 'AI already replacing this job (tools / products / research / news)', aiDisruptAlso: 'Also affects:',
    navHome: 'Home', navAbout: 'About', navGraph: 'AI map', navRisk: 'AI Risk Map',
    agTitle: 'AI Career Map: which jobs get compressed, which get amplified?',
    agSubtitle: 'We group occupations into 6 clusters by automation exposure, licensing/accountability, on-site work, human trust and regulatory responsibility.',
    agMatrix: 'Map view (2D matrix)', agAxisX: 'AI automation exposure (low → high)', agAxisY: 'Human accountability / on-site (low → high)',
    agQuadTL: 'Most resilient', agQuadTR: 'AI-augmented', agQuadBL: 'Stable but limited growth', agQuadBR: 'High compression risk',
    agCore: 'Core verdict', agAction: 'What to do', agRepJobs: 'Representative occupations',
    agWhy: 'Why this cluster is affected', agFit: 'Who it fits', agUnfit: 'Who it does not fit',
    agActionIn: 'Already in it: what to build next', agActionOut: 'Not yet in: is it worth entering', agPivot: 'Pivot toward',
    agScores: 'Four scores (1-5)', agAuto: 'Automation exposure', agMoat: 'Human moat', agEntry: 'Entry compression', agUpside: 'AI upside',
    agMyPos: 'Where {name} sits in the AI map', agViewGraph: 'See the full AI Career Map →',
    navRank: 'Rankings',
    rkHubTitle: 'AI-era career rankings', rkHubSub: 'Different people care about different things: fear of replacement, migration, pay, fast entry. We give several rankings, not one master list.',
    rkViewFull: 'See full ranking →', rkRank: 'Rank', rkReason: 'Why', rkRelated: 'Related rankings',
    rkWhyHeader: 'About this ranking', rkAiRisk: 'AI risk', rkGrowth: 'Growth', rkPay: 'Senior pay', rkPr: 'PR-friendly',
    rkAll: 'Full ranking', rkSrcTitle: 'Data sources & methodology',
    rkMethod: 'Rankings are computed automatically by transparent formulas from each occupation’s rating dimensions (AI risk, demand, PR friendliness, etc.) and the four AI-map scores (automation exposure, human moat, entry compression, AI upside) — not hand-picked. Scores and salaries are estimates aggregated from public data, updated periodically and indicative only.',
    homeRkTitle: 'AI-era career rankings', homeRkBody: 'Afraid of replacement? Want migration, high pay, or fast entry? We offer 8 rankings across different dimensions to help you find your direction.',
    homeAgTitle: 'The AI-era career map',
    homeAgBody: 'Not every job will be replaced by AI. More precisely, AI rewrites the task structure of every job: some roles get compressed, some amplified, and some stay resilient thanks to licensing, on-site work, care relationships and public responsibility. We group occupations into 6 clusters to help you judge where your job risk is, what to build in the next 5 years, and which more durable roles you can pivot to.',
    vCompressed: 'Compressed by automation', vAmplified: 'Amplified by AI', vMixed: 'Mixed',
    winnerNote: '"Higher" is judged by dimension polarity (for negative dimensions such as AI risk / competition / difficulty, lower is better).',
    // —— Global home (/[locale]/) ——
    hLead: 'Plan your career in the age of AI.',
    hHeadline: 'AI is reshaping {n} jobs worldwide — is yours still in the safe zone?',
    hSub: 'Explore how AI changes jobs across countries: automation risk, human moat, salary, migration pathways, rankings and future career routes.',
    hCtaSearch: 'Search a career', hCtaCountry: 'Choose a country', hCtaMap: 'Explore the AI Career Map',
    hSearchPh: 'Type job name and check risk',
    hSearchHint: 'Global search across {n} careers — results are tagged by country.',
    hPickCountry: 'Choose a country', hCountryMeta: '{n} careers · salary · migration · AI risk', hEnter: 'Enter {name} →',
    hCapH: 'What you can do',
    hCap1T: 'AI Career Map', hCap1B: 'See which jobs are compressed, amplified, protected by licensing, or protected by human trust.',
    hCap2T: 'Career Rankings', hCap2B: 'Find low-AI-risk, high-growth, migration-friendly, high-salary and fast-entry careers.',
    hCap3T: 'Career Comparisons', hCap3B: 'Compare two careers by salary, AI risk, training time, migration pathway and future outlook.',
    hCap4T: 'Country Career Guides', hCap4B: 'Explore local salary, licensing, immigration and job-market conditions by country.',
    hMethodH: 'Our methodology', hMethodB: 'We combine public labour-market data, occupation classifications, salary ranges, migration pathways and AI-era task analysis. Our goal is not to predict the future perfectly, but to help people ask better career questions.',
    // —— Popular career searches ——
    hHotH: 'Popular career searches', hHotB: 'What people are checking for AI risk and outlook',
    // —— Home ticker (pre-generated at build; placeholders {name}/{cat}/{pct}/{n}/{a}{b}{c}) ——
    hTk1: 'Highest AI-exposure roles in {cat}: {a}, {b}, {c}',
    hTk2: '{name}: estimated ~{pct}% chance of AI displacement within 5 years',
    hTk6: '{name} has an AI exposure score of {pct}/100',
    hTk4: '{n} people working as {name} are considering a career switch (visitor poll)',
    hTk5: "{n} readers rate {name}'s AI-replacement risk at about {pct}% (visitor poll)",
    hWhoH: "Who it's for",
    hWho1: 'Students choosing a major', hWho2: 'Immigrants comparing career pathways', hWho3: 'Workers worried about AI replacement',
    hWho4: 'Career changers looking for safer routes', hWho5: 'Parents helping children plan future work',
    hQH: 'Questions people ask',
    hQ1T: 'Will AI affect my career?', hQ1B: 'See whether your job is compressed, amplified or protected — task by task — on the AI Career Map.', hQ1Go: 'See the AI map →',
    hQ2T: 'Which jobs are safer?', hQ2B: 'Browse low-AI-risk, high-growth and migration-friendly careers in the rankings.', hQ2Go: 'View rankings →',
    hQ3T: 'What should I learn in the AI era?', hQ3B: 'Search your career to see future skills, an AI-era upgrade path and safer adjacent roles.', hQ3Go: 'Search a career →',
    hBottomCountry: 'Choose your country', hBottomRank: 'Explore AI Career Rankings', hBottomSearch: 'Search your career',
    hFoot: 'AI Career Graph · Data-driven occupation guides for the AI era · Estimates only, always check official sources.',
    // —— /jobs occupation aggregate ——
    jLead: 'A global AI analysis is below; pick a country for local salary, licensing and migration data.',
    jByCountry: 'Local data by country', jWork: 'Workforce', jAvail: 'Available countries',
    jAioeT: 'AI Exposure Index (AIOE)', jAioeD: 'More exposed than about {pct}% of occupations (percentile; higher = more exposed to AI)',
    jTitleG: 'AI risk, what AI replaces & the human moat', jTitleC: 'AI risk, salary, migration & career path',
    jClassic: 'Open the full {c} guide (classic page)',
    // —— Home search results (client-side) ——
    hSrNoResults: 'No careers found.', hSrAvailIn: 'Available in:',
    hSrAiAugmented: 'AI-augmented', hSrAiLowRisk: 'Low AI replacement risk', hSrAiHigherExp: 'Higher AI exposure', hSrAiMixed: 'Mixed AI impact',
    hSrMigFriendly: 'Migration-friendly', hSrMigRestricted: 'Restricted migration',
    // —— Global About (/[locale]/about/) ——
    abTitle: 'About AI Career Graph',
    abLead: 'AI Career Graph is a career-mapping project for the AI era — beyond describing jobs, it helps you judge which roles get compressed by AI, which get amplified, what to build over the next 5 years, and which more durable roles you can pivot to.',
    abS1h: 'Who we are',
    abS1: 'AI Career Graph is a career-mapping project for the AI era, helping students, career changers, migration applicants and working professionals understand the risks, opportunities and transition paths of different occupations across countries.',
    abS2h: 'The problem we solve',
    abS2a: 'We don’t simply ask “will AI replace this job?” — we break down which tasks within a job get automated, which get amplified, and which capabilities still require humans.',
    abS2b: 'We group occupations into 6 clusters (high AI exposure / AI-augmented / licensed / on-site / human-trust / regulated) and annotate each: tasks AI will take over, tasks AI will augment, the human moat, whether entry-level narrows, an AI-era upgrade path, and adjacent careers to pivot to if risk is high.',
    abS3h: 'How we analyse occupations',
    abS3a: 'Each occupation is scored across several dimensions: AI automation risk, human moat, entry-level narrowing, AI-augmentation upside, salary, demand, licensing and migration friendliness.',
    abS3b: 'The AI Career Map visualises occupations on a 2D matrix (automation exposure × human accountability/on-site). The AI-era rankings give several lists across these dimensions, computed by transparent, reproducible formulas — not hand-picked.',
    abS7h: 'The 11 rating dimensions',
    abS7lead: 'Each occupation is scored across the following 11 dimensions (10-point scale, shown as stars on detail pages). Dimensions are either positive or negative: for positive ones higher is better, for negative ones lower is better. The overall score averages them after inverting the negative dimensions.',
    abS4h: 'Data sources & methodology',
    abS4a: 'We aggregate public data: job-platform salary ranges, official occupation classifications (e.g. ANZSCO for Australia/New Zealand, NOC for Canada, SOC for the United States and the United Kingdom, KldB for Germany, ROME for France, CNO for Spain), migration authorities’ occupation lists and employment agencies’ demand forecasts, and build a scoring model on top.',
    abS4b: 'All salaries, scores and migration details are estimates and indicative only, updated periodically — always rely on the latest official sources.',
    abS5h: 'What we don’t do',
    abS5: 'We don’t sell courses, and we don’t provide migration, legal or financial advice, nor guarantee employment or visa outcomes. All content is for information only.',
    abS6h: 'What’s next',
    abS6: 'Starting with Australia, we have expanded to Canada, New Zealand and the United States, and continue to refine the AI-era analysis and career-path data for each country.',
    abCountrySrcH: 'Country data sources',
    abCountrySrcNote: 'Salary, licensing and migration details differ by country and follow each country’s official sources. See the country guide for full source links:',
    abCountryGuide: '— country guide →',
    filterCountries: 'Countries:', colCountry: 'Country',
  },
};

// 取某语言的 UI 文案，缺失键回退到 en
export function strings(locale: Locale): Record<string, string> {
  return { ...UI['en'], ...(UI_I18N[locale]?.ui || {}), ...(UI[locale] || {}) };
}

// 数据来源文案：按国家区分（AU 走 UI 字典的 10 语言；CA/NZ 给 zh/en，其余语言回退 en）
const SOURCES_BODY: Record<string, { 'zh-CN': string; en: string }> = {
  CA: {
    'zh-CN': '本页薪资为综合 Job Bank、Indeed、Glassdoor、ERI SalaryExpert 等公开区间的估算；就业与需求预测引用加拿大统计局（Statistics Canada）及加拿大就业与社会发展部（ESDC / Job Bank）；移民信息以加拿大移民部（IRCC）的快速通道（Express Entry）与各省提名（PNP）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Job Bank, Indeed, Glassdoor and ERI SalaryExpert; employment and demand outlook cite Statistics Canada and ESDC (Job Bank); immigration details follow the latest IRCC Express Entry and Provincial Nominee (PNP) rules. Figures are indicative only — always refer to the latest official sources.',
  },
  NZ: {
    'zh-CN': '本页薪资为综合 Seek NZ、Trade Me Jobs、Glassdoor、PayScale 等公开区间的估算；就业与需求预测引用新西兰统计局（Stats NZ）及商业、创新与就业部（MBIE）；移民信息以新西兰移民局（Immigration New Zealand）的 Green List 及技术移民（SMC / AEWV）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Seek NZ, Trade Me Jobs, Glassdoor and PayScale; employment and demand outlook cite Stats NZ and MBIE; immigration details follow the latest Immigration New Zealand Green List and skilled migration (SMC / AEWV) rules. Figures are indicative only — always refer to the latest official sources.',
  },
  US: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、ERI SalaryExpert 及美国劳工统计局（BLS OEWS）等公开区间的估算；就业与需求预测引用美国劳工统计局（BLS Occupational Outlook）及 O*NET；签证与移民信息以美国公民及移民服务局（USCIS）的工作签证（H-1B / O-1 / L-1）与职业移民绿卡（EB-2 / EB-3，含劳工部 PERM 劳工证）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor, ERI SalaryExpert and the U.S. Bureau of Labor Statistics (BLS OEWS); employment and demand outlook cite the BLS Occupational Outlook and O*NET; visa and migration details follow the latest USCIS work-visa (H-1B / O-1 / L-1) and employment-based green-card (EB-2 / EB-3, incl. DOL PERM labor certification) rules. Figures are indicative only — always refer to the latest official sources.',
  },
  UK: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、Reed、ONS ASHE（年度工时与收入调查）等公开区间的估算；就业与需求预测引用英国国家统计局（ONS）及 HMRC PAYE 数据；签证与移民信息以英国签证与移民局（UKVI）的技术工作签证（Skilled Worker）、全球人才（Global Talent）、医疗与护理（Health and Care）及短缺职业清单（Immigration Salary List）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor, Reed and ONS ASHE (Annual Survey of Hours and Earnings); employment and demand outlook cite the Office for National Statistics (ONS) and HMRC PAYE data; visa and migration details follow the latest UK Visas and Immigration (UKVI) Skilled Worker, Global Talent, Health and Care, and Immigration Salary List rules. Figures are indicative only — always refer to the latest official sources.',
  },
  DE: {
    'zh-CN': '本页薪资为综合 StepStone、Glassdoor、Gehalt.de 及德国联邦统计局（destatis）等公开区间的估算；就业与需求预测引用德国联邦劳工局（Bundesagentur für Arbeit）及 destatis；签证与移民信息以德国《技术移民法》（Fachkräfteeinwanderungsgesetz）下的欧盟蓝卡（EU Blue Card）、技术工人签证、求职机会卡（Chancenkarte）及学历认证（Anerkennung）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on StepStone, Glassdoor, Gehalt.de and the Federal Statistical Office (destatis); employment and demand outlook cite the Federal Employment Agency (Bundesagentur für Arbeit) and destatis; visa and migration details follow the latest German Skilled Immigration Act (Fachkräfteeinwanderungsgesetz) rules covering the EU Blue Card, skilled-worker visa, Opportunity Card (Chancenkarte) and qualification recognition (Anerkennung). Figures are indicative only — always refer to the latest official sources.',
  },
  FR: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、APEC、HelloWork 等公开区间的估算；就业与需求预测引用法国就业局（France Travail）、法国国家统计与经济研究所（INSEE）及劳动研究院（DARES）；签证与移民信息以法国《外国人入境与居留法》下的欧盟蓝卡（Carte bleue européenne）、人才护照（Passeport Talent）、受雇工作居留（Salarié）及受规管职业的资质认证（reconnaissance des qualifications）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor, APEC and HelloWork; employment and demand outlook cite France Travail, the National Institute of Statistics (INSEE) and DARES; visa and migration details follow the latest French rules covering the EU Blue Card (Carte bleue européenne), the Talent Passport (Passeport Talent), the Salarié work-residence permit and qualification recognition (reconnaissance des qualifications) for regulated professions. Figures are indicative only — always refer to the latest official sources.',
  },
  ES: {
    'zh-CN': '本页薪资为综合 InfoJobs、Indeed、Glassdoor、Tecnoempleo 等公开区间的估算；就业与需求预测引用西班牙国家就业局（SEPE）及国家统计局（INE）；签证与移民信息以西班牙《企业家法》（Ley 14/2013）下的欧盟蓝卡（Tarjeta azul UE）、高技能专业人才居留、受雇工作居留（Cuenta ajena）及受规管职业的学历认证（homologación）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on InfoJobs, Indeed, Glassdoor and Tecnoempleo; employment and demand outlook cite the Spanish Public Employment Service (SEPE) and the National Statistics Institute (INE); visa and migration details follow the latest Spanish rules covering the EU Blue Card (Tarjeta azul UE), the highly-qualified professional permit under Ley 14/2013, the Cuenta ajena work-residence permit and qualification recognition (homologación) for regulated professions. Figures are indicative only — always refer to the latest official sources.',
  },
  IT: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、JobPricing 等公开区间及意大利国家统计局（ISTAT）与欧盟统计局（Eurostat）数据的估算；就业与需求预测引用 ISTAT 与 Eurostat；签证与移民信息以意大利欧盟蓝卡（Carta blu UE）、《移民配额法令》（Decreto Flussi）下的受雇工作居留（Nulla Osta）及受规管职业的资质认证（riconoscimento）最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor and JobPricing alongside the National Institute of Statistics (ISTAT) and Eurostat; employment and demand outlook cite ISTAT and Eurostat; visa and migration details follow the latest Italian rules covering the EU Blue Card (Carta blu UE), employer-sponsored permits (Nulla Osta) under the annual quota decree (Decreto Flussi) and qualification recognition (riconoscimento) for regulated professions. Figures are indicative only — always refer to the latest official sources.',
  },
  NL: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、Nationale Beroepengids 等公开区间及荷兰统计局（CBS）与欧盟统计局（Eurostat）数据的估算；就业与需求预测引用 CBS 与 Eurostat；签证与移民信息以荷兰高技能移民（Kennismigrant）、欧盟蓝卡、应届毕业生求职年（Orientation Year）及荷兰移民局（IND）认证雇主担保与薪资门槛最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor and the Nationale Beroepengids alongside Statistics Netherlands (CBS) and Eurostat; employment and demand outlook cite CBS and Eurostat; visa and migration details follow the latest Dutch rules covering the Highly Skilled Migrant (Kennismigrant) route, the EU Blue Card, the Orientation Year for graduates and IND recognised-sponsor employment with salary thresholds. Figures are indicative only — always refer to the latest official sources.',
  },
  IE: {
    'zh-CN': '本页薪资为综合 Indeed、Glassdoor、IrishJobs 等公开区间及爱尔兰中央统计局（CSO）与欧盟统计局（Eurostat）数据的估算；就业与需求预测引用 CSO 与 Eurostat；签证与移民信息以爱尔兰关键技能就业许可（Critical Skills Employment Permit）、一般就业许可（General Employment Permit）、欧盟蓝卡及企业、贸易与就业部（DETE）薪资门槛最新规则为准。数据仅供参考，请以官方最新发布为准。',
    en: 'Salary ranges are estimates aggregated from public listings on Indeed, Glassdoor and IrishJobs alongside the Central Statistics Office (CSO) and Eurostat; employment and demand outlook cite the CSO and Eurostat; visa and migration details follow the latest Irish rules covering the Critical Skills Employment Permit, the General Employment Permit, the EU Blue Card and the salary thresholds set by the Department of Enterprise, Trade and Employment (DETE). Figures are indicative only — always refer to the latest official sources.',
  },
};
// 移民/签证文案：按国家区分（AU 走 UI 字典的 10 语言；US/NZ/CA 给 zh/en，其余语言经 tr() 回退 en）。
// 各国签证类别为公开事实；不在此杜撰个案资格，仅指明通道与主管部门。
interface MigText { restrictedOcc: Bi; mig1Tip: Bi; mig2Tip: Bi; restrictedNote: Bi; nonMigVisa: Bi; }
const MIG_TEXT: Record<string, MigText> = {
  US: {
    restrictedOcc: { 'zh-CN': '受限移民职业（仅雇主担保）', en: 'Restricted migration (employer-sponsored only)' },
    mig1Tip: { 'zh-CN': '该职业通常支持美国「工作签证→职业移民绿卡」通道（H-1B 工签，后续 EB-2 / EB-3 绿卡）；这是一条移民路径，并非保证，也不代表「只有绿卡才能从事」。以 USCIS 最新规定为准。',
               en: 'This occupation commonly supports US work-to-green-card pathways (H-1B, then EB-2 / EB-3) — a pathway, not a guarantee, and not a requirement to already hold a green card. Refer to USCIS.' },
    mig2Tip: { 'zh-CN': '该职业较难走常规职业移民，但可通过雇主担保（H-1B 工签后申请 EB-3 绿卡，含 PERM 劳工证）移民——名额与配额紧张。以 USCIS 最新规定为准。',
               en: 'Standard employment-based migration is harder for this occupation, but it is possible via employer sponsorship (H-1B then EB-3, incl. PERM labor certification) — caps and quotas are tight. Refer to USCIS.' },
    restrictedNote: { 'zh-CN': '本职业不在常见的快速职业移民通道上，无法直接积分移民；但可通过雇主担保（H-1B 工签 + EB-3 绿卡，含劳工部 PERM 劳工证）移民——名额与配额受限，以 USCIS 最新规定为准。',
                      en: 'This occupation is not on a fast employment-based track and has no points-tested route; however migration is possible via employer sponsorship (H-1B + EB-3, incl. DOL PERM labor certification) — caps and quotas are limited. Refer to the latest USCIS rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配相应申请类别，以美国公民及移民服务局（USCIS）最新规定及对应申请类别结果为准。',
                  en: 'Visa pathways depend on matching the specific duties to the right petition category; refer to the latest USCIS rules and the relevant category.' },
  },
  NZ: {
    restrictedOcc: { 'zh-CN': '受限移民职业（仅雇主担保 / AEWV）', en: 'Restricted migration (employer-sponsored / AEWV only)' },
    mig1Tip: { 'zh-CN': '该职业在新西兰移民局（INZ）的 Green List 或技术移民（SMC）通道上，是一条居留路径；与你当前签证身份无关，也不代表「只有居民才能从事」。以 INZ 最新规定为准。',
               en: "This occupation is on Immigration New Zealand's Green List or skilled migration (SMC) pathway — a residence pathway, not a requirement to already hold residence. Refer to INZ." },
    mig2Tip: { 'zh-CN': '该职业不在 Green List 直接居留通道上，但可通过认证雇主工签（AEWV）等通道，后续申请居留——通道受限。以 INZ 最新规定为准。',
               en: 'Not on the Green List straight-to-residence track, but migration is possible via an accredited-employer work visa (AEWV) then residence — a restricted pathway. Refer to INZ.' },
    restrictedNote: { 'zh-CN': '本职业不在 Green List 直接居留通道上，无法直接技术移民；但可通过认证雇主工签（AEWV）等通道后续申请居留——通道与名额受限，以新西兰移民局（INZ）最新规定为准。',
                      en: 'This occupation is not on the Green List straight-to-residence track, so direct skilled migration is unavailable; however migration is possible via an accredited-employer work visa (AEWV) then residence — pathways and places are limited. Refer to the latest Immigration New Zealand rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 ANZSCO，以新西兰移民局（Immigration New Zealand）最新职业清单及相关规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct ANZSCO; refer to the latest Immigration New Zealand occupation lists and rules.' },
  },
  CA: {
    restrictedOcc: { 'zh-CN': '受限移民职业（仅雇主担保 / LMIA）', en: 'Restricted migration (employer-sponsored / LMIA only)' },
    mig1Tip: { 'zh-CN': '该职业支持加拿大技术移民（快速通道 Express Entry / 省提名 PNP），是一条移民路径；与你当前签证身份无关，也不代表「只有 PR 才能从事」。以 IRCC 最新规定为准。',
               en: 'This occupation supports Canadian skilled migration (Express Entry / Provincial Nominee Program) — a pathway, not a requirement to already hold PR. Refer to IRCC.' },
    mig2Tip: { 'zh-CN': '该职业较难直接走快速通道，但可通过雇主担保（LMIA 工签）或省提名（PNP）通道移民——通道受限。以 IRCC 最新规定为准。',
               en: 'Direct Express Entry may be harder, but migration is possible via employer sponsorship (LMIA work permit) or a Provincial Nominee Program (PNP) — a restricted pathway. Refer to IRCC.' },
    restrictedNote: { 'zh-CN': '本职业较难直接走快速通道（Express Entry），但可通过雇主担保（LMIA 工签）或省提名（PNP）通道移民——通道与名额受限，以加拿大移民部（IRCC）最新规定为准。',
                      en: 'Direct Express Entry may be unavailable for this occupation, but migration is possible via employer sponsorship (LMIA work permit) or a Provincial Nominee Program (PNP) — pathways and places are limited. Refer to the latest IRCC rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 NOC，以加拿大移民部（IRCC）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct NOC; refer to the latest IRCC rules.' },
  },
  UK: {
    restrictedOcc: { 'zh-CN': '受限移民职业（仅雇主担保）', en: 'Restricted migration (employer-sponsored only)' },
    mig1Tip: { 'zh-CN': '该职业通常可走英国「技术工作签证（Skilled Worker）→ 永居（ILR）」通道，部分高技能者亦可走全球人才签证（Global Talent）；这是一条移民路径，并非保证，也不代表「只有持永居才能从事」。以英国签证与移民局（UKVI）最新规定为准。',
               en: 'This occupation commonly supports the UK Skilled Worker visa (then settlement / ILR), and high-skill talent may use Global Talent — a pathway, not a guarantee, and not a requirement to already hold settlement. Refer to UK Visas and Immigration (UKVI).' },
    mig2Tip: { 'zh-CN': '该职业较难走常规技术签证，但仍可能通过持牌雇主担保（Skilled Worker）或医疗与护理签证（Health and Care）等通道移民——薪资门槛与名额受限。以 UKVI 最新规定为准。',
               en: 'Standard skilled routes are harder for this occupation, but migration may still be possible via a licensed employer (Skilled Worker) or the Health and Care visa — salary thresholds and places are limited. Refer to UKVI.' },
    restrictedNote: { 'zh-CN': '本职业不在常规技术移民通道上，无法直接积分移民；但可通过持牌雇主担保（Skilled Worker）等通道移民——是否满足薪资门槛与英语要求需个案评估，以英国签证与移民局（UKVI）最新规定为准。',
                      en: 'This occupation is not on a standard skilled track and has no direct points route; however migration is possible via a licensed-employer Skilled Worker sponsorship — meeting salary thresholds and English requirements is assessed case by case. Refer to the latest UKVI rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 SOC 与薪资门槛，以英国签证与移民局（UKVI）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct SOC and salary threshold; refer to the latest UKVI rules.' },
  },
  DE: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需学历认证 / 雇主担保）', en: 'Restricted migration (qualification recognition / employer-sponsored)' },
    mig1Tip: { 'zh-CN': '该职业通常可走德国《技术移民法》下的欧盟蓝卡（EU Blue Card）或技术工人签证，并可申请永久居留；这是一条移民路径，并非保证，通常需先完成学历认证（Anerkennung）。以德国主管机关最新规定为准。',
               en: 'This occupation commonly supports the EU Blue Card or skilled-worker visa under the German Skilled Immigration Act (with a route to permanent residence) — a pathway, not a guarantee, usually requiring qualification recognition (Anerkennung). Refer to the German authorities.' },
    mig2Tip: { 'zh-CN': '该职业较难直接走蓝卡，但可通过求职机会卡（Chancenkarte）或雇主担保的技术工人签证等通道移民——通常需学历认证且名额受限。以德国主管机关最新规定为准。',
               en: 'The Blue Card route may be harder, but migration is possible via the Opportunity Card (Chancenkarte) or an employer-sponsored skilled-worker visa — usually needing qualification recognition, with limited places. Refer to the German authorities.' },
    restrictedNote: { 'zh-CN': '本职业不在直接蓝卡通道上，无法直接技术移民；但可通过求职机会卡（Chancenkarte）或雇主担保的技术工人签证移民——通常需先完成学历认证（Anerkennung），通道与名额受限，以德国《技术移民法》及主管机关最新规定为准。',
                      en: 'This occupation is not on the direct Blue Card track, so direct skilled migration is unavailable; however migration is possible via the Opportunity Card (Chancenkarte) or an employer-sponsored skilled-worker visa — usually requiring qualification recognition (Anerkennung), with limited pathways and places. Refer to the latest Skilled Immigration Act rules and German authorities.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 KldB 职业并完成学历认证，以德国主管机关（Make it in Germany / 联邦劳工局）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct KldB occupation and on qualification recognition; refer to the latest German authorities (Make it in Germany / Federal Employment Agency).' },
  },
  FR: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需资质认证 / 雇主担保）', en: 'Restricted migration (qualification recognition / employer-sponsored)' },
    mig1Tip: { 'zh-CN': '该职业通常可走法国欧盟蓝卡（Carte bleue européenne）或人才护照（Passeport Talent）／受雇工作居留（Salarié），并可申请长期居留；这是一条移民路径，并非保证，受规管职业通常需先完成资质认证（reconnaissance）。以法国主管机关最新规定为准。',
               en: 'This occupation commonly supports the French EU Blue Card (Carte bleue européenne) or the Talent Passport (Passeport Talent) / Salarié permit, with a route to long-term residence — a pathway, not a guarantee, and regulated professions usually require qualification recognition (reconnaissance). Refer to the French authorities.' },
    mig2Tip: { 'zh-CN': '该职业较难直接走蓝卡或人才护照，但可通过雇主担保的受雇工作居留（Salarié）或紧缺职业（métier en tension）通道移民——通常需资质认证且名额受限。以法国主管机关最新规定为准。',
               en: 'The Blue Card or Talent Passport route may be harder, but migration is possible via an employer-sponsored Salarié permit or the shortage-occupation (métier en tension) route — usually needing qualification recognition, with limited places. Refer to the French authorities.' },
    restrictedNote: { 'zh-CN': '本职业不在直接蓝卡／人才护照通道上，无法直接技术移民；但可通过雇主担保的受雇工作居留（Salarié）或紧缺职业通道移民——通常需先完成资质认证（reconnaissance），通道与名额受限，以法国主管机关最新规定为准。',
                      en: 'This occupation is not on the direct Blue Card / Talent Passport track, so direct skilled migration is unavailable; however migration is possible via an employer-sponsored Salarié permit or the shortage-occupation route — usually requiring qualification recognition (reconnaissance), with limited pathways and places. Refer to the latest French authorities.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 ROME 职业，受规管职业需完成资质认证（reconnaissance），以法国主管机关（France Travail / 内政部）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct ROME occupation, with qualification recognition (reconnaissance) for regulated professions; refer to the latest French authorities (France Travail / Ministry of the Interior).' },
  },
  ES: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需学历认证 / 雇主担保）', en: 'Restricted migration (qualification recognition / employer-sponsored)' },
    mig1Tip: { 'zh-CN': '该职业通常可走西班牙欧盟蓝卡（Tarjeta azul UE）或《企业家法》（Ley 14/2013）下的高技能专业人才居留，并可申请长期居留；这是一条移民路径，并非保证，受规管职业通常需先完成学历认证（homologación）。以西班牙主管机关最新规定为准。',
               en: 'This occupation commonly supports the Spanish EU Blue Card (Tarjeta azul UE) or the highly-qualified professional permit under Ley 14/2013, with a route to long-term residence — a pathway, not a guarantee, and regulated professions usually require qualification recognition (homologación). Refer to the Spanish authorities.' },
    mig2Tip: { 'zh-CN': '该职业较难直接走蓝卡或高技能通道，但可通过雇主担保的受雇工作居留（Cuenta ajena）或紧缺职业（Catálogo de ocupaciones de difícil cobertura）通道移民——通常需学历认证且名额受限。以西班牙主管机关最新规定为准。',
               en: 'The Blue Card or highly-qualified route may be harder, but migration is possible via an employer-sponsored Cuenta ajena permit or the shortage-occupation catalogue (ocupaciones de difícil cobertura) — usually needing qualification recognition, with limited places. Refer to the Spanish authorities.' },
    restrictedNote: { 'zh-CN': '本职业不在直接蓝卡／高技能通道上，无法直接技术移民；但可通过雇主担保的受雇工作居留（Cuenta ajena）或紧缺职业通道移民——通常需先完成学历认证（homologación），通道与名额受限，以西班牙主管机关最新规定为准。',
                      en: 'This occupation is not on the direct Blue Card / highly-qualified track, so direct skilled migration is unavailable; however migration is possible via an employer-sponsored Cuenta ajena permit or the shortage-occupation route — usually requiring qualification recognition (homologación), with limited pathways and places. Refer to the latest Spanish authorities.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 CNO 职业，受规管职业需完成学历认证（homologación），以西班牙主管机关（SEPE / 移民总局）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct CNO occupation, with qualification recognition (homologación) for regulated professions; refer to the latest Spanish authorities (SEPE / immigration office).' },
  },
  IT: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需资质认证 / 雇主担保）', en: 'Restricted migration (qualification recognition / employer-sponsored)' },
    mig1Tip: { 'zh-CN': '该职业通常可走意大利欧盟蓝卡（Carta blu UE）或《移民配额法令》（Decreto Flussi）下的受雇工作居留（Nulla Osta），并可申请长期居留；这是一条移民路径，并非保证，受规管职业通常需先完成资质认证（riconoscimento）。以意大利主管机关最新规定为准。',
               en: 'This occupation commonly supports the Italian EU Blue Card (Carta blu UE) or an employer-sponsored work permit (Nulla Osta) under the annual quota decree (Decreto Flussi), with a route to long-term residence — a pathway, not a guarantee, and regulated professions usually require qualification recognition (riconoscimento). Refer to the Italian authorities.' },
    mig2Tip: { 'zh-CN': '该职业较难直接走蓝卡，但可通过《移民配额法令》（Decreto Flussi）名额下的雇主担保受雇居留移民——名额与开放窗口有限，通常需资质认证。以意大利主管机关最新规定为准。',
               en: 'The Blue Card route may be harder, but migration is possible via an employer-sponsored permit within the annual quota decree (Decreto Flussi) — quotas and application windows are limited and qualification recognition is usually needed. Refer to the Italian authorities.' },
    restrictedNote: { 'zh-CN': '本职业不在直接蓝卡通道上，无法直接技术移民；但可通过《移民配额法令》（Decreto Flussi）名额下的雇主担保受雇居留（Nulla Osta）移民——通常需先完成资质认证（riconoscimento），名额与开放窗口有限，以意大利主管机关最新规定为准。',
                      en: 'This occupation is not on the direct Blue Card track, so direct skilled migration is unavailable; however migration is possible via an employer-sponsored permit (Nulla Osta) within the annual quota decree (Decreto Flussi) — usually requiring qualification recognition (riconoscimento), with limited quotas and windows. Refer to the latest Italian authorities.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 ISCO 职业并受《移民配额法令》名额约束，受规管职业需完成资质认证（riconoscimento），以意大利主管机关（内政部 / 劳工部）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct ISCO occupation and on the annual quota decree, with qualification recognition (riconoscimento) for regulated professions; refer to the latest Italian authorities (Ministry of the Interior / Labour).' },
  },
  NL: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需雇主认证担保）', en: 'Restricted migration (recognised-sponsor employer required)' },
    mig1Tip: { 'zh-CN': '该职业通常可走荷兰高技能移民（Kennismigrant）或欧盟蓝卡，并可申请永久居留；这是一条移民路径，并非保证，需由荷兰移民局（IND）认证的雇主担保并满足薪资门槛。以荷兰移民局（IND）最新规定为准。',
               en: 'This occupation commonly supports the Dutch Highly Skilled Migrant (Kennismigrant) route or the EU Blue Card, with a route to permanent residence — a pathway, not a guarantee, requiring an IND recognised-sponsor employer and meeting the salary threshold. Refer to the Dutch immigration service (IND).' },
    mig2Tip: { 'zh-CN': '该职业较难达到高技能移民薪资门槛，但仍可能通过认证雇主担保或应届毕业生「求职年」（Orientation Year）通道移民——薪资门槛与担保资格受限。以荷兰移民局（IND）最新规定为准。',
               en: 'Reaching the Highly Skilled Migrant salary threshold may be harder, but migration may still be possible via a recognised-sponsor employer or the Orientation Year for graduates — salary thresholds and sponsor eligibility are limited. Refer to the IND.' },
    restrictedNote: { 'zh-CN': '本职业不在直接积分移民通道上，无法直接技术移民；但可通过荷兰移民局（IND）认证雇主的高技能移民（Kennismigrant）担保移民——需满足薪资门槛，担保资格受限，以荷兰移民局（IND）最新规定为准。',
                      en: 'This occupation has no direct points route, so direct skilled migration is unavailable; however migration is possible via an IND recognised-sponsor employer under the Highly Skilled Migrant (Kennismigrant) route — meeting the salary threshold, with limited sponsor eligibility. Refer to the latest IND rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 ISCO 职业并由认证雇主担保、满足薪资门槛，以荷兰移民局（IND）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct ISCO occupation and on recognised-sponsor employment meeting the salary threshold; refer to the latest IND rules.' },
  },
  IE: {
    restrictedOcc: { 'zh-CN': '受限移民职业（需就业许可 / 雇主担保）', en: 'Restricted migration (employment permit / employer-sponsored)' },
    mig1Tip: { 'zh-CN': '该职业通常可走爱尔兰关键技能就业许可（Critical Skills Employment Permit）或欧盟蓝卡，并可申请长期居留；这是一条移民路径，并非保证，需雇主聘用并满足薪资门槛。以爱尔兰企业、贸易与就业部（DETE）最新规定为准。',
               en: 'This occupation commonly supports the Irish Critical Skills Employment Permit or the EU Blue Card, with a route to long-term residence — a pathway, not a guarantee, requiring a job offer and meeting the salary threshold. Refer to the Department of Enterprise, Trade and Employment (DETE).' },
    mig2Tip: { 'zh-CN': '该职业较难走关键技能许可，但仍可能通过一般就业许可（General Employment Permit）移民——受薪资门槛与劳动力市场需求测试约束。以爱尔兰企业、贸易与就业部（DETE）最新规定为准。',
               en: 'The Critical Skills route may be harder, but migration is possible via the General Employment Permit — subject to salary thresholds and a labour-market needs test. Refer to the DETE.' },
    restrictedNote: { 'zh-CN': '本职业不在直接移民通道上，无法直接技术移民；但可通过一般就业许可（General Employment Permit）等雇主担保通道移民——需满足薪资门槛并可能需劳动力市场需求测试，以爱尔兰企业、贸易与就业部（DETE）最新规定为准。',
                      en: 'This occupation is not on a direct migration track, so direct skilled migration is unavailable; however migration is possible via an employer-sponsored General Employment Permit — meeting the salary threshold and possibly a labour-market needs test. Refer to the latest DETE rules.' },
    nonMigVisa: { 'zh-CN': '签证路径需按具体职责匹配对应 ISCO 职业并取得相应就业许可、满足薪资门槛，以爱尔兰企业、贸易与就业部（DETE）最新规则为准。',
                  en: 'Visa pathways depend on matching the specific duties to the correct ISCO occupation and obtaining the appropriate employment permit meeting the salary threshold; refer to the latest DETE rules.' },
  },
};
// ───────────────────────── AI 职业图谱：6 大类 ─────────────────────────
export const AI_CLUSTER_ORDER = [
  'licensed_accountable', 'regulated_public_safety', 'physical_site_based',
  'human_trust_care', 'ai_augmented', 'high_ai_exposure',
] as const;
type Bi = { 'zh-CN': string; en: string };
type BiList = { 'zh-CN': string[]; en: string[] };
export interface ClusterDef {
  color: string; risk: 'low' | 'med' | 'high';
  name: Bi; riskLabel: Bi; meaning: Bi; why: Bi;
  replaced: BiList; moat: BiList; fit: BiList; unfit: BiList;
  actionIn: Bi; actionOut: Bi; pivot: Bi;
}
export const AI_CLUSTERS: Record<string, ClusterDef> = {
  high_ai_exposure: {
    color: '#ef4444', risk: 'high',
    name: { 'zh-CN': 'AI 高替代 / 高压缩', en: 'High AI exposure' },
    riskLabel: { 'zh-CN': '高风险', en: 'High risk' },
    meaning: { 'zh-CN': '大量任务是文字、录入、检索和标准分析，最容易被 AI 直接接管。', en: 'Much of the work is text, data entry, lookup and standard analysis — easiest for AI to take over.' },
    why: { 'zh-CN': '日常产出高度标准化、可被语言模型与 RPA 复制，任务被整段自动化，岗位数量随之收缩。', en: 'Highly standardised output that LLMs and RPA can replicate, so whole tasks get automated and headcount shrinks.' },
    replaced: { 'zh-CN': ['资料录入与表格整理', '标准邮件与基础文案', '简单报表生成', '基础检索与归档', '模板化设计'], en: ['Data entry and spreadsheets', 'Standard emails and basic copy', 'Simple report generation', 'Lookup and filing', 'Templated design'] },
    moat: { 'zh-CN': ['客户与同事的人际信任', '对业务流程的整体把握', '异常与例外的判断处理'], en: ['Trust with clients and colleagues', 'Grasp of the whole process', 'Handling exceptions and judgement'] },
    fit: { 'zh-CN': ['想快速入行、再向上转型的人', '愿意学工具+行业知识的人'], en: ['People entering fast then leveling up', 'Those willing to learn tools + domain'] },
    unfit: { 'zh-CN': ['只想长期做基础执行的人', '抗拒学习新工具的人'], en: ['Those wanting only basic execution long-term', 'Those resisting new tools'] },
    actionIn: { 'zh-CN': '不要只学工具，往「行业知识 + 客户沟通 + 合规责任 + 数据判断」升级。', en: "Don't just learn tools — level up into domain knowledge, client communication, compliance and data judgement." },
    actionOut: { 'zh-CN': '可作为短期入口，但尽快规划转向更稳的方向，不要长期停留。', en: 'Fine as a short-term entry, but plan to move toward more durable roles quickly.' },
    pivot: { 'zh-CN': '推荐转向：Medical Receptionist、Practice Manager、Compliance Officer、Payroll Specialist、Data Analyst。', en: 'Pivot toward: Medical Receptionist, Practice Manager, Compliance Officer, Payroll Specialist, Data Analyst.' },
  },
  ai_augmented: {
    color: '#f59e0b', risk: 'med',
    name: { 'zh-CN': 'AI 增强型', en: 'AI-augmented' },
    riskLabel: { 'zh-CN': '机会型（入门收窄）', en: 'Opportunity (entry narrows)' },
    meaning: { 'zh-CN': 'AI 会吃掉初级任务，但能显著放大高阶判断与产出。', en: 'AI absorbs junior tasks but greatly amplifies senior judgement and output.' },
    why: { 'zh-CN': '初级执行被自动化，价值上移到问题定义、判断与跨团队协作；会用 AI 的人产出倍增。', en: 'Junior execution gets automated; value moves up to framing, judgement and collaboration — AI users multiply output.' },
    replaced: { 'zh-CN': ['样板代码与基础脚本', '初步数据清洗与图表', '标准文档与初稿', '基础调研汇总'], en: ['Boilerplate code and scripts', 'Initial data cleaning and charts', 'Standard docs and first drafts', 'Basic research summaries'] },
    moat: { 'zh-CN': ['问题定义与方案设计', '业务理解与判断', '跨团队沟通与落地', '对 AI 产出的核验能力'], en: ['Problem framing and design', 'Business understanding', 'Cross-team delivery', 'Verifying AI output'] },
    fit: { 'zh-CN': ['能从执行者成长为判断者的人', '愿意把 AI 纳入工作流的人'], en: ['Those who grow from doer to decision-maker', 'Those embedding AI in workflows'] },
    unfit: { 'zh-CN': ['只靠重复执行的人', '不愿持续学习的人'], en: ['Those relying on repetition', 'Those not learning continuously'] },
    actionIn: { 'zh-CN': '入门岗位会变窄，必须尽快从「执行者」变成「判断者」。', en: 'Entry roles narrow — move from executor to decision-maker fast.' },
    actionOut: { 'zh-CN': '仍值得进入，但要带着「能用 AI + 懂业务」的目标入场。', en: 'Still worth entering — aim to combine AI fluency with domain sense.' },
    pivot: { 'zh-CN': '建议补：行业软件、数据分析、业务理解、AI 工作流、项目沟通。', en: 'Build: domain software, data analysis, business sense, AI workflows, project communication.' },
  },
  licensed_accountable: {
    color: '#10b981', risk: 'low',
    name: { 'zh-CN': '强执照 / 强责任', en: 'Licensed & accountable' },
    riskLabel: { 'zh-CN': '较稳', en: 'Resilient' },
    meaning: { 'zh-CN': 'AI 可辅助，但最终责任由持证人承担，难以被替代。', en: 'AI can assist, but the licensed professional carries final accountability.' },
    why: { 'zh-CN': '需持证执业并承担法律责任，AI 只能减负而不能担责；现场与判断仍由人完成。', en: 'Licensed practice with legal liability — AI offloads work but cannot take responsibility; judgement stays human.' },
    replaced: { 'zh-CN': ['记录与文书的初稿', '检索与资料整理', '初步风险/异常提示', '排程与事务性工作'], en: ['First drafts of records', 'Lookup and collation', 'Initial risk/anomaly flags', 'Scheduling and admin'] },
    moat: { 'zh-CN': ['执照与法律责任', '现场操作与复杂判断', '对结果的问责', '客户/患者信任'], en: ['Licence and legal liability', 'On-site work and complex judgement', 'Accountability for outcomes', 'Client/patient trust'] },
    fit: { 'zh-CN': ['愿意考证、承担责任的人', '重视稳定与专业深度的人'], en: ['Those willing to certify and own responsibility', 'Those valuing stability and depth'] },
    unfit: { 'zh-CN': ['不愿考证或持续合规的人', '想完全远程/纯线上的人'], en: ['Those avoiding certification/compliance', 'Those wanting fully remote work'] },
    actionIn: { 'zh-CN': '把 AI 当效率工具，重点深化专业判断、专科方向与责任经验。', en: 'Use AI as an efficiency tool; deepen judgement, specialisation and accountable experience.' },
    actionOut: { 'zh-CN': 'AI 替代风险低，值得进入，但要做好考证与持续合规的准备。', en: 'Low automation risk and worth entering — be ready for certification and ongoing compliance.' },
    pivot: { 'zh-CN': '建议补：执照/专科、AI 辅助工具的核验、英语、客户沟通、团队协调。', en: 'Build: licences/specialisation, verifying AI tools, English, client communication, coordination.' },
  },
  physical_site_based: {
    color: '#0ea5e9', risk: 'low',
    name: { 'zh-CN': '强现场 / 强体力', en: 'Hands-on & site-based' },
    riskLabel: { 'zh-CN': '较稳', en: 'Resilient' },
    meaning: { 'zh-CN': '工作依赖到场、工具、环境判断和身体操作，难以远程自动化。', en: 'Work depends on being on-site, tools, environmental judgement and physical operation.' },
    why: { 'zh-CN': '任务发生在物理现场，需手眼协调与即时判断，AI/机器人短期难以整体替代。', en: 'Tasks happen in the physical world needing dexterity and on-the-spot judgement — hard to fully automate soon.' },
    replaced: { 'zh-CN': ['报价与材料估算的草稿', '排期与记录', '标准操作的资料查询'], en: ['Draft quotes and material estimates', 'Scheduling and records', 'Looking up standard procedures'] },
    moat: { 'zh-CN': ['现场操作与身体技能', '环境与安全判断', '应对突发与变量', '客户现场信任'], en: ['On-site operation and physical skill', 'Environment and safety judgement', 'Handling surprises', 'On-site client trust'] },
    fit: { 'zh-CN': ['动手能力强、愿到现场的人', '想要稳定且抗 AI 的技工方向'], en: ['Hands-on people who like field work', 'Those wanting AI-resilient trades'] },
    unfit: { 'zh-CN': ['排斥体力与户外的人', '不愿考技工证照的人'], en: ['Those avoiding physical/outdoor work', 'Those avoiding trade licences'] },
    actionIn: { 'zh-CN': '巩固证照与安全规范，往班组长/承包/经营方向叠加管理与报价能力。', en: 'Solidify licences and safety; add supervision, contracting and quoting skills.' },
    actionOut: { 'zh-CN': 'AI 替代风险低，但体力与证照门槛高，入行前评估身体与学徒投入。', en: 'Low automation risk but high physical/licensing barriers — weigh the apprenticeship commitment.' },
    pivot: { 'zh-CN': '建议补：执照、英语、安全规范、客户沟通、报价/经营能力。', en: 'Build: licences, English, safety standards, client communication, quoting/business skills.' },
  },
  human_trust_care: {
    color: '#8b5cf6', risk: 'low',
    name: { 'zh-CN': '强人际信任 / 照护', en: 'Human trust & care' },
    riskLabel: { 'zh-CN': '较稳', en: 'Resilient' },
    meaning: { 'zh-CN': '价值来自情绪劳动、照护关系、说服与信任，难以被自动化。', en: 'Value comes from emotional labour, care relationships, persuasion and trust.' },
    why: { 'zh-CN': '核心是人对人的关系与信任，AI 可辅助记录与提示，但无法替代共情与建立关系。', en: 'The core is human relationships and trust; AI can assist with notes and prompts but cannot replace empathy.' },
    replaced: { 'zh-CN': ['记录与个案文书', '资料检索与转介信息整理', '标准化沟通材料'], en: ['Case notes and paperwork', 'Lookup and referral info', 'Standard communication materials'] },
    moat: { 'zh-CN': ['共情与情绪劳动', '长期照护关系与信任', '复杂家庭/个案的judgement', '危机处理'], en: ['Empathy and emotional labour', 'Long-term care relationships', 'Judgement on complex cases', 'Crisis handling'] },
    fit: { 'zh-CN': ['有同理心、抗压的人', '认同助人价值的人'], en: ['Empathetic, resilient people', 'Those who value helping others'] },
    unfit: { 'zh-CN': ['难以承受情绪压力的人', '追求高薪快速回报的人'], en: ['Those who struggle with emotional load', 'Those chasing fast high pay'] },
    actionIn: { 'zh-CN': '用 AI 减少文书负担，把时间投入关系与判断，发展专科与督导能力。', en: 'Use AI to cut paperwork; invest time in relationships and judgement; develop specialisation and supervision.' },
    actionOut: { 'zh-CN': 'AI 替代风险低、需求稳定，适合重视意义感的人；薪资中等需有预期。', en: 'Low automation risk and steady demand — suits those valuing meaning; expect mid-level pay.' },
    pivot: { 'zh-CN': '建议补：专科资格、个案管理、督导/培训、合规与跨机构协调。', en: 'Build: specialist qualifications, case management, supervision, compliance and coordination.' },
  },
  regulated_public_safety: {
    color: '#2563eb', risk: 'low',
    name: { 'zh-CN': '强监管 / 公共安全', en: 'Regulated & public safety' },
    riskLabel: { 'zh-CN': '较稳', en: 'Resilient' },
    meaning: { 'zh-CN': '涉及公共安全、执法、合规、审批与问责，由人承担决定权。', en: 'Involves public safety, enforcement, compliance, approvals and accountability held by people.' },
    why: { 'zh-CN': '决策牵涉公共安全与法律问责，监管要求人工监督；AI 仅作辅助。', en: 'Decisions carry public-safety and legal accountability requiring human oversight; AI only assists.' },
    replaced: { 'zh-CN': ['记录与报告初稿', '资料核对与检索', '标准合规清单生成'], en: ['Draft records and reports', 'Cross-checking and lookup', 'Generating standard checklists'] },
    moat: { 'zh-CN': ['执法/审批的决定权与问责', '现场处置与判断', '法定授权与合规责任', '公众信任'], en: ['Decision authority and accountability', 'On-scene response and judgement', 'Statutory powers and compliance', 'Public trust'] },
    fit: { 'zh-CN': ['注重秩序、责任与公正的人', '能通过背景审查/体能的人'], en: ['Those valuing order, duty and fairness', 'Those passing vetting/fitness'] },
    unfit: { 'zh-CN': ['排斥轮班/高压/风险的人', '以技术移民为唯一目标的人'], en: ['Those avoiding shifts/pressure/risk', 'Those whose only goal is migration'] },
    actionIn: { 'zh-CN': '用 AI 提升合规与分析效率，积累现场处置、调查与管理经验。', en: 'Use AI for compliance and analysis efficiency; build field, investigation and management experience.' },
    actionOut: { 'zh-CN': 'AI 替代风险低、就业稳定，多需公民身份与背景审查，提前规划。', en: 'Low automation risk and stable — often needs citizenship and vetting, so plan ahead.' },
    pivot: { 'zh-CN': '建议补：合规/调查资质、数据分析、报告写作、法规知识、跨部门协调。', en: 'Build: compliance/investigation credentials, data analysis, report writing, regulatory knowledge, coordination.' },
  },
};
const pick = (b: Bi | undefined, locale: Locale) => (b ? (locale === 'zh-CN' ? b['zh-CN'] : b.en) : '');
const pickL = (b: BiList | undefined, locale: Locale) => (b ? (locale === 'zh-CN' ? b['zh-CN'] : b.en) : []);
export function clusterField(key: string, field: keyof ClusterDef, locale: Locale): any {
  const c = AI_CLUSTERS[key]; if (!c) return '';
  const v = (c as any)[field];
  return Array.isArray((v || {})['zh-CN']) ? pickL(v, locale) : pick(v, locale);
}
export const clusterColor = (key: string) => AI_CLUSTERS[key]?.color || '#94a3b8';
// 某国某类的职业；graphOccs：该国所有已分配 cluster 的职业（矩阵用）
export const occByCluster = (country: string, cluster: string) =>
  occByCountry(country).filter((o) => o.ai?.cluster === cluster);
export const graphOccs = (country: string) =>
  occByCountry(country).filter((o) => o.ai?.cluster && o.ai?.automation_exposure != null && o.ai?.human_moat != null);
// 全球（跨国合并）变体：用于无国家区分的全球 AI 图谱页
export const graphOccsGlobal = () => graphOccs(undefined as any);
export const occByClusterGlobal = (cluster: string) =>
  occupations.filter((o) => o.ai?.cluster === cluster);

export function sourcesBody(country: string, locale: Locale): string {
  const v = SOURCES_BODY[country];
  // CA/NZ：中文母本经翻译记忆 tr() 解析到各语言（TM 缺失则回退 en 文案）
  if (v) return locale === 'zh-CN' ? v['zh-CN'] : (hasTr(v['zh-CN'], locale) ? tr(v['zh-CN'], locale) : v.en);
  return strings(locale).sourcesBody; // AU：走 UI 字典的多语言文案
}

// 移民/签证文案取值：US/NZ/CA 走 MIG_TEXT（zh-CN 母本经 tr() 解析其余语言），AU/其它回退 UI 字典 10 语言。
function migText(country: string | undefined, key: keyof MigText, locale: Locale): string {
  const v = country ? MIG_TEXT[country]?.[key] : undefined;
  if (v) return locale === 'zh-CN' ? v['zh-CN'] : (hasTr(v['zh-CN'], locale) ? tr(v['zh-CN'], locale) : v.en);
  // AU/默认：复用 UI 字典里对应的澳洲文案键
  const fallback: Record<keyof MigText, keyof ReturnType<typeof strings>> = {
    restrictedOcc: 'migRestrictedOcc', restrictedNote: 'migRestrictedNote', nonMigVisa: 'nonMigVisa',
    mig1Tip: 'migRestrictedNote', mig2Tip: 'migRestrictedNote', // tip 仅 cardBadges 用，AU 用其内联文案，不会走到此分支
  };
  return strings(locale)[fallback[key]] as string;
}
export const migRestrictedOccOf = (country: string, locale: Locale) => migText(country, 'restrictedOcc', locale);
export const migRestrictedNoteOf = (country: string, locale: Locale) => migText(country, 'restrictedNote', locale);
export const nonMigVisaOf = (country: string, locale: Locale) => migText(country, 'nonMigVisa', locale);

// 精选对比配对（同类高价值），仅保留两端都存在的
const RAW_PAIRS: [string, string][] = [
  ['web-developer', 'software-engineer'],
  ['cook', 'baker'],
  ['electrician', 'plumber'],
  ['accountant-cpa-ca', 'auditor'],
  ['bookkeeper', 'accountant-cpa-ca'],
  ['data-analyst', 'bi-analyst'],
  ['receptionist', 'medical-receptionist'],
];
export const COMPARE_PAIRS = RAW_PAIRS.filter(([a, b]) => getBySlug(a) && getBySlug(b));
export const pairKey = (a: string, b: string) => `${a}-vs-${b}`;

// 雷达维度固定顺序（对比时两序列对齐）
export const DIM_ORDER = [
  'income_level', 'job_demand', 'future_prospect', 'pr_friendliness', 'ai_risk', 'competition',
  'work_intensity', 'learning_difficulty', 'learning_duration', 'certification_difficulty', 'pr_difficulty',
];
export function radarLabels(locale: Locale) { return DIM_ORDER.map((d) => dimLabel(d, locale)); }
export function radarValues(o: Occ) {
  const m = Object.fromEntries(o.ratings.map((r) => [r.dimension, r.stars ?? 0]));
  return DIM_ORDER.map((d) => (m[d] as number) ?? 0);
}
// 货币符号：按国家区分。UK 用英镑 £、DE 用欧元 €，其余用 $。
export const CURRENCY_SYMBOL: Record<string, string> = { AU: '$', NZ: '$', CA: '$', US: '$', UK: '£', DE: '€', FR: '€', ES: '€', IT: '€', NL: '€', IE: '€' };
export function money(v: number | null, country?: string) {
  if (!v) return '—';
  return ((country && CURRENCY_SYMBOL[country]) || '$') + Number(v).toLocaleString('en-US');
}

// 资深/高级阶段薪资：取首个含「资深/高级/senior」的档位，否则回退到最高（最后一档）
export function seniorSalary(o: Occ) {
  const kw = o.salaries.find((s) => /资深|高级|senior/i.test(s.label));
  return kw || (o.salaries.length ? o.salaries[o.salaries.length - 1] : null);
}
export function seniorSalaryText(o: Occ): string {
  const s = seniorSalary(o);
  if (!s || (s.min == null && s.max == null)) return '';
  const lo = money(s.min as any, o.country), hi = money(s.max as any, o.country);
  return lo === hi || !s.max ? lo : `${lo}~${hi}`;
}

// 培训/教育周期摘要：取核心 1-2 个长周期阶段（排除海外互认/技能评估等替代项）
const EDU_SKIP = /海外|互认|\bTRA\b|技能评估|资历评估|注册评估|Bridging|桥梁|可选|替代|移民|\bAHPRA\b|\bACS\b|英语能力|雅思|\bPTE\b/;
function durMonths(d: string | null): number {
  if (!d) return 0;
  const y = d.match(/(\d+(?:\.\d+)?)\s*(?:[~\-](\d+(?:\.\d+)?))?\s*年/);
  if (y) return parseFloat(y[2] || y[1]) * 12;
  const m = d.match(/(\d+)\s*(?:[~\-](\d+))?\s*个?月/);
  if (m) return parseFloat(m[2] || m[1]);
  return 0;
}
function durShort(d: string | null): string {
  if (!d) return '';
  const y = d.match(/\d+(?:\.\d+)?(?:[~\-]\d+(?:\.\d+)?)?\s*年/);
  if (y) return y[0].replace(/\s+/g, '');
  const m = d.match(/\d+(?:[~\-]\d+)?\s*个?月/);
  if (m) return m[0].replace(/\s+/g, '');
  return d.length > 10 ? d.slice(0, 10) : d;
}
function eduLabel(stage: string): string {
  const s = stage.replace(/[（(][^)）]*[)）]/g, '').trim();
  const zh = s.replace(/[a-zA-Z0-9/.&'+\-]/g, '').replace(/\s+/g, '').replace(/^[或、，,]+/, '').trim();
  return zh.length >= 2 ? zh : s.split('/')[0].trim();
}
function corePicks(o: Occ) {
  if (!o.education || !o.education.length) return [] as Occ['education'];
  const core = o.education.filter((e) => !EDU_SKIP.test(e.stage));
  const pool = core.length ? core : o.education;
  let pick = pool.filter((e) => durMonths(e.duration) >= 12).slice(0, 2);
  if (!pick.length) pick = pool.slice(0, 1);
  return pick;
}
export function trainingSummary(o: Occ): string {
  return corePicks(o).map((e) => `${eduLabel(e.stage)} ${durShort(e.duration)}`.trim()).join(' + ');
}
// 数值版指标（供排序/筛选/精选板块用）
export function trainingMonths(o: Occ): number {
  const m = corePicks(o).reduce((s, e) => s + durMonths(e.duration), 0);
  return m || 9999; // 无数据排到最后
}
export function seniorMax(o: Occ): number {
  const s = seniorSalary(o);
  return s ? Number(s.max ?? s.min ?? 0) : 0;
}
export function prScore(o: Occ): number {
  const r = o.ratings.find((x) => x.dimension === 'pr_friendliness');
  return r && r.stars != null ? r.stars : 0;
}
function dimStars(o: Occ, dim: string): number | null {
  const r = o.ratings.find((x) => x.dimension === dim);
  return r && r.stars != null ? r.stars : null;
}
// 卡片标签行：移民通道 + 条件标签（移民门槛/需求/AI替代/竞争）。cls: mig=正向绿 / warn=橙 / bad=红 / ''=中性
// 「可技术移民」表示该职业在澳洲技术移民职业清单上、可作为提名职业申请技术移民——是一条移民「路径」，
// 与读者当前签证身份无关，也不代表「只有 PR 才能从事」。不在清单上的职业不展示该标签（避免误读）。
export function cardBadges(o: Occ, locale: Locale): { text: string; cls: string; title?: string }[] {
  const zh = locale === 'zh-CN';
  const out: { text: string; cls: string; title?: string }[] = [];
  const migTip = MIG_TEXT[o.country];
  if (o.is_migration === 1) out.push({
    text: zh ? '可技术移民' : 'PR pathway', cls: 'mig',
    title: migTip ? (zh ? migTip.mig1Tip['zh-CN'] : migTip.mig1Tip.en)
         : zh ? '该职业在澳洲技术移民职业清单上，可作为提名职业申请技术移民（189/190/491）；与你当前签证身份无关，也不代表「只有 PR 才能从事」。'
             : 'This occupation is on the Australian skilled migration list and can be nominated for skilled migration (189/190/491) — a pathway, not a requirement to already hold PR.',
  });
  if (o.is_migration === 2) out.push({
    text: zh ? '雇主担保移民' : 'Employer-sponsored', cls: 'warn',
    title: migTip ? (zh ? migTip.mig2Tip['zh-CN'] : migTip.mig2Tip.en)
         : zh ? '该职业不在独立技术移民清单（189/190）上，但可通过雇主担保（482/494）、偏远地区指定协议（DAMA）或劳务协议移民——移民通道受限。'
             : 'Not on the independent skilled migration list (189/190), but migration is possible via employer sponsorship (482/494), Designated Area Migration Agreements (DAMA) or labour agreements — a restricted pathway.',
  });
  if (o.is_public_servant) out.push({
    text: zh ? '公职' : 'Public sector', cls: 'gov',
    title: zh ? '政府 / 公共部门岗位（联邦、州或地方政府、公共机构），类似国内的公务员 / 事业编 / 国企。'
             : 'A government or public-sector role (federal, state or local government, or a public agency).',
  });
  // 阈值按 10 分制（原 5 分制阈值 ×2）
  const prd = dimStars(o, 'pr_difficulty');
  if (o.is_migration === 1 && prd != null && prd <= 4) out.push({ text: zh ? '移民门槛低' : 'Easier PR', cls: 'mig' });
  const dem = dimStars(o, 'job_demand');
  if (dem != null && dem >= 8) out.push({ text: zh ? '需求大' : 'High demand', cls: 'mig' });
  const ai = dimStars(o, 'ai_risk');
  if (ai != null) {
    if (ai <= 4) out.push({ text: zh ? '低AI替代' : 'Low AI risk', cls: 'mig' });
    else if (ai <= 6) out.push({ text: zh ? '中AI替代' : 'Med AI risk', cls: 'warn' });
    else out.push({ text: zh ? '高AI替代' : 'High AI risk', cls: 'bad' });
  }
  const comp = dimStars(o, 'competition');
  if (comp != null && comp <= 4) out.push({ text: zh ? '竞争低' : 'Low competition', cls: 'mig' });
  return out;
}

// 精选板块（各取前 N，按国家过滤）
export function bestMigration(n = 6, country?: string) {
  return occByCountry(country).filter((o) => o.is_migration === 1)
    .sort((a, b) => prScore(b) - prScore(a) || (b.overall_score ?? 0) - (a.overall_score ?? 0)).slice(0, n);
}
export function bestIncome(n = 6, country?: string) {
  return [...occByCountry(country)].sort((a, b) => seniorMax(b) - seniorMax(a)).slice(0, n);
}
export function fastestEntry(n = 6, country?: string) {
  return [...occByCountry(country)].sort((a, b) => trainingMonths(a) - trainingMonths(b) || (b.overall_score ?? 0) - (a.overall_score ?? 0)).slice(0, n);
}

// ───────────────────────── AI 时代职业榜单 ─────────────────────────
export const RANKING_ORDER = [
  'low_ai_replacement', 'ai_augmented_rank', 'licensed_moat', 'physical_site',
  'human_trust', 'high_growth', 'migration_friendly', 'cautious_newbie',
] as const;
// 全球（跨国）榜单：全部榜单均跨国合并、按国家标签呈现（不再保留各国独立榜单页）
export const GLOBAL_RANKING_ORDER = [
  'low_ai_replacement', 'ai_augmented_rank', 'licensed_moat', 'physical_site',
  'human_trust', 'high_growth', 'migration_friendly', 'cautious_newbie',
] as const;
export const RANKINGS: Record<string, { name: Bi; sub: Bi; why: Bi }> = {
  low_ai_replacement: {
    name: { 'zh-CN': '低 AI 替代榜', en: 'Lowest AI replacement' },
    sub: { 'zh-CN': '这些职业更依赖现场操作、执照责任、人际信任或复杂判断，AI 更可能辅助而不是替代。', en: 'These rely on on-site work, licensing, human trust or complex judgement — AI assists rather than replaces.' },
    why: { 'zh-CN': '它们的任务结构当前更难被完全自动化；但不代表永远安全，仍需持续提升判断与专业深度。', en: 'Their task structure is currently hard to fully automate — not a guarantee forever, so keep deepening judgement.' },
  },
  ai_augmented_rank: {
    name: { 'zh-CN': 'AI 增强榜', en: 'Best AI-augmented' },
    sub: { 'zh-CN': 'AI 会吃掉初级任务，但能显著放大高阶能力与收入，值得尽早把 AI 纳入工作流。', en: 'AI absorbs junior tasks but amplifies senior capability and pay — embed AI early.' },
    why: { 'zh-CN': '高 AI 放大潜力叠加较高收入，会用 AI 的人产出与议价能力都更强。', en: 'High AI upside plus strong pay — AI-fluent practitioners out-produce and out-earn.' },
  },
  licensed_moat: {
    name: { 'zh-CN': '强执照护城河榜', en: 'Licensed moat' },
    sub: { 'zh-CN': '需要持证执业并承担责任，AI 只能辅助，资质本身就是壁垒。', en: 'Licensed practice with accountability — the credential itself is the moat.' },
    why: { 'zh-CN': '执照、注册与法律责任难以被自动化，专业深度越高越稳。', en: 'Licences, registration and legal liability resist automation; depth means stability.' },
  },
  physical_site: {
    name: { 'zh-CN': '强现场职业榜', en: 'Hands-on & on-site' },
    sub: { 'zh-CN': '工作依赖到场、工具与身体操作，自动化程度低。', en: 'Work depends on being on-site, tools and physical operation; low automation.' },
    why: { 'zh-CN': '物理现场与即时判断难被远程替代，技工类长期稳定。', en: 'Physical presence and on-the-spot judgement are hard to replace remotely.' },
  },
  human_trust: {
    name: { 'zh-CN': '强人际信任榜', en: 'Human trust & care' },
    sub: { 'zh-CN': '价值来自照护关系、情绪劳动与信任，难以自动化。', en: 'Value comes from care relationships, emotional labour and trust.' },
    why: { 'zh-CN': '人对人的关系是核心，AI 只能减负，无法替代共情与建立信任。', en: 'Human relationships are central; AI offloads work but cannot replace empathy.' },
  },
  high_growth: {
    name: { 'zh-CN': '高增长职业榜', en: 'Highest growth' },
    sub: { 'zh-CN': '需求旺盛、前景看好，未来几年招聘持续扩张。', en: 'Strong demand and outlook — hiring keeps expanding.' },
    why: { 'zh-CN': '按职位需求与发展前景综合排序，反映中短期就业机会。', en: 'Ranked by demand and outlook — reflects near-term opportunity.' },
  },
  migration_friendly: {
    name: { 'zh-CN': '移民友好榜', en: 'Migration-friendly' },
    sub: { 'zh-CN': '技术移民路径更顺畅、门槛更低，且多在短缺清单上。', en: 'Smoother skilled-migration pathways with lower hurdles, often on shortage lists.' },
    why: { 'zh-CN': '按 PR 友好度、移民难度与短缺状态综合排序，仅含技术移民职业。', en: 'Ranked by PR friendliness, difficulty and shortage status; migration occupations only.' },
  },
  cautious_newbie: {
    name: { 'zh-CN': 'AI 时代新手谨慎榜', en: 'Newcomers, be cautious' },
    sub: { 'zh-CN': '入门任务正被 AI 压缩、竞争又激烈，零基础进入需格外谨慎。', en: 'Entry tasks are being compressed by AI and competition is high — enter with caution.' },
    why: { 'zh-CN': '入门压缩、竞争与自动化三高，建议带着差异化技能或转向更稳方向。', en: 'High entry compression, competition and automation — bring differentiated skills or pivot.' },
  },
};
const rstar = (o: Occ, dim: string) => dimStars(o, dim) ?? 0;
const A = (o: Occ, k: 'automation_exposure' | 'human_moat' | 'entry_risk' | 'ai_upside') => (o.ai?.[k] as number) ?? 0;
// 公式按 10 分制：反向常数 6→12、加成 +3→+6 / +2→+4（所有项与原 5 分制成 2× 等比，排序不变）
const RANK_SCORE: Record<string, { filter: (o: Occ) => boolean; score: (o: Occ) => number }> = {
  low_ai_replacement: { filter: (o) => !!o.ai?.cluster, score: (o) => A(o, 'human_moat') * 2 + (12 - A(o, 'automation_exposure')) + rstar(o, 'job_demand') },
  ai_augmented_rank: { filter: (o) => !!o.ai?.cluster, score: (o) => A(o, 'ai_upside') * 2 + rstar(o, 'income_level') + rstar(o, 'future_prospect') },
  licensed_moat: { filter: (o) => !!o.ai?.cluster, score: (o) => A(o, 'human_moat') + rstar(o, 'certification_difficulty') + (o.ai?.cluster === 'licensed_accountable' ? 6 : 0) },
  physical_site: { filter: (o) => o.ai?.cluster === 'physical_site_based', score: (o) => A(o, 'human_moat') + (12 - A(o, 'automation_exposure')) },
  human_trust: { filter: (o) => o.ai?.cluster === 'human_trust_care', score: (o) => A(o, 'human_moat') + rstar(o, 'future_prospect') },
  high_growth: { filter: () => true, score: (o) => rstar(o, 'future_prospect') + rstar(o, 'job_demand') },
  migration_friendly: { filter: (o) => o.is_migration === 1, score: (o) => rstar(o, 'pr_friendliness') * 2 + (12 - rstar(o, 'pr_difficulty')) + (o.shortage_listed ? 4 : 0) },
  cautious_newbie: { filter: (o) => !!o.ai?.cluster, score: (o) => A(o, 'entry_risk') * 2 + rstar(o, 'competition') + A(o, 'automation_exposure') },
};
export function rankingList(key: string, country: string, n?: number): Occ[] {
  const def = RANK_SCORE[key]; if (!def) return [];
  const arr = occByCountry(country).filter(def.filter)
    .map((o) => ({ o, s: def.score(o) })).sort((a, b) => b.s - a.s || (b.o.overall_score ?? 0) - (a.o.overall_score ?? 0));
  const list = arr.map((x) => x.o);
  return n ? list.slice(0, n) : list;
}
// 卡片用的「AI 结论标签」：由 cluster 推导
const CLUSTER_TAG: Record<string, Bi> = {
  high_ai_exposure: { 'zh-CN': '入门变窄', en: 'Entry narrows' },
  ai_augmented: { 'zh-CN': 'AI 增强', en: 'AI-augmented' },
  licensed_accountable: { 'zh-CN': '强执照', en: 'Licensed' },
  physical_site_based: { 'zh-CN': '强现场', en: 'On-site' },
  human_trust_care: { 'zh-CN': '强人际', en: 'Human trust' },
  regulated_public_safety: { 'zh-CN': '强监管', en: 'Regulated' },
};
export function aiTag(o: Occ, locale: Locale): { text: string; low: boolean } | null {
  const c = o.ai?.cluster; if (!c) return null;
  const low = c !== 'high_ai_exposure';
  return { text: pick(CLUSTER_TAG[c], locale), low };
}
export const starOf = (o: Occ, dim: string): number | null => o.ratings.find((r) => r.dimension === dim)?.stars ?? null;
// 10 分制数值 → 5 颗星字符串（÷2 取最近半星，半星用 ½）
export function renderStars(n10: number | null | undefined): string {
  if (n10 == null) return '—';
  const v = Math.max(0, Math.min(10, Number(n10))) / 2;     // 0..5
  const r = Math.round(v * 2) / 2;                          // 取最近半星
  const full = Math.floor(r), half = r - full === 0.5;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(5 - full - (half ? 1 : 0));
}
export const rankName = (key: string, locale: Locale) => pick(RANKINGS[key]?.name, locale);
export const rankSub = (key: string, locale: Locale) => pick(RANKINGS[key]?.sub, locale);
export const rankWhy = (key: string, locale: Locale) => pick(RANKINGS[key]?.why, locale);
