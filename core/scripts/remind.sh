#!/usr/bin/env bash
# Put one reminder into the owner's list on a Mac (Apple Reminders, through osascript). Local only: a cloud session has no Reminders.
#   core/scripts/remind.sh "Call the accountant about the statement" ["a note"]
# The list comes from _config/reminders.json {"list": "todo"}; default "todo". The list must exist: this script never creates one.
# invariant: the agent writes only to the catch-all list. Moving a thing to "today" is the owner's decision.
# trust: unverified until it has been run once with the owner watching (setup step 10 does exactly that).
set -eu
title="${1:?usage: remind.sh \"title\" [\"note\"]}"; note="${2:-}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
list="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('list','todo'))" "$root/_config/reminders.json" 2>/dev/null || echo todo)"
command -v osascript >/dev/null || { echo "remind: no osascript here; this channel works on a Mac only. See core/skills/setup/recipes/reminders-*.md"; exit 1; }
osascript - "$list" "$title" "$note" <<'OSA'
on run argv
  set listName to item 1 of argv
  tell application "Reminders"
    if not (exists list listName) then error "no list named " & listName
    make new reminder at end of list listName with properties {name:item 2 of argv, body:item 3 of argv}
  end tell
  return "remind: added to " & listName
end run
OSA
