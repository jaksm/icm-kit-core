// <icm-confirm> — yes or no, and the answer stays visible so he sees where he got to.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';
import {LABELS} from '../primitives/labels.js';

export class IcmConfirm extends IcmElement {
  static properties = {question: {}, yes: {}, no: {}, value: {}};

  _pick(v) {
    this.value = v;
    this.dispatchEvent(new CustomEvent('icm-answer', {bubbles: true, composed: true,
      detail: {value: v}}));
  }

  render() {
    return html`<div class="icm-confirm">
      ${this.question ? html`<div class="icm-confirm-q">${this.question}</div>` : null}
      <div class="icm-confirm-row">
        <button type="button" class=${this.value === 'yes' ? 'is-on' : ''}
          @click=${() => this._pick('yes')}>${this.yes || LABELS.yes}</button>
        <button type="button" class=${this.value === 'no' ? 'is-on' : ''}
          @click=${() => this._pick('no')}>${this.no || LABELS.no}</button>
      </div>
    </div>`;
  }
}
customElements.define('icm-confirm', IcmConfirm);
