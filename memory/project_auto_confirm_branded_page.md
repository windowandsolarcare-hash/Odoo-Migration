---
name: project_auto_confirm_branded_page
description: "Daily auto-confirm texts (4-day batch + maintenance Stage 1) now send the BRANDED self-confirm page link (?c=1 'Yes, I'll be there') instead of 'reply YES'. Part of the specialist's one-page schedule/confirm lifecycle. reminders.py, 2026-08-06, DJ approved."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-07T23:11:01.799Z
---

**★ REGRESSION 2026-08-07 (re-applied):** this whole change was SILENTLY REVERTED by a later 8-07 specialist commit to reminders.py (mark_confirmed/approve_request) built on a pre-change copy — `_confirm_page_body` vanished, `build_batch('confirm')` went back to `TEMPLATES['confirm']` ("reply YES"), maint Stage 1 back to `MAINT_CONFIRM_TEMPLATE`, `_maint_confirmed_batch` lost the CONFIRM_KEY reconciliation. DJ caught it ("I thought we were into buttons only"). Re-applied all four on top of current-live + pushed + mailed the collision. reminders.py is HEAVILY co-edited by both sessions → verify these 4 anchors survive after any specialist reminders.py push; ping "who's holding reminders.py" before pushing. (Smart-detect/`_ai_is_confirmation`/`_mark_awaiting` survived.)

**Context:** the specialist unified the schedule→confirm→remind lifecycle into ONE branded page (schedule + confirm are the same page; `?c=1` = confirmation flavor). They asked lead to switch the DAILY auto-confirm engine (reminders.py) to match. DJ approved 2026-08-06.

**What changed (reminders.py, all additive/surgical):**
- New shared helper **`_confirm_page_body(first, so_id, when_phrase)`** — builds the confirm text with the branded link: `from routers.booking import make_sched_token` → `_SCHED_BASE + '/book/sched/' + tok + '?c=1'`, wording = "…We have you on the schedule for {when} — tap here to confirm, or let me know if you need to reschedule: {link}". Falls back to the old reply-YES line if the token can't build (never send an unanswerable confirm).
- **`build_batch('confirm')`** (the 4-day-out batch, `CONFIRM_LEAD_DAYS=4`): confirm body now `_confirm_page_body(...)` instead of `TEMPLATES['confirm']` ("reply YES").
- **Maintenance Stage 1** (`_maint_stage_rows`, stage=='confirm'): body now `_confirm_page_body(first, so_id, day+time)` instead of `MAINT_CONFIRM_TEMPLATE`.
- Old template constants (`TEMPLATES['confirm']`, `MAINT_CONFIRM_TEMPLATE`) left in place (vestigial/fallback ref) — not removed.

**Two-confirm-system reconciliation (the crux):**
- `CONFIRM_KEY = 'wsc.reminders.confirmed.<so_id>'` is the UNIFIED confirmed flag — set by the YES-reply handler (reminders L420) AND the branded page (`/api/sched/confirm`, specialist). The generic `build_batch` "already confirmed" check already reads CONFIRM_KEY → a page-confirm already suppresses it. ✓
- Maintenance used a SEPARATE key `MAINT_CONFIRM_KEY = 'wsc.maint.confirmed.<so_id>'`. Fixed: `_maint_confirmed_batch` now searches BOTH keys, so a page-confirm (or generic YES) also suppresses maint re-sends and flips the night-before text to the CONFIRMED wording.
- Replying YES to the text still works everywhere (unchanged).

**Not changed:** WHEN/whether it sends (still approval-gated via the HUD/review page — DJ taps Send). Only the wording/link changed. Skipped the specialist's optional YES-handler date_key binding (not urgent; reschedule-clear of CONFIRM_KEY covers day-changes). Verified the link builds live (John SO 17389 → `wscare.pro/book/sched/17389-…?c=1`). See [[project_appt_confirmation_odoo]].
