---
trust_tier: unverified
---

# Any mail provider

**What the capability must provide:** (1) the provider sorts known senders at arrival by rules that
run on its servers, with the computer off; (2) the owner can say for each sender whether its mail
stays in the inbox; (3) ideally the agent can read the inbox and relabel or archive, never send and
never delete. Part 3 is optional; parts 1 and 2 are the point.

**What to find out, from the provider's current help pages and the owner's settings screen:**
where server-side rules live (not rules of a desktop app, which run only while it is open);
whether it uses folders or labels, because with folders "label it and keep it in the inbox" does
not exist and needs a flag or category instead; whether rules can be imported or written as text
(Sieve is common); the limit on the number of rules; the order they run in and whether one rule
stops the others; whether any existing rule deletes or forwards.

**With folders instead of labels:** the `label` column holds the folder name. `keep_in_inbox: yes`
then means no moving rule at all (at most a flag or a category), because a moved message has left
the inbox. Write down what the rule list shows after saving, in the provider's own words: button
names differ from the help pages more often than not.

**How the agent reads the mailbox, in order of preference:** a connector the harness has; IMAP with
an app-specific password kept in the harness's secret storage and a small read-only script built
for this owner in their `skills/`; nothing. With nothing, sorting still works and that is said plainly.

**Proof:** the rule list counted after creation, and one real message seen where its rule says.

**When to say no:** a provider whose only rules run in a desktop app; a mailbox an employer
controls (ask whether they are allowed to automate it at all before touching it).
