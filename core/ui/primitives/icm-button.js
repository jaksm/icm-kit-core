// <icm-button> — the plain button of the system: quiet by default, pill when `variant="pill"`.
import {html} from '../vendor/lit.js';
import {IcmElement} from './base.js';
import './icm-icon.js';

export class IcmButton extends IcmElement {
  static properties = {label: {}, icon: {}, variant: {}, pressed: {type: Boolean},
                       disabled: {type: Boolean}};
  render() {
    return html`<button class="icm-button is-${this.variant || 'quiet'}" type="button"
      aria-pressed=${this.pressed == null ? undefined : String(!!this.pressed)}
      ?disabled=${this.disabled}
      @click=${() => this.dispatchEvent(new CustomEvent('icm-press', {bubbles: true}))}>
      ${this.icon ? html`<icm-icon name=${this.icon} ?filled=${this.pressed}></icm-icon>` : null}
      ${this.label ? html`<span>${this.label}</span>` : null}
    </button>`;
  }
}
customElements.define('icm-button', IcmButton);
