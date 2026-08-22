---
name: project_hud_realtime_redesign
description: "IN PROGRESS (phase-1 seam shipped 2026-08-12) — HUD → live projection (never-stale) instead of stored pushed-snapshot inbox. Plan in HUD_REALTIME_BRIEF.md. Joint w/ specialist session."
metadata: 
  node_type: memory
  type: project
  originSessionId: 23c6be5c-2f5a-4176-8708-315cee1b2909
  modified: 2026-08-12T07:31:09.408Z
---

DJ approved 2026-08-12: the HUD should be a **live dashboard, never stale** — cards dealt with should vanish on their own, not persist until manually marked done.

**Root cause (confirmed in feed.py):** the Attention Feed stores PUSHED snapshots in `ir.config_parameter wsc.feed.items`. A card is a frozen moment; it only leaves on manual done or when the producing module re-runs `delete_item()`. Handling something elsewhere (Workiz/Odoo/inbox) doesn't clear its card → stale.

**Agreed design:** HUD = a live PROJECTION. Two card families —
1. **Derived (condition) cards** computed at VIEW TIME via a new per-producer read-only `live_list()`; auto-clear when the condition is no longer true (nothing to mark done).
2. **Record-backed task/approval cards** (My Day `project.task`, approvals) reflect their record's live state.
Badge = live count. Refresh on open / app-resume / 20–30s poll (push for money+urgent is a LATER phase). "handled ✓" fade + "Cleared today" tuck-away on auto-clear. One batched build per load + ~5–10s server cache so Odoo (SaaS, rate-limited) isn't hammered — "never stale" = a few seconds behind.

**Scope:** 14 card producers push to the feed; ~10 are specialist-owned (reminders, scheduler, specialist_billing/booking/reschedule/paywatch/payroll/digest/morningnews, sms/messaging). feed.py + ATTENTION_FEED_CONTRACT are SHARED → **joint redesign, contract v2 adds `live_list()`.** Co-plan before ANY code (mail posted 2026-08-12).

**Phase 1 SHIPPED 2026-08-12 (non-breaking, parallel):** NEW `routers/owner/feed_live.py` (view-time `live_cards()` + `LIVE_PRODUCERS`/`LIVE_IDS` registry = the contract-v2 seam); feed.py added `GET /api/feed/live_list` (same shape as /api/feed/list, Lane-A cards recomputed fresh + auto-cleared; reads store, writes nothing). First 2 live cards: `inbox:queue` (sms._needs_reply_count), `holding:queue` (messaging.hold_count). Verified live: same 10 cards/order as /api/feed/list, EXCEPT live showed inbox=6 vs the stored HUD's stale 5 — i.e. it already caught the current HUD being one behind. HUD UI still on /api/feed/list; flip only after more Lane-A producers migrate + specialist signs off. NEXT: migrate remaining Lane-A producers' `live_list()` (billing/reminders/scheduler/reschedule/myday-overdue/schedule-today) — specialist-owned ones jointly; resolve the 2 overlaps (reminders:confirm≡maint_confirm, sched_req dual-source).

**Plan doc:** `3_Documentation/HUD_REALTIME_BRIEF.md` (rollout phases: audit → contract v2 → build aggregator beside store → migrate producers by family → flip badge/list live → fade+cleared-today+push). See [[project_hud_feed_ordering.md]].
