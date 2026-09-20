// Provider marks, so a card shows WHERE an action lands before it is tapped.
// invariant: Lit `svg` templates, never strings through unsafeHTML - see icons/ui.js.
import {svg} from '../vendor/lit.js';

export const PROVIDERS = {
  gmail: svg`<path d="M3 6.5 12 13l9-6.5" fill="none"/><rect x="3" y="5" width="18" height="14" rx="2" fill="none"/>`,
  calendar: svg`<rect x="3" y="5" width="18" height="16" rx="2" fill="none"/><path d="M3 10h18M8 3v4M16 3v4" fill="none"/>`,
  notion: svg`<rect x="4" y="3" width="16" height="18" rx="2" fill="none"/><path d="M8 8v8l8-8v8" fill="none"/>`,
  drive: svg`<path d="M9 3h6l6 11H3z" fill="none"/><path d="M3 14h18l-3 6H6z" fill="none"/>`,
  local: svg`<rect x="3" y="4" width="18" height="12" rx="2" fill="none"/><path d="M8 20h8" fill="none"/>`,
};

// Connector display name -> mark. Anything unknown falls back to `local`.
export const PROVIDER_OF = {
  'Gmail': 'gmail',
  'Google Calendar': 'calendar',
  'Notion': 'notion',
  'Google Drive': 'drive',
};
