// LABELS — every string the library itself puts on screen. English by default; a page that
// speaks another language sets globalThis.ICM_LABELS before this module runs (build.py does
// it from a labels.json beside lib/), so components never carry a second language.
export const LABELS = {
  locale: 'en',
  yes: 'yes', no: 'no',
  asking: 'sure?', running: 'working…', done: 'done', failed: 'did not go through',
  today: 'today', dueIn: 'in {n} {days}', dueAgo: '{n} {days} ago',
  days: {one: 'day', other: 'days'},
  fixes: {
    needs_reauth: 'reconnect the account in Settings',
    server_not_connected: 'add the connector in Settings',
    selection_required: 'choose which account, in Settings',
    not_in_manifest: 'this page has no permission for that',
    blocked_by_policy: 'an organization policy blocks this',
    approval_required: 'needs approval',
    server_unavailable: 'the service is not responding, try again',
    rate_limited: 'too many requests, wait a moment',
    tool_error: 'the service refused the action',
    cancelled: 'interrupted, outcome unknown',
  },
  ...(globalThis.ICM_LABELS || {}),
};

// "in 3 days" in any language: Intl knows the plural category, the label holds the forms.
export const countDays = (n, template) => {
  const forms = LABELS.days;
  const word = forms[new Intl.PluralRules(LABELS.locale).select(n)] || forms.other;
  return template.replace('{n}', n).replace('{days}', word);
};
