// <icm-next> — the one next move, in the imperative. Never invented to give a card an ending.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';
import '../primitives/icm-icon.js';

export class IcmNext extends IcmElement {
  static properties = {text: {}};
  render() {
    return this.text ? html`<div class="icm-next"><icm-icon name="next"></icm-icon><span>${this.text}</span></div>` : null;
  }
}
customElements.define('icm-next', IcmNext);
