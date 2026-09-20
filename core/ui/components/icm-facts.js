// <icm-facts> — facts in pairs, for when the answer is a set that gets compared.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

const LONG = 34;   // a value past this is a sentence, not a number, so it gets its own row

export class IcmFacts extends IcmElement {
  static properties = {rows: {type: Array}};   // [[label, value], ...]
  render() {
    const rows = (this.rows || []).filter(r => r && r.length);
    if (!rows.length) return null;
    return html`<dl class="icm-facts">${rows.map(([k, v]) => html`
      <div class="icm-facts-row ${String(v).length > LONG ? 'is-long' : ''}">
        <dt>${k}</dt><dd>${v}</dd>
      </div>`)}</dl>`;
  }
}
customElements.define('icm-facts', IcmFacts);
