// <icm-slider> — a number in a range, with the value alive above the track.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmSlider extends IcmElement {
  static properties = {question: {}, min: {type: Number}, max: {type: Number},
                       step: {type: Number}, unit: {}, value: {type: Number}};

  _move(e) {
    this.value = Number(e.target.value);
    this.dispatchEvent(new CustomEvent('icm-answer', {bubbles: true, composed: true,
      detail: {value: this.value}}));
  }

  render() {
    const min = this.min ?? 0, max = this.max ?? 100;
    const v = this.value ?? Math.round((min + max) / 2);
    return html`<div class="icm-slider">
      ${this.question ? html`<div class="icm-slider-q">${this.question}</div>` : null}
      <div class="icm-slider-v">${v}${this.unit ? html`<small>${this.unit}</small>` : null}</div>
      <input type="range" min=${min} max=${max} step=${this.step ?? 1} .value=${String(v)}
             @input=${this._move}>
    </div>`;
  }
}
customElements.define('icm-slider', IcmSlider);
