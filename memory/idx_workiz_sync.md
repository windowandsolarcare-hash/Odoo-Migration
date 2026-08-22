# Workiz / phases / sync — memory index

- [project_workiz_lineitem_descriptions_not_migrated.md](project_workiz_lineitem_descriptions_not_migrated.md) — Workiz per-LINE-ITEM Descriptions did NOT migrate to Odoo (SO lines = product name + price only). RECOVERABLE from full export `4_Reference_Data/Workiz_Final_Export_2026-08-02/workiz_all_jobs_2026-08-02.json` (3,860 jobs, LineItems[].Description). Match SerialId↔SO name. Backfill viable, proposed not run.

- [project_workiz_status_field_survived_retirement.md](project_workiz_status_field_survived_retirement.md) — x_studio_x_studio_workiz_status is STILL live post-retirement (Odoo-native, legacy name) — verified 22/23 SOs since 8/03. Don't rip it out. 'Service happened'=Done ≠ 'paid in full'.

- [project_shared_payment_closeout.md](project_shared_payment_closeout.md) — Shared finalize_payment() (Done + next visit + funds-received thank-you). ★ CARD/Stripe was BROKEN: _stripe_phase6_sync undefined → card never closes out. Dormant fn pushed; co-plan wiring w/ lead. 2026-08-14.

- [project_one_month_frequency.md](project_one_month_frequency.md) — "1 Month" now a valid maint frequency (monthly customers). Added to SO selection (field 15538) + 2 hardcoded UI dropdowns (brain/dashboard); v2_new_job already had it. res.partner freq=char. Next-date math handles any "N Month". Norman switched. 2026-08-13.

- [project_paywatch_auto_tip.md](project_paywatch_auto_tip.md) — PayWatch card auto-handles tips: overage over job total → Approve adds a "Tip" line (WSC-TIP product) so invoice matches exactly, records, marks Done, creates next maint visit. Split shown on card face. Also clears stale zelle_engaged card. Verified Norman SO 004652 ($250=$220+$30). 2026-08-13.

- [project_hud_approve_false_failure_slow_op.md](project_hud_approve_false_failure_slow_op.md) — HUD approve cards falsely showed "Launch failed — nothing sent" on heavy/slow ops (paywatch record ~20s > 30s timeout) that actually SUCCEEDED. Fixed v2_hud.html doApprove: null≠fail, _cardCleared re-check (idempotent approvals delete own card on success), 45s. Also cleaned paywatch card wording (no Workiz). 2026-08-06.

- [project_mark_done_refuses_workiz_uuid.md](project_mark_done_refuses_workiz_uuid.md) — ★ RESOLVED 2026-08-06: customer job = Done only when PAID IN FULL. _execute_payment now, on full payment, marks Done + rolls up snapshot + spawns next maintenance visit (works regardless of Workiz UUID). set_block_status = Personal Time green-dot only (no next-job). mark_job_done AI tool still pokes dead Workiz (untouched). _sync_so_with_workiz gate left in (flagged to lead).
- [project_pending_catchup_paid_undone_sweep.md](project_pending_catchup_paid_undone_sweep.md) — DEFERRED one-time sweep: already-fully-paid but still-un-Done jobs need Done + next-visit. Surface when DJ asks "what's next"; review list before running; don't run unprompted. 2026-08-06.

- [project_daily_sync_shadow_reverting_odoo.md](project_daily_sync_shadow_reverting_odoo.md) — ★ Overnight "WSC Daily Sync" (Render cron /api/cron/daily_sync, 4am) was reverting DJ's Odoo edits from Workiz (reverted John 004557 date+pricing) — NOT Zapier. cron.py paused 8-3 but dashboard.py SHADOWS it; paused dashboard.py copy (sos=[]) 8-6. Lesson: dashboard.py shadows cron.py routes.

- [project_duplicate_job_odoo_native.md](project_duplicate_job_odoo_native.md) — Customer Brain "Duplicate job" now ODOO-NATIVE (was Workiz/clipboard, dead): clones SO w/ line items+gate+service, two buttons Submitted-draft vs Confirm-onto-schedule. NOTE: new Odoo SOs get S00xxx names not 6-digit.

- [project_workiz_final_export.md](project_workiz_final_export.md) — ★ Final full Workiz export 2026-08-02 (3860 jobs 2019→2027, local + GitHub). HOW to bulk-pull job/all: offset=PAGE-INDEX (0,1,2 not skip-count), records max 100, start_date or defaults to 14d, has_more to page, UA header required. 1272 open = exact match, complete.

- [project_workiz_get_needs_user_agent.md](project_workiz_get_needs_user_agent.md) — Workiz GET → HTTP 403 from bare urllib = MISSING User-Agent, not a bad token. Send `User-Agent: Mozilla/5.0`. Codes: 403=no UA, 429=rate limit, 204/404=job deleted.

- [project_calendly_offzapier_odoo_webhook.md](project_calendly_offzapier_odoo_webhook.md) — SUPERSEDED by self-hosting (kept for reference). Built capture webhook SA 1340/automation 8//web/hook/d319ad6f (dormant now).
- [project_clock_system_rebuild.md](project_clock_system_rebuild.md) — READ FIRST before any clock code. Offline-first clock spec + 4 confirmed bugs (home arrival only clocks out DJ not crew;
- [project_customer_analytics_datamodel.md](project_customer_analytics_datamodel.md) — Customer Analytics app (LIVE 2026-06-11): /owner/analytics, own file analytics.py+html.
- [project_customer_jobs_status_selfheal.md](project_customer_jobs_status_selfheal.md) — customer_jobs (dashboard.py) now SELF-HEALS stale Workiz status on OLD non-terminal jobs: the daily sync's −7/+90 window never revisits them, so…
- [project_daily_sync_date_window_excludes_old.md](project_daily_sync_date_window_excludes_old.md) — Daily Workiz sync cron only sweeps date_order −7/+90 days (+ invoice_status='to invoice', not Done), so OLD past-dated Submitted jobs never sync…
- [project_daily_sync_monitor.md](project_daily_sync_monitor.md) — CHECK BEFORE RECREATING. Call daily_sync_log endpoint, read created_at — if < 5 days skip.
- [project_date_order_is_start_time.md](project_date_order_is_start_time.md) — SO date_order ALWAYS = Workiz JobDateTime (start time) in UTC.
- [project_delete_job_paired.md](project_delete_job_paired.md) — Safe job delete (invoice-guard → tasks → cancel→unlink SO → Workiz delete LAST) lives in TWO synced places: field.py delete_workiz_job tool +…
- [project_future_overnight_sync_phase4.md](project_future_overnight_sync_phase4.md) — FUTURE TASK: switch overnight _run_daily_sync to call action 955 via _phase4_full_sync() for unified sync including tasks.
- [project_missing_invoice_audit.md](project_missing_invoice_audit.md) — 2026-06-04: 73 missing invoices created+paid (2020–2024).
- [project_next_job_link.md](project_next_job_link.md) — Phase 5 writes the NEXT maintenance job's Workiz URL (app.workiz.com/root/job/{uuid}/1) onto the COMPLETED job's INVOICE…
- [project_phase4_task_reentry_bug.md](project_phase4_task_reentry_bug.md) — Phase 4/sync_action_955 bug: task deleted on Workiz status exit from Scheduled, not recreated on return.
- [project_phase4a_sync.md](project_phase4a_sync.md) — READ when extending payment flow or Workiz sync. 2026-05-01: Phase 4A pre-payment sync helper _sync_so_lines() auto-called by…
- [project_phase5_activity_flow.md](project_phase5_activity_flow.md) — READ when editing Phase 3 activity creation, Phase 4 confirm, or activities.html.
- [project_phase6_tech_gate.md](project_phase6_tech_gate.md) — Phase 6 checks SO workiz_tech field before any action. No tech = blocks entire run with clear error.
- [project_phase_flowcharts.md](project_phase_flowcharts.md) — 2026-04-24: Phase 3/4/5 SVG+PNG flowcharts (3200px mobile-readable) with narrative, routing logic, date_order=JobDateTime (start time always)…
- [project_preselect_coverage_check.md](project_preselect_coverage_check.md) — PENDING: when accounting migration phase 4-5 lands, run coverage check on field-assistant payment preselect.
- [project_property_partner_naming_quirk.md](project_property_partner_naming_quirk.md) — READ when finding all of a customer's records. Property partners may be named "Customer, address" OR just "address".
- [project_property_rollup_on_sync.md](project_property_rollup_on_sync.md) — SA 955 (field 🔄 Sync) now ROLLS UP gate/pricing/frequency/type-of-service to the Property master ONLY when the synced job is the property's…
- [project_shared_workiz_clone.md](project_shared_workiz_clone.md) — DONE: canonical Workiz job-cloner = Odoo server action WORKIZ_CLONE (SA 1338, always-up — moved off flaky Render).
- [project_task_deletion_stage_filter.md](project_task_deletion_stage_filter.md) — Only delete tasks in New(16)/Planned(17) on Submitted — protect In Progress(18)/Done(19).
- [project_workiz_api_access.md](project_workiz_api_access.md) — Workiz API blocks local machine (403). Must proxy through Odoo temp server action.
- [project_workiz_canceled_is_status.md](project_workiz_canceled_is_status.md) — To cancel a Workiz job set top-level Status='Canceled' (NOT SubStatus='Canceled' → HTTP 400).
- [project_workiz_chat_export_to_odoo.md](project_workiz_chat_export_to_odoo.md) — Workiz per-customer SMS export → Odoo importer. BULK DONE 2026-06-25: 832 files → 441 customers imported (+5 = 446 total), 8 ambiguous…
- [project_workiz_delete_job_api.md](project_workiz_delete_job_api.md) — Workiz jobs CAN be hard-deleted via API: POST api.workiz.com/job/delete/{UUID}/ with {"ID": "UUID"} in body.
- [project_workiz_end_before_start_400.md](project_workiz_end_before_start_400.md) — Workiz job-create returns HTTP 400 when JobEndDateTime <= JobDateTime (end at/before start).
- [project_workiz_job_all_quirk.md](project_workiz_job_all_quirk.md) — Workiz job/all/ endpoint skips unscheduled jobs. Use job/get/{UUID}/ directly.
- [project_workiz_jobs_not_in_odoo.md](project_workiz_jobs_not_in_odoo.md) — When listing/auditing a customer's jobs, search BOTH Odoo AND Workiz — Re-engagement/Reactivation Lead jobs can be Workiz-ONLY (no sale.order…
- [project_workiz_scheduling_quirk.md](project_workiz_scheduling_quirk.md) — Workiz may need Submitted status first before Send Confirmation - Text works after Calendly booking;
- [project_workiz_substatus_needs_status.md](project_workiz_substatus_needs_status.md) — Workiz API quirk: setting SubStatus requires parent Status="Pending" in same body.
- [project_workiz_type_of_service_2.md](project_workiz_type_of_service_2.md) — Workiz API field is type_of_service_2 (NOT type_of_service) — wrong name causes Phase 5 to create activities instead of jobs
- [project_workiz_update_needs_uuid_in_body.md](project_workiz_update_needs_uuid_in_body.md) — Workiz API quirk: job/update/ needs "UUID" in body, job/delete/ needs "ID" in body.
- [session_apr27_summary.md](session_apr27_summary.md) — 2026-04-27 big session: Activities page + Follow-Up flow + odoo_write auto-cancel + Phase 3 filter extension + 85+ SO cleanup + payment-aware…
- [session_may22_summary.md](session_may22_summary.md) — 2026-05-22: delete_workiz_job 3-path tool, /api/search_so live SO search, commands page 2 delete cards, SO format fix, CLAUDE.md rules rewrite…
- [session_may28_summary.md](session_may28_summary.md) — 2026-05-28: task sync disabled (Phase 3+4), Phase 5 reminder activities (Follow-up type 15), ql_panel calculator, note sharing, pre-deposit…
- [project_phase4_missing_task_backfill.md](project_phase4_missing_task_backfill.md) — Phase 4 skips task sync when a confirmed SO has 0 tasks — needs a backfill path to create tasks directly via API.
- [project_workiz_jobtype_valid_values.md](project_workiz_jobtype_valid_values.md) — Valid Workiz JobType values must match EXACTLY or Workiz 400s. "Window Cleaning" is NOT valid (old field.py default → job-create failures).
- [project_workiz_tech_not_api_settable.md](project_workiz_tech_not_api_settable.md) — Workiz tech/Team assignment CANNOT be set via the Workiz API (DJ 2026-06-09) — must be done in the Workiz UI. Affects schedule-a-job automation.
- [project_workiz_retirement.md](project_workiz_retirement.md) — ★ NEXT BIG PROJECT: Workiz RETIRED — remove every Workiz API call, Odoo = single source of truth. DISCUSS each touchpoint first; inventory + 7 roles + approach in file.
- [project_appt_confirmation_odoo.md](project_appt_confirmation_odoo.md) — Odoo-native appt CONFIRMATION text (replaces Workiz status hand-off). scheduler.py confirm_preview+send_confirm (preview-gated, messaging.send); field.html apptConfirm(). ~15 Workiz pts still in field.html.
