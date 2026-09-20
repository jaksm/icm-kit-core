// <icm-icon name="heart"> — one inline SVG from the icon set, sized by font-size.
import {html} from '../vendor/lit.js';
import {IcmElement} from './base.js';
import {UI} from '../icons/ui.js';

export class IcmIcon extends IcmElement {
  static properties = {name: {}, filled: {type: Boolean}};
  render() {
    const path = UI[this.name];
    if (!path) return null;
    return html`<svg class="icm-icon ${this.filled ? 'is-filled' : ''}" viewBox="0 0 24 24"
      aria-hidden="true">${path}</svg>`;
  }
}
customElements.define('icm-icon', IcmIcon);
