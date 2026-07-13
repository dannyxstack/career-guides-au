// 首页滚动播报：构建期从 occupations 预生成一批「洞察句」，前端每次展示一行、轮播。
// 数据全部来自 data.ts（occupations_v2.json，含 polls 烘焙），无需运行时后端。
import { occupations, name, strings, type Locale, type Occ } from './data';

const fill = (tpl: string, vars: Record<string, string | number>) =>
  tpl.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''));

// automation_exposure(1–10) → 「未来5年被AI替代概率」估算值（%），标注为预计
const expToPct = (exp: number) => Math.min(92, Math.max(10, Math.round(exp * 9)));

// ai_replace 投票的加权平均风险（选项 mid 值，与 polls.json 对齐）
const AI_REPLACE_MID: Record<string, number> = { lt10: 5, '10_30': 20, '40_60': 50, '60_80': 70, gt80: 90 };

// 交错三组，让相邻播报格式不同，读起来更活
function interleave<T>(...groups: T[][]): T[] {
  const out: T[] = [];
  const max = Math.max(0, ...groups.map((g) => g.length));
  for (let i = 0; i < max; i++) for (const g of groups) if (i < g.length) out.push(g[i]);
  return out;
}

export function buildTicker(locale: Locale): string[] {
  const t = strings(locale);
  // 以 AU 母本为职业池（数据最全、去重后职业不跨国重复）
  const AU = occupations.filter((o) => o.country === 'AU' && o.ai?.automation_exposure != null);

  // #1 每个分类里 AI 暴露最高的 3 个职业
  const byCat = new Map<string, Occ[]>();
  for (const o of AU) {
    const arr = byCat.get(o.category) ?? [];
    arr.push(o);
    byCat.set(o.category, arr);
  }
  const g1: string[] = [];
  for (const [cat, list] of byCat) {
    const top = [...list].sort((a, b) => b.ai!.automation_exposure! - a.ai!.automation_exposure!).slice(0, 3);
    if (top.length === 3)
      g1.push(fill(t.hTk1, { cat, a: name(top[0], locale), b: name(top[1], locale), c: name(top[2], locale) }));
  }

  // #2 未来5年被AI替代概率（由暴露度换算，措辞为「预计/约」）
  const byExp = [...AU].sort((a, b) => b.ai!.automation_exposure! - a.ai!.automation_exposure!);
  const g2 = byExp.slice(0, 30).map((o) => fill(t.hTk2, { name: name(o, locale), pct: expToPct(o.ai!.automation_exposure!) }));

  // #6 AIOE 学术 AI 暴露度（0–100）
  const byAioe = AU.filter((o) => o.ai?.aioe_pct != null).sort((a, b) => b.ai!.aioe_pct! - a.ai!.aioe_pct!);
  const g6 = byAioe.slice(0, 30).map((o) => fill(t.hTk6, { name: name(o, locale), pct: o.ai!.aioe_pct! }));

  // #4/#5 投票类：仅当有真实票数时才生成（后端上线前 polls 为空，自动跳过）
  const gPoll: string[] = [];
  for (const o of occupations) {
    const p: any = o.polls;
    if (!p) continue;
    const cc = p.career_change;
    const yes = cc?.counts?.yes ?? 0;
    if (cc?.total > 0 && yes > 0) gPoll.push(fill(t.hTk4, { n: yes, name: name(o, locale) }));
    const ar = p.ai_replace;
    if (ar?.total > 0 && ar.counts) {
      let n = 0, s = 0;
      for (const [k, c] of Object.entries<number>(ar.counts)) { n += c; s += c * (AI_REPLACE_MID[k] ?? 50); }
      if (n > 0) gPoll.push(fill(t.hTk5, { n: ar.total, name: name(o, locale), pct: Math.round(s / n) }));
    }
  }

  const lines = interleave(g2, g6, g1, gPoll);
  return Array.from(new Set(lines)).slice(0, 100);
}
