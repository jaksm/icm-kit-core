// <icm-choice> — the feed asks, one tap answers. Buttons in a row, never a <select>:
// a select hides the options behind a tap and costs one more gesture on a phone.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmChoice extends IcmElement {
  static properties = {
    question: {},
    options: {type: Array},      // ["da", "ne"] or [{value, label}]
    multi: {type: Boolean},
    value: {type: Array},        // chosen values
  };

  _pick(v) {
    const now = this.value || [];
    this.value = this.multi
      ? (now.includes(v) ? now.filter(x => x !== v) : [...now, v])
      : [v];
    this.dispatchEvent(new CustomEvent('icm-answer', {bubbles: true, composed: true,
      detail: {value: this.multi ? this.value : this.value[0]}}));
  }

  render() {
    const opts = (this.options || []).map(o => typeof o === 'string' ? {value: o, label: o} : o);
    if (!opts.length) return null;
    const chosen = this.value || [];
    return html`<div class="icm-choice">
      ${this.question ? html`<div class="icm-choice-q">${this.question}</div>` : null}
      <div class="icm-choice-row">${opts.map(o => html`
        <button type="button" class=${chosen.includes(o.value) ? 'is-on' : ''}
          aria-pressed=${String(chosen.includes(o.value))}
          @click=${() => this._pick(o.value)}>${o.label}</button>`)}
      </div>
    </div>`;
  }
}
customElements.define('icm-choice', IcmChoice);
