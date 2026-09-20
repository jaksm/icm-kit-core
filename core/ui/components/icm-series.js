// <icm-series> — the shape over time that the latest number does not show.
import {html, svg} from '../vendor/lit.js';
import {IcmElement} from '../primitives/base.js';

const W = 210, H = 34, PAD = 3;

export class IcmSeries extends IcmElement {
  static properties = {values: {type: Array}, label: {}, variant: {}};  // variant: line | bars
  render() {
    const v = (this.values || []).map(Number).filter(isFinite).slice(0, 24);
    // invariant: refuse fewer than two values. A line through one point pretends to show a
    // trend, and a single bar is a number that already has a better component.
    if (v.length < 2) return null;
    const hi = Math.max(...v, 1), lo = Math.min(...v, 0), last = v.length - 1;
    const x = i => PAD + i * (W - 2 * PAD) / Math.max(last, 1);
    const y = t => H - PAD - (t - lo) * (H - 2 * PAD) / (hi - lo || 1);
    let shape;
    if (this.variant === 'bars') {
      // bars compare separate periods; a line is for when the shape of the flow matters
      const w = (W - 2 * PAD) / v.length * 0.62;
      shape = v.map((t, i) => svg`<rect x=${x(i) - w / 2} y=${y(t)} width=${w}
        height=${Math.max(1, H - PAD - y(t))}
        class=${i === last ? 'is-last' : ''}/>`);
    } else {
      const d = v.map((t, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(t).toFixed(1)).join(' ');
      shape = [svg`<path d=${d} fill="none" stroke-width="1.5" stroke-linejoin="round"/>`,
               svg`<circle cx=${x(last)} cy=${y(v[last])} r="2.8" class="is-last"/>`];
    }
    return html`<div class="icm-series">
      <svg width=${W} height=${H} viewBox="0 0 ${W} ${H}" aria-hidden="true">${shape}</svg>
      ${this.label ? html`<div class="icm-series-label">${this.label}</div>` : null}
    </div>`;
  }
}
customElements.define('icm-series', IcmSeries);
