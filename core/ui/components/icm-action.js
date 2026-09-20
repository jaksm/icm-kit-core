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
    confirm: {type: Boolean},  // destructive: asks once more before it runs
    state: {},                 // idle | asking | running | done | error
    error: {},                 // mcp error code
  };

  _press() {
    const s = this.state || 'idle';
    if (s === 'running' || s === 'done') return;
    if (this.confirm && s !== 'asking') { this.state = 'asking'; return; }
    this.state = 'running';
    this.dispatchEvent(new CustomEvent('icm-action', {bubbles: true, composed: true}));
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
      return html`<a class="icm-action is-link" href=${this.href}
        target=${out ? '_blank' : '_self'} rel="noopener"
        @click=${() => this.dispatchEvent(new CustomEvent('icm-action',
          {bubbles: true, composed: true, detail: {link: true}}))}
        >${this._mark()}<span>${this.label}</span></a>`;
    }
    const s = this.state || 'idle';
    const text = s === 'asking' ? LABELS.asking
      : s === 'running' ? LABELS.running
      : s === 'done' ? (this.done || LABELS.done)
      : this.label;
    return html`
      <button class="icm-action is-${s}" type="button" ?disabled=${s === 'running' || s === 'done'}
              @click=${this._press}>${this._mark()}<span>${text}</span></button>
      ${s === 'error' ? html`<div class="icm-action-error">${
        LABELS.fixes[this.error] || LABELS.failed}</div>` : null}`;
  }
}
customElements.define('icm-action', IcmAction);
