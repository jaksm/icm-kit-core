# Setting up the feed

Needs the adapter's **publish a page** capability with a store the page can write to; without the
store the feed still works and nothing is learned from it, say so. `sources` and `morning-review`
are not required, they add the `inbox` row. The funnel scripts run through `uv` (they declare their
own dependencies); images need ImageMagick, video needs `yt-dlp` and `ffmpeg`: see
`recipes/cloud-binaries.md` before relying on any of them in a routine.

## Ask

Which areas of the ICM should show up every morning, and which never. Which topics they follow
outside (three are enough to start), **and for each, what would make an item matter to them**. Where they read now, so sources come from their habits and not
from a list. What language the page speaks. Whether the feed should be the last phase of the morning routine.

## Writes

`_config/feed.json`, every key optional; defaults and what each number means are in `scripts/common.py`:

```json
{
  "data": "domains/system/data/feed", "media_dir": "pages/media", "out": "pages/feed.html",
  "max_age_hours": 48,
  "covers": {"<row id>": "media/<file>"},
  "hosts": {"youtube\\.com|youtu\\.be": "Watch on YouTube"},
  "labels": {"title": "...", "endTitle": "...", "cards": {"one": "...", "other": "..."}}
}
```

Label keys are `LABELS` in `scripts/build-feed-page.py`; plural forms are keyed by the
`Intl.PluralRules` categories of the locale (`one`, `few`, `other`...).

`_config/labels.json`, when the page is not in English: `{"locale": "de"}` is enough for the feed.
The same file may translate the component library's own words (keys in
`core/ui/primitives/labels.js`); a partial file is fine, English fills the rest.

**A record per followed topic**, in the area it belongs to (or `domains/system/output/` when it has
none): what they follow and what would make an item matter. Without it nothing from outside can
become a card, by rule 1 of `SKILL.md`, and the first feed will rightly be empty of signals.

`_config/feed/feeds.csv`: `group,name,url,status,notes`. One group becomes one row. **Run every url
through `core/scripts/check-feed.py` before it is written**, and write only `ok`
ones; tell the owner which ones were not and why. `_config/feed/channels.csv`: `group,channel,channel_id,status,notes`.

`.gitignore`, with `<data>` replaced by the folder from the config: `<data>/signals/*/00-pulled.jsonl`, `<data>/signals/*/01-unique.jsonl`, `pages/feed*.html`
(a built page carries text of the ICM; media files are kept).

`domains/system/output/pages.md`: a row for the feed: name, source (`core/workflows/feed`, data in
`<data>`), how it is rebuilt (`build-feed-page.py --publish`), and its address once published.

**A standing cover per row.** For each row they named, pick an image with them once (their own photo
is best; `fetch-media.py <page-url> <row id>` otherwise), and write it under `covers`. It is what a
row shows on days when no card brings its own picture.

## First run and proof

1. `pull-signals.py`, then `read-sources.py`. Read `manifest.json` with the owner: how many feeds
   answered, how many items passed, what `00-errors.csv` and `025-unread.csv` say.
2. Write the first day together, small: one row per area they named, two at most, and the
   signal rows that scored, a few stories in all. `template/example-day.json` is the shape. If no signal scored, show
   them `03-scores/` and ask whether the topic records say what they meant.
3. `build-feed-page.py --preview`, serve the folder locally, open it at phone width. Proof: the
   cards show, details open, and after a like `window.__writes` holds an item with `liked: true`.
4. Publish on the owner's word. Proof on their phone: the page opens, and the next morning the
   diary document for that day exists in the page store with the same `build` as `<data>/<date>.json`.
5. Only then add it to the routine (setup step 13): "Make today's feed per core/workflows/feed/SKILL.md".
