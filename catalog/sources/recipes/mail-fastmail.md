---
trust_tier: unverified
---

# Fastmail

Read `core/RECIPES.md` first: nobody has run this. Menu names change; trust what is on the owner's screen over this text.

Rules are in Settings, Filters and Rules, and underneath they are a Sieve script, which can be edited as text. That makes it the closest to a file import: generate the Sieve block from `senders.csv` (fileinto for a folder, or a label when the account is set to labels mode), show it to the owner, and paste it into the custom Sieve section. Check which mode the account is in first: folders or labels changes what "keep in inbox" means.

Proof, as always: after creating the rules, open the list and count them, then wait for one real message and see where it landed.
