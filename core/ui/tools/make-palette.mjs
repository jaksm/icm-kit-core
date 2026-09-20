#!/usr/bin/env node
// For the agent: node tools/make-palette.mjs --hue 150 --chroma .5 --tint .3 [--mark 40]  ->  a palette object for a theme JSON.
import { palette, contrast } from '../themes/palette.js';
const arg = k => { const i = process.argv.indexOf('--' + k); return i < 0 ? undefined : +process.argv[i + 1] };
const p = palette({ hue: arg('hue'), chroma: arg('chroma'), tint: arg('tint'), markHue: arg('mark') });
if (process.argv.includes('--selfcheck')) {   // the smallest thing that fails if fit() breaks: a sweep of hues, every text pair at AA
  for (let h = 0; h < 360; h += 15) for (const c of [.1, .5, 1]) { const q = palette({ hue: h, chroma: c, tint: .5 });
    for (const t of [q.light, q.dark]) for (const g of [t.paper, t.card]) for (const [k, need] of [['ink', 7], ['ink-2', 4.5], ['ink-muted', 4.5], ['accent', 4.5]])
      if (contrast(t[k], g) < need) { console.error('fail', h, c, k, contrast(t[k], g).toFixed(2)); process.exit(1) } }
  console.log('ok');
} else console.log(JSON.stringify({ id: 'custom', name: 'Custom', ...p }, null, 2));
