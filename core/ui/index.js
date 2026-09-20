// ICM component library — the single import point. Every artifact loads this and nothing else.
export {IcmElement} from './primitives/base.js';
export {LABELS} from './primitives/labels.js';

// primitives: no meaning of their own, used by the components
export {IcmIcon} from './primitives/icm-icon.js';
export {IcmLink} from './primitives/icm-link.js';
export {IcmButton} from './primitives/icm-button.js';

// components: each one has a row in schema.json
export {IcmMetric} from './components/icm-metric.js';
export {IcmTags} from './components/icm-tags.js';
export {IcmDeadline} from './components/icm-deadline.js';
export {IcmDelta} from './components/icm-delta.js';
export {IcmGauge} from './components/icm-gauge.js';
export {IcmSeries} from './components/icm-series.js';
export {IcmList} from './components/icm-list.js';
export {IcmFacts} from './components/icm-facts.js';
export {IcmQuote} from './components/icm-quote.js';
export {IcmNext} from './components/icm-next.js';
export {IcmAction} from './components/icm-action.js';

// forms: the feed asking him something, answers land in the artifact's db
export {IcmChoice} from './components/icm-choice.js';
export {IcmSlider} from './components/icm-slider.js';
export {IcmInput} from './components/icm-input.js';
export {IcmConfirm} from './components/icm-confirm.js';

export {UI} from './icons/ui.js';
export {PROVIDERS, PROVIDER_OF} from './icons/providers.js';
