import fs from 'fs';
const src = fs.readFileSync('site/src/lib/data.ts','utf8');
const m = src.match(/export const UI:[^=]*=\s*(\{[\s\S]*?\n\});/);
if(!m){console.error('UI block not found');process.exit(1);}
const UI = eval('('+m[1].replace(/;\s*$/,'')+')');
const out = { ui: UI.en };
fs.writeFileSync('scripts/_ui_src.json', JSON.stringify(out,null,1));
console.log('en keys:', Object.keys(UI.en).length, '| zh keys:', Object.keys(UI['zh-CN']).length);
