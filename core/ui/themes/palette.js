// Palette generator: one or two seed colors in, a full set of color tokens out, light and dark, already at WCAG AA.
// The ONLY implementation: the theme editor imports it, tools/make-palette.mjs wraps it for the agent. Python never repeats it;
// build.py only checks the explicit values that come out. invariant: every text pair it returns passes the same thresholds
// as build.py check_contrast (4.5 text, 7 ink on paper, 3 fills), because fit() walks lightness until it does.
const lin = c => c <= .0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - .055;
export function oklch(L, C, h) {                         // -> "#rrggbb", chroma reduced until it fits sRGB
  for (let c = C; c >= 0; c -= .004) {
    const a = c * Math.cos(h * Math.PI / 180), b = c * Math.sin(h * Math.PI / 180);
    const l = (L + .3963377774 * a + .2158037573 * b) ** 3, m = (L - .1055613458 * a - .0638541728 * b) ** 3, s = (L - .0894841775 * a - 1.291485548 * b) ** 3;
    const rgb = [4.0767416621 * l - 3.3077115913 * m + .2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - .3413193965 * s, -.0041960863 * l - .7034186147 * m + 1.707614701 * s].map(lin);
    if (rgb.every(v => v >= -.0005 && v <= 1.0005)) return '#' + rgb.map(v => Math.round(Math.min(1, Math.max(0, v)) * 255).toString(16).padStart(2, '0')).join('');
  }
  return L > .5 ? '#ffffff' : '#000000';
}
const lum = hex => { const f = c => c <= .03928 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4; const [r, g, b] = [1, 3, 5].map(i => f(parseInt(hex.slice(i, i + 2), 16) / 255)); return .2126 * r + .7152 * g + .0722 * b };
export const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + .05) / (y + .05) };
// walk lightness away from the ground until the pair reaches `need`
function fit(L, C, h, ground, need, dir) { let l = L; for (let k = 0; k < 60 && contrast(oklch(l, C, h), ground) < need; k++) l = Math.min(1, Math.max(0, l + dir * .012)); return oklch(l, C, h) }
const alpha = (hex, a) => `rgba(${[1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)).join(',')},${a})`;

// hue 0..360 and chroma 0..1 for the accent; tint 0..1 = how much of the hue the paper takes; markHue = the highlighter (default: opposite-ish warm)
// ground: optional {light:{paper:[L,C,h],card:[L,C,h]},dark:{…}} for a theme whose page is not near-white or near-black (a blue
// blueprint, a green phosphor); mark: [L,C,h]; inkHue: the hue text leans to. Everything else is still fitted to AA on that ground.
export function palette({ hue = 265, chroma = .7, tint = .25, markHue = (hue + 190) % 360, ground = {}, mark: markLCH, inkHue = hue, inkC } = {}) {
  const C = .04 + chroma * .2, T = tint * .03;
  const side = dark => {
    const g = ground[dark ? 'dark' : 'light'] || {};
    const paper = g.paper ? oklch(...g.paper) : oklch(dark ? .19 : .955, T, hue), card = g.card ? oklch(...g.card) : oklch(dark ? .24 : .99, T * .6, hue);
    const isDark = lum(paper) < .25, dir = isDark ? 1 : -1;            // a "light" scheme may still have a dark ground (blueprint)
    const worst = contrast(paper, isDark ? '#ffffff' : '#000000') < contrast(card, isDark ? '#ffffff' : '#000000') ? paper : card;
    const iC = inkC ?? T * 1.5, ink = fit(isDark ? .93 : .24, iC, inkHue, worst, 7.5, dir);
    const mark = markLCH ? oklch(...markLCH) : oklch(dark ? .82 : .85, .15, markHue);
    const accentFill = fit(isDark ? .6 : .48, C, hue, worst, 3.2, dir);
    const out = {
      paper, card, ink, 'ink-2': fit(isDark ? .8 : .4, iC, inkHue, worst, 6, dir), 'ink-muted': fit(isDark ? .68 : .5, iC * .8, inkHue, worst, 4.6, dir),
      line: alpha(ink, .22), 'line-soft': alpha(ink, .12),
      accent: fit(isDark ? .74 : .45, C, hue, worst, 4.6, dir), 'accent-fill': accentFill,
      'on-accent': contrast('#ffffff', accentFill) >= 4.5 ? '#ffffff' : fit(.2, .02, hue, accentFill, 4.6, -1),
      edge: alpha(ink, isDark ? .26 : .24), 'edge-strong': isDark ? alpha(ink, .7) : ink, 'press-color': isDark ? alpha(ink, .7) : ink,
      mark, 'on-mark': lum(mark) > .3 ? fit(.25, .03, markHue, mark, 4.6, -1) : fit(.9, .02, markHue, mark, 4.6, 1),
    };
    // states and the twelve category colors are fitted on the same ground, so a theme never inherits Ledger's and fails on its own paper
    for (const [k, h] of [['good', 150], ['warn', 75], ['bad', 25]]) out['state-' + k] = fit(isDark ? .78 : .5, .15, h, worst, 4.6, dir);
    for (let i = 0; i < 12; i++) out['cat-' + (i + 1)] = fit(isDark ? .72 : .58, i < 8 ? .14 : .05, (hue + 35 + i * 47) % 360, worst, 3.2, dir);
    return out;
  };
  return { light: side(false), dark: side(true) };
}
