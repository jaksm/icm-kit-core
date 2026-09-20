// <icm-link> — a pill that leads out of the page: a listing, an unsubscribe, ANOTHER ARTIFACT.
import {html} from '../vendor/lit.js';
import {IcmElement} from './base.js';
import './icm-icon.js';

export class IcmLink extends IcmElement {
  static properties = {href: {}, label: {}};
  render() {
    if (!this.href) return null;
    return html`<a class="icm-link" href=${this.href} target="_blank" rel="noopener"
      >${this.label || 'Otvori'}<icm-icon name="external"></icm-icon></a>`;
  }
}
customElements.define('icm-link', IcmLink);
