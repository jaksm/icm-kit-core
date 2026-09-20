// <icm-quote> — the exact wording, when the wording is what carries the decision.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmQuote extends IcmElement {
  static properties = {text: {}, from: {}};
  render() {
    if (!this.text) return null;
    return html`<blockquote class="icm-quote"><p>${this.text}</p>
      ${this.from ? html`<cite>${this.from}</cite>` : null}</blockquote>`;
  }
}
customElements.define('icm-quote', IcmQuote);
