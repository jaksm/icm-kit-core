---
trust_tier: unverified
---

# What a scheduled runner does not have

Read `core/RECIPES.md` first. The facts are from one harness's cloud runner (Ubuntu 24.04, seen
2026-09-19); the rule is general.

**Nothing in the routine may depend on a binary being installed.** A runner's setup script is often
cached for days, so a machine that looks identical predates the line that installs the tool. A
routine once wrote its record, then died on a missing image tool, and the phone kept yesterday's page.

- The build reads image and video sizes from file headers itself; external tools are a fallback.
- `magick` is ImageMagick 7. Distributions that ship version 6 have `convert` and `identify` and no
  `magick` at all, **even after installing the package**. `fetch-media.py` tries both.
- `uv` missing: the funnel cannot run. The routine still builds the feed from the ICM alone and says
  `funnel failed: uv missing` in its phases. `yt-dlp` or `ffmpeg` missing: no new video, images only.
- Media fetched on the owner's computer and committed works everywhere; prefer fetching there when a
  card can wait.

If the adapter has a setup script for its runner, add the tools there too, and still assume they are absent.
