// <icm-list> — the answer is a list, not a number.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmList extends IcmElement {
  static properties = {items: {type: Array}, variant: {}};  // variant: checks | dots | steps
  render() {
    const items = (this.items || []).slice(0, 7).map(x =>
      Array.isArray(x) ? {text: x[0], done: !!x[1]} : (typeof x === 'string' ? {text: x} : x));
    if (!items.length) return null;
    const v = ['dots', 'steps'].includes(this.variant) ? this.variant : 'checks';
    return html`<ul class="icm-list is-${v}">${items.map(i =>
      html`<li class=${i.done ? 'is-done' : ''}>${i.text}</li>`)}</ul>`;
  }
}
customElements.define('icm-list', IcmList);
