# Field app (field.html / job detail) — memory index

- [project_voice_reschedule_tool.md](project_voice_reschedule_tool.md) — Voice reschedule_job WRITE tool (dashboard.py, confirm-gated) moves a job by voice via scheduler.schedule_odoo_so; NO Workiz. Postpone/dup/cancel/new-job still app-only. Preceded by the dead-Workiz 401 guard.

- [project_voice_ask_lives_in_dashboard.md](project_voice_ask_lives_in_dashboard.md) — ★ LIVE voice /owner/ask = dashboard.py (shadows field.py's dead twin; dashboard registers first). Edit dashboard.py for ANY voice-assistant change. field.py edits = no effect.

- [project_field_voice_history_sanitize.md](project_field_voice_history_sanitize.md) — Voice 400 "Extra inputs not permitted" (tool_use.toolset_name): SDK model_dump emits fields API rejects on replay. Fixed by _sanitize_messages() whitelisting block fields before every create(); self-heals poisoned sessions. Hits quick+deep both.

- [project_voice_deep_think_mode.md](project_voice_deep_think_mode.md) — Voice assistant 🧠 "Think hard" DEEP mode: button (field.html, localStorage wsc_deep_mode) + spoken phrases → run_agent(deep=True) skips Haiku, uses CLAUDE_DEEP_MODEL + extended thinking (thinking_budget) + richer prompt. Graceful degrade if SDK/model lacks thinking.

- [project_voice_text_draft_tool.md](project_voice_text_draft_tool.md) — Voice "text <customer>" → field.py open_text_draft: resolves partner (company_id in [1,False], numbered), grounded _draft_outbound (sms.py), opens v2_inbox ?open=<pid>&draft= prefilled. NEVER sends.

- [project_payment_finalize_shared_closeout.md](project_payment_finalize_shared_closeout.md) — ONE shared closeout = payment_finalize.finalize_payment(so_id, method, source). FIXED card bug: /api/stripe/success called never-defined _stripe_phase6_sync → card paid but never Done/next-visit/thank. Now wired to finalize.
- [project_stripe_payment_methods.md](project_stripe_payment_methods.md) — Stripe Checkout methods = Dashboard config, not code. 2026-08-13: card/Link/ApplePay/CashApp ON; PayPal+GooglePay OFF (customer can't pay by PayPal via link). Charge-at-Door reads #pay-amount, fixed popup silent-fail → same-tab.

- [project_so_activity_breadcrumb.md](project_so_activity_breadcrumb.md) — 🧭 Activity button + GET /api/so_activity: per-job timeline from SO chatter (append-only). Shows if CUSTOMER pressed confirm/ack (via page/text) vs your manual mark vs sends, survives clearing a flag. Reuses existing chatter logging. 2026-08-11.

- [project_edit_select_empty_first_option.md](project_edit_select_empty_first_option.md) — Job-detail edit dropdowns showed options[0] when value empty → unset Frequency read "3 Months", Type read "Maintenance" (esp. after duplicate). Fixed w/ blank "— not set —" option in v2_field.html select renderer. Duplicate endpoint itself was fine. 2026-08-10.

- [project_job_photo_gallery.md](project_job_photo_gallery.md) — Share job photos via a LINK: token-signed public gallery (/api/job/gallery + /api/job/photo, PUBLIC_EXACT) + "📤 Text photos to customer" button in field.html photo card → /api/job/photos_send. Verified John SO 17389 (22 pics).

- [project_command_center_page_map.md](project_command_center_page_map.md) — ★★ VERIFIED page map: daily SCHEDULE = schedule_hub.html (/owner/command-center); job DETAIL = field.html (/owner/field?open_so, via onScheduleTap). v2_*.html are DEAD previews. Cards render via WSCKit/report_kit.js (extra=escaped text, use badges for color). Burned 2 sessions guessing — verify vs screenshot.
- [project_render_app_redesign.md](project_render_app_redesign.md) — ★ UI redesign lives at PREVIEW URLs (/static/owner/v2_*.html — no route change, StaticFiles mount). Flagship = new Owner Home, brand blue #1e5aa8, real data. Originals untouched. (2026-07-15)

- [project_v2field_deeplink_open_flash.md](project_v2field_deeplink_open_flash.md) — v2_field.html deep-link open (Command Center card) flashed ⭐ banner ~3x + jumped to top: openJob ran twice (skeleton+so_history). Guarded loadNextVisitNote per-pid + scroll-reset to new-job-only (2026-07-22).
- [project_field_refresh_rerenders_open_job.md](project_field_refresh_rerenders_open_job.md) — Schedule refresh re-ran FULL openJob() on the open detail → ⭐ banner flashes + scroll jumps to top (Kristen bug). NEVER call openJob() from a refresh/poll path; use surgical _repaintActiveMeta/_repaintActiveLines/_setPaidUI. Fixed 2026-07-22.
- [project_field_delete_odoo_only.md](project_field_delete_odoo_only.md) — Field "Delete (Odoo only)"/"Delete Block" now HARD-deletes via /api/delete_so (cancel+unlink, refuse if invoiced) — was cancel-only, couldn't remove already-cancelled SOs (S00119). cancel_so stays cancel-only for calendar. 2 partner recs per customer (Contact+Property).
- [reference_customer_brain_deeplink.md](reference_customer_brain_deeplink.md) — Deep-link to a customer's Customer Brain: `/owner/field?tab=customers&cust_q=<name>&cust_pid=<pid>`. Reuse for any "🧠 research this customer" link (stopPropagation if card has onclick). Added to Maintenance cards 2026-07-10.

- [project_account_payment_no_ref_field.md](project_account_payment_no_ref_field.md) — Odoo 19 account.payment has NO 'ref' field — only 'memo'.
- [project_addschedule_gcal_picker.md](project_addschedule_gcal_picker.md) — Field "📅 Add to schedule" modal now has "📇 Pick from Google Calendar" (GET /owner/api/gcal_events, read-only iCal) → prefills What/Day/Time/Notes. GCal is read-only in-app (no push OUT).
- [project_activities_unified_flow.md](project_activities_unified_flow.md) — READ when adding new activity automations. All activities open detail modal first (shows every field).
- [project_credit_card_payment_flow.md](project_credit_card_payment_flow.md) — Credit card at-door: JobAmountDue=0 + Status!=Done = CC taken.
- [project_customer_search_multifield.md](project_customer_search_multifield.md) — Customer tab search (/api/search) is tokenized multi-field: name OR street OR city, partial/any-order + any-token fallback (2026-06-10).
- [project_duplicate_job_fields_fix.md](project_duplicate_job_fields_fix.md) — 2026-04-26 fix: duplicate_workiz_job now copies ServiceArea + sets last_date_cleaned=source JobDateTime[:10].
- [project_field_delete_return_origin.md](project_field_delete_return_origin.md) — Field app: after deleting a job OR recording a payment it dumped DJ on the empty TODAY schedule (dead end);
- [project_field_detail_collapse.md](project_field_detail_collapse.md) — Field assistant: open job → schedule collapses to only the selected row, panel 80vh (phone).
- [project_field_paid_banner.md](project_field_paid_banner.md) — Field payment card: confirm dialog names method+check#; green Paid banner (method/ref/amount/date) replaces button when paid.
- [project_field_sync_button_repaint.md](project_field_sync_button_repaint.md) — Field 🔄 Sync button MUST repaint the open detail's line items after sync (_repaintActiveLines after await loadField()).
- [project_foldable_mobile_modal_fixes.md](project_foldable_mobile_modal_fixes.md) — DJ uses a SAMSUNG FOLDABLE — recipe to make owner/field pages + bottom-sheet modals fit the cover screen: (1)…
- [project_future_job_shows_today_bug.md](project_future_job_shows_today_bug.md) — FIXED: future jobs opened in the field detail showed TODAY not their real date (upcoming/past payloads lacked date_raw → _apHeaderWhen fallback…
- [project_future_record_check_payment_sync.md](project_future_record_check_payment_sync.md) — TODAY TASK: add _phase4_full_sync() into record_check_payment before invoice creation — Render Claude currently skips Workiz sync on all…
- [project_last_communication_rollup_field.md](project_last_communication_rollup_field.md) — res.partner.x_last_communication (date, field 21336, PLAIN stored) = max of all outreach send-date fields (currently last_followup_sent +…
- [project_log_touch_css_injection.md](project_log_touch_css_injection.md) — "📣 Log a touch" button did nothing on field.html JOB-DETAIL screen (worked from Customer Brain).
- [project_new_order_tech_field.md](project_new_order_tech_field.md) — New Order (new_job.html→/api/intake/create-job) Tech field is DEAD while Workiz is live: backend receives tech_name but ignores it (only in the…
- [project_next_job_date_field.md](project_next_job_date_field.md) — COMPLETE: x_studio_next_job_date on res.partner, written by Phase 3/5, cleared by Phase 4 on Done/Canceled, backfilled 48 contacts 2026-04-02.
- [project_note_scopes_field_app.md](project_note_scopes_field_app.md) — 3 note systems & scope: field_note + to-do list = PARTNER-scoped (repeat every visit at a property);
- [project_odoo_payment_je_approach.md](project_odoo_payment_je_approach.md) — Odoo 19 SaaS: payment.register wizard creates in_process/move_id=False.
- [project_odoo_payment_register_fields.md](project_odoo_payment_register_fields.md) — Odoo 19: account.payment.register uses communication (not memo);
- [project_payment_date_field.md](project_payment_date_field.md) — Record Payment (job detail, field.html) now has a Payment DATE field (all methods;
- [project_payment_sync_tools.md](project_payment_sync_tools.md) — 2026-05-01: sync_so_verify + process_payment_with_sync Render Claude tools for payment flow.
- [project_pending_sync_before_payment.md](project_pending_sync_before_payment.md) — REMIND DJ: discuss auto-running Workiz sync (with slight lag) before Payment button fires, to ensure SO data fresh.
- [project_service_area_field_twin.md](project_service_area_field_twin.md) — Service Area = x_studio_service_area (values Hemet / Desert / All areas), NOT the empty twin x_studio_x_studio_service_area that CLAUDE.md's…
- [project_type_of_service_fields_map.md](project_type_of_service_fields_map.md) — Definitive Odoo "Type of Service" field map (verified 2026-06-22): TWO real fields w/ values Maintenance/On Request/Unknown…
- [project_workiz_exit_field_editability.md](project_workiz_exit_field_editability.md) — KEY future project: when Workiz drops (soon), Render detail screen must become EDITABLE (add/edit job fields, descriptions, notes) — DJ refuses…
- [project_workiz_sync_field_casing.md](project_workiz_sync_field_casing.md) — Daily SO↔Workiz sync "⚠ Workiz=blank" false alarms = wrong-CASE Workiz JSON keys in _sync_so_with_workiz (dashboard.py ~L9491).
- [session_apr29_summary.md](session_apr29_summary.md) — Apr 29 big build: Quote Tool replaces AppSheets, activities unified flow + 5s undo grace, three-dots menu fix, stats drill-down, payment history…
- [session_jun03b_clockin_bar.md](session_jun03b_clockin_bar.md) — 2026-06-03 PM: clock-in bar (all 18 pages, VISIBILITY UNRESOLVED), hist modal (address/freq/editable note/payment), Add Note save fix.
- [project_utc_today_bug.md](project_utc_today_bug.md) — Client-side "today" via new Date().toISOString().slice(0,10) is UTC → after ~5pm Pacific reads as TOMORROW. Use a Pacific-anchored date.
- [project_so_full_start_time_edit.md](project_so_full_start_time_edit.md) — Customer & Order Detail (so_full) now has editable Start date + Start time (PT) → writes date_order on the Odoo SO. dashboard.py so_full + brain.py brain_job_save + v2_field render. DJ's manual time-change without the reschedule menu.
- [project_field_voice_workiz_retired.md](project_field_voice_workiz_retired.md) — Field VOICE assistant de-Workiz'd (field.py): HELP_TEXT + SYSTEM_PROMPT rewritten Odoo-only, 9 dead workiz tools hidden via DEAD_WORKIZ_TOOLS filter + execute_write_tool guard. Payments sync already safe.
- [project_next_visit_note_on_card.md](project_next_visit_note_on_card.md) — ⭐ next-visit note (Log a touch) = res.partner.x_next_visit_note (text); now surfaced on Command Center cards (amber, below the green CONFIRMED bar). Get a screenshot before assuming which screen "covered" means.
- [project_shared_text_thread_component.md](project_shared_text_thread_component.md) — wsc_thread.js (WSCThread) = shared Texts modal; put reply/text actions HERE so they appear everywhere. Now has ✨Claude rewrite (/api/ai/rewrite). Inbox composer still a partial duplicate (unify later).
- [2nd contact + recipient picker](project_second_contact_and_recipient_picker.md) — x_studio_secondary_phone/_name on the PERSON; "who to text" picker in _openSendBox (opts.recipients, always-show >=1, validated `to` override); edit person-level fields via so_full + brain_job cust_ maps (_CUST_PERSON).
- [project_maint_confirm_ack_attribution.md](project_maint_confirm_ack_attribution.md) — Maint ACK+CONFIRM tracks attribute WHO (customer vs Dan/tech) + WHEN. reminders.py appt_confirm branches on source; new CONFIRM_BY_KEY (customer|manual) at all confirm set-sites; sched/state returns confirmed_by+when; v2_field ack-pill + confirm banner show by-Dan vs by-customer + PT timestamp. Same set: pill reorder + journal date fix (today_pt).
