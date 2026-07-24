// 榜单计算（rankings.html 的 6 个 board）：按国家从 occupations 派生，默认 US（薪资为真实官方均值）。
// 全部由透明规则自动排序，非人工指定。
import { occByCountry, catSlug, name as occName, tr, type Occ, type Locale } from './data';

export interface RankItem {
  name: string; slug: string; cat: string; catSlug: string;
  aioe: number | null; salary: number | null; workforce: number | null;
  demand: number | null; moat: number | null;
}
export interface Board { id: string; title: string; desc: string; metric: 'aioe' | 'salary' | 'workforce' | 'demand' | 'moat'; items: RankItem[] }

function toItem(o: Occ, loc: Locale): RankItem {
  const demand = o.ratings.find((r) => r.dimension === 'job_demand')?.stars ?? null;
  return {
    name: occName(o, loc), slug: o.slug, cat: o.category, catSlug: catSlug(o.category),
    aioe: o.ai?.aioe_pct ?? null, salary: o.avg_salary ?? null,
    workforce: o.workforce_size ?? null, demand, moat: o.ai?.human_moat ?? null,
  };
}

const byDesc = (f: (i: RankItem) => number | null) => (a: RankItem, b: RankItem) =>
  (f(b) ?? -Infinity) - (f(a) ?? -Infinity);
const byAsc = (f: (i: RankItem) => number | null) => (a: RankItem, b: RankItem) =>
  (f(a) ?? Infinity) - (f(b) ?? Infinity);

export function buildBoards(country: string, top = 5, loc: Locale = 'en'): Board[] {
  const all = occByCountry(country).map((o) => toItem(o, loc));
  const withExp = all.filter((i) => i.aioe != null);
  const withPay = all.filter((i) => i.salary != null);
  const withWork = all.filter((i) => i.workforce != null && i.workforce > 0);
  const withDemand = all.filter((i) => i.demand != null);
  const withMoat = all.filter((i) => i.moat != null);
  return [
    { id: 'most-exposed', title: tr('Most exposed to AI', loc), desc: tr('Highest generative-AI exposure percentile', loc), metric: 'aioe',
      items: [...withExp].sort(byDesc((i) => i.aioe)).slice(0, top) },
    { id: 'least-exposed', title: tr('Least exposed to AI', loc), desc: tr('Most resilient to automation', loc), metric: 'aioe',
      items: [...withExp].sort(byAsc((i) => i.aioe)).slice(0, top) },
    { id: 'highest-paying', title: tr('Highest paying', loc), desc: tr('Average annual salary', loc), metric: 'salary',
      items: [...withPay].sort(byDesc((i) => i.salary)).slice(0, top) },
    { id: 'largest-workforce', title: tr('Largest workforce', loc), desc: tr('Total employed', loc), metric: 'workforce',
      items: [...withWork].sort(byDesc((i) => i.workforce)).slice(0, top) },
    { id: 'strongest-demand', title: tr('Strongest job demand', loc), desc: tr('Projected demand (1–10 scale)', loc), metric: 'demand',
      items: [...withDemand].sort(byDesc((i) => i.demand)).slice(0, top) },
    { id: 'deepest-moat', title: tr('Deepest human moat', loc), desc: tr('Hardest for AI to replace (1–10 scale)', loc), metric: 'moat',
      items: [...withMoat].sort(byDesc((i) => i.moat)).slice(0, top) },
  ];
}

export function boardById(country: string, id: string, top = 50, loc: Locale = 'en'): Board | null {
  return buildBoards(country, top, loc).find((b) => b.id === id) || null;
}
