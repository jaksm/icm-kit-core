# Ready code and recipes

Two ways this kit gets something done for an owner.

**Ready code** covers the case we ran ourselves. It works as shipped.

**A recipe** is instructions for the agent, for everything else: another platform, another
provider, or a part that can only ever be the owner's (their bank's statement format, their
sources). A recipe produces a result in the owner's ICM, in their `skills/` or `_config/`, never in `core/`.

## Trust

Every recipe starts with frontmatter:

```yaml
---
trust_tier: verified | unverified
verified_on: 2026-09-20, macOS 15, run by the maintainers     # only with verified
---
```

`unverified` means exactly this: written from documentation and common sense, **never executed by
anyone**. It is a map drawn from descriptions, not from walking the road. Most recipes start here,
and that is fine as long as nobody pretends otherwise.

## How to run an unverified recipe

1. Tell the owner, in their manner, that this path has not been tried before and that you will go
   carefully. Do not soften it and do not dramatize it.
2. One step at a time. After each step, **verify where the result shows**, not where the tool
   reports: open the list of rules and count them, look at the phone, read the file back.
3. Install nothing and change nothing outside the ICM without the owner's word, as everywhere in setup.
4. When reality differs from the recipe (a menu that is not there, a flag that does not exist),
   **stop and say so**. Look at the provider's current documentation, propose the adjusted step, and
   go on only with the owner's word. Never improvise over a mismatch silently.
5. If it cannot be done, say that. Write the capability down as missing, with the manual fallback,
   and mark the step `skipped` with the honest reason. A working ICM with one gap beats a faked success.

## Freestyle: `any-<what>.md`

For a case no recipe covers. It does not list steps, because there are none to list. It says what
the capability must provide, what to look for in the provider's documentation, how to prove it
works, when to say honestly that it cannot, and what the manual fallback is. Read it before you
start inventing.

## Recipes mature from real setups

When an unverified recipe got someone through, write what differed from the recipe into the owner's
`domains/system/output/connectors-and-routines.md`, and offer them the text of an issue for
`icm-kit-core` with those differences and the platform and version. They decide whether to send
it. There is no telemetry; this is the only way a recipe becomes `verified`.
