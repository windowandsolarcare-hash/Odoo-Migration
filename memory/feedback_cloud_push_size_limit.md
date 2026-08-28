---
name: feedback_cloud_push_size_limit
description: "★ STANDING RULE for CLOUD sessions: you cannot push a file bigger than roughly 60-100 KB. The GitHub MCP Contents API takes the file's ENTIRE contents inline in one tool call, which exceeds a single message for big files — the push truncates and silently corrupts live code. This is what truncated AGENT_MAIL.md to one entry on 2026-08-27. Never attempt AGENT_MAIL.md (423 KB), dashboard.py (735 KB), field.html, v2_field.html (264 KB). Hand those to a session with gh."
metadata:
  node_type: memory
  type: feedback
  modified: 2026-08-28T19:20:00.000Z
---

**Discovered 2026-08-28 (Specialists, cloud) while shipping the Card-at-Door page.**

**The limit.** A cloud Claude Code session has no `gh` CLI, so its only write path is the GitHub MCP
`create_or_update_file`, whose `content` is **inline file text** ([[feedback_mcp_push_content_is_inline]]).
Inline means the model must emit every byte of the file in ONE tool call. A message has a max output
size, so past roughly **60–100 KB the call is truncated** — and a truncated push is a *successful* API
call that silently replaces good code with a fragment. There is no regression guard on this path, and a
cloud session **cannot restore the file afterwards** (restoring means pushing the original back, which
is the same oversized push).

**This already happened.** `AGENT_MAIL.md` was truncated to a single entry on 2026-08-27 — Lead's note
calls it "an earlier automated push of this same review truncated this file to one entry; restored full
history from a1702632." That was this failure mode, not a one-off glitch.

**Known unpushable-from-cloud files** (sizes as of 2026-08-28):
- `saunders-render-app/3_Documentation/AGENT_MAIL.md` — **423 KB** ← the fleet's whole history
- `routers/owner/dashboard.py` — **735 KB**
- `static/owner/v2_field.html` — **264 KB**; `static/owner/field.html` — same class
- `routers/owner/payments.py` — **143 KB** (borderline; do not risk it)

**How to apply — a cloud session:**
1. **CHECK THE SIZE BEFORE PLANNING AN EDIT:** `git show origin/main:<path> | wc -c`. Over ~60 KB → you
   are not pushing it. Decide that *before* you build, because it changes the design.
2. **Restructure so your change lands in a NEW small file** instead of a big existing one. That is what
   the Card-at-Door build did: the server code went into a brand-new `routers/owner/carddoor.py` (34 KB)
   plus a 15 KB `main.py` registration, instead of appending to the 143 KB `payments.py`. New files also
   sidestep the fidelity problem entirely — you author them, you are not re-transcribing existing bytes.
3. **Hand the leftover big-file edit to a session with `gh`** (local Specialists / DJ), with the exact
   patch text and its `node --check` / `py_compile` result. Do not improvise a workaround — in
   particular **never** override a function from another already-loaded script, and **never** reorder
   `main.py` router includes to shadow a route, just to avoid editing a big file.
4. **NEVER post to `AGENT_MAIL.md` from a cloud session.** Write your report to its own small
   `3_Documentation/*_STATUS.md` and reach the other session directly (`SendMessage`) or through DJ.
5. **ALWAYS verify a push by content**: re-fetch (`git fetch origin main && git show origin/main:<path>`)
   and `diff` against the local file you validated. Byte-exact or it did not land. The GitHub result's
   `size` is BYTES while Python's `len(str)` is CHARACTERS — on a file with emoji/box-drawing/em-dashes
   those differ by over a thousand and look alarmingly like truncation when nothing is wrong. Diff, don't
   eyeball the number.

**Why:** the project's single biggest historical risk is a stale or partial push over a large live file
(the 2026-04-30 dashboard.py incident dropped 2,277 lines; the Jun-8 field.html push dropped 1,377).
Cloud sessions have that risk *structurally*, on every big file, with no guard and no undo — so the
correct move is to design around it, not to push carefully and hope.
