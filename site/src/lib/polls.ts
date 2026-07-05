// 投票配置（单一真相源 = polls.json，前端与 API 共用同一份定义）。
// 加新投票只需往 polls.json 加一项；票表 / API / widget 不动。
import pollsData from '../data/polls.json';
import type { Locale } from './data';

export interface PollOption {
  key: string;
  mid?: number; // 数值中点（单选折算“大众平均%”用）
  label: Record<string, string>;
}
export interface Poll {
  code: string;
  type: 'single' | 'slider';
  scope: string;
  q: Record<string, string>;
  conclusion?: Record<string, string>;
  options: PollOption[];
}

export const POLLS: Poll[] = (pollsData as any).polls as Poll[];

// 取本地化文案：缺失回退 en（站点只维护中英文母本）
export function locText(m: Record<string, string>, locale: Locale): string {
  return m[locale] ?? m.en ?? Object.values(m)[0] ?? '';
}

// 单选聚合折算大众平均分（用 option.mid 加权），无 mid 或无票返回 null
export function avgFromCounts(poll: Poll, counts: Record<string, number>): number | null {
  let n = 0, s = 0;
  for (const o of poll.options) {
    if (o.mid == null) return null;
    const c = counts[o.key] || 0;
    n += c; s += c * o.mid;
  }
  return n ? Math.round(s / n) : null;
}

export function totalCount(counts: Record<string, number>): number {
  return Object.values(counts || {}).reduce((a, b) => a + (b || 0), 0);
}

// 各选项百分比：{optionKey: pct(0-100 整数)}
export function pctOf(counts: Record<string, number>): Record<string, number> {
  const total = totalCount(counts);
  const out: Record<string, number> = {};
  for (const k of Object.keys(counts || {})) out[k] = total ? Math.round((counts[k] * 100) / total) : 0;
  return out;
}

// 模板填充：{name} {n} {avg} 以及 {pct.<optionKey>}。
// 只替换传入的键，未提供的占位符原样保留（便于分两步填：先服务端填 name，再客户端填 n/avg/pct）。
export function fillTpl(
  tpl: string,
  vars: { name?: string; n?: number | string; avg?: number | string | null },
  pct?: Record<string, number>,
): string {
  let s = tpl || '';
  if (pct) s = s.replace(/\{pct\.(\w+)\}/g, (m, k) => (k in pct ? String(pct[k]) : m));
  s = s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? ((vars as any)[k] == null ? '' : String((vars as any)[k])) : m));
  return s;
}
