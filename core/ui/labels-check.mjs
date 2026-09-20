// Runnable check for primitives/labels.js: node labels-check.mjs. Fails if plural selection breaks.
import assert from 'node:assert';
import fs from 'node:fs';
const sr = new URL('../labels.json', import.meta.url);   // a repo's own language, when it has one
if (fs.existsSync(sr)) globalThis.ICM_LABELS = JSON.parse(fs.readFileSync(sr, 'utf8'));
const {LABELS, countDays} = await import('./primitives/labels.js');
const forms = n => countDays(n, '{days}');
if (LABELS.locale === 'sr') {
  // 1 and 21 take `one`, 2-4 `few`, 5+ and 11-14 `other`
  assert.deepEqual([1, 2, 5, 11, 21].map(forms), [LABELS.days.one, LABELS.days.few, LABELS.days.other, LABELS.days.other, LABELS.days.one]);
} else {
  assert.deepEqual([1, 2].map(forms), [LABELS.days.one, LABELS.days.other]);
}
assert.equal(countDays(3, 'x {n} y'), 'x 3 y');
console.log('ok', LABELS.locale);
