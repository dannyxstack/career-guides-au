// 从 aijobrisk/src/lib/data.ts 提取内嵌双语字典常量为 JSON，供 Go 版加载（零手工转写）。
// 用法：node tools/extract_dicts.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.resolve(__dir, '../../aijobrisk/src/lib/data.ts');
const OUT = path.resolve(__dir, '../data/derived');
fs.mkdirSync(OUT, { recursive: true });

const text = fs.readFileSync(SRC, 'utf8');

// 从 `const NAME` 处起，找到 '=' 后的首个 '{'，做字符串感知的花括号匹配，返回对象字面量文本。
function sliceObject(name) {
  const re = new RegExp(`\\bconst\\s+${name}\\b`);
  const m = re.exec(text);
  if (!m) throw new Error(`not found: ${name}`);
  let i = text.indexOf('=', m.index);
  i = text.indexOf('{', i);
  const start = i;
  let depth = 0, str = null, esc = false;
  for (; i < text.length; i++) {
    const c = text[i];
    if (str) {
      if (esc) { esc = false; continue; }
      if (c === '\\') { esc = true; continue; }
      if (c === str) str = null;
      continue;
    }
    if (c === '"' || c === "'" || c === '`') { str = c; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  return text.slice(start, i);
}

const names = ['DIM_LABEL', 'DIM_DESC', 'DIS_TYPE', 'DIS_LEVEL', 'UI', 'SOURCES_BODY', 'RANKINGS', 'MIG_TEXT', 'COUNTRY_FLAG', 'COUNTRY_NAME'];
for (const n of names) {
  const lit = sliceObject(n);
  // eslint-disable-next-line no-eval
  const obj = eval('(' + lit + ')');
  fs.writeFileSync(path.join(OUT, `${n}.json`), JSON.stringify(obj), 'utf8');
  console.log(`[extract] ${n} -> ${n}.json (${Object.keys(obj).length} keys)`);
}
console.log('done ->', OUT);
