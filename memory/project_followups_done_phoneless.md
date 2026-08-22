---
name: project_followups_done_phoneless
description: "Follow-ups screen (followups.py /api/followups/view): the ✓ Done / ⏰ Snooze buttons removed a card by PHONE match only. The STOP opt-out cards ('Mark Do-Not-Contact (texted STOP)') are stored in wsc.followups.data with phone:'' (no pid/id) — so Done posted an empty phone → server 'phone required' → card never disappeared (DJ hit this 2026-08-08). Fixed with a NAME fallback."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-08T15:39:30.179Z
---

**Symptom (DJ 2026-08-08):** on the Follow-ups screen, the 4 "Opt-out - mark Do-Not-Contact (texted STOP)" cards (Dawn Hay, Rochelle Lozdon, Steven Hess, Willard Sterling) would not clear — pressing ✓ Done did nothing.

**Root cause:** `/api/followups/resolve` (followups.py) removes a card by matching `_norm_phone(r.phone)==phone`. The STOP records in `wsc.followups.data` carry **`phone:''`** and no `pid`/`id`/`number` — only `name/cat/do/last/draft`. The rendered Done button therefore had `data-ph=""`; `resolveFU`/`snoozeFU` posted an empty phone → server returned `{ok:false,'phone required'}` → card stayed. (Non-STOP cards have real phones and worked.)

**Fix (commit fcadaa6, followups.py — SPECIALIST's file, mailed):**
- resolve endpoint now reads `name` too; guard = `if not phone and not name`. Done: `if phone` drop-by-phone (unchanged) **else** drop records where `name` matches AND the record has NO phone (so a real phone-bearing record can never be removed by a name collision). Snooze: same name fallback for phone-less rows.
- Inline JS `resolveFU` now sends `name` (from the card's `.nm`); `snoozeFU` no longer bails on empty `ph` (guards `if(!ph && !nm) return`) and sends `name`.
- Verified live: POST /api/followups/resolve `{name:"Dawn Hay",action:"done"}` → ok; view dropped Dawn, kept the other 3.

**Deeper note:** these STOP cards are informational (Phase 2B STOP webhook already marks Do-Not-Contact); the card has no pid so Done just dismisses. If a future need is "Done should also write DNC," the record would first need a pid/phone. See [[feedback_ported_means_twilio]].
