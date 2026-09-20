// <icm-theme-editor>: pick a theme, a palette, a type set, or make a palette from a color, and see the page change at once.
// One element for two places (the Theme editor artifact and the site). Vanilla custom element in the light DOM, styled with the
// same primitives it edits, so it is itself a live sample. It does not save anything: it fires `icm-theme-save` with the theme
// choice and the host page decides where that goes (an artifact's db, the clipboard, nothing).
// invariant: what it writes is the same three blocks build.py theme_css() writes, so a saved choice renders identically at build time.
// invariant: Save stays disabled while any text pair is under WCAG AA; Zap never lands on such a combination.
import { palette, contrast } from '../themes/palette.js';

const CSS = `
icm-theme-editor{display:block;color:var(--c-fg)}
.te{display:grid;gap:var(--s-5)}
.te-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:var(--s-2)}
.te-card{all:unset;box-sizing:border-box;cursor:pointer;display:grid;gap:6px;padding:8px;border:var(--border) solid var(--c-edge);border-radius:var(--radius-s);background:var(--c-fill)}
.te-card:focus-visible{outline:2px solid var(--c-fg);outline-offset:2px}
.te-card[aria-pressed=true]{border-color:var(--c-on-mark);background:var(--c-mark);color:var(--c-on-mark)}
.te-swatch{height:44px;border-radius:calc(var(--radius-s) - 1px);display:flex;align-items:end;gap:3px;padding:5px;border:1px solid rgba(128,128,128,.35)}
.te-swatch i{flex:1;height:10px;border-radius:2px}.te-swatch b{font:700 15px/1 var(--f);margin-right:auto;align-self:center}
.te-name{font-size:var(--t-1);line-height:1.2}
.te-aa{font-size:22px;line-height:1;height:30px;display:flex;align-items:center}
.te-pad{position:relative;height:150px;border-radius:var(--radius-s);border:var(--border) solid var(--c-edge-strong);touch-action:none;cursor:crosshair;
  background:linear-gradient(to top,#8a8a8a,transparent),linear-gradient(to right,#e5484d,#e5b800,#3fb950,#00b3c4,#4c6fff,#b04cff,#e5484d)}
.te-knob{position:absolute;width:22px;height:22px;margin:-11px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 0 1.5px #000;pointer-events:none}
.te-row{display:flex;flex-wrap:wrap;gap:var(--s-2);align-items:center}
.te-range{display:grid;grid-template-columns:7em 1fr;gap:var(--s-3);align-items:center;font-size:var(--t-2)}
.te-range input{width:100%;accent-color:var(--c-accent)}
.te-code{width:100%;min-height:160px;font:400 var(--t-1)/1.5 var(--font-mono);max-width:none}
.te-bad{color:var(--state-bad)}
/* inside a theme everything that can interpolate does, in plain CSS: colors, corners, shadows, and (variable fonts only) weight and width.
   A change of theme swaps font families, which cannot interpolate, so that one goes through the ripple instead. */
:root.icm-theming *,:root.icm-theming *::before,:root.icm-theming *::after{transition:background-color .45s var(--ease),color .45s var(--ease),border-color .45s var(--ease),border-radius .45s var(--ease),box-shadow .45s var(--ease),font-weight .45s var(--ease),font-stretch .45s var(--ease),letter-spacing .45s var(--ease),fill .45s var(--ease),stroke .45s var(--ease)!important}
::view-transition-old(root){animation:none}
::view-transition-new(root){animation:icm-te-ripple .55s cubic-bezier(.3,.7,.2,1) both}
@keyframes icm-te-ripple{from{clip-path:circle(0 at var(--te-x,50%) var(--te-y,50%))}to{clip-path:circle(150vmax at var(--te-x,50%) var(--te-y,50%))}}
`;
const PAIRS = [['ink', 7], ['ink-2', 4.5], ['ink-muted', 4.5], ['accent', 4.5]];
const isHex = v => /^#[0-9a-f]{6}$/i.test(v || '');
const pick = (items, id) => items.find(x => x.id === id) || items[0];

class IcmThemeEditor extends HTMLElement {
  connectedCallback() {
    if (this._on) return; this._on = true;
    if (!document.getElementById('icm-te-css')) document.head.insertAdjacentHTML('beforeend', `<style id="icm-te-css">${CSS}</style>`);
    this.themes = this.themes || globalThis.ICM_THEMES || [];
    this.base = this.base || globalThis.ICM_BASE || { light: {}, dark: {} };      // Ledger's colors, what an empty palette means
    let saved = {}; try { saved = JSON.parse(localStorage.getItem('icm-theme') || '{}') } catch {}
    this.state = { theme: 'ledger', palette: '', type: '', scheme: 'auto', custom: null, radius: null, size: null, ...(this.initial || saved) };
    this.classList.add('on-paper'); this.apply(); this.render();
  }
  get theme() { return pick(this.themes, this.state.theme) }
  // the choice as the three token maps theme_css() would write
  tokens() {
    const t = this.theme, s = this.state, ty = pick(t.type, s.type), pal = s.custom ? palette(s.custom) : pick(t.palettes, s.palette);
    const shared = { ...t.shape, ...t.effects, ...t.motion, ...ty.tokens };
    if (s.radius != null) { shared.radius = s.radius + 'px'; shared['radius-s'] = Math.round(s.radius / 2) + 'px' }
    if (s.size != null) [13, 14, 16, 18, 22, 28].forEach((px, i) => shared['t-' + (i + 1)] = Math.max(13, Math.round(px * s.size)) + 'px');
    const extra = k => s.custom ? Object.fromEntries(Object.entries(pick(t.palettes, s.palette)[k] || {}).filter(([n]) => /fill|page-bg|glow|press-color|edge/.test(n) && !/accent/.test(n))) : {};
    const light = pal.light || pal.dark, dark = pal.dark || pal.light;
    return { light: { ...shared, ...extra('light'), ...light }, dark: { ...shared, ...extra('dark'), ...dark }, google: ty.google };
  }
  // text pairs under AA, for the scheme given
  failures(k) { const t = { ...this.base[k], ...this.tokens()[k] }, bad = [];
    for (const g of ['paper', 'card']) for (const [fg, need] of PAIRS) if (isHex(t[fg]) && isHex(t[g]) && contrast(t[fg], t[g]) < need) bad.push(`${fg} on ${g} ${contrast(t[fg], t[g]).toFixed(1)}`);
    if (isHex(t['on-mark']) && isHex(t.mark) && contrast(t['on-mark'], t.mark) < 4.5) bad.push('on-mark on mark');
    if (isHex(t['on-accent']) && isHex(t['accent-fill']) && contrast(t['on-accent'], t['accent-fill']) < 4.5) bad.push('on-accent on accent-fill');
    return bad }
  apply(ev) {
    const go = () => { const { light, dark, google } = this.tokens(), body = t => Object.entries(t).map(([k, v]) => `--${k}:${v};`).join('');
      let st = document.getElementById('icm-theme'); if (!st) { st = document.createElement('style'); st.id = 'icm-theme'; document.head.append(st) }
      st.textContent = `:root{${body(light)}}@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){${body(dark)}}}:root[data-theme="dark"]{${body(dark)}}`;
      let ln = document.getElementById('icm-theme-fonts'); if (!ln) { ln = document.createElement('link'); ln.id = 'icm-theme-fonts'; ln.rel = 'stylesheet'; document.head.append(ln) }
      if (google) ln.href = `https://fonts.googleapis.com/css2?${google}&display=swap`; else ln.removeAttribute('href');
      this.state.scheme === 'auto' ? document.documentElement.removeAttribute('data-theme') : document.documentElement.dataset.theme = this.state.scheme;
      try { localStorage.setItem('icm-theme', JSON.stringify(this.state)) } catch {}
      this.dispatchEvent(new CustomEvent('icm-theme-change', { detail: this.choice(), bubbles: true })) };
    // a flat ripple from where the hand was; still when the platform or the person says so
    const calm = matchMedia('(prefers-reduced-motion:reduce)').matches;
    const swap = ev && ev.target.closest && ev.target.closest('[data-theme],[data-zap]');   // only a whole-theme change ripples
    if (!swap && !calm) { const c = document.documentElement.classList; c.add('icm-theming'); clearTimeout(this._tw); this._tw = setTimeout(() => c.remove('icm-theming'), 650) }
    if (swap && document.startViewTransition && !calm) { const r = document.documentElement.style; r.setProperty('--te-x', ev.clientX + 'px'); r.setProperty('--te-y', ev.clientY + 'px'); document.startViewTransition(go) } else go();
  }
  choice() { const s = this.state, o = { theme: s.theme, palette: s.palette || this.theme.palettes[0].id, type: s.type || this.theme.type[0].id, overrides: {} };
    if (s.custom) { o.palette = 'custom'; o.custom = { id: 'custom', name: 'Custom', seeds: s.custom, ...palette(s.custom) } }
    if (s.radius != null) o.overrides.radius = s.radius + 'px'; if (s.size != null) o.overrides.size = s.size; return o }
  set(patch, ev) { Object.assign(this.state, patch); this.apply(ev); this.render() }
  zap(ev) { for (let k = 0; k < 40; k++) { const t = this.themes[Math.random() * this.themes.length | 0], p = t.palettes[Math.random() * t.palettes.length | 0], ty = t.type[Math.random() * t.type.length | 0];
      Object.assign(this.state, { theme: t.id, palette: p.id, type: ty.id, custom: null, radius: null, size: null });
      if (!this.failures('light').length && !this.failures('dark').length) break } this.apply(ev); this.render() }
  render() {
    const s = this.state, t = this.theme, sw = (p, k = 'light') => { const c = { ...this.base[k], ...(p[k] || p.dark || p.light) }; return `<span class="te-swatch" style="background:${c.paper};color:${c.ink}"><b>Aa</b><i style="background:${c['accent-fill']}"></i><i style="background:${c.mark}"></i><i style="background:${c.card};outline:1px solid rgba(128,128,128,.4)"></i></span>` };
    const bad = [...this.failures('light').map(x => 'light: ' + x), ...this.failures('dark').map(x => 'dark: ' + x)];
    const c = s.custom || { hue: 265, chroma: .7, tint: .25 };
    this.innerHTML = `<div class="te icm-stack">
      <section class="icm-stack is-tight"><h3 class="icm-subheading">Theme</h3><div class="te-grid">${this.themes.map(x => `<button class="te-card" data-theme="${x.id}" aria-pressed="${x.id === t.id}" title="${x.blurb}">${sw(x.palettes[0], x.palettes[0].light ? 'light' : 'dark')}<span class="te-name">${x.name}</span></button>`).join('')}</div>
        <p class="icm-caption">${t.blurb}</p></section>
      <section class="icm-stack is-tight"><h3 class="icm-subheading">Palette</h3><div class="te-grid">${t.palettes.map(p => `<button class="te-card" data-palette="${p.id}" aria-pressed="${!s.custom && p.id === pick(t.palettes, s.palette).id}">${sw(p, p.light ? 'light' : 'dark')}<span class="te-name">${p.name}</span></button>`).join('')}</div>
        <div class="te-pad" role="application" aria-label="Make a palette: across is hue, down is less color"><span class="te-knob" style="left:${c.hue / 3.6}%;top:${(1 - c.chroma) * 100}%;background:hsl(${c.hue} ${c.chroma * 100}% 50%)" ${s.custom ? '' : 'hidden'}></span></div>
        <label class="te-range">Paper tint<input type="range" min="0" max="1" step=".05" value="${c.tint}" data-k="tint"></label></section>
      <section class="icm-stack is-tight"><h3 class="icm-subheading">Type</h3><div class="te-grid">${t.type.map(y => `<button class="te-card" data-type="${y.id}" aria-pressed="${y.id === pick(t.type, s.type).id}"><span class="te-aa" style="font-family:${(y.tokens['font-display'] || y.tokens['font-sans'] || 'inherit').replace(/"/g, "'")};font-weight:${y.tokens['w-loud'] || 800}">Aa</span><span class="te-name">${y.name}</span></button>`).join('')}</div>
        <label class="te-range">Size<input type="range" min=".9" max="1.25" step=".05" value="${s.size ?? 1}" data-k="size"></label>
        <label class="te-range">Corners<input type="range" min="0" max="24" step="1" value="${s.radius ?? parseInt(t.shape.radius ?? 8)}" data-k="radius"></label></section>
      <section class="te-row" role="group" aria-label="Light or dark">${['auto', 'light', 'dark'].map(k => `<button class="icm-option" data-scheme="${k}" aria-pressed="${s.scheme === k}">${k[0].toUpperCase() + k.slice(1)}</button>`).join('')}
        <button class="icm-option" data-zap>Zap</button><button class="icm-option" data-code aria-pressed="${!!this._code}">Code</button></section>
      ${this._code ? `<textarea class="icm-field te-code" readonly aria-label="The theme as JSON">${JSON.stringify(this.choice(), null, 1).replace(/[<]/g, '&lt;')   /* not /</: inlined into a <script>, build.py escapes every </ and would break the regex */}</textarea>` : ''}
      <section class="icm-stack is-tight">${bad.length ? `<p class="icm-caption te-bad">Not saved: contrast under AA. ${bad.slice(0, 3).join('; ')}</p>` : `<p class="icm-caption">Contrast passes AA in light and dark.</p>`}
        <div class="te-row"><button class="icm-option" data-copy>Copy for the agent</button><button class="icm-option" data-save ${bad.length ? 'disabled' : ''}>Save theme</button></div></section></div>`;
    this.wire();
  }
  wire() {
    this.onclick = e => { const b = e.target.closest('button'); if (!b) return; const d = b.dataset;
      if (d.theme) this.set({ theme: d.theme, palette: '', type: '', custom: null, radius: null }, e);
      else if (d.palette) this.set({ palette: d.palette, custom: null }, e);
      else if (d.type) this.set({ type: d.type }, e);
      else if (d.scheme) this.set({ scheme: d.scheme }, e);
      else if ('zap' in d) this.zap(e);
      else if ('code' in d) { this._code = !this._code; this.render() }
      else if ('copy' in d) navigator.clipboard?.writeText('Use this icm-kit theme (write it to _config/theme.json, a custom palette to _config/themes/):\n' + JSON.stringify(this.choice(), null, 1)).then(() => { b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy for the agent', 1400) });
      else if ('save' in d) { this.dispatchEvent(new CustomEvent('icm-theme-save', { detail: this.choice(), bubbles: true })); b.textContent = 'Saved'; setTimeout(() => b.textContent = 'Save theme', 1400) } };
    this.oninput = e => { const k = e.target.dataset?.k; if (!k) return; const v = +e.target.value;
      if (k === 'tint') Object.assign(this.state, { custom: { ...(this.state.custom || { hue: 265, chroma: .7 }), tint: v } }); else this.state[k] = v;
      this.apply(); clearTimeout(this._t); this._t = setTimeout(() => this.render(), 250) };   // sliders apply at once, the panel redraws when the hand rests
    const pad = this.querySelector('.te-pad'), move = e => { const r = pad.getBoundingClientRect(), x = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), y = Math.min(1, Math.max(0, (e.clientY - r.top) / r.height));
      this.state.custom = { tint: .25, ...(this.state.custom || {}), hue: Math.round(x * 360), chroma: +(1 - y).toFixed(2) }; this.apply();
      const k = pad.firstElementChild; k.hidden = false; k.style.left = x * 100 + '%'; k.style.top = y * 100 + '%'; k.style.background = `hsl(${x * 360} ${(1 - y) * 100}% 50%)` };
    pad.onpointerdown = e => { pad.setPointerCapture(e.pointerId); move(e); pad.onpointermove = move };
    pad.onpointerup = pad.onpointercancel = () => { pad.onpointermove = null; this.render() };
  }
}
customElements.get('icm-theme-editor') || customElements.define('icm-theme-editor', IcmThemeEditor);
