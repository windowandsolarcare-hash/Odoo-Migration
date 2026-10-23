---
name: project_hiring_compare_round2_answer_placeholder
description: "PARKED cosmetic TODO — the Round-2 (Zoom) answer boxes in hiring_compare.html still show the 'fills in from the recording' placeholder, but Round 2 is manual. Fix on NEXT touch of that file."
metadata:
  node_type: memory
  type: project
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-23T22:58:09.065Z
---

**PARKED cosmetic — do on the NEXT edit of `static/owner/hiring_compare.html` (Lead+Audit, 2026-10-23).**
Not worth a standalone re-push (DJ knows Round 2 is manual); fold it into the next change to the file.

**What:** The per-candidate Round-2 (Zoom) questions added 2026-10-23 (`ROUND2_Q`, james 8Q / alfonso 10Q,
rendered with key space `r2q*`) reuse `ivItem` → so each r2q row renders both an `ivNote` box AND an
`ivAns` ("Answer") box. The `ivAns` placeholder reads *"answer fills in from the recording automatically
after the call…"* — WRONG for Round 2: it's a live Zoom with manual note capture, no recording/transcript.
(The transcript auto-fill builds its qs from `INTERVIEW_Q` only, so it never actually touches r2q* — this
is purely a misleading placeholder, not a data bug.)

**Fix (either):** (a) give r2q rows a round-2-specific answer placeholder ("type notes during the call"),
or (b) drop the `ivAns` box entirely for r2q rows and keep only the note box. Cleanest = pass a flag
through `ivItem`/`ivAns` (e.g. `manual=true`) so the placeholder/box differs for r2q* without touching the
q* (phone-screen) rows. Keep it ADDITIVE — do NOT alter `INTERVIEW_Q`, the `q*` keying, or `#ivqcount`
(all verified frozen on the 2026-10-23 ship, commit 26a07585). Save path is already correct (notes/answers
key by the box's own `data-note`/`data-answer` = the real candidate id; all DATA ids non-empty).

Frontdoor owns hiring_compare.*. See [[feedback_next_not_later_ai_blindspots]] (deferral with a real
trigger is legit), [[feedback_field_whitelist_strip_silent_inert]].
