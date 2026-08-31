---
name: feedback_cloud_push_size_limit
description: "★ SCOPE CORRECTED 2026-08-30: this ceiling belongs to ONE write path (MCP create_or_update_file, inline file text) — NOT to cloud sessions. git push to a branch + PR + squash-merge has NO size limit and is proven (92 KB v2_command.html, PR #2). Original rule below still governs any Contents-API push: The GitHub MCP Contents API takes the file's ENTIRE contents inline in one tool call, which exceeds a single message for big files — the push truncates and silently corrupts live code. This is what truncated AGENT_MAIL.md to one entry on 2026-08-27. Never attempt AGENT_MAIL.md (423 KB), dashboard.py (735 KB), field.html, v2_field.html (264 KB). Hand those to a session with gh. AND: when re-emitting ANY file, read it to EOF and diff after pushing — a partial Read silently drops the tail."
metadata:
  node_type: memory
  type: feedback
  modified: 2026-08-28T20:35:00.000Z
---

**Discovered 2026-08-28 (Specialists, cloud) while shipping the Card-at-Door page.**

---

## ★ SCOPE CORRECTION 2026-08-30 (cloud Lead) — READ THIS BEFORE APPLYING THE RULE BELOW

**Everything below is accurate about the MCP Contents-API path. It is NOT a property of cloud
sessions, and the "hand it to a session with `gh`" / "NEVER post to AGENT_MAIL.md" conclusions are
too strong.** There is a second write path with no size limit at all:

**`git push` a branch → `mcp__github__create_pull_request` → `mcp__github__merge_pull_request`.**

- Git-over-HTTPS is **not** blocked from cloud (only `api.github.com` REST is). The `main` ruleset
  protects `main`, not every ref — so pushing a feature branch works, and the PR merge lands it on main.
- **File bytes never pass through the model.** Git sends a packfile; you edit the file on disk with a
  script. That is the same property that makes the local `gh api | base64` recipe safe. So the
  truncation failure mode below **cannot occur on this path** — 445 KB behaves exactly like 4 KB.
- **Proven 2026-08-30:** this cloud session pushed `static/owner/v2_command.html` at **94,256 bytes**
  — inside the "60–100 KB" band called a wall below — plus `scheduler.py` (51 KB) in the same commit
  (PR #2, `15fba33`), then PR #4 and PR #5. All landed byte-clean.

**So:** `AGENT_MAIL.md` (445 KB) **IS postable from a cloud session** — append to it with a script
(never read it into context), push the branch, verify the diff is purely additive (`git diff
--numstat` must show `+N  0`), then merge. Rule 4 below ("NEVER post to AGENT_MAIL.md from a cloud
session") is superseded for the git path; it still stands for any Contents-API push.

**Use the Contents API only for genuinely small files** (a few KB) where one call beats four.

Root cause of the over-broad rule: the 2026-08-27 truncation was real, but only one write path was
ever tested, and its failure was generalized to the whole session type. See
[[feedback_verify_limits_before_declaring]] — this is the exact pattern that memory exists to stop.

---


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

**★ THE SECOND WAY IT BITES — a partial READ, not the size limit. I did this to `routers/printing/jobs.py`
the same day.** The file was 740 lines. I read it in two chunks and the second was
`Read(offset=407, limit=332)` → lines 407–**738**. Nothing warned me the file had two more lines, so I
emitted 738 of 740 and **pushed a `drive_download` missing its `return`** — it still compiled and the app
still booted, so no error surfaced; the endpoint just silently returned `null`. Caught only by diffing
the pushed file against my local copy, and fixed in a follow-up push.
- **Read to EOF and prove it:** `wc -l` the file FIRST, and check `offset + limit > total`. A `Read` that
  ends exactly at your limit is a tail-truncation waiting to happen — it looks identical to a complete read.
- **Never assemble an emission from stitched partial reads without re-checking the boundaries.**

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
5. **ALWAYS verify a push by content — this is the step that saves you**: re-fetch
   (`git fetch origin main && git show origin/main:<path>`) and `diff` against the local file you
   validated. Byte-exact or it did not land. Two gotchas while reading the numbers:
   - The GitHub result's `size` is **BYTES** while Python's `len(str)` is **CHARACTERS** — on a file with
     emoji/box-drawing/em-dashes those differ by over a thousand and look alarmingly like truncation when
     nothing is wrong. **Diff, don't eyeball the number.**
   - **CRLF files** (e.g. `routers/printing/jobs.py`) come back with `\r\n`; an inline push writes LF, so
     git shows the WHOLE file as changed. That is cosmetic and fine on Render/Linux, but it hides your
     real change from a reviewer — say so in the commit message and tell the reviewer to use
     `git diff --ignore-cr-at-eol`, and diff locally with `tr -d '\r'` on both sides so you can still see
     your own deletions.

**Why:** the project's single biggest historical risk is a stale or partial push over a large live file
(the 2026-04-30 dashboard.py incident dropped 2,277 lines; the Jun-8 field.html push dropped 1,377).
Cloud sessions have that risk *structurally*, on every big file, with no guard and no undo — so the
correct move is to design around it, not to push carefully and hope.
