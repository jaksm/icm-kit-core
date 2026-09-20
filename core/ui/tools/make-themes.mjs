#!/usr/bin/env node
// Writes themes/*.json from the recipes below, so a bundled theme is reproducible: a recipe is seeds + a few hand-set tokens,
// palette() fits everything else to AA. Ledger's first palette and Houseguest are explicit (they match something that exists).
// Run: node tools/make-themes.mjs && python3 build.py --check
import fs from 'node:fs';
import { palette } from '../themes/palette.js';
const G = (...f) => f.map(x => 'family=' + x).join('&');
const sans = f => `"${f}",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif`;
const serif = f => `"${f}",ui-serif,Georgia,Cambria,"Times New Roman",serif`;
const mono = f => `"${f}",ui-monospace,SFMono-Regular,Menlo,monospace`;
const flat = { 'stretch-title': '100%', 'stretch-num': '100%' };
// a palette recipe: seeds for palette(), then tokens set by hand per scheme (extra), `only` = a one-scheme palette
const pal = (id, name, seeds, extra = {}, only) => { const p = palette(seeds), o = { id, name };
  for (const k of only ? [only] : ['light', 'dark']) o[k] = { ...p[k], ...(extra[k] || extra.both || {}) }; return o };

const LEDGER_MARK = { light: [.85, .15, 95], dark: [.85, .15, 95] };
const themes = [
{ id: 'ledger', name: 'Ledger', blurb: 'Calm brutal: cold paper, blue-black ink, one highlighter, a hard shadow on what can be pressed. The default; its first palette equals the token files.',
  palettes: [{ id: 'ultramarine', name: 'Ultramarine', light: {}, dark: {} },
    pal('oxblood', 'Oxblood', { hue: 22, chroma: .75, tint: .2, mark: [.85, .15, 95] }), pal('forest', 'Forest', { hue: 155, chroma: .55, tint: .25, mark: [.85, .15, 95] })],
  type: [{ id: 'archivo', name: 'Archivo', tokens: {}, google: G('Archivo:wdth,wght@62..125,100..900', 'JetBrains+Mono:wght@400..700') },
    { id: 'archivo-narrow', name: 'Archivo Narrow', tokens: { 'stretch-title': '72%', 'stretch-num': '68%', 'track-title': '-.02em' }, google: G('Archivo:wdth,wght@62..125,100..900', 'JetBrains+Mono:wght@400..700') },
    { id: 'grotesk', name: 'Space Grotesk', tokens: { 'font-sans': sans('Space Grotesk'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', ...flat }, google: G('Space+Grotesk:wght@400..700', 'JetBrains+Mono:wght@400..700') }],
  shape: {}, effects: {}, motion: {} },

{ id: 'aquarium', name: 'Aquarium', blurb: 'Liquid glass: translucent cards over a colored depth, blur behind, large radii, a bright rim, soft shadows.',
  palettes: [['lagoon', 'Lagoon', 215, 190], ['dusk', 'Dusk', 290, 330], ['pearl', 'Pearl', 40, 250]].map(([id, name, hue, h2]) => pal(id, name, { hue, chroma: .7, tint: .8, mark: [.9, .1, h2] }, {
    light: { 'card-fill': 'rgba(255,255,255,.55)', edge: 'rgba(255,255,255,.75)', 'edge-strong': 'rgba(255,255,255,.95)', 'press-color': `hsla(${hue},40%,25%,.22)`,
      'page-bg': `radial-gradient(120% 80% at 10% 0%,hsl(${hue} 80% 86%),transparent 60%),radial-gradient(100% 70% at 100% 30%,hsl(${h2} 80% 88%),transparent 55%),var(--paper)` },
    dark: { 'card-fill': 'rgba(255,255,255,.07)', edge: 'rgba(255,255,255,.16)', 'edge-strong': 'rgba(255,255,255,.34)', 'press-color': 'rgba(0,0,0,.5)',
      'page-bg': `radial-gradient(120% 80% at 10% 0%,hsl(${hue} 60% 22%),transparent 60%),radial-gradient(100% 70% at 100% 30%,hsl(${h2} 55% 20%),transparent 55%),var(--paper)` } })),
  type: [{ id: 'geist', name: 'Geist', tokens: { 'font-sans': sans('Geist'), 'font-mono': mono('Geist Mono'), 'w-body': '400', 'w-strong': '600', 'w-loud': '650', 'w-ui': '500', ...flat }, google: G('Geist:wght@300..800', 'Geist+Mono:wght@400..700') },
    { id: 'instrument', name: 'Instrument Sans', tokens: { 'font-sans': sans('Instrument Sans'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'stretch-title': '90%', 'stretch-num': '85%' }, google: G('Instrument+Sans:wdth,wght@75..100,400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'manrope', name: 'Manrope', tokens: { 'font-sans': sans('Manrope'), 'w-body': '500', 'w-strong': '700', 'w-loud': '800', ...flat }, google: G('Manrope:wght@400..800', 'JetBrains+Mono:wght@400..700') }],
  shape: { radius: '20px', 'radius-s': '12px', border: '1px', 'press-x': '0px', 'press-y': '2px', 'press-blur': '18px' }, effects: { 'card-backdrop': 'blur(18px) saturate(1.5)' }, motion: {} },

{ id: 'tty', name: 'TTY', blurb: 'A terminal: one monospace for everything, square corners, a one-pixel edge, no shadow; the marker is a block cursor.',
  palettes: [pal('phosphor', 'Phosphor', { hue: 145, chroma: .9, tint: .6, inkHue: 145, inkC: .17, ground: { dark: { paper: [.15, .02, 150], card: [.19, .025, 150] } }, mark: [.86, .22, 145] }, {}, 'dark'),
    pal('amber', 'Amber', { hue: 75, chroma: .9, tint: .6, inkHue: 80, inkC: .15, ground: { dark: { paper: [.15, .015, 70], card: [.19, .02, 70] } }, mark: [.84, .17, 80] }, {}, 'dark'),
    pal('paper', 'Paper', { hue: 250, chroma: .5, tint: .1, mark: [.25, .02, 250] })],
  type: [['jetbrains', 'JetBrains Mono', 'JetBrains+Mono:wght@400..800'], ['roboto', 'Roboto Mono', 'Roboto+Mono:wght@400..700'], ['fira', 'Fira Code', 'Fira+Code:wght@400..700']].map(([id, name, g]) =>
    ({ id, name, tokens: { 'font-sans': mono(name), 'font-mono': mono(name), 'w-body': '400', 'w-strong': '700', 'w-loud': '700', 'w-ui': '500', 'track-title': '0', 'track-heading': '0', 'track-sub': '0', 'track-num': '-.02em', ...flat }, google: G(g) })),
  shape: { radius: '0px', 'radius-s': '0px', border: '1px', 'press-x': '0px', 'press-y': '0px', 'press-blur': '0px' }, effects: {}, motion: {} },

{ id: 'houseguest', name: 'Houseguest', blurb: 'At home in the Claude desktop app: its warm paper, its ink, its clay accent, serif titles, quiet edges. Colors are the host values icm-ui matched before 0.3; the muted ink is darkened to reach AA.',
  palettes: [{ id: 'claude', name: 'Claude',
    light: { paper: '#f0eee6', card: '#faf9f5', ink: '#141413', 'ink-2': '#3d3d3a', 'ink-muted': '#66655f', line: '#cccbc8', 'line-soft': '#e3dacc', accent: '#a3481f', 'accent-fill': '#b4532a', 'on-accent': '#ffffff',
      edge: 'rgba(20,20,19,.16)', 'edge-strong': 'rgba(20,20,19,.4)', 'press-color': 'rgba(20,20,19,.1)', mark: '#f2cb4e', 'on-mark': '#141413', 'scrim-ink': '20,19,17', 'scrim-floor': '#141311' },
    dark: { paper: '#262624', card: '#30302e', ink: '#faf9f5', 'ink-2': '#c2c0b6', 'ink-muted': '#a3a199', line: '#4a4945', 'line-soft': '#3d3d3a', accent: '#f0a27f', 'accent-fill': '#d97757', 'on-accent': '#141413',
      edge: 'rgba(250,249,245,.16)', 'edge-strong': 'rgba(250,249,245,.4)', 'press-color': 'rgba(0,0,0,.35)', mark: '#f2cb4e', 'on-mark': '#141413', 'scrim-ink': '20,19,17', 'scrim-floor': '#141311' } }],
  type: [{ id: 'host', name: 'Host faces', tokens: { 'font-sans': '"Anthropic Sans",ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', 'font-display': '"Anthropic Serif",ui-serif,Georgia,Cambria,"Times New Roman",serif',
    'font-mono': 'ui-monospace,SFMono-Regular,Menlo,monospace', 'w-body': '400', 'w-strong': '600', 'w-loud': '500', 'w-ui': '500', 'track-title': '-.01em', 'track-heading': '-.005em', 'track-sub': '0', 'track-num': '-.02em', ...flat }, google: '' }],
  shape: { radius: '10px', 'radius-s': '6px', border: '1px', 'press-x': '0px', 'press-y': '1px', 'press-blur': '3px' }, effects: {}, motion: {} },

{ id: 'orchard', name: 'Orchard', blurb: 'Organic: serif faces, pastel grounds, soft corners and soft shadows, room to breathe.',
  palettes: [['sage', 'Sage', 145, 60], ['peach', 'Peach', 45, 150], ['butter', 'Butter', 95, 20]].map(([id, name, hue, mh]) => pal(id, name, { hue, chroma: .4, tint: 1, mark: [.9, .09, mh],
    ground: { light: { paper: [.95, .025, hue], card: [.985, .012, hue] } } }, { light: { 'press-color': 'rgba(60,50,30,.14)' }, dark: { 'press-color': 'rgba(0,0,0,.4)' } })),
  type: [{ id: 'fraunces', name: 'Fraunces + Inter', tokens: { 'font-sans': sans('Inter'), 'font-display': serif('Fraunces'), 'w-body': '400', 'w-strong': '600', 'w-loud': '600', 'w-ui': '500', 'track-title': '-.02em', 'lh-body': '1.6', ...flat }, google: G('Fraunces:opsz,wght@9..144,400..700', 'Inter:wght@400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'newsreader', name: 'Newsreader', tokens: { 'font-sans': serif('Newsreader'), 'font-display': serif('Newsreader'), 'w-body': '400', 'w-strong': '600', 'w-loud': '600', 'w-ui': '500', 'track-title': '-.015em', 'lh-body': '1.6', 't-3': '17px', ...flat }, google: G('Newsreader:opsz,wght@6..72,400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'source-serif', name: 'Source Serif', tokens: { 'font-sans': serif('Source Serif 4'), 'font-display': serif('Source Serif 4'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '600', 'track-title': '-.015em', 'lh-body': '1.6', 't-3': '17px', ...flat }, google: G('Source+Serif+4:opsz,wght@8..60,400..700', 'JetBrains+Mono:wght@400..700') }],
  shape: { radius: '14px', 'radius-s': '8px', border: '1px', 'press-x': '0px', 'press-y': '4px', 'press-blur': '14px' }, effects: {}, motion: {} },

{ id: 'night-drive', name: 'Night Drive', blurb: 'Synthwave: deep indigo, magenta and cyan, a glow on titles and on what can be pressed, a horizon behind the page. Dark only.',
  palettes: [['sunset', 'Sunset', 335, 200, 290], ['arcade', 'Arcade', 200, 335, 270], ['miami', 'Miami', 355, 175, 300]].map(([id, name, hue, mh, gh]) => pal(id, name, { hue, chroma: 1, tint: 1, inkHue: gh, inkC: .03, mark: [.85, .15, mh],
    ground: { dark: { paper: [.17, .06, gh], card: [.22, .075, gh] } } }, { dark: { 'press-color': `hsla(${hue},100%,60%,.55)`, 'text-glow': `0 0 .5em hsla(${hue},100%,65%,.6)`, edge: `hsla(${mh},90%,70%,.35)`, 'edge-strong': `hsla(${mh},90%,70%,.8)`,
      'page-bg': `linear-gradient(to bottom,transparent 55%,hsla(${hue},90%,45%,.22) 100%),var(--paper)` } }, 'dark')),
  type: [{ id: 'oxanium', name: 'Oxanium', tokens: { 'font-sans': sans('Oxanium'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'track-title': '.01em', 'track-heading': '.01em', 'track-sub': '0', ...flat }, google: G('Oxanium:wght@300..800', 'JetBrains+Mono:wght@400..700') },
    { id: 'grotesk', name: 'Space Grotesk', tokens: { 'font-sans': sans('Space Grotesk'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', ...flat }, google: G('Space+Grotesk:wght@400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'sora', name: 'Sora', tokens: { 'font-sans': sans('Sora'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', ...flat }, google: G('Sora:wght@300..800', 'JetBrains+Mono:wght@400..700') }],
  shape: { radius: '6px', 'radius-s': '3px', border: '1.5px', 'press-x': '0px', 'press-y': '0px', 'press-blur': '16px' }, effects: {}, motion: {} },

{ id: 'broadsheet', name: 'Broadsheet', blurb: 'A newspaper: serif headlines, hairlines, black on newsprint and one red. Square, flat, dense.',
  palettes: [pal('newsprint', 'Newsprint', { hue: 25, chroma: .85, tint: .1, inkC: .005, mark: [.92, .09, 98], ground: { light: { paper: [.965, .008, 90], card: [.985, .005, 90] } } }),
    pal('salmon', 'Salmon', { hue: 250, chroma: .6, tint: .1, inkC: .01, mark: [.97, .02, 60], ground: { light: { paper: [.91, .045, 50], card: [.94, .035, 50] } } }, {}, 'light'),
    pal('night-edition', 'Night edition', { hue: 25, chroma: .85, tint: .1, inkC: .005, mark: [.92, .09, 98] }, {}, 'dark')],
  type: [{ id: 'playfair', name: 'Playfair + Source Sans', tokens: { 'font-sans': sans('Source Sans 3'), 'font-display': serif('Playfair Display'), 'w-body': '400', 'w-strong': '600', 'w-loud': '800', 'w-ui': '600', 'track-title': '-.015em', ...flat }, google: G('Playfair+Display:wght@400..900', 'Source+Sans+3:wght@400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'bodoni', name: 'Bodoni Moda', tokens: { 'font-sans': sans('Source Sans 3'), 'font-display': serif('Bodoni Moda'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '600', 'track-title': '-.01em', ...flat }, google: G('Bodoni+Moda:opsz,wght@6..96,400..900', 'Source+Sans+3:wght@400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'roboto-serif', name: 'Roboto Serif + DM Sans', tokens: { 'font-sans': sans('DM Sans'), 'font-display': serif('Roboto Serif'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'track-title': '-.01em', ...flat }, google: G('Roboto+Serif:opsz,wght@8..144,400..800', 'DM+Sans:wght@400..700', 'JetBrains+Mono:wght@400..700') }],
  shape: { radius: '0px', 'radius-s': '0px', border: '1px', 'press-x': '2px', 'press-y': '2px', 'press-blur': '0px' }, effects: {}, motion: {} },

{ id: 'blueprint', name: 'Blueprint', blurb: 'A cyanotype: a blue ground, white line work, a drafting grid behind the page, mono labels.',
  palettes: [pal('cyanotype', 'Cyanotype', { hue: 205, chroma: .5, tint: .3, inkHue: 250, inkC: .01, mark: [.9, .13, 98], ground: { light: { paper: [.37, .13, 262], card: [.42, .13, 262] }, dark: { paper: [.24, .09, 262], card: [.29, .095, 262] } } },
      { both: null, light: { 'page-bg': 'linear-gradient(rgba(255,255,255,.08) 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px) 0 0/24px 24px,var(--paper)' },
        dark: { 'page-bg': 'linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px) 0 0/24px 24px,var(--paper)' } }),
    pal('drafting', 'Drafting white', { hue: 262, chroma: .8, tint: .15, mark: [.88, .14, 98] }, { light: { 'page-bg': 'linear-gradient(rgba(40,70,200,.08) 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,rgba(40,70,200,.08) 1px,transparent 1px) 0 0/24px 24px,var(--paper)' } }, 'light')],
  type: [{ id: 'plex', name: 'IBM Plex', tokens: { 'font-sans': sans('IBM Plex Sans'), 'w-body': '400', 'w-strong': '600', 'w-loud': '600', 'w-ui': '500', ...flat }, google: G('IBM+Plex+Sans:wdth,wght@75..100,400..700', 'JetBrains+Mono:wght@400..700') },
    { id: 'sometype', name: 'Sometype Mono titles', tokens: { 'font-sans': sans('Space Grotesk'), 'font-display': mono('Sometype Mono'), 'font-mono': mono('Sometype Mono'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'track-title': '-.03em', ...flat }, google: G('Space+Grotesk:wght@400..700', 'Sometype+Mono:wght@400..700') }],
  shape: { radius: '2px', 'radius-s': '1px', border: '1px' }, effects: {}, motion: {} },

{ id: 'index-card', name: 'Index Card', blurb: 'A card file: cream cards ruled in faint blue, a red accent like the margin line, monospaced faces like a typewriter.',
  palettes: [['manila', 'Manila', 25, 85, 'light'], ['mint', 'Mint', 25, 165, 'light'], ['graphite', 'Graphite', 25, 250, 'dark']].map(([id, name, hue, gh, only]) => pal(id, name, { hue, chroma: .85, tint: .4, inkHue: 260, inkC: .02, mark: [.88, .13, 98],
    ground: { light: { paper: [.92, .035, gh], card: [.975, .025, gh] } } },
    { light: { 'card-fill': 'repeating-linear-gradient(transparent 0 27px,rgba(70,110,200,.16) 27px 28px),var(--card)', 'press-color': 'rgba(60,45,20,.28)' }, dark: { 'card-fill': 'repeating-linear-gradient(transparent 0 27px,rgba(150,180,255,.1) 27px 28px),var(--card)', 'press-color': 'rgba(0,0,0,.5)' } }, only)),
  type: [{ id: 'sometype', name: 'Sometype Mono + Inter', tokens: { 'font-sans': sans('Inter'), 'font-display': mono('Sometype Mono'), 'font-mono': mono('Sometype Mono'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'track-title': '-.02em', ...flat }, google: G('Sometype+Mono:wght@400..700', 'Inter:wght@400..700') },
    { id: 'azeret', name: 'Azeret Mono + Inter', tokens: { 'font-sans': sans('Inter'), 'font-display': mono('Azeret Mono'), 'font-mono': mono('Azeret Mono'), 'w-body': '400', 'w-strong': '600', 'w-loud': '700', 'w-ui': '500', 'track-title': '0', ...flat }, google: G('Azeret+Mono:wght@400..800', 'Inter:wght@400..700') },
    { id: 'all-typewriter', name: 'All typewriter', tokens: { 'font-sans': mono('Red Hat Mono'), 'font-display': mono('Red Hat Mono'), 'font-mono': mono('Red Hat Mono'), 'w-body': '400', 'w-strong': '700', 'w-loud': '700', 'w-ui': '700', 'track-title': '-.02em', 'track-heading': '-.01em', ...flat }, google: G('Red+Hat+Mono:wght@400..700') }],
  shape: { radius: '3px', 'radius-s': '2px', border: '1px', 'press-x': '1px', 'press-y': '2px', 'press-blur': '0px' }, effects: {}, motion: {} },
];
for (const t of themes) fs.writeFileSync(new URL(`../themes/${t.id}.json`, import.meta.url), JSON.stringify(t, null, 1) + '\n');
console.log('wrote', themes.map(t => t.id).join(', '));
