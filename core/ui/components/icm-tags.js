// <icm-tags> — state pills. Only for state that changes what he does, never decoration.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

const KINDS = ['neutral', 'good', 'warn', 'bad'];

export class IcmTags extends IcmElement {
  static properties = {items: {type: Array}};   // [{text, kind}]
  render() {
    const items = (this.items || []).slice(0, 3);
    if (!items.length) return null;
    return html`<div class="icm-tags">${items.map(t => html`
      <span class="icm-badge is-${KINDS.includes(t.kind) ? t.kind : 'neutral'}">${t.text}</span>`)}</div>`;
  }
}
customElements.define('icm-tags', IcmTags);
