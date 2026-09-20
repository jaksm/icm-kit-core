# Catalog

Optional workflows. Nothing here is installed until the owner asks for it:

```bash
./install.sh <icm> --add <name>       # lands in core/workflows/<name>/, recorded in core.lock
./install.sh <icm> --remove <name>
```

Every workflow is a folder with the same three parts, so setup can offer it without knowing it:

| File | What it is |
| --- | --- |
| `SKILL.md` | the contract of the work: Inputs, Process with checkpoints, Outputs |
| `setup.md` | what setup asks, which keys it writes in `_config/`, the first run, and the proof that it worked |
| `recipes/` | ready code covers the common case; a recipe tells the agent how to fit it to this owner, or how to build the part that can only be theirs |

| Name | What the owner gets | Needs | State |
| --- | --- | --- | --- |
| `sources` | newsletters, feeds and notices arriving by mail, sorted by the provider's own rules, which are kept in the ICM | a mail provider with server-side rules; ready code for Gmail, recipes for others | 0.3.0 |
| `morning-review` | a routine that sorts the inbox, leaves unread only what needs the owner, writes a daily record with proof it ran | `sources`; the adapter's mail capability; routines for the schedule | 0.3.0 |
| `import` | an old system (a notes app, another assistant's memory, an old repo, a disk, a large mailbox) walked through with the owner, five items at a time | nothing | 0.4.0 |
| `expenses` | spending per month as aggregates and a page. Categorizing, aggregating and the page are ready; the statement parser is a recipe, built for the owner's bank | a sample statement; publishing a page, optional | 0.4.0 |
| `feed` | a daily page of what is open in the ICM and what arrived, to flick through on the phone | sources, routines, publishing a page | planned, 0.5.0 |

The graph of the ICM is not here: it is part of `core/`, every ICM has it.
A row is added when the folder exists; `planned` rows are a promise, not an install target.
