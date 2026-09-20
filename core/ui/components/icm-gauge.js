// <icm-gauge> — how far along you are, with a tick at the target.
import {html} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

export class IcmGauge extends IcmElement {
  static properties = {value: {type: Number}, target: {type: Number}, label: {}};
  render() {
    const v = Number(this.value), t = Number(this.target);
    if (!isFinite(v) || !v) return null;
    // the scale sits above both value and target, so neither ever touches the edge
    const scale = Math.max(v, isFinite(t) ? t : 0) * 1.06 || 1;
    return html`<div class="icm-gauge">
      <div class="icm-gauge-bar icm-bar" style="--v:${(v / scale * 100).toFixed(1)}%">
        <i></i>
        ${isFinite(t) && t ? html`<b style="left:${(t / scale * 100).toFixed(1)}%"></b>` : null}
      </div>
      ${this.label ? html`<div class="icm-gauge-label icm-caption">${this.label}</div>` : null}
    </div>`;
  }
}
customElements.define('icm-gauge', IcmGauge);
