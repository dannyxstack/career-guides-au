// 由 RiskLayout 生成 RiskMap 组件需要的 tooltip meta（含方块颜色与跳转链接）。
import type { RiskLayout } from './riskmap';
import { riskColor } from './riskmap';
import { hrefJob, type Display } from './i18n';

export function riskMeta(layout: RiskLayout, locale: Display = 'en') {
  return layout.occs.map((o) => ({
    n: o.name, c: o.cat, w: o.workforce, r: Number(o.risk.toFixed(1)),
    a: o.avgSalary, cur: o.currency,
    u: hrefJob(locale, o.slug),
    col: riskColor(o.risk),
  }));
}
