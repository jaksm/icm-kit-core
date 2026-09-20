// <icm-metric> — the hero number a card is built around, with its unit and label.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmMetric extends IcmElement {
  static properties = {
    value: {},                          // the number, already formatted for reading
    unit: {},                           // L, €, RSD, days
    label: {},                          // what it measures; a metric without one is refused
    variant: {},                        // loud | quiet
    state: {},                          // good | warn | bad; colors the number when a
                                        // threshold decides how to read it
  };
  render() {
    if (this.value == null || this.value === '') return null;
    return html`
      <div class="icm-metric ${this.variant === 'quiet' ? 'is-quiet' : ''} ${
        ['good', 'warn', 'bad'].includes(this.state) ? 'is-' + this.state : ''}">
        <b class="icm-num">${this.value}${this.unit ? html`<small>${this.unit}</small>` : null}</b>
      </div>
      ${this.label ? html`<div class="icm-metric-label icm-caption">${this.label}</div>` : null}`;
  }
}
customElements.define('icm-metric', IcmMetric);
