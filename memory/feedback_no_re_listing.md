---
name: Don't re-print tables/lists/buckets across responses — use a working file
description: When work involves a list/table that spans multiple turns (SO triage, payment scans, batch reviews), write it to a file once and reference it. Re-printing forces DJ to scroll back through compacted history to find the canonical version, and each repeat tends to drop detail.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
When a task involves a list, table, or bucketed data that we'll revisit across multiple turns (SO triage lists, payment scans, batch deletions, line-item reviews, etc.):

1. **Write the data to a working file** — typically under `4_Reference_Data/` with a date-stamped name (e.g. `so_triage_apr27.md`)
2. **Update the file as items are resolved** — not the chat
3. **In chat, reference the file by name** — don't re-paste the table
4. **Chat replies stay terse** — decisions and actions only

**Why:** DJ flagged this on 2026-04-27 — *"why do you keep repeating your answers... each additional repeat is missing some part. so i have to go all the way up to the first response (find it). then come back down to type next response. very confusing and time consuming."* Lossy compaction over a long session makes the problem compound: each re-print may drop a column or summarize a bucket, so the user no longer trusts any single copy as canonical. They end up scrolling far back to find the original, which kills flow.

**How to apply:**
- Triggers: any time I'm about to print a list of >5 items that we'll act on across turns. SOs, contacts, jobs, accounts, anything.
- The first time, dump it to a file and tell DJ the path. Every subsequent turn, reference the file (e.g. "Bucket 1a in `so_triage_apr27.md`") and avoid re-printing.
- One exception: a final "here's what got done" recap at the end of a triage session is fine — that's a closeout, not a working reference.
- This is independent of `feedback_save_filter.md` (memory writes) and `feedback_chatter_format.md` (Odoo chatter formatting). Different surface, same principle: write once, reference forever.

Related: this is also why `MEMORY.md` is an index — same principle at the meta level (memory files exist so chats don't keep re-deriving the same facts).
