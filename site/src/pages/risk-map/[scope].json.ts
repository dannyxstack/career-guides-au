// 风险地图元数据外置为静态 JSON：/risk-map/WORLD.json 与 /risk-map/{cc}.json。
// 客户端 tooltip 按需 fetch，避免把整份 meta 内联进每个风险地图页的 HTML（world 图尤其大）。
// meta 用英文名 + 英文链接，故与 locale 无关，各语言共享同一份。
import type { APIRoute } from 'astro';
import { COUNTRIES, jobHref } from '../../lib/data';
import { buildRiskMap, buildGlobalRiskMap, riskColor } from '../../lib/riskmap';

export function getStaticPaths() {
  return [{ params: { scope: 'WORLD' } }, ...COUNTRIES.map((cc) => ({ params: { scope: cc } }))];
}

export const GET: APIRoute = ({ params }) => {
  const scope = params.scope as string;
  const layout = scope === 'WORLD' ? buildGlobalRiskMap() : buildRiskMap(scope);
  const meta = layout.occs.map((o) => ({
    n: o.name, c: o.cat, w: o.workforce, r: Math.round(o.risk * 10) / 10,
    a: o.avgSalary, cur: o.currency,
    u: scope === 'WORLD' ? jobHref('en', o.slug) : jobHref('en', o.slug, o.country),
    col: riskColor(o.risk),
  }));
  return new Response(JSON.stringify(meta), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
