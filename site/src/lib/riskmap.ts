// AI Job Risk Map 布局：按职业分类分成带间隔的大块（块面积∝该类总从业人数），
// 每块内部用 squarified treemap 把各职业铺成长宽比接近 1 的矩形（面积∝从业人数）。
// 颜色由页面按 automation_exposure 决定；国家边界作为背后隐约水印单独给出路径。
import outlinesRaw from '../data/country-outline.json';
import { occByCountry, catSlug, name as occName } from './data';

// 每国一组环（多边形外环，含周边岛屿）
const outlines = outlinesRaw as Record<string, [number, number][][]>;

export interface RiskRect { x: number; y: number; w: number; h: number; i: number }
export interface OccMeta {
  name: string; cat: string; catSlug: string; slug: string; country: string;
  risk: number; workforce: number; score: number | null;
}
export interface CatBlock { x: number; y: number; w: number; h: number; text: string; count: number }
export interface RiskLayout {
  W: number; H: number; rects: RiskRect[]; occs: OccMeta[];
  catBlocks: CatBlock[]; outlinePath: string; total: number; hasData: boolean;
}

// automation_exposure(1..10) -> 绿→黄→红
export function riskColor(v: number): string {
  const t = Math.max(0, Math.min(1, (v - 1) / 9));
  const stops = [
    [16, 185, 129],  // green  低
    [245, 158, 11],  // amber  中
    [239, 68, 68],   // red    高
  ];
  const seg = t < 0.5 ? 0 : 1;
  const lt = t < 0.5 ? t / 0.5 : (t - 0.5) / 0.5;
  const a = stops[seg], b = stops[seg + 1];
  const c = a.map((av, i) => Math.round(av + (b[i] - av) * lt));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

// 把国家的全部环（多边形，含岛屿）用同一变换投影（等距 + cos(midLat) 横向校正）
// 等比缩放居中到 W×H 内，返回含多个子路径的 SVG path。
function outlineToPath(rings: [number, number][][], W: number, H: number, margin: number): string {
  const all = rings.flat();
  if (all.length === 0) return '';
  const lons = all.map((p) => p[0]), lats = all.map((p) => p[1]);
  const minLon = Math.min(...lons), maxLon = Math.max(...lons);
  const minLat = Math.min(...lats), maxLat = Math.max(...lats);
  const kx = Math.cos(((minLat + maxLat) / 2) * Math.PI / 180);
  const gw = (maxLon - minLon) * kx || 1, gh = (maxLat - minLat) || 1;
  const s = Math.min((W - 2 * margin) / gw, (H - 2 * margin) / gh);
  const dw = gw * s, dh = gh * s;
  const ox = (W - dw) / 2, oy = (H - dh) / 2;
  const project = (ring: [number, number][]) =>
    'M' + ring.map(([lon, lat]) =>
      `${(ox + (lon - minLon) * kx * s).toFixed(1)} ${(oy + (maxLat - lat) * s).toFixed(1)}`
    ).join('L') + 'Z';
  return rings.map(project).join('');
}

// --- squarified treemap（Bruls et al.）---
interface SqItem<T> { value: number; ref: T }
interface SqRect<T> { x: number; y: number; w: number; h: number; ref: T }

function worstRatio<T>(row: SqItem<T>[], side: number): number {
  let sum = 0, mn = Infinity, mx = -Infinity;
  for (const r of row) { sum += r.value; if (r.value < mn) mn = r.value; if (r.value > mx) mx = r.value; }
  const s2 = sum * sum, side2 = side * side;
  return Math.max((side2 * mx) / s2, s2 / (side2 * mn));
}

function squarify<T>(data: SqItem<T>[], x: number, y: number, w: number, h: number): SqRect<T>[] {
  const out: SqRect<T>[] = [];
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total <= 0 || w <= 0 || h <= 0) return out;
  const scale = (w * h) / total;
  const items = data.map((d) => ({ value: Math.max(d.value * scale, 1e-6), ref: d.ref }));
  let rx = x, ry = y, rw = w, rh = h, i = 0;
  while (i < items.length) {
    let row = [items[i]];
    let side = Math.min(rw, rh);
    let cur = worstRatio(row, side);
    let j = i + 1;
    while (j < items.length) {
      const test = row.concat([items[j]]);
      const tr = worstRatio(test, side);
      if (tr <= cur) { row = test; cur = tr; j++; } else break;
    }
    const rowSum = row.reduce((s, r) => s + r.value, 0);
    if (rw >= rh) { // 行竖着排成一列，占宽 colW
      const colW = rowSum / rh;
      let yy = ry;
      for (const it of row) { const hh = it.value / colW; out.push({ x: rx, y: yy, w: colW, h: hh, ref: it.ref }); yy += hh; }
      rx += colW; rw -= colW;
    } else {
      const rowH = rowSum / rw;
      let xx = rx;
      for (const it of row) { const ww = it.value / rowH; out.push({ x: xx, y: ry, w: ww, h: rowH, ref: it.ref }); xx += ww; }
      ry += rowH; rh -= rowH;
    }
    i = j;
  }
  return out;
}

// 把长宽比 > cap 的矩形沿长边等分成若干 ≤cap:1 的同职业小块（兜底，杜绝长条）。
function splitAspect(r: SqRect<number>, cap: number): SqRect<number>[] {
  const long = Math.max(r.w, r.h), short = Math.min(r.w, r.h);
  if (short <= 0 || long / short <= cap + 1e-6) return [r];
  const n = Math.ceil(long / (short * cap));
  const out: SqRect<number>[] = [];
  if (r.w >= r.h) {
    const cw = r.w / n;
    for (let k = 0; k < n; k++) out.push({ x: r.x + k * cw, y: r.y, w: cw, h: r.h, ref: r.ref });
  } else {
    const ch = r.h / n;
    for (let k = 0; k < n; k++) out.push({ x: r.x, y: r.y + k * ch, w: r.w, h: ch, ref: r.ref });
  }
  return out;
}

const W = 1600, H = 720;  // 宽屏画布（数据量大，横向铺更多格）
const OUTER = 6;   // 画布外边距
const GAP = 12;    // 分类块之间的大间隔
const LABEL = 22;  // 分类块顶部标题高度
const PAD = 5;     // 块内边距

export function buildRiskMap(country: string): RiskLayout {
  const occsAll = occByCountry(country).filter(
    (o) => o.workforce_size != null && o.workforce_size > 0 && o.ai?.automation_exposure != null,
  );
  const occs: OccMeta[] = occsAll.map((o) => ({
    name: occName(o, 'en'),
    cat: o.category, catSlug: catSlug(o.category), slug: o.slug, country: o.country,
    risk: o.ai!.automation_exposure as number,
    workforce: o.workforce_size as number,
    score: o.overall_score,
  }));
  const rings = outlines[country];
  const outlinePath = rings ? outlineToPath(rings, W, H, 30) : '';

  if (occs.length === 0) {
    return { W, H, rects: [], occs, catBlocks: [], outlinePath, total: 0, hasData: false };
  }

  // 按分类聚合
  const byCat = new Map<string, number[]>();
  occs.forEach((o, i) => { const a = byCat.get(o.cat); if (a) a.push(i); else byCat.set(o.cat, [i]); });
  const cats = [...byCat.entries()]
    .map(([cat, idxs]) => ({ cat, idxs, total: idxs.reduce((s, i) => s + occs[i].workforce, 0) }))
    .sort((a, b) => b.total - a.total);

  // 外层 treemap：分类块
  const catRects = squarify(
    cats.map((c) => ({ value: c.total, ref: c })),
    OUTER, OUTER, W - 2 * OUTER, H - 2 * OUTER,
  );

  const rects: RiskRect[] = [];
  const catBlocks: CatBlock[] = [];
  for (const cr of catRects) {
    const c = cr.ref;
    const bx = cr.x + GAP / 2, by = cr.y + GAP / 2, bw = cr.w - GAP, bh = cr.h - GAP;
    if (bw <= 2 || bh <= 2) continue;
    catBlocks.push({ x: bx, y: by, w: bw, h: bh, text: c.cat, count: c.idxs.length });
    const ix = bx + PAD, iy = by + LABEL, iw = bw - 2 * PAD, ih = bh - LABEL - PAD;
    if (iw <= 2 || ih <= 2) continue;
    // 内层 treemap：该分类各职业（按人数降序，squarify 效果更好）。
    // 面积设下限（均值的 30%），压缩悬殊比例，避免小职业被挤成细条；面积因此为近似值。
    const floorV = (c.total / c.idxs.length) * 0.3;
    const items = c.idxs.slice()
      .sort((a, b) => occs[b].workforce - occs[a].workforce)
      .map((i) => ({ value: Math.max(occs[i].workforce, floorV), ref: i }));
    for (const r of squarify(items, ix, iy, iw, ih)) {
      for (const s of splitAspect(r, 2)) rects.push({ x: s.x, y: s.y, w: s.w, h: s.h, i: s.ref });
    }
  }

  return { W, H, rects, occs, catBlocks, outlinePath, total: occs.length, hasData: true };
}
