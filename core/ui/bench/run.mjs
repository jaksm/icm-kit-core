#!/usr/bin/env node
// Performance bench for icm-ui pages. Drives the installed Chrome (puppeteer-core, nothing downloaded), records a trace per
// scenario and reports what rAF timing cannot see: where the frame time goes (style, layout, paint, raster, GPU) and how many
// frames were actually drawn. Two profiles: plain, and CPU 4x at DPR 2 (a weaker machine on a retina screen, several tabs open).
//   node run.mjs                    table + results/<stamp>.json       node run.mjs --only theme      one page
//   node run.mjs --save-baseline    writes baseline.json               node run.mjs --check           fails past the budget
// invariant: numbers from headless Chrome are for comparing a change against itself, not absolute truths about a Mac's GPU.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url)), HOME = process.env.HOME;
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const arg = k => { const i = process.argv.indexOf('--' + k); return i < 0 ? null : process.argv[i + 1] ?? true };
const PAGES = {
  theme: process.env.BENCH_THEME || 'file://' + HOME + '/icm-kit-core/previews/theme.html',
  docs: process.env.BENCH_DOCS || 'file://' + path.resolve(HERE, '../docs/index.html'),
  expenses: 'file://' + HOME + '/icm-kit-core/previews/expenses.html',
  site: process.env.BENCH_SITE || 'http://localhost:8915/',
};
// --check is a regression gate against baseline.json, not an absolute bar: headless Chrome draws at 30 fps and its numbers only
// mean something next to the same run on the same machine. A scenario fails when its style or paint time grows past 1.3x + 50 ms,
// when it draws 3 fps fewer, or when a click goes over 100 ms under CPU 4x.
const WORK = ['UpdateLayoutTree', 'Layout', 'PrePaint', 'Paint', 'Layerize', 'Commit', 'RasterTask', 'GPUTask'];

async function traced(page, ms, fn) {
  await page.tracing.start({ categories: ['devtools.timeline', 'disabled-by-default-devtools.timeline.frame', 'cc', 'gpu', 'viz'] });
  const t0 = Date.now(); await fn(); const spent = Date.now() - t0; if (spent < ms) await new Promise(r => setTimeout(r, ms - spent));
  const dur = Date.now() - t0, ev = JSON.parse(Buffer.from(await page.tracing.stop()).toString('utf8')).traceEvents;
  const sum = {}; for (const e of ev) if (e.ph === 'X' && WORK.includes(e.name)) sum[e.name] = (sum[e.name] || 0) + e.dur / 1000;
  const drawn = ev.filter(e => e.name === 'DrawFrame').length;
  const o = { fps: +(drawn / dur * 1000).toFixed(1) }; for (const k of WORK) o[k] = Math.round(sum[k] || 0); o.ms = dur; return o;
}
// input to the frame after next, on the main thread: what a click feels like
const clickMs = (page, js) => page.evaluate(async js => { const t = performance.now(); await (0, eval)(js); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); return +(performance.now() - t).toFixed(1) }, js);
const ED = "document.querySelector('icm-theme-editor')";
const scroll = page => page.evaluate(async () => { const max = document.documentElement.scrollHeight - innerHeight, n = 120; for (let i = 0; i <= n; i++) { scrollTo(0, max * i / n); await new Promise(r => requestAnimationFrame(r)) } scrollTo(0, 0) });

async function benchEditorPage(page, out, themes) {
  for (const th of themes) {
    await page.evaluate(`${ED}.set({theme:'${th}',palette:'',type:'',custom:null,radius:null,size:null,scheme:'light'})`); await new Promise(r => setTimeout(r, 1200));
    out[`scroll ${th}`] = await traced(page, 2200, () => scroll(page));
    const pals = await page.evaluate(`${ED}.theme.palettes.map(p=>p.id)`);
    if (pals.length > 1) { out[`palette tween ${th}`] = await traced(page, 900, () => page.evaluate(`${ED}.set({palette:'${pals[1]}'})`)); out[`palette tween ${th}`].click_ms = await clickMs(page, `${ED}.set({palette:'${pals[0]}'})`) }
  }
  await page.evaluate(`${ED}.set({theme:'ledger',palette:'',type:'',custom:null,scheme:'light'})`); await new Promise(r => setTimeout(r, 800));
  out['type tween ledger'] = await traced(page, 900, () => page.evaluate(`${ED}.set({type:'archivo-narrow'})`));
  out['theme switch x4 (ripple)'] = await traced(page, 3200, async () => { for (const th of ['aquarium', 'night-drive', 'orchard', 'ledger']) { await page.evaluate(`(()=>{const b=${ED}.querySelector('[data-theme=${th}]');b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();b.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:r.x+9,clientY:r.y+9}))})()`); await new Promise(r => setTimeout(r, 750)) } });
  out['theme switch x4 (ripple)'].click_ms = await clickMs(page, `${ED}.set({theme:'tty',palette:'',type:''})`);
  await page.evaluate(`${ED}.set({theme:'ledger',palette:'',type:'',custom:null})`); await new Promise(r => setTimeout(r, 600));
  // a real drag across the color pad: real pointer events, one move per 16 ms
  const box = await page.evaluate(`(()=>{const p=${ED}.querySelector('.te-pad');p.scrollIntoView({block:'center'});const r=p.getBoundingClientRect();return[r.x,r.y,r.width,r.height]})()`);
  out['pad drag 2s'] = await traced(page, 2200, async () => { await page.mouse.move(box[0] + 5, box[1] + 20); await page.mouse.down(); for (let i = 0; i < 110; i++) { await page.mouse.move(box[0] + 5 + (box[2] - 10) * i / 110, box[1] + 20 + 40 * Math.sin(i / 9)); await new Promise(r => setTimeout(r, 16)) } await page.mouse.up() });
  await page.evaluate(`${ED}.set({custom:null})`);
}
async function benchSite(page, out) {
  out['site idle 3s'] = await traced(page, 3000, async () => {});
  out['site scroll'] = await traced(page, 2600, () => scroll(page));
  const st = await page.evaluate(() => { const s = document.querySelector('.stack'); if (!s) return null; s.scrollIntoView({ block: 'center' }); const r = s.getBoundingClientRect(); return [r.x, r.y, r.width, r.height] });
  if (st) out['site pointer over stack 2s'] = await traced(page, 3200, async () => { for (let i = 0; i < 110; i++) { await page.mouse.move(st[0] + st[2] * (.5 + .45 * Math.sin(i / 8)), st[1] + st[3] / 2); await new Promise(r => setTimeout(r, 16)) } });
}

const only = arg('only'), results = {};
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--use-angle=metal', '--enable-gpu-rasterization', '--window-size=1440,900', '--hide-scrollbars'] });
for (const profile of ['plain', 'cpu4x']) for (const [name, url] of Object.entries(PAGES)) {
  if (only && only !== name) continue;
  const page = await browser.newPage(); await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
  try { await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 }) } catch (e) { console.error(`skip ${name}: ${e.message.split('\n')[0]}`); await page.close(); continue }
  if (profile === 'cpu4x') await page.emulateCPUThrottling(4);
  const out = results[`${name} / ${profile}`] = {};
  const size = await page.evaluate(() => ({ dom: document.querySelectorAll('*').length, html_kb: Math.round(document.documentElement.outerHTML.length / 1024), font_kb: Math.round(performance.getEntriesByType('resource').filter(r => /\.woff2/.test(r.name)).reduce((a, r) => a + (r.transferSize || r.encodedBodySize || 0), 0) / 1024), fcp: Math.round(performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0) }));
  out.load = size;
  const hasEditor = await page.evaluate(`!!${ED}`);
  if (name === 'site') await benchSite(page, out);
  else if (hasEditor) await benchEditorPage(page, out, name === 'theme' ? ['ledger', 'aquarium', 'night-drive', 'blueprint', 'tty'] : ['ledger', 'aquarium']);
  else out['scroll'] = await traced(page, 2200, () => scroll(page));
  await page.close();
}
await browser.close();

const rows = []; for (const [pg, sc] of Object.entries(results)) for (const [k, v] of Object.entries(sc)) if (k !== 'load') rows.push({ page: pg, scenario: k, fps: v.fps, click: v.click_ms ?? '', style: v.UpdateLayoutTree, layout: v.Layout, paint: v.Paint + v.PrePaint, raster: v.RasterTask, gpu: v.GPUTask });
console.table(rows); for (const [pg, sc] of Object.entries(results)) console.log(pg, JSON.stringify(sc.load));
fs.mkdirSync(path.join(HERE, 'results'), { recursive: true });
fs.writeFileSync(path.join(HERE, 'results', new Date().toISOString().slice(0, 19).replace(/:/g, '') + (arg('tag') ? '-' + arg('tag') : '') + '.json'), JSON.stringify(results, null, 1));
if (arg('save-baseline')) fs.writeFileSync(path.join(HERE, 'baseline.json'), JSON.stringify(results, null, 1));
if (arg('check')) { const base = JSON.parse(fs.readFileSync(path.join(HERE, 'baseline.json'), 'utf8')), bad = [];
  for (const r of rows) { const b = base[r.page]?.[r.scenario]; if (!b) continue;
    for (const [k, was] of [['style', b.UpdateLayoutTree], ['paint', b.Paint + b.PrePaint]]) if (r[k] > was * 1.3 + 50) bad.push(`${r.page} / ${r.scenario}: ${k} ${was} -> ${r[k]} ms`);
    if (/scroll|drag/.test(r.scenario) && r.fps < b.fps - 3) bad.push(`${r.page} / ${r.scenario}: ${b.fps} -> ${r.fps} fps`);
    if (/cpu4x/.test(r.page) && r.click !== '' && r.click > 100) bad.push(`${r.page} / ${r.scenario}: click ${r.click} ms`) }
  if (bad.length) { console.error('slower than the baseline:\n  ' + bad.join('\n  ')); process.exit(1) } console.log('no slower than the baseline') }
