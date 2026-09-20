// UI icons. Inline because the artifact CSP blocks external images.
// invariant: these are Lit `svg` templates, not HTML strings. A <path> inserted with
// unsafeHTML is parsed in the HTML namespace, becomes an HTMLUnknownElement and draws
// NOTHING, while every computed style still reads correct - the icon is simply invisible.
import {svg} from '../vendor/lit.js';

export const UI = {
  heart: svg`<path d="M12 20s-7-4.6-7-9.3A3.7 3.7 0 0 1 12 8a3.7 3.7 0 0 1 7 2.7C19 15.4 12 20 12 20z"/>`,
  details: svg`<path d="M4 7h16M4 12h16M4 17h9"/>`,
  external: svg`<path d="M7 17L17 7M9 7h8v8"/>`,
  source: svg`<path d="M4 5h7l2 2h7v12H4z"/>`,
  next: svg`<path d="M9 6l6 6-6 6"/>`,
  up: svg`<path d="M5 15l7-7 7 7"/>`,
  call: svg`<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/>`,
  sms: svg`<path d="M4 5h16v11H9l-5 4z"/>`,
  mail: svg`<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>`,
  map: svg`<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>`,
  down: svg`<path d="M5 9l7 7 7-7"/>`,
  comment: svg`<path d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-7l-5 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><path d="M8 10h8M8 13h5"/>`,
};
