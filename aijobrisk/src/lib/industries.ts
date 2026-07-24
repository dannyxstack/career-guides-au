// 行业轴（多对多 occupation↔industry）：读 occ_industries_v2 + industries_v2。
// 行业与「职业族 category」是并行两根轴。行业成员由 BLS 就业矩阵映射（阈值≥1%）。
import occIndData from '../data/occ_industries_v2.json';
import indData from '../data/industries_v2.json';
import { occByCountry, catSlug, name as occName, type Occ, type Locale } from './data';

interface OccIndEntry { s: string; n: string; p: number }
const OCC_IND = (occIndData as any).occ as Record<string, OccIndEntry[]>;

export interface Sector { id: string; name: string; occ_total: number; by_country: Record<string, number> }
export const SECTORS: Sector[] = (indData as any).sectors as Sector[];
export const sectorById = (id: string) => SECTORS.find((s) => s.id === id) || null;

// 行业图标（Font Awesome）：按 sector id 映射，无匹配用通用图标。
export const SECTOR_ICON: Record<string, string> = {
  'admin-support': 'fa-clipboard-list', government: 'fa-landmark', education: 'fa-graduation-cap',
  'other-services': 'fa-screwdriver-wrench', professional: 'fa-briefcase', manufacturing: 'fa-industry',
  wholesale: 'fa-boxes-stacked', retail: 'fa-cart-shopping', health: 'fa-heart-pulse',
  construction: 'fa-helmet-safety', management: 'fa-sitemap', arts: 'fa-masks-theater',
  'real-estate': 'fa-building', information: 'fa-tower-broadcast', transport: 'fa-truck-fast',
  hospitality: 'fa-utensils', finance: 'fa-coins', utilities: 'fa-plug', mining: 'fa-mountain',
  agriculture: 'fa-tractor',
};
export const sectorIcon = (id: string) => SECTOR_ICON[id] || 'fa-layer-group';

// 职业族 category（11 类）显示名 → Font Awesome 图标。用于榜单/首页/对比等处，
// 在每个 {industry} 标签前加一致的小图标（req）。无匹配回退通用图标。
export const CATEGORY_ICON: Record<string, string> = {
  'Trades & Construction': 'fa-helmet-safety',
  'Business, Finance & Legal': 'fa-briefcase',
  'Healthcare & Care': 'fa-heart-pulse',
  'Engineering & Infrastructure': 'fa-gears',
  'Creative, Media & Personal Services': 'fa-palette',
  'Hospitality, Retail & Tourism': 'fa-utensils',
  'Transport, Logistics & Mining': 'fa-truck-fast',
  'Education & Community': 'fa-graduation-cap',
  'Agriculture & Environment': 'fa-leaf',
  'Government & Public Sector': 'fa-landmark',
  'IT & Digital': 'fa-code',
};
export const categoryIcon = (name: string | null | undefined) =>
  (name && CATEGORY_ICON[name]) || 'fa-briefcase';

export interface SectorOcc {
  name: string; slug: string; catSlug: string; pct: number;
  aioe: number | null; salary: number | null; workforce: number | null;
}

// 某国某行业下的职业（按占该职业就业比降序返回，含暴露/薪资/人数）
export function occupationsInSector(country: string, sectorId: string, loc: Locale = 'en'): SectorOcc[] {
  const out: SectorOcc[] = [];
  for (const o of occByCountry(country)) {
    const rels = OCC_IND[String(o.id)];
    if (!rels) continue;
    const hit = rels.find((r) => r.s === sectorId);
    if (!hit) continue;
    out.push({
      name: occName(o as Occ, loc), slug: o.slug, catSlug: catSlug(o.category), pct: hit.p,
      aioe: o.ai?.aioe_pct ?? null, salary: o.avg_salary ?? null, workforce: o.workforce_size ?? null,
    });
  }
  return out.sort((a, b) => (b.workforce ?? 0) - (a.workforce ?? 0));
}

// 首页/卡片用：某行业前若干职业名（按人数）作示例
export function sectorExamples(country: string, sectorId: string, n = 3, loc: Locale = 'en'): string[] {
  return occupationsInSector(country, sectorId, loc).slice(0, n).map((o) => o.name);
}
