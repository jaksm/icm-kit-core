---
trust_tier: verified
verified_on: 2026-09, Gmail web, by the first owner of an ICM (import of a filter file, about thirty filters)
---

# Gmail

1. `python3 core/workflows/sources/scripts/make-mail-filters.py` writes `_config/sources/mail-filters.xml` from `senders.csv`.
2. The owner opens Settings, Filters and Blocked Addresses, **Import filters**, picks the file,
   ticks all, Create filters. **Importing a file beats clicking through the dialog**: driven by an
   agent, the create-filter dialog has closed twice with no error and no filter.
3. Open the filter list and **count**. It must match the number the script printed, plus what was there before.
4. Importing the same file twice makes duplicates. After a change, delete the old filters of that
   label and import again, or create only the new row by hand and keep the CSV in step.
5. Labels are created by the import if they do not exist. A label with a slash is a nested label.
6. Reading existing filters: the same page has **Export**. Read the exported file instead of the screen.
