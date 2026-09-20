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
    // invariant: a LINE is scaled to its own range, because its shape is the point and a zero baseline flattens 58..66 into
    // a ruler; BARS compare amounts, so they keep zero.
    const bars = this.variant === 'bars', last = v.length - 1;
    const hi = bars ? Math.max(...v, 1) : Math.max(...v), lo = bars ? Math.min(...v, 0) : Math.min(...v);
    const x = i => PAD + i * (W - 2 * PAD) / Math.max(last, 1);
    const y = t => H - PAD - (t - lo) * (H - 2 * PAD) / (hi - lo || 1);
    let shape;
    if (bars) {
      // bars compare separate periods; a line is for when the shape of the flow matters
      // each bar sits in its own slot, so the first and the last stay inside the box
      const slot = (W - 2 * PAD) / v.length, w = slot * 0.62;
      shape = v.map((t, i) => svg`<rect x=${PAD + i * slot + (slot - w) / 2} y=${y(t)} width=${w}
        height=${Math.max(1, H - PAD - y(t))}
        class=${i === last ? 'is-last' : ''}/>`);
    } else {
      const d = v.map((t, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(t).toFixed(1)).join(' ');
      shape = [svg`<path d=${d} fill="none" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>`,
               // the last point is a zero-length round stroke: the viewBox is stretched, and a <circle> would stretch into an ellipse with it
               svg`<path class="is-last" d=${'M' + x(last).toFixed(1) + ' ' + y(v[last]).toFixed(1) + 'h0'} stroke-width="9" stroke-linecap="round" vector-effect="non-scaling-stroke"/>`];
    }
    return html`<div class="icm-series">
      <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">${shape}</svg>
      ${this.label ? html`<div class="icm-series-label icm-caption">${this.label}</div>` : null}
    </div>`;
  }
}
customElements.define('icm-series', IcmSeries);
