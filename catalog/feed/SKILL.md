---
name: feed
description: A daily page for the phone that shows what is open in the ICM and what arrived from outside, as rows to flick through (a topic downward, deeper sideways), and that reports back what the owner looked at. Use as the last phase of the morning routine, or when the owner says "make today's feed", "what is open", or asks for the feed.
---

# Feed

**Vocabulary, fixed and enforced in code.** The *feed* is the page the owner opens every day. A *row*
of the feed is one topic, or anything that needs several cards to explain; rows are flicked top to
bottom. A *card* (in the data: `stories`) is one slide of content inside a row, flicked sideways.
The first screen of a row is its *cover*: the name of the topic and its aggregate. Down changes the topic, sideways goes deeper. A card has two states: the front
(media, at most three components, one sentence of at most 80 characters) and the details.

## Inputs

- The ICM itself: for each area, its `CONTEXT.md` and `output/`. Only what is **open or changing**
  becomes a card, never what is finished.
- The mailbox, if `morning-review` runs: what it left as "needs you" becomes the row `inbox`, one
  story per message, `source: {"kind": "mail", "id": ...}`.
- Signals from outside: `_config/feed/feeds.csv` and `channels.csv`, through the funnel below.
- Yesterday's attention diary, read through the adapter's page store, and `<data>/diary.csv`.
- `_config/feed.json` (see `setup.md`), `core/ui/schema.json` (every field a card may carry, with
  limits and when to use it: read it before writing cards), and `template/example-day.json`, a
  whole day in the shape the build accepts. The catalog of actions is `_config/actions.json`; when
  the owner has none, the library's default in `core/ui/actions.json` is used.

## Process

| Step | What | Who |
| --- | --- | --- |
| 0 to 2 | pull every feed, dedupe, drop what is old, seen or has no url | `scripts/pull-signals.py` |
| 2.5 | **read the source** of what passed, before anything judges it | `scripts/read-sources.py` |
| 3 | score against what is **open in the ICM**; with many groups one subagent per group in parallel, with a few dozen items yourself. Either way one judgement per item, from its text, not a keyword pass | the agent |
| 4 | quota per row, three to five stories | the agent |
| 5 | write the cards into `<data>/<date>.json`, fetch media, build, publish | the agent, `fetch-media.py`, `build-feed-page.py` |

Each step leaves a file in `<data>/signals/<date>/`, because that is the only way the work can be
checked afterwards. Steps 3 and 4 are judgement, and they leave files too, so any scorer can stand
between 2.5 and 5:

- `03-scores/<group>.jsonl`, one row per item of `025-read.jsonl`:
  `{"url", "score": 0-3, "open_item": "<path in the ICM it touches, or empty>", "why": "<one sentence>"}`
  3 changes an open decision or has a deadline, 2 is worth knowing for an open item, 1 is related
  and changes nothing, 0 touches nothing. **A card needs 2 or more.**
- `04-selected.json`: `{"<row id>": ["<url>", ...]}`, what goes into the feed after the quota.

**Rules of judgement**

1. **Score against the ICM, not against the topic.** "A new model is out" is not a card by itself;
   it is one if it changes a decision that stands open. An item with an empty `open_item` scores 0.
   Without this the feed becomes a news site. An ad is never a card because it arrived. What the
   owner follows out of interest counts as open **once it is written down**: a record in the area
   it belongs to, saying what they follow and what would make an item matter. `open_item` points
   at that record. A topic that lives only in a conversation cannot produce a card.
2. **Order and choice are not invented.** Look for a written rule in the area and quote it on the
   card. If there is none, say so on the aggregate card instead of deriving a score.
3. Every story carries `source`: a path in the ICM, or `{kind, url}` for a signal. The build refuses
   a card without one. A number without a record behind it does not enter.
4. When a reader failed and the feed's own summary was used (`text_source: feed-summary`), the card
   may be written, but from the summary only, and `manifest.json` must show `fallback_reason`.
   **A fallback must never hide that the real read stopped working.**
5. The quota of three to five stories is a ceiling, not a floor: a row with one honest story is
   fine, padding is not. An item goes to the row of the record it touches, whichever feed brought
   it. A signal row's cover takes the topic record as its `source`; a story's is
   `{"kind": "link", "url": ...}`. A text cut at the reader's limit may carry a card that says so.
   About fifteen items is the upper measure for one run of flicking. A row may instead tell one
   story in 5 to 20 cards when the order carries meaning; the cover then names the story, not the area.
6. **Every screen shows an image, and never a lying one.** A card without media of its own shows
   its row's cover; a cover without media takes the row's standing cover from `covers` in
   `_config/feed.json` (an image the owner chose once for that topic). The build prints how many
   screens are still bare and **refuses one image file under several names**: the same picture on
   four cards is a placeholder pretending to be content; let them fall back to the cover instead.
   Order for a card's own media: real before default. The image the source hands over,
   then the page's own image (`fetch-media.py`), then a CC image searched by the thing's name. A
   photo that merely looks related is a lie; a card without media stays in the tone of its topic
   and looks like a choice. `--fill` searches only for a fact that names a thing, never for a
   topic, tries the page's own image first, and lists every image it took from a page or found by search: **open each one and look before
   it stays** (a site's logo is not a picture of the thing);
   when its licence asks for credit, the credit from the report goes into the card's `facts`.
   Someone else's video is a work: six silent seconds on a card *about that
   video* is a quote, the same clip as decoration is not. A listing photo is an auxiliary frame.
7. A link's label says what happens ("Watch on ...", "Open the thread"), never who the author is.
8. Money appears as aggregates only. What the owner asked not to keep does not become a card.

**Yesterday's diary, before today's feed.** On the first day, and whenever the page has no store,
there is no diary: say so in the phases and go on. One document per day in the page store, collection
`diary`, id `<date>`: `{date, build, builds, rows, items}`; an item's key is `<row id>#<index>`
(0 is the cover) and it holds `ms`, `detailsMs`, `liked`, `links`, `topic`, `hook`, and when present
`comment`, `thumb`, `commentedAt`, `actions[]`, `answers{}`. Append it to `<data>/diary.csv`
(`date,row,key,topic,seconds,details_seconds,liked,links,thumb`), so the signal outlives the page.

- **Compare `build` with the `build` in `<data>/<date>.json` first.** If they differ, or `builds` is
  not empty, the diary measured another page: write it to the CSV and **change nothing** on its evidence.
- The signal is asymmetric: read what attracted, not what did not. A like, a followed link and a
  comment are strong; dwell is compared with the other cards **of that day**, not in absolute
  seconds; a short dwell or no record means almost nothing (a dull card and a busy morning look the same).
- **A card with a `deadline` is never dropped for being skipped.** It is written differently tomorrow.
- Comments are read across days. A preference becomes a rule only in the owner's record of feed
  preferences, with the comment that led to it quoted, and only when the owner confirms.
- Form answers (`answers`) go where the card's question said they go, the same morning.

**Build and publish**

```bash
python3 core/workflows/feed/scripts/fetch-media.py --fill <data>/<date>.json
python3 core/workflows/feed/scripts/build-feed-page.py --stale      # which rows need reading again
python3 core/workflows/feed/scripts/build-feed-page.py --preview    # locally, with a fake store
python3 core/workflows/feed/scripts/build-feed-page.py --publish    # prints the connector manifest
```

`--publish` also writes `<out>-publish.files.json`: exactly the media files this day refers to, as
`{"media/<file>": "<path in the ICM>"}`. **Publish with that map, every time.** A file that is
referenced and not published is a blank card on the phone and no error anywhere.

Publishing is the adapter's "publish a page": always to the page's existing address (listed in
`domains/system/output/pages.md`), with the store capability, the printed manifest, and the media
folder as files beside the page under `media/`. The page is assembled by a machine from the ICM and
nobody edits it elsewhere, so it is overwritten, not merged. **Checkpoint: the first publication,
and any publication after the template or the catalog of actions changed, waits for the owner's word.**

**The feed is published even when empty**, as one row whose cover says so. A missing page cannot be
told from a broken routine. In a routine, end with the phases section like every routine: `funnel
ok`, `cards ok`, `build ok`, `publish ok`, or `<phase> failed: <reason>`.

Weekly, from the funnel's files, propose to the owner (never apply silently): a feed with volume and
no card in four weeks goes; three errors in a row or 60 days silent is dead
(`core/scripts/check-feed.py` confirms); new sources grow from domains that
surviving cards link to, and from areas newly opened in the ICM.

## Outputs

`<data>/<date>.json` with `prints` and `build` written back by the build; `<data>/signals/<date>/`;
`<data>/diary.csv`; media in `media_dir`; the page. `00-pulled.jsonl` and `01-unique.jsonl` are
large and stay out of git. `<data>/signals/seen.csv` holds what earlier days served, so an item is a
card once; running the same day again is safe, that day's own rows are ignored.
