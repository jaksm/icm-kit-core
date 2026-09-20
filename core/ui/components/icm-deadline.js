// <icm-deadline> — the date after which it is late; counts the days from TODAY, so a card
// does not go stale the moment it is published.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';
import {LABELS, countDays} from '../primitives/labels.js';

export class IcmDeadline extends IcmElement {
  static properties = {date: {}, label: {}};   // date: ISO; label: what expires
  render() {
    if (!this.date) return null;
    const d = new Date(this.date + 'T12:00:00');
    if (isNaN(d)) return null;          // a malformed date renders nothing, never "NaN days"
    const days = Math.round((d - new Date()) / 864e5);
    const state = days <= 0 ? 'is-now' : days <= 3 ? 'is-near' : '';
    const when = days < 0 ? countDays(-days, LABELS.dueAgo)
      : days === 0 ? LABELS.today
      : countDays(days, LABELS.dueIn);
    return html`<div class="icm-deadline ${state}"><b>${when}</b>${
      this.label ? html`<span>${this.label}</span>` : null}</div>`;
  }
}
customElements.define('icm-deadline', IcmDeadline);
