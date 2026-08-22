---
name: project_reschedule_specialist
description: "Fourth AI specialist LIVE 2026-07-26: routers/owner/specialist_reschedule.py = Reschedule HUD. Shows ONLY jobs DJ tapped 'Reschedule' on in billing (wsc.billing.skipped.* marks), NOT the auto CC Skipped list (DJ chose option 2 — one job in one place). ONE attention card -> /api/reschedule/review page with the smart best-day picker inline (reuses so-suggest + WSCDayPlan)."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-27T04:23:01.006Z
---

**2026-07-26 — fourth specialist.** DJ: "build me a hud for rescheduled which carries with it the scheduling logic... reuse, again 1 hud card that opens to all the jobs." `routers/owner/specialist_reschedule.py`, registered main.py prefix /owner, cron hook in cron.py `_run_daily_sync` (guarded, alongside payroll/digest/billing).

**Source = explicit marks, NOT auto-detection (DJ chose option 2).** `detect_skipped()` reads `wsc.billing.skipped.<so_id>` marks (written by billing's "Reschedule later" — [[project_billing_specialist]]), NOT the CC `_isSkipped` auto-list. Rationale DJ agreed: keep every past-not-done job in ONE place — it stays on the billing collect card (where he triages bill-vs-skip) until he taps Reschedule, then billing drops it and it appears here. So billing = the triage; reschedule = only what he decided to reschedule. (The CC Command-Center Skipped bucket still auto-shows everything independently — that's the browse-all screen; this HUD card is the curated action queue.) A job falls off `detect_skipped` once rescheduled forward (date_order >= today), Done/Canceled, or paid.

**Endpoints (my lane):** `GET /api/reschedule/candidates` (READ-ONLY JSON — the eyeball-first deliverable; verified 3 jobs = Jim Hitt/Marie White/Donna Parrish, $395, matching exactly the 3 DJ marked). `GET /api/reschedule/review` = the page: lists each marked job, "📅 Pick the best day" opens a shared reschedule sheet (ONE WSCDayPlan instance at a time), "↩ Not a skip" clears the mark → job returns to billing. `POST /api/reschedule/clear {so_id}` (used by both reschedule-success and Not-a-skip — clears `wsc.billing.skipped.<so_id>`). `POST /api/reschedule/sweep` (manual). `run_sweep()`/`run_daily_trigger()` submit/refresh ONE `reschedule:review` attention card.

**Smart picker REUSE (no rebuild):** the sheet embeds Leaflet + `/static/owner/route_map.js` (self-injects its CSS; exports WSCDayPlan/WSCMiniCal/WSCTime/WSCRouteMap). Copies field.html's job-rs-* markup + jobRsLoadSuggest/jobRsPick/jobRsRenderDay/submitJobRs, adapted: fetches `GET /api/scheduler/so-suggest?so_id=` for route-tight day chips + coords, renders `WSCDayPlan.render({date,lat,lon,name,timeInputId:'job-rs-time',ids:{...}})`, saves via `POST /api/schedule/reschedule {so_id,date,time}` (Workiz day/time, Phase 4 syncs — [[project_cc_reschedule_via_workiz]]). **KEY difference from field.html:** a skipped job defaults to the soonest route-tight suggestion (move FORWARD), not its old past date. Verified live: Jim Hitt → "Tue Jul 28 12:30 PM 0.3mi" best chip + calendar rendered.

**LIVE + card fired** ("Reschedule 3 jobs — put them back on the calendar"). Touched shared files: main.py + cron.py (additive/guarded). See [[project_billing_specialist]] (the skip marks come from there), [[project_cc_reschedule_best_slot]], [[project_operating_system_vision]], [[feedback_reuse_canonical_endpoint]].
