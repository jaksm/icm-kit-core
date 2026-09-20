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
/* Zap: the one loud control, a floating button in the bottom right corner of the screen. It lives on <body>, not in the panel: a
   panel that slides (translate) would become the containing block of a fixed child and carry the button away with it. */
.te-fab{position:fixed;right:max(var(--gutter),env(safe-area-inset-right,0px));bottom:calc(var(--gutter) + env(safe-area-inset-bottom,0px));z-index:40;display:inline-flex;align-items:center;gap:8px;
  min-height:56px;padding:0 22px 0 18px;border-radius:var(--radius-pill);border:var(--border) solid var(--edge-strong);background:var(--mark);color:var(--on-mark);cursor:pointer;
  font:var(--w-strong) var(--t-3)/1 var(--font-sans);box-shadow:var(--press-x) var(--press-y) var(--press-blur) var(--press-color);transition:translate .08s ease-out,box-shadow .08s ease-out}
.te-fab:active{translate:var(--press-x) var(--press-y);box-shadow:0 0 0 var(--press-color)}
.te-fab:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.te-fab svg{width:20px;height:20px;fill:currentColor}
.te-bit{position:fixed;z-index:41;width:9px;height:9px;pointer-events:none;will-change:transform,opacity}
/* Every discrete change is a view transition: the browser styles the page ONCE, takes two snapshots and the compositor animates
   between them, so the cost does not grow with the page. (A transition rule on every element cost 125 ms of style per change on a
   400-node page, 450 ms on a slow CPU: bench/.) A change inside a theme cross-fades, which for colors is what a tween looks like;
   a change of theme spreads like water from where the hand was: a soft-edged circle, fast out of the gate. */
::view-transition-group(root){animation-duration:.24s}
/* the wave: clip-path on the new snapshot. A basic-shape clip-path animation runs on the compositor (no paint per frame), which a
   mask driven by a custom property does not; the water feel comes from the curve (bursts out, glides to the edges) and from the old
   page sinking a little under it, not from a blurred edge. */
:root.te-wave::view-transition-old(root){animation:icm-te-sink .5s cubic-bezier(.2,.7,.2,1) both}
:root.te-wave::view-transition-new(root){animation:icm-te-wave .5s cubic-bezier(.12,.82,.26,1) both}
@keyframes icm-te-wave{from{clip-path:circle(0 at var(--te-x,50%) var(--te-y,50%))}to{clip-path:circle(150vmax at var(--te-x,50%) var(--te-y,50%))}}
@keyframes icm-te-sink{to{filter:brightness(.92)}}
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
    this.fab = document.createElement('button'); this.fab.className = 'te-fab'; this.fab.dataset.zap = ''; this.fab.setAttribute('aria-label', 'Randomize the theme');
    this.fab.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg>Randomize'; this.fab.onclick = e => this.zap(e); document.body.append(this.fab);
  }
  disconnectedCallback() { this.fab?.remove(); this._on = false }
  // confetti in the new theme's colors, thrown up and left from the button; transform and opacity only, so the compositor carries it
  burst() { if (matchMedia('(prefers-reduced-motion:reduce)').matches) return; const r = this.fab.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2, cs = ['--mark', '--accent-fill', '--ink', '--state-good', '--cat-5', '--cat-2'];
    for (let i = 0; i < 28; i++) { const b = document.createElement('i'); b.className = 'te-bit'; b.style.cssText = `left:${x}px;top:${y}px;background:var(${cs[i % cs.length]});border-radius:${i % 3 ? 0 : 50}%`;
      const a = Math.PI * (1.02 + Math.random() * .62), d = 120 + Math.random() * 260, dx = Math.cos(a) * d, dy = Math.sin(a) * d; document.body.append(b);
      b.animate([{ transform: 'translate(0,0) rotate(0)', opacity: 1 }, { transform: `translate(${dx}px,${dy}px) rotate(${Math.random() * 540 - 270}deg)`, opacity: 1, offset: .55 }, { transform: `translate(${dx * 1.15}px,${dy + 160}px) rotate(${Math.random() * 720 - 360}deg)`, opacity: 0 }],
        { duration: 900 + Math.random() * 500, easing: 'cubic-bezier(.15,.8,.3,1)' }).onfinish = () => b.remove() } }
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
  // resolves when the type set's families are usable, or after 700 ms, whichever is first
  fontsReady(google) { let ln = document.getElementById('icm-theme-fonts'); if (!ln) { ln = document.createElement('link'); ln.id = 'icm-theme-fonts'; ln.rel = 'stylesheet'; document.head.append(ln) }
    if (!google) { ln.removeAttribute('href'); return Promise.resolve() }
    const href = `https://fonts.googleapis.com/css2?${google}&display=swap`; if (ln.href === href) return Promise.resolve();
    const fams = google.split('&').map(f => decodeURIComponent(f.replace(/^family=/, '').split(':')[0]).replace(/\+/g, ' '));
    const css = new Promise(r => { ln.onload = ln.onerror = r; ln.href = href });
    return Promise.race([css.then(() => Promise.all(fams.map(f => document.fonts.load(`16px "${f}"`)))), new Promise(r => setTimeout(r, 700))]) }
  apply(ev) {
    const go = async () => { await this.fontsReady(this.tokens().google); const { light, dark } = this.tokens(), body = t => Object.entries(t).map(([k, v]) => `--${k}:${v};`).join('');
      let st = document.getElementById('icm-theme'); if (!st) { st = document.createElement('style'); st.id = 'icm-theme'; document.head.append(st) }
      st.textContent = `:root{${body(light)}}@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){${body(dark)}}}:root[data-theme="dark"]{${body(dark)}}`;
      this.state.scheme === 'auto' ? document.documentElement.removeAttribute('data-theme') : document.documentElement.dataset.theme = this.state.scheme;
      try { localStorage.setItem('icm-theme', JSON.stringify(this.state)) } catch {}
      this.dispatchEvent(new CustomEvent('icm-theme-change', { detail: this.choice(), bubbles: true })) };
    const calm = matchMedia('(prefers-reduced-motion:reduce)').matches, root = document.documentElement;
    if (!ev || !document.startViewTransition || calm) return go();
    const wave = !!(ev.target.closest && ev.target.closest('[data-theme],[data-zap]'));
    root.classList.toggle('te-wave', wave); root.style.setProperty('--te-x', ev.clientX + 'px'); root.style.setProperty('--te-y', ev.clientY + 'px');
    // a transition is skipped when the page is hidden or another one starts; the change itself still lands, so the rejection is not an error
    const vt = document.startViewTransition(go); vt.ready.catch(() => {}); vt.finished.catch(() => {}).finally(() => root.classList.remove('te-wave'));
  }
  // continuous input (the color pad, a slider): only the tokens that changed, written on :root once per frame. No stylesheet swap
  // (that invalidates the whole document), no storage, no event; apply() runs once when the hand lets go.
  live() { if (this._raf) return; this._raf = requestAnimationFrame(() => { this._raf = 0; const { light, dark } = this.tokens(), r = document.documentElement;
      const isDark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme:dark)').matches, t = isDark ? dark : light;
      this._live = this._live || {}; for (const k in t) if (this._live[k] !== t[k]) { r.style.setProperty('--' + k, t[k]); this._live[k] = t[k] } }) }
  settle() { const r = document.documentElement; for (const k in this._live || {}) r.style.removeProperty('--' + k); this._live = null; this.apply(); this.render() }
  choice() { const s = this.state, o = { theme: s.theme, palette: s.palette || this.theme.palettes[0].id, type: s.type || this.theme.type[0].id, overrides: {} };
    if (s.custom) { o.palette = 'custom'; o.custom = { id: 'custom', name: 'Custom', seeds: s.custom, ...palette(s.custom) } }
    if (s.radius != null) o.overrides.radius = s.radius + 'px'; if (s.size != null) o.overrides.size = s.size; return o }
  set(patch, ev) { Object.assign(this.state, patch); this.apply(ev); this.render() }
  zap(ev) { for (let k = 0; k < 40; k++) { const t = this.themes[Math.random() * this.themes.length | 0], p = t.palettes[Math.random() * t.palettes.length | 0], ty = t.type[Math.random() * t.type.length | 0];
      Object.assign(this.state, { theme: t.id, palette: p.id, type: ty.id, custom: null, radius: null, size: null });
      if (!this.failures('light').length && !this.failures('dark').length) break } this.apply(ev); this.render(); this.burst() }
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
        <button class="icm-option" data-code aria-pressed="${!!this._code}">Code</button></section>
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
      else if ('code' in d) { this._code = !this._code; this.render() }
      else if ('copy' in d) navigator.clipboard?.writeText('Use this icm-kit theme (write it to _config/theme.json, a custom palette to _config/themes/):\n' + JSON.stringify(this.choice(), null, 1)).then(() => { b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy for the agent', 1400) });
      else if ('save' in d) { this.dispatchEvent(new CustomEvent('icm-theme-save', { detail: this.choice(), bubbles: true })); b.textContent = 'Saved'; setTimeout(() => b.textContent = 'Save theme', 1400) } };
    this.oninput = e => { const k = e.target.dataset?.k; if (!k) return; const v = +e.target.value;
      if (k === 'tint') Object.assign(this.state, { custom: { ...(this.state.custom || { hue: 265, chroma: .7 }), tint: v } }); else this.state[k] = v;
      this.live() };
    this.onchange = e => { if (e.target.dataset?.k) this.settle() };   // the slider was let go
    const pad = this.querySelector('.te-pad'), move = e => { const r = pad.getBoundingClientRect(), x = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), y = Math.min(1, Math.max(0, (e.clientY - r.top) / r.height));
      this.state.custom = { tint: .25, ...(this.state.custom || {}), hue: Math.round(x * 360), chroma: +(1 - y).toFixed(2) }; this.live();
      const k = pad.firstElementChild; k.hidden = false; k.style.left = x * 100 + '%'; k.style.top = y * 100 + '%'; k.style.background = `hsl(${x * 360} ${(1 - y) * 100}% 50%)` };
    pad.onpointerdown = e => { pad.setPointerCapture(e.pointerId); move(e); pad.onpointermove = move };
    pad.onpointerup = pad.onpointercancel = () => { pad.onpointermove = null; this.settle() };
  }
}
customElements.get('icm-theme-editor') || customElements.define('icm-theme-editor', IcmThemeEditor);
