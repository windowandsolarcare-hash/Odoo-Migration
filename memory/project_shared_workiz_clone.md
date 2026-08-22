---
name: project_shared_workiz_clone
description: "Canonical shared Workiz job-cloner (build_clone_payload + /api/workiz/clone_job) unifying Phase 5, reactivation, and duplicate. Stage status + per-phase differences."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

Phase 5 (maintenance), Phase 2 (reactivation graveyard), and Duplicate all create a new Workiz job from a prior job and had drifted copies of the same ~20-field payload. DJ approved unifying behind ONE canonical builder so fields update in one place (2026-06-14).

**THEY RUN IN 3 RUNTIMES** (can't share a Python import): Phase 5 = Zapier (`zapier_phase5_FLATTENED_FINAL.py`), Reactivation = Odoo **server action 563** (no imports), Duplicate = Render app `dashboard.py`. Unification = one shared builder all three call.

## ⭐ FINAL STATE 2026-06-14: CANONICAL BUILDER MOVED TO ODOO (always-up, not flaky Render)
DJ's point: Render goes down too often; Odoo is always up. So the one true builder is now an **Odoo server action "WORKIZ_CLONE" = SA id 1338** (model 670). File `1_Production_Code/odoo_sa_workiz_clone.py`. It reads context params (`clone_source` dict | `clone_source_uuid`; `clone_job_type`; `clone_job_datetime` None=unscheduled; `clone_job_source`; `clone_line_items`; `clone_tos_default`; `clone_extra` dict), builds the canonical payload, GETs source from Workiz if uuid, creates the job, and **returns `{ok, workiz_uuid, workiz_link, create_status, payload}` via `action = {...}`** (run() returns it — VERIFIED works via RPC AND in-process). 
**All 3 callers now use SA 1338:**
- Duplicate (dashboard.py `api_duplicate_job`): `odoo_rpc('ir.actions.server','run',[[1338]],{'context':{clone_*}})` → reads `workiz_uuid`.
- Phase 5 (zapier_phase5 `create_next_maintenance_job`): same via its `odoo_rpc` helper (JSON-RPC to Odoo), retry 3× kept.
- Reactivation SA 563: **in-process** `env['ir.actions.server'].browse(1338).with_context(**clone_ctx).run()` — NO HTTP, no Render. 2-attempt retry.
**Render is OUT of the Phase 5 + reactivation create path.** Reliability = Odoo + Workiz (both always-up). To clone a Workiz job from anywhere: call SA 1338.
**DORMANT RENDER COPY REMOVED 2026-06-14** (commit dashboard 26f39855, phase5 71ead5a; Render deploy dep-…rdm0 live): deleted Render `dashboard.build_clone_payload` (was ~line 281) + `POST /owner/api/workiz/clone_job` endpoint, and Phase5's dead `RENDER_CLONE_URL`/`RENDER_CLONE_TOKEN` constants + stale "shared Render cloner" comment. Canonical builder is ONLY Odoo SA 1338 now — edit fields there. (The LIVE Duplicate context dict in dashboard `api_duplicate_job` uses keys `clone_source`/`clone_job_type`/… → SA 1338; that stayed, do not confuse it with the removed builder.)

**STAGE 1 DONE + TESTED (2026-06-14, commit f73a2105):**
- `build_clone_payload(source, job_type, job_datetime, job_source, line_items, tos_default, extra)` in `routers/owner/dashboard.py` (right after `workiz_post`) = SINGLE SOURCE OF TRUTH for the field set.
- Endpoint `POST /owner/api/workiz/clone_job` (token `wsc-daily-sync-2026`): body {source_uuid|source, job_type?, job_datetime?(None=unscheduled), job_source?, line_items?, tos_default?, extra?, substatus?} → builds payload → workiz_post create → returns {ok, workiz_uuid, workiz_link, payload}. External callers (Phase 5 Zapier, server action 563) will POST here.
- **Duplicate (`api_duplicate_job`) now uses `build_clone_payload`** (gate-snapshot fallback injected into source first; ClientId/Phone passed via extra). Verified end-to-end: created+deleted a real test job; payload correct.

**STANDARDIZED across all (DJ approved):** Country='US' always; JobSource source-or-'Referral'; carry `alternating` + `Email`; `frequency` default 'Unknown'. `type_of_service_2` default stays per-phase via `tos_default` ('Maintenance' Phase 5, else 'On Request').

**KEEP-AS-PARAM per-phase differences (by design):** JobType (P5 derives next maint type; reactivation='Reactivation Lead' flag set real at booking; duplicate=picked/source); JobDateTime (P5 calculated, reactivation None until booked, duplicate picked); next_job_line_items content (P5 'AUTO-SCHEDULED…'+prev UUID; reactivation SMS prices; duplicate source items); reactivation-only `information_to_remember` (pass via extra).

**STAGE 2 DONE (2026-06-14, commit 6e9523f):** Phase 5 `create_next_maintenance_job` (zapier_phase5_FLATTENED_FINAL.py) now POSTs to RENDER_CLONE_URL (`https://wsc-field-assistant.onrender.com/owner/api/workiz/clone_job`, token RENDER_CLONE_TOKEN='wsc-daily-sync-2026') with source=completed_job_data, job_type=get_next_job_type, job_datetime=scheduled, tos_default='Maintenance', line_items=AUTO-SCHEDULED ref, extra={ServiceArea via _service_area_for_job, SecondPhone}. Removed its own ~100-line payload+POST. Caller unchanged (uses {success,new_job_uuid}); find_new_job_uuid_after_create was already dead.

**STAGE 3 DONE (2026-06-14):** reactivation server action **563** graveyard create now POSTs to RENDER_CLONE_URL with source=historical_job, job_type='Reactivation Lead', NO job_datetime (unscheduled), tos_default='On Request', line_items=actual_prices_sent, extra={ClientId, Phone=phone_clean, PostalCode=postal_clean, ServiceArea, information_to_remember, last_date_cleaned}. UUID extraction now reads `create_result.get('workiz_uuid')`. Live 563 patched + GitHub `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` synced to the live code (two-step done). Downstream SMS-trigger/status logic unchanged.

**RETRIES (2026-06-14, DJ flagged Render goes down often):** both callers now retry the endpoint 3× with backoff before failing. Phase 5: `time.sleep(attempt*6)` (6s,12s); stops early on a real validation error (only retries 502/timeout/conn). SA 563: busy-wait backoff (`while datetime.now()-ws < 4*(attempt+1)`) since server actions have no `time.sleep`; guards create_response=None after all-fail; fail message says "re-run reactivation (Render may have been down)". Covers brief Render outages (deploy switchovers / transient 502s = seconds). RESIDUAL RISK: a multi-minute Render outage during a Phase 5 trigger still fails (Phase 5 is automated, no auto-re-fire — reactivation is manual so DJ re-launches). Options if needed: investigate Render uptime root causes ([[project_render_502_uptime_fixes]], [[project_render_deploy_failed_check]], [[project_render_python_pin_incident]]) or add a direct-Workiz fallback to Phase 5 (reintroduces a duplicated payload for the fallback path only).

**VALIDATED:** both call-shapes tested end-to-end against the live endpoint (create+delete) — Phase 5 shape (date + ServiceArea override) and reactivation shape (Reactivation Lead, no JobDateTime, info_to_remember) both create correct jobs. UNIFICATION COMPLETE — Workiz clone fields now update in ONE place (build_clone_payload). Caveat: Phase 5 + reactivation now depend on the Render endpoint being up.
