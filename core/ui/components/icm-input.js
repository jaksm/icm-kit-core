// <icm-input> — one short line of text. `inputmode` decimal, never type=number: in the
// Serbian locale a number input returns an EMPTY string for "39,7", so the value vanishes
// and nothing looks broken. That cost two debugging sessions on the calculators.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmInput extends IcmElement {
  static properties = {question: {}, placeholder: {}, mode: {}, value: {}};

  _type(e) {
    this.value = e.target.value;
    this.dispatchEvent(new CustomEvent('icm-answer', {bubbles: true, composed: true,
      detail: {value: this.value}}));
  }

  render() {
    return html`<div class="icm-input">
      ${this.question ? html`<div class="icm-input-q icm-question">${this.question}</div>` : null}
      <input class="icm-field" type="text" inputmode=${this.mode || 'text'} placeholder=${this.placeholder || ''}
             .value=${this.value || ''} @input=${this._type}>
    </div>`;
  }
}
customElements.define('icm-input', IcmInput);
