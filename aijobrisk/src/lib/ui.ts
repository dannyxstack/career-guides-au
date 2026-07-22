// 共享展示助手：AI 暴露度分档、10分制风险档、薪资/数字格式化。
// 暴露百分位（aioe_pct 0-100）与 10分制自动化暴露（automation_exposure 1-10）是两套不同刻度。
import { CURRENCY } from './data';

export interface Band { label: string; cls: string }

// 生成式 AI 暴露百分位（0-100，越高越暴露）→ 语义档（含无障碍文字标签）
export function expBand(pct: number | null | undefined): Band {
  if (pct == null) return { label: 'n/a', cls: 'verylow' };
  if (pct >= 90) return { label: 'critical', cls: 'critical' };
  if (pct >= 70) return { label: 'high', cls: 'high' };
  if (pct >= 40) return { label: 'moderate', cls: 'moderate' };
  if (pct >= 20) return { label: 'low', cls: 'low' };
  return { label: 'very low', cls: 'verylow' };
}

// 10 分制自动化暴露（automation_exposure）→ 简档（详情页大徽章用）
export function riskBand10(v: number | null | undefined): Band {
  if (v == null) return { label: 'Unknown', cls: 'verylow' };
  if (v >= 7) return { label: 'High', cls: 'high' };
  if (v >= 4.5) return { label: 'Moderate', cls: 'moderate' };
  return { label: 'Lower', cls: 'low' };
}

export function fmtNum(n: number | null | undefined): string {
  if (n == null) return '—';
  return Math.round(n).toLocaleString('en');
}

export function fmtSalary(v: number | null | undefined, country?: string): string {
  if (v == null) return '—';
  const cur = (country && CURRENCY[country]) || 'USD';
  try {
    return new Intl.NumberFormat('en', { style: 'currency', currency: cur, maximumFractionDigits: 0 }).format(v);
  } catch {
    return fmtNum(v) + ' ' + cur;
  }
}
