// <icm-delta> — how far a number sits from something else; a number nobody compares says little.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmDelta extends IcmElement {
  static properties = {value: {}, good: {}, direction: {}, label: {}};   // direction: up | down
  render() {
    if (this.value == null || this.value === '') return null;
    const up = this.direction !== 'down';
    const good = (this.good === 'up') === up;          // `good` names the direction that is good news; down by default
    return html`<div class="icm-delta ${up ? 'is-up' : 'is-down'} ${good ? 'is-good' : 'is-bad'}">
      <i>${up ? '▲' : '▼'}</i>${this.value}${this.label ? html` ${this.label}` : null}</div>`;
  }
}
customElements.define('icm-delta', IcmDelta);
