---
name: project_slot_offer_hold_leak_fix
description: "Slot-offer stray-hold leak fix A (LIVE 2026-11-13): offer box frees the 48h hold on any real dismissal; a confirmed-today guard refuses offering on a job already scheduled today. Fix-B (reserve-at-send) is DEFERRED — its go/no-go trigger is the /owner/api/offers/leak_stats residual. Don't build B until that residual is material."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-11-13T08:25:13.688Z
---

**The leak (Greg 17457, Larry 17490):** `/api/offers/reserve` writes a 48h slot hold the instant DJ taps "📤 Send these N times", BEFORE the preview box opens. Originally only the box's "Don't send" button cleared it, so ANY other dismissal (backdrop tap, refresh, navigate, screen-sleep-then-abandon) left a live hold with no text sent → the slot sat blocked up to 48h.

**Fix A — LIVE 2026-11-13** (commits wsc_offerbox a429308d, slot_offers 32da54a0, ENDPOINT_MAP f4376ff3; Lead byte-QC, DJ-greenlit "both" with the auto-retry):
- `static/owner/wsc_offerbox.js`: ONE `abandon()` path frees the hold on backdrop-tap + "Don't send" + a TRUE page unload (`pagehide` with `persisted===false`, via `sendBeacon('/owner/api/offers/clear')`). **`visibilitychange` is deliberately NOT wired** — a screen-sleep/app-background is NOT abandonment (DJ glances away and returns to tap Send), so clearing on background would drop a hold he still intends to use (Lead req #3). Committing to Send nulls the `_active` tracker first, so a later unload can't free a sent hold.
- `routers/owner/slot_offers.py`: **confirmed-today guard** (`_so_scheduled_today`) on BOTH the reserve and record entry points — refuses floating NEW offer times onto an SO already on today's schedule (state∈sale/done + date_order's Pacific date == today); returns `{ok:false, guard:'scheduled_today'}`. Fail-open on any read error (never blocks a legit offer). `record_offer` + `/api/offers/send` are UNTOUCHED — guard is a pre-record early-return → stayed in the byte-QC lane (no Audit).

**★ Fix-B (reserve-at-send) is DEFERRED, NOT dropped.** B is the correct-by-construction fix (hold exists IFF an offer was sent) but changes a contract shared by Operator's /record path + the sms inbound reserve chain + the waiting surface + the overlay = real blast radius. A's residual = only a hard-kill mid-box (no unload event fires), backstopped by the 48h expiry. **The go/no-go trigger for B is DATA:** `GET /owner/api/offers/leak_stats` (owner-walled, read-only) returns `expired_unsent` = offers that reached 48h expiry while never-sent (the hard-kill leak signature). The counter reuses the EXACT `offer_sent:<id>` key the send path writes — so it's accurate. **How to apply: before anyone builds fix-B, check leak_stats. ~0 residual → B stays deferred; material residual → promote B.** Don't re-litigate A-vs-B or rebuild B blind.

Non-blocking fast-follow logged (not built): opening a new offer box while a prior is open-unsent orphans the prior hold (`_active` overwritten) — largely unreachable (box is a fullscreen overlay), caught by 48h + the leak counter; a "free prior hold when a box replaces an open one" tweak would close it.

Related: [[feedback_money_adjacent_staging_risk_calibrated]] (byte-QC-lane rationale), [[feedback_operator_followup_verify]].
