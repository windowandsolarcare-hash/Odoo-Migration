# Scheduling & Command Center — memory index

- [project_gcal_event_deeplink.md](project_gcal_event_deeplink.md) — Calendar "Open in GCal": Google iCal export leaves URL empty for normal events → build link yourself: event?eid=base64url('<eventId> <calendarId>'), eventId=UID minus @google.com, calendarId from feed /ical/<id>/. Also unescape iCal \, \; \n. dashboard.py /api/gcal_events (NOT calendar.py). Commit d8df08f.

- [project_lessons_referral_scheduling.md](project_lessons_referral_scheduling.md) — Jim/Robert + Linnea took too many iterations: front-load the customer's constraints (read thread + ONE clarifying Q) BEFORE booking (don't book-then-rebook); search line-item DESCRIPTIONS for past add-ons (Linnea's 3 lights hid under "Mirrors Cleaned"); verify weekdays with a date calc; run the whole referral play in ONE pass; calibrate pitch/slots with DJ up front.

- [project_two_night_before_reminder_tracks.md](project_two_night_before_reminder_tracks.md) — reminders.py has TWO night-before builders (plain eve + maintenance eve); the maint one (gated on advance ok/sent, honors backfilled ok) can surface instead & drop regular confirmed jobs (Gayle-not-Fred). Editable per-person; can send per-SO.

- [project_offer_link_resolver.md](project_offer_link_resolver.md) — Slot-offer customer booking-link half (Lead 2026-08-17): make_token carries offer_id; /book/api/offer/{get,book,decline} in booking.py. Token secret server-side → Reserve mints link via booking.make_token. Customer /book/c page render still TODO.

- [project_slot_offers_reserve_design.md](project_slot_offers_reserve_design.md) — ★ DJ's LOCKED design for pending offers (don't offer a slot twice): Reserve BUTTON bolted onto the existing shared scheduling picker (not a new screen) + booking link, 3 editable slots (manual override wins, conflict=soft warn), 48h expiry, NO AI text parsing. slot_offers.py store. Not built — contract pending lead. 2026-08-15.

- [project_slot_finder_gaps.md](project_slot_finder_gaps.md) — 3 slot gaps (2026-08-15): AI drafter (open_days_for_partner, day-level) ≠ reschedule modal (_find_scheduling_openings, route-optimized) on TIME; no offered-slot tracking → double-offer; finder ignores x_job_length_min (fixed 90 min). Brief: SCHEDULING_OFFERS_BRIEF.md.

- [project_hud_optimistic_approve.md](project_hud_optimistic_approve.md) — HUD Approve now OPTIMISTIC (v2_hud.html doApprove): clears card instantly, runs 30s+ work in bg, restores only on definitive failure; feed refresh = safety net. Applies to all approval cards. 2026-08-13.

- [project_send_acknowledgement_button.md](project_send_acknowledgement_button.md) — v2_field.html "📩 Send acknowledgement" button sends Stage-0 maint heads-up (branded calendar / I'll-be-there page) per job. Reuses /api/maint/advance/send (now supports send:false preview + edited message) + send_maint_advance(body=). Distinct from Send confirmation. 2026-08-11.

- [project_command_conf_pills_cached.md](project_command_conf_pills_cached.md) — Command Center CONFIRMED/Accepted/Ack pills were blank 7-10s on every login (in-memory _CONF/_SCHED/_ACK reset on load; jobs render cache-first). Now cached in localStorage wsc_cc_states + hydrated synchronously → pills instant on login. v2_command.html only. 2026-08-11.

- [project_status_scheduled_now_confirms.md](project_status_scheduled_now_confirms.md) — Setting job Status → on-schedule state (Scheduled/Send Confirmation/Next Appt) now auto-confirms the SO (draft→sale) in brain.py /api/brain/job, so it appears on the schedule. Create-from-scratch = draft by design; duplicate "Create & Schedule" = confirmed. Fixes invisible Scheduled drafts (Van). 2026-08-11.

- [project_maint_stacked_message.md](project_maint_stacked_message.md) — Maint heads-up rebuilt to DJ's STACKED format (When/Service/Where/Tech) + "confirm it works" CTA (dropped "nothing you need to do"). reminders.py MAINT_TEMPLATE + _maint_row (adds service/where/time); calfeed.py /appt page = 2-col facts, one screen, kept calendar/confirm/reschedule/cancel. Live 2026-08-07.

- [project_hud_denoise.md](project_hud_denoise.md) — HUD too noisy (DJ 2026-08-07): FAB badge=70 because it SUMS inner item.badge across cards (should = COUNT OF CARDS ~8); customer texts duplicated across 19 inbox_ai HUD cards + Follow-ups → live in INBOX only (one capture); clear-once-clears-everywhere. Speced to specialist (feed.py/inbox_ai).

- [project_maint_ack_backfill.md](project_maint_ack_backfill.md) — One-time maint ✓Acknowledged backfill (2026-08-08): tie the "ok" to the heads-up naming THAT job's exact date + non-Done (NOT any "ok" in the thread — 54 loose→13 correct; old histories have years of heads-ups). Set wsc.maint.advance.<so> state=ok. Auto going forward.
- [project_request_confirm_flow.md](project_request_confirm_flow.md) — AGREED 3-state customer-request→confirm flow (DJ 2026-08-07): REQUESTED="we'll confirm the exact time" (never "all set"; ctx bug shows all-set for requested) → DJ Accepts+sets time+presses "Launch Confirmation" (explicit) → CONFIRMED="You're all set". Customer picks morning/afternoon only. +fixes: kill exact-time picker, 1-tap Accept-his-day, 📍in-your-area pin. Speced to specialist, not coded.

- [project_auto_confirm_branded_page.md](project_auto_confirm_branded_page.md) — Daily auto-confirm (4-day batch + maint Stage 1) now texts the branded self-confirm page (?c=1 "Yes I'll be there"), not "reply YES". reminders.py _confirm_page_body. CONFIRM_KEY=wsc.reminders.confirmed is the unified flag; _maint_confirmed_batch now honors it too. Still approval-gated. 2026-08-06.

- [project_sched_page_window_and_fit.md](project_sched_page_window_and_fit.md) — Customer confirm/reschedule page: "pick my own day" = Morning/Afternoon/No-pref WINDOW (no exact time; DJ sets by route), sends window not clock; day list shows 📍in-your-area/available via _open_dates_for_city fit; requested-day HUD approve books + auto-confirms. 2026-08-07.
- [project_wsc_sendbox_shared.md](project_wsc_sendbox_shared.md) — wsc_sendbox.js = shared send-box widget WSCSendBox.open({so_id,mode}) (branded preview + ✨AI tailor + sched/launch). Wired into specialist_reschedule (GAP#2 fixed). TODO: repoint v2_field _openSendBox; lead wires HUD cards. 2026-08-07.
- [project_sched_lifecycle_one_page.md](project_sched_lifecycle_one_page.md) — ONE branded page for schedule AND confirm (?c=1 flavor, all 3 options both ways). Confirmed flag = wsc.reminders.confirmed.<so>; page-book+YES set it, reschedule clears it. v2_field: plain confirm btn RETIRED, reschedule >14d→schedule / ≤14d→confirm; ✓Confirmed banner+badge. sched/launch mode param; sched/states returns confirmed[]. 2026-08-06.

- [project_day_off_capacity_block.md](project_day_off_capacity_block.md) — Day off (Work Hours = wsc.capacity.overrides[date]=0) now blocks CUSTOMER availability via shared.is_day_off, gated in scheduler.build_day_plan + booking._open_dates_for_city. 3 dup paths (field/dashboard find_next_opening, new_job suggest-dates) still to guard. NOTE: shared.py __all__ gates import *.

- [project_two_quote_pages_two_launchers.md](project_two_quote_pages_two_launchers.md) — TWO quote pages: OLD quote.html (/owner/quote, ql_panel single-column launcher) vs CURRENT v2_quote.html (opened by v2 WSCLauncher ★Favorites/All). DJ uses v2_quote.html — edit THAT. 2026-07-30.

- [project_quote_rates_editable.md](project_quote_rates_editable.md) — Quote per-pane/slider prices now DJ-editable at /owner/quote-rates (table + last-changed date). Saved as ir.config_parameter 'quote.rates.override' merged over QUOTE_RATES/QUOTE_DIFFICULTY defaults via _get_quote_config() in dashboard.py; calculator reads effective config instantly. 2026-07-30.

- [project_new_job_reuse_vs_duplicate.md](project_new_job_reuse_vs_duplicate.md) — v2_new_job "Previous jobs": button renamed to "Duplicate this" (always clones a new job); not-done/not-scheduled jobs also get "Use this job" (opens existing Workiz link). recent-jobs now includes draft/sent Submitted + returns workiz_status/link. 2026-07-29.

- [project_goal_task_reorder.md](project_goal_task_reorder.md) — Goal tasks reorder with ▲▼ like milestones (project.task sequence + /task/reorder); changing a task's date auto-re-sorts that milestone's tasks by date. 2026-07-26.

- [project_fixed_sheet_offscreen_headglow.md](project_fixed_sheet_offscreen_headglow.md) — Fixed bottom-sheet's right edge (✕/strip/pills) off-screen on phone = PAGE horizontal overflow (.head-glow right:-40px) widens mobile layout viewport under the fixed sheet. Fix: overflow-x:clip on html+body. NOT the sheet's own width. Swept to all 41 v2 pages. 2026-07-25.
- [project_calendar_day_ondemand_load.md](project_calendar_day_ondemand_load.md) — Calendar day-sheet showed "No jobs scheduled" (while Capacity showed jobs) when roaming strip/arrows to a day outside the loaded month — calData is month-only. Fix: openDay loads that day's jobs+gcal on demand via ?start=&end=, stale-guard. 2026-07-25.
- [project_calendar_daysheet_snooze.md](project_calendar_daysheet_snooze.md) — Calendar day-sheet My Day rows get a ⏰ move menu: Quick (Tom/+3/week), capacity-aware "Days with room" (reuses /api/goals/next_slots, shows free hrs/day), Pick-a-date. Moves via existing /api/myday snooze+bulk-date. No new backend. 2026-07-25. (Now via shared WSCSnooze — see below.)
- [project_wscsnooze_shared_module.md](project_wscsnooze_shared_module.md) — WSCSnooze (static/owner/v2_snooze.js) = the ONE shared capacity-aware "move a My Day task" menu. Used by v2_myday, v2_calendar, v2_activities (each old snooze logic removed). Include the script + call WSCSnooze.open. NOT for job/block/lead snoozes. 2026-07-25.

- [project_capacity_overview_screen.md](project_capacity_overview_screen.md) — "See the full picture" (My Day cap strip) now opens v2_capacity.html: weeks jobs/todos/goals vs work hours + tap week for day-by-day (goals.py /api/goals/days). Also fixed Journal smart-back (reclaim from v2_apps WSCBack). 2026-07-25.

- [project_personal_time_capacity.md](project_personal_time_capacity.md) — Personal Time blocks counted as 0h in ALL capacity math (doctor's appt didn't reduce free time). Fixed: add_block/move_block store x_job_length_min (default 60m) + v2_field "How long" picker → _job_minutes counts it everywhere. 2026-07-24.

- [project_google_places_location.md](project_google_places_location.md) — Add-to-schedule Location field: Google Places autocomplete (address OR business name). Key in Render GOOGLE_PLACES_KEY, server-proxied via /api/places/suggest+details. MUST use NEW Places API (legacy not enabled).

- [project_duplicate_and_reschedule_fixes.md](project_duplicate_and_reschedule_fixes.md) — Shared scheduler = WSCDayPlan (route_map.js), reuse don't rebuild. Fixed: Brain Duplicate copies line items (return _li_text), Reschedule defaults to current scheduled date (so-suggest current_date). OPEN: per-date job-count badges on date picker.

- [project_cc_overdue_and_snooze.md](project_cc_overdue_and_snooze.md) — CC "Overdue — schedule now" = Submitted next-jobs past target date (1yr window), not snoozed/DNC. NEW 🔕 Not ready snooze on field 3-dot menu → /api/schedule/snooze writes x_snooze_until on partner+PARENT (filter reads parent-preferring _cust). 2026-07-11.

- [project_bank_feed_qb_double_booking.md](project_bank_feed_qb_double_booking.md) — Detailed execution log of the bank/income/expense de-dup cleanup.
- [project_booking_detail_preserved.md](project_booking_detail_preserved.md) — Online booking APPROVE now keeps the full customer request (notes/pref/requested-date) in the approved log + posts it to the customer chatter…
- [project_calendar_photo_viewer.md](project_calendar_photo_viewer.md) — Schedule Calendar photo lightbox (calendar.html openHistLb/#hist-lightbox): ✕ lowered 16→52px to clear the 36px clock-in bar;
- [project_calendar_search.md](project_calendar_search.md) — Schedule Calendar job search box (customer/address/SO# → tap opens job detail via goToField).
- [project_calendly_booking_alert.md](project_calendly_booking_alert.md) — Calendly online booking handler = zapier_calendly_booking_FLATTENED_FINAL.py (Odoo-Migration, push=deploy).
- [project_cc_reschedule_best_slot.md](project_cc_reschedule_best_slot.md) — CC Reschedule sheet now SUGGESTS the route-tightest soonest day/time + draws the day route/slots (override-able), REUSING the shared scheduler…
- [project_cc_reschedule_via_workiz.md](project_cc_reschedule_via_workiz.md) — CC "Needs scheduling" Reschedule now updates WORKIZ (source of truth) when SO has a UUID — workiz_post job/update {JobDateTime:Pacific-local…
- [project_cc_skipped_excludes_submitted.md](project_cc_skipped_excludes_submitted.md) — FIXED 2026-07-01 (commit d7f88595): CC "🔁 Skipped — reschedule" list no longer hides past confirmed jobs whose Workiz status is Submitted.
- [project_city_next_available.md](project_city_next_available.md) — Command Center "📍 Next available by city" (2026-07-01): pick a city (no customer needed) → route-tight open days + times + day map.
- [project_city_service_weekday_map.md](project_city_service_weekday_map.md) — City→service-weekday map (Mon=0) gating ALL date offering (wscare.pro booking, CC next-available, Phase5, reactivation Book).
- [project_claude_remote_control.md](project_claude_remote_control.md) — Claude Code Remote Control auto-starts at login via scheduled task "ClaudeRemoteControl".
- [project_command_center.md](project_command_center.md) — Schedule Command Center = schedule_hub.html @ /owner/command-center (route in scheduler.py, no-store).
- [project_command_center_offline.md](project_command_center_offline.md) — Command Center offline/field model: cjson(url,keyOverride) IndexedDB cache-first (instant, non-blocking, can't blank screen);
- [project_customer_brain_job_actions.md](project_customer_brain_job_actions.md) — "Customer brain" = Customers tab in field.html (toggleCustJobs, /api/customer_jobs).
- [project_dashboard_erp_redesign.md](project_dashboard_erp_redesign.md) — Owner hub /owner/ redesigned ERP-style into 10 module cards (Schedule/Customers/Sales/Marketing/Money/Team/MyDay/Reports/Assistant/Tools)…
- [project_gate_code_on_schedule.md](project_gate_code_on_schedule.md) — Command Center schedule cards show 🔑 gate per job (2026-07-09).
- [project_gate_code_sms_corruption.md](project_gate_code_sms_corruption.md) — Customer-brain "Gate Code" reads res.partner x_studio_x_gate_code (code correct).
- [project_customer_card_no_gate_code.md](project_customer_card_no_gate_code.md) — Customer Brain card ALWAYS shows Gate Code row; renders "NO GATE CODE" when property blank (2026-07-22, customer_jobs). Don't re-hide it.
- [project_gcal_to_work_schedule.md](project_gcal_to_work_schedule.md) — Schedule Calendar = forward-planning HUB (look-ahead beyond the ~3wk field schedule).
- [project_job_end_time.md](project_job_end_time.md) — Job length now captured in Odoo x_job_length_min (int minutes) since Workiz (its only JobEndDateTime source) is retiring.
- [project_job_note_vs_task.md](project_job_note_vs_task.md) — UNIFIED "Log a touch" (2026-07-09): ONE POST /api/touch {partner_id,kind,text,date?,next_visit?} for all 4 kinds (call/text/inperson/note) does…
- [project_maintenance_sync_all.md](project_maintenance_sync_all.md) — Submitted next-jobs get STUCK on Maintenance/Upcoming after DJ schedules them IN WORKIZ because nothing pushes the new status back to Odoo…
- [project_maintenance_to_schedule.md](project_maintenance_to_schedule.md) — "Submitted Jobs"→"Maintenance to Schedule" (/owner/maintenance).
- [project_navigate_gps_first.md](project_navigate_gps_first.md) — Field app Navigate now routes by GPS coords first (nav_lat/lon/addr added to /api/dashboard, /api/upcoming, /api/past_jobs + navUrlForJob in…
- [project_navigate_next_address.md](project_navigate_next_address.md) — Field job screen "🧭 Navigate to Next Address" button (after Charge at Door): routes to the next stop on the SAME DAY as the job you're viewing…
- [project_new_job_intake.md](project_new_job_intake.md) — New Job intake (/owner/new-job) in new_job.py (deleted 446-line dupe from dashboard.py that SHADOWED it).
- [project_personal_time_schedule_desc.md](project_personal_time_schedule_desc.md) — Schedule: "Personal Time" rows show job description (notes_snapshot1, [Job Notes] stripped) instead of job type, wide.
- [project_property_address_cascade_bug.md](project_property_address_cascade_bug.md) — Multi-property customers NAVIGATED TO WRONG ADDRESS. Root cause = Odoo built-in address inheritance: a property res.partner with type='contact'…
- [project_route_map_geocode_on_miss.md](project_route_map_geocode_on_miss.md) — Route-map "no map pin" = Property res.partner with 0/blank partner_latitude (never geocoded).
- [project_schedule_add_block.md](project_schedule_add_block.md) — "Add to schedule" (2026-06-16): POST /owner/api/schedule/add_block creates+confirms a Personal Time block (partner 23054;
- [project_scheduled_sos_shadowed_in_dashboard.md](project_scheduled_sos_shadowed_in_dashboard.md) — Maintenance-to-Schedule (/owner/maintenance) "1 job not accurate" = /api/scheduled_sos DUPLICATED: dashboard.py copy (registered first) SHADOWS…
- [project_scheduling_app.md](project_scheduling_app.md) — Scheduling app: 2-week lookahead, AI suggests date+time first, monthly calendar as fallback.
- [project_session_apr12_fixes.md](project_session_apr12_fixes.md) — April 12 fixes: orphaned task restore (sale_order_id + property partner_id), SO smart button, staggered task times, Sunday tag (508 SOs)…
- [project_shared_scheduler.md](project_shared_scheduler.md) — Shared scheduling brain (2026-06-15): scheduler.py build_day_plan (slots + route-tightest GPS) + /api/scheduler/day-plan endpoint +…
- [project_stranded_next_jobs.md](project_stranded_next_jobs.md) — Maintenance next-jobs Phase 5 created in Workiz but never synced to Odoo (old rule: stayed Workiz-only until DJ changed status).
- [project_type_of_service_read_order.md](project_type_of_service_read_order.md) — A job's type_of_service/frequency display MUST read SO field x_studio_x_studio_type_of_service_so/_frequency_so FIRST, then Property, NEVER…
- [project_new_job_book_asis.md](project_new_job_book_asis.md) — New Job previous-job cards: "Book as-is" button (green) = Duplicate prefill but jumps straight to date+Create; skips service editing. Reuses createJob.
- [project_customer_selfschedule_spec.md](project_customer_selfschedule_spec.md) — ★ DJ payoff feature: 3-choice self-schedule msg + job-detail launch button + Accepted banner/reset + 4-day confirm + night-before gated-conditional. Spec doc in repo.
- [project_status_label_vs_so_state.md](project_status_label_vs_so_state.md) — Schedule gates on SO state (sale/done) NOT the workiz_status LABEL; marking Submitted does not unconfirm. Unconfirm = action_cancel then action_draft.
- [project_click_to_call.md](project_click_to_call.md) — Outbound click-to-call: POST /voice/dial rings DJ then bridges to customer w/ business caller ID (customer never sees DJ cell). Buttons wiring routed to specialist.
- [project_call_recording_transcript.md](project_call_recording_transcript.md) — Call recording (in+out) + consent line + readable TRANSCRIPT via Twilio Voice Intelligence (svc GAe3e7…) → lands in customer thread/Odoo.
- [project_postpone_needs_scheduling.md](project_postpone_needs_scheduling.md) — Postpone tool (inbox ⚡ Actions): parks a confirmed job to Needs-scheduling via a dedicated 'Postponed' status (keeps its real date) — scheduler.postpone_odoo_so; 5 schedule/route queries exclude Postponed, scheduled_sos includes it, reschedule promotes it.
- [project_blower_banner_gutter.md](project_blower_banner_gutter.md) — Command Center "bring the blower" banner pops when TODAY has a gutter job (job_type OR gutter line item; calendar_jobs `gutter` flag). Dismissable per-so_id via localStorage wsc_blower_cleared.

- [project_card_at_door_wrongcard_incident.md](project_card_at_door_wrongcard_incident.md) — 2026-08-26: door-charge (hosted Checkout on DJ phone) let Stripe Link charge a PREVIOUS customer (Vincent Russo) $200 for Bob Lis SO 264956; refunded. Build the Elements card-at-door page (P0); no webhook = Stripe is source of truth.

- [project_job_seed_shared_copier.md](project_job_seed_shared_copier.md) — job_seed.py is the ONE shared copier for BOTH link-booking seed (booking.api_request) + Duplicate button (dashboard.api_duplicate_job). Never write a second copier. Gate seeds from PROPERTY master not SO snapshot; property_id=None = duplicate's byte-identical behaviour.

- [project_cheryl_hud_v1.md](project_cheryl_hud_v1.md) — Cheryl's HUD (/cheryl/hud) = additive per-viewer layer over the SAME wsc.feed.items store; feed.list_items_for_viewer/ack_for_viewer + audience/viewers (DJ byte-identical); v2_hud.html reused via FEED_BASE/HUD_EXTRAS; session carries p. Go-live gates: data in wsc.decisions.2026, AUTH_ENFORCE=1, DJ login row.
