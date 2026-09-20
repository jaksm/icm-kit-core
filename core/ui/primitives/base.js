// IcmElement — base class for every element in this library.
import {LitElement} from '../vendor/lit.js';

// invariant: render into LIGHT DOM, not a shadow root. One global stylesheet then serves
// every instance, and page-level fixes for iOS compositing, clip-path and scroll-snap keep
// working unchanged. A shadow root would put a new
// boundary exactly where those bugs lived.
export class IcmElement extends LitElement {
  createRenderRoot() { return this; }
}
