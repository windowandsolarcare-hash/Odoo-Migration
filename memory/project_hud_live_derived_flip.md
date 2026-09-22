---
name: project_hud_live_derived_flip
description: "The HUD was flipped (2026-09-22) from the stored feed (/api/feed/list) to live-derived (/api/feed/live_list). How the live aggregation, status-carryover, live badge, producer migration (Lane-A), and the DJ \"HUD-room\" card pattern (server-side access_code) work."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T16:06:47.303Z
---

**HUD realtime flip (2026-09-22).** Per HUD_REALTIME_BRIEF, the HUD is now a live PROJECTION, not a stored inbox. DJ's read points flipped from `/api/feed/list` → `/api/feed/live_list`; the FAB badge `/api/feed/badge` is live-derived. Revert = point the 4 refs back (v2_hud.html ×2, v2_needsyou_banner.js, badge to `len(list_items())`).

## feed.py mechanics (routers/owner/feed.py)
- `_assemble_live(include_done, include_snoozed)` — the shared view-time build: pass-through stored NON-live cards + each Lane-A producer's fresh card merged via `_merge_live_card`. **owned = fixed `feed_live.LIVE_IDS` ∪ {ids emitted this load}** — so DYNAMIC-id live cards (e.g. day-scoped `planner:meditate:<date>`) override their stored copy without double-listing; fixed LIVE_IDS auto-clear when a producer emits nothing. Used by both `/api/feed/live_list` and `/api/feed/badge` (badge == HUD set).
- `_merge_live_card(card, stored, now, include_done, include_snoozed)` — the FLIP PREREQ (foundation for KILL/PARK): a stored TERMINAL (done/approved/declined) SUPPRESSES the live card (no resurrection); SNOOZE holds until `snooze_until` passes. Terminal suppresses regardless of `created` (Lane-A producers stamp created=now(), so a created-reset would defeat it). "Condition cleared then RE-triggers → reappear" is DEFERRED to the heat/decay/KILL work (Lead 2026-09-22).
- `api_feed_ack` — now SYNTHESIZES a status holder for a live-only card id (from `feed_live.live_cards()`/`cheryl_cards()`) when no stored entry exists, so DJ's snooze/dismiss — and future KILL/PARK — PERSIST for cards that no longer have a pushed copy. (Was 404 before.)

## Producer migration (routers/owner/feed_live.py — Lane A)
- `LIVE_PRODUCERS` / `LIVE_IDS` registry. Migrated so far: `_inbox_queue`, `_holding_queue`, `_schedule_today` (F1 — reuses briefing._jobs_for_day, no nightly expiry), `_meditate`. A migrated producer's old push (e.g. briefing's schedule:today) can stay — live overrides/omits it — but the goal is to stop pushing derived cards.
- ★ `myday:overdue` is RETIRED (briefing.py deletes it; a pinned My Day card replaced it). The brief's audit predates that — do NOT resurrect it as a live producer.
- Remaining families (Lead's order): F2 library:new + sched_req unify + maint_advance:reschedule; F3 billing/reschedule (money); F4 reminders/maint_confirm (customer sends, LAST, with the Norman-Woodel confirm-collapse dedupe). Lane B stays push (paywatch/payroll/booking); Lane C stays expiry digests.

## ★ DJ "HUD-room" card pattern (governing, DJ 2026-09-22)
"HUD is DJ's single workspace" — every ROOM surfaces actionable Lane-A cards whose button calls the room's OWN endpoint. First instance = MEDITATE (`_meditate`): after 9pm PT, if the meditate habit isn't done today, a card with "✅ Done" → `POST /api/planner/checkin_hud`.
- **Server-side access_code:** the planner keys data by `personal.planner.<access_code>.*` where access_code = DJ's Render PIN (`hr.employee` id 1 `x_render_access_code`). A HUD card payload must NEVER carry the PIN. `/api/planner/checkin_hud` (planner.py — a UNIQUE path, so not shadowed by dashboard.py's `/api/planner/checkin`) derives the code SERVER-SIDE from emp 1, stamps today PT, writes history + `planner_checkin_to_myday`. The card sends only `{habit_id, status}`. Reuse this pattern for any future room card that needs DJ's planner identity. See [[project_thumbtack_capture_card_selfclear]], [[feedback_hud_cards_live_not_inbox]], [[feedback_never_relay_credential_via_session]].
