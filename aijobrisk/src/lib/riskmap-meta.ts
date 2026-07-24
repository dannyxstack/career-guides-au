// 由 RiskLayout 生成 RiskMap 组件需要的 tooltip meta（含方块颜色与跳转链接）。
import type { RiskLayout } from './riskmap';
import { riskColor } from './riskmap';
import { hrefJob, contentLocale, type Display } from './i18n';
import { tr } from './data';

export function riskMeta(layout: RiskLayout, locale: Display = 'en') {
  const CL = contentLocale(locale);
  return layout.occs.map((o) => ({
    n: tr(o.name, CL), c: tr(o.cat, CL), w: o.workforce, r: Number(o.risk.toFixed(1)),
    a: o.avgSalary, cur: o.currency,
    u: hrefJob(locale, o.slug),
    col: riskColor(o.risk),
  }));
}
