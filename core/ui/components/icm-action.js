// <icm-action> — one thing a card can DO: open something, or call a connector.
// The element owns the whole lifecycle and the error copy; the page only performs the work.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';
import {PROVIDERS, PROVIDER_OF} from '../icons/providers.js';
import {LABELS} from '../primitives/labels.js';
import '../primitives/icm-icon.js';

// invariant: one fix per error code, never one banner for all of them. The mcp contract
// calls the catch-all banner the named anti-pattern: it hides the single thing that would
// make the page work again (reconnect, add the connector, or simply wait). Copy: LABELS.fixes.

export class IcmAction extends IcmElement {
  static properties = {
    label: {},                 // what it says while idle
    done: {},                  // what it says once it worked
    icon: {},                  // ui icon name
    server: {},                // connector display name; draws its mark
    href: {},                  // set for link actions; makes this an <a>, not a <button>
    sameTab: {type: Boolean},  // tel:, sms:, mailto: navigate instead of opening a tab
    confirm: {type: Boolean},  // changes something outside: confirmed by holding (keyboard: asks once more)
    state: {},                 // idle | asking | running | done | error
    error: {},                 // mcp error code
  };

  // invariant: an action that changes something outside is confirmed by HOLDING, not by a second tap that looks like
  // a warning: the fill runs left to right while the finger is down, letting go early drains it, and nothing about
  // it is red. The two-tap `asking` state stays as the path for the keyboard and for reduced motion, where a timed
  // hold is either unreachable or would have to jump.
  static HOLD = 800;
  _still() { return matchMedia('(prefers-reduced-motion: reduce)').matches; }

  _down(e) {
    const s = this.state || 'idle';
    if (!this.confirm || this._still() || s === 'running' || s === 'done' || (e.button ?? 0) !== 0) return;
    // invariant: the button never changes size under the finger: the label swaps (hold, working, done) keep the idle width as a floor
    e.currentTarget.style.minWidth = e.currentTarget.offsetWidth + 'px';
    this.holding = true; this.hinted = false; this.requestUpdate();
    this._t = setTimeout(() => { this.holding = false; this._run(); }, IcmAction.HOLD);
  }
  _up() {
    if (!this.holding) return;
    clearTimeout(this._t); this.holding = false; this.hinted = true; this.requestUpdate();   // let go early: say what it wants
  }
  _run() {
    this.state = 'running';
    this.dispatchEvent(new CustomEvent('icm-action', {bubbles: true, composed: true}));
  }
  _press(e) {
    const s = this.state || 'idle';
    if (s === 'running' || s === 'done') return;
    if (this.confirm) {
      if (e.detail !== 0 && !this._still()) return;          // a pointer confirms by holding; _down/_up own it
      if (s !== 'asking') { this.state = 'asking'; return; }
    }
    this._run();
  }
  updated(changed) {
    if (changed.has('state') && this.state === 'done' && changed.get('state') === 'running' && !this._still()) this._burst();
  }
  // Success is rare and earned, so it may celebrate: a dozen paper squares thrown from the button, once, gone in under a second.
  _burst() {
    const wrap = this.querySelector('.icm-action-wrap'); if (!wrap) return;
    const box = document.createElement('span'); box.className = 'icm-burst'; box.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < 14; i++) {
      const a = -Math.PI / 2 + (i / 13 - .5) * 2.6 + (Math.random() - .5) * .3, d = 34 + Math.random() * 46, p = document.createElement('i');
      p.style.cssText = `--dx:${Math.cos(a) * d}px;--dy:${Math.sin(a) * d}px;--r:${(Math.random() - .5) * 540}deg;--c:var(--burst-${i % 3});left:${20 + Math.random() * 60}%`;
      box.append(p);
    }
    wrap.append(box); setTimeout(() => box.remove(), 1000);
  }

  _mark() {
    const m = PROVIDERS[PROVIDER_OF[this.server] || (this.server ? 'local' : '')];
    return m ? html`<svg class="icm-action-mark" viewBox="0 0 24 24" aria-hidden="true">${m}</svg>`
      : this.icon ? html`<icm-icon name=${this.icon}></icm-icon>` : null;
  }

  render() {
    // invariant: a link action is a REAL anchor. window.open is blocked in the artifact's
    // sandboxed frame and fails without throwing, so a scripted "open" silently does nothing.
    if (this.href) {
      const out = /^https?:/i.test(this.href) && !this.sameTab;
      return html`<span class="icm-action-wrap"><a class="icm-action is-link" href=${this.href}
        target=${out ? '_blank' : '_self'} rel="noopener"
        @click=${() => this.dispatchEvent(new CustomEvent('icm-action',
          {bubbles: true, composed: true, detail: {link: true}}))}
        >${this._mark()}<span>${this.label}</span></a></span>`;
    }
    const s = this.state || 'idle';
    const text = s === 'asking' ? LABELS.asking
      : s === 'idle' && this.hinted && !this.holding ? LABELS.hold
      : s === 'running' ? LABELS.running
      : s === 'done' ? (this.done || LABELS.done)
      : this.label;
    return html`
      <span class="icm-action-wrap"><button class="icm-action is-${s} ${this.holding ? 'is-holding' : ''}" type="button"
              style="--hold:${IcmAction.HOLD}ms" ?disabled=${s === 'running' || s === 'done'}
              @pointerdown=${this._down} @pointerup=${this._up} @pointerleave=${this._up} @pointercancel=${this._up}
              @click=${this._press}>${this._mark()}<span>${text}</span></button></span>
      ${s === 'error' ? html`<div class="icm-action-error">${
        LABELS.fixes[this.error] || LABELS.failed}</div>` : null}`;
  }
}
customElements.define('icm-action', IcmAction);
