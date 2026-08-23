# Infra / deploy / GitHub / Render — memory index

- [project_odoo_rpc_429_retry.md](project_odoo_rpc_429_retry.md) — ★ Odoo JSON-RPC 200-with-no-`error` = SUCCESS even if `result` absent (VOID methods like mail.mail.send omit it). Never bare res['result'] → do res.get('result'). Was the Saunders preview 500 (send WAS working; UI lied). shared/odoo.py fixed dd5ccdf; +429/5xx retry. Owner-side routers/owner/shared.py may need same.
- [project_silent_lie_swallowed_reads.md](project_silent_lie_swallowed_reads.md) — RULE: `except: return []` on a read that FEEDS A PAGE is a silent lie if empty renders as plausible-but-false (429 gave a real customer an empty service history). Raise + degrade honestly; soften only where empty==failed to the viewer. Also: KeyError:'result' (error checked first) ≠ masked Odoo error; check fix didn't postdate the logs.

- [project_ask_route_shadow_dashboard.md](project_ask_route_shadow_dashboard.md) — ★ LIVE field-voice `/owner/ask` is dashboard.py, NOT field.py (dead shadow; main.py includes dashboard first). Edit voice-assistant changes in dashboard.py. Voice text-draft tool LIVE + fresh-eyes SAFE (hard company guard in code). `anthropic` pinned ==0.122.0 (0.123/4 → API 400s). Namespace late routes to avoid shadowing.

- [project_outbound_call_callerid.md](project_outbound_call_callerid.md) — Outbound CALL caller-ID = the 'Call from' line DJ picks in v2_dialer (default Main 5355), NOT pooled like SMS. CNAM on 5355 shows only "PALM DESERT" — no business name registered; branded calling not set up.

- [project_gusto_upload_extensionless.md](project_gusto_upload_extensionless.md) — Gusto S3 report exports download with NO extension → Android picker greys them out under any accept filter. Payroll out-files input now accept="*/*". upload_docs server-side already extension-tolerant. 2026-08-10.

- [project_shared_send_box.md](project_shared_send_box.md) — DJ: ONE shared AI send/preview widget, don't rebuild per card. WSCThread already does reply+suggest+edit+send→thread; specialist's _openSendBox = branded schedule/confirm ✨ box. Plan = shared wsc_sendbox.js (SHARED_SENDBOX_PLAN.md). PENDING specialist reply on who authors; lead wires HUD confirm/night-before cards after.
- [project_settings_screen.md](project_settings_screen.md) — ⚙️ Settings screen (v2_settings.html): one place for business vars that change periodically. Config-backed (ir.config_parameter) + safe defaults; each knob LIVE. Shipped: Quiet hours (wired in messaging.py _quiet_bounds) + Days off (wsc.capacity.overrides). API in myday.py /api/settings/*. Roadmap: cooldowns/pricing/hours next.

- [project_dj_return_today_20260805.md](project_dj_return_today_20260805.md) — ★ DJ's 2 return-today (2026-08-05) tasks: (1) kill Zapier, (2) clean-login cycle + flip AUTH_ENFORCE=1. When he asks "what do I need to do?" tell him these two. Delete when done.

- [project_twilio_port_complete.md](project_twilio_port_complete.md) — ★ Twilio port COMPLETE 2026-07-31: all 7 Workiz numbers now in DJ's acct (ACc937...), reconfigured via REST API to app voice/SMS webhooks; 5 locals added to WSC Sender MG9d92. Drive Twilio via curl w/ SID+AuthToken (creds = Render env vars on srv-d78le0..., not in memory). voice.py VOICE const now Polly.Matthew-Neural. Toll-free SMS verify + Workiz extension still open.
- [project_voice_answered_call_logging_gap.md](project_voice_answered_call_logging_gap.md) — Answered calls logged NOWHERE if caller unrecognized + no existing thread (recording-saved/transcript-ready never CREATED a conv). FIXED 2026-08-11 (create thread like voicemail). _find_customer now matches Second Phone. New `/voice/recordings` diag endpoint. ⚠ VI transcripts never worked (0 keys ever).

- [project_v1v2_retirement_plan.md](project_v1v2_retirement_plan.md) — ★ PLAN (audit done 2026-07-30, NOT executed): retire ~30 legacy V1 owner pages w/ V2 twin via archive+redirect (keep API sub-routes + /tech/*). 5 must-keep (field/hiring/quote_rates/library/index_classic). BLOCKED on DJ's 4 decisions + "every v2 is Preview" parity Q. Map artifact linked inside.

- [project_owner_page_nostore_cache.md](project_owner_page_nostore_cache.md) — Owner HTML pages served via f.read() with NO Cache-Control get stale-cached on DJ's phone (PWA, no service worker). Fix: HTMLResponse(..., headers={'Cache-Control':'no-store, must-revalidate'}). Immediate unstick: load ?fresh=1 once. 2026-07-30.

- [project_stripe_duplicate_payments_dashboard.md](project_stripe_duplicate_payments_dashboard.md) — ★ Stripe endpoints exist TWICE (payments.py + dashboard.py) and shadow inconsistently — payment_link served by payments.py, tip_page by dashboard.py. Editing only one silently does nothing. If an endpoint edit has no live effect, grep for a 2nd copy. (payments.py's missing urllib import broke all Stripe links 2026-07-27.)

- [project_authz_block_b.md](project_authz_block_b.md) — ★ Auth layer LIVE IN MONITOR MODE (2026-07-26): authz.py session cookies + gate; blocks nothing until AUTH_ENFORCE=1. READ the flip checklist before enforcing.

- [project_pwa_stale_page_reload.md](project_pwa_stale_page_reload.md) — ★ "Deployed fix but DJ still sees old behavior on resume" = Android keeps the PWA page ALIVE for days running old JS (3rd staleness mechanism). v2_apps.js now reloads after 30+ min hidden. Suspect this FIRST.

- [project_attention_feed_seam.md](project_attention_feed_seam.md) — feed.py LIVE 2026-07-26: attention-feed seam (contract v1) — specialists `from .feed import submit_item, delete_item`; /owner/api/feed/* verified in prod. Storage wsc.feed.items.

- [project_launcher_fixes_2026_07_25.md](project_launcher_fixes_2026_07_25.md) — Two shared 🚀 launcher fixes in v2_apps.js (all pages): force #fab-launch z500/#launch z600 so pop-ups can't bury it; close launcher on visibilitychange-hidden so it doesn't reappear on app resume. 2026-07-25.

- [project_data_visuals_charts.md](project_data_visuals_charts.md) — Shared inline-SVG chart module v2_charts.js (window.WSCChart: sparkline/bars/funnel/stacked/donut, CSP-safe, no libs). Visuals added to Journal/Stats/Outreach/TimeClock/Waiting. Use it for ALL new charts. Remaining opps listed. 2026-07-25.

- [project_launcher_back_bfcache.md](project_launcher_back_bfcache.md) — 🚀 launcher: Back landed on the launcher (not the page before it) because bfcache restored the prior page with the overlay still .open. Fix: close #launch on pageshow in v2_apps.js. Reusable overlay+bfcache gotcha. 2026-07-24.

- [project_home_dir_shadows_stdlib.md](project_home_dir_shadows_stdlib.md) — Don't run python from C:\Users\dj — a dev file C:\Users\dj\calendar.py shadows stdlib `calendar`, breaks `import requests` with a misleading "No module named 'fastapi'". Run scripts from the scratchpad / a neutral dir.

- [project_dead_shadowed_routers.md](project_dead_shadowed_routers.md) — ★ payments.py/timeclock.py/shift_review.py are DEAD — dashboard.py shadows them by include order. Edit dashboard.py copy, not these. (2026-07-15 audit)
- [project_render_app_no_auth_layer.md](project_render_app_no_auth_layer.md) — ★ App has NO server-side auth; PIN login is cosmetic; every /owner endpoint is public. Hardcoded keys + unsigned webhooks too. (2026-07-15 audit)
- [project_render_app_audit_2026-07.md](project_render_app_audit_2026-07.md) — Full 6-auditor code+UX audit: 59 findings (6 crit/11 high), + redesign plan on preview routes. Artifact link inside. (2026-07-15)

- [project_cheryl_repo_split.md](project_cheryl_repo_split.md) — 2026-04-20: Cheryl project split into its own repo (cheryl-real-estate) + local folder (A Cheryl Real Estate).
- [project_sw_cache_stale_page.md](project_sw_cache_stale_page.md) — "Deployed but DJ still sees old UI" = service worker (auth.py _SW_JS, cache `wsc-shell-v2`, network-first w/ 3.5s timeout → stale on slow signal). Verify server via curl FIRST; force-update by bumping cache version.
- [project_clockin_uses_hr_attendance.md](project_clockin_uses_hr_attendance.md) — Live Render timeclock stores shifts in Odoo hr.attendance (NOT ir.config_parameter like local code says).
- [project_delete_audit_and_log_forensics.md](project_delete_audit_and_log_forensics.md) — Delete audit (2026-06-11): /api/delete_job writes full job snapshot to stdout [DELETE-AUDIT] + durable Odoo param render.audit.delete (last 200).
- [project_employee_referral_program.md](project_employee_referral_program.md) — Employee referral text + $250 incentive structure. Requires Zapier→Render migration first.
- [project_fellthrough_recovery.md](project_fellthrough_recovery.md) — Recovery of customers who fell through (pre-Feb-2026 jobs got no follow-up — Phase 5/6 started ~Feb 2026 w/ Render billing).
- [project_gcal_integration.md](project_gcal_integration.md) — Google Calendar overlay on calendar.html: iCal feeds, RRULE recurring event expansion, toggle UI.
- [project_multi_business_architecture.md](project_multi_business_architecture.md) — Master plan: one Render + one Odoo serving DJ (W&SC), Danny (payroll), Cheryl (real estate), future businesses.
- [project_open_items_2026-07.md](project_open_items_2026-07.md) — BACKLOG of things discussed but NOT handled (July 2026): (1) 5 overdue maintenance customers need next-job scheduled — Mette Haydt/Vince…
- [project_owner_page_nostore_stale.md](project_owner_page_nostore_stale.md) — "Fix deployed but DJ can't see it" on an owner page = STALE CACHED HTML (route returns bare f.read() with no Cache-Control → phone caches…
- [project_payroll_hr_attendance_retrofit.md](project_payroll_hr_attendance_retrofit.md) — 2026-04-24: Complete migration JSON→hr.attendance, quarter-hour rounding (FLSA 7-min rule), CA 4h RTP minimum, W&SC Field Work calendar, Manage…
- [project_payroll_tracker.md](project_payroll_tracker.md) — DJ + Danny payroll: clock in/out via Render, hours in Odoo timesheets, manual sync to Gusto.
- [project_reeng_launch_review_page.md](project_reeng_launch_review_page.md) — NEW page /owner/reeng-review (2026-06-25): pre-text safety check before re-engaging — flags per customer whether they/you texted SINCE last…
- [project_render_502_uptime_fixes.md](project_render_502_uptime_fixes.md) — 502 causes + fixes (2026-06-06): /healthz health check = zero-downtime deploys;
- [project_render_app_apr18.md](project_render_app_apr18.md) — Full state of app.py + index.html as of 2026-04-18: all tools, endpoints, recent changes (photos, mic, timer times, saved requests, 10-day…
- [project_render_app_architecture.md](project_render_app_architecture.md) — READ BEFORE ADDING ANY ROUTE. One file per app rule, full file→app map, how to add new apps.
- [project_render_app_tools.md](project_render_app_tools.md) — 18 GPT tools in Render app. get_sales_week (Mon-Sat), duplicate_workiz_job added.
- [project_render_claude_field_architecture.md](project_render_claude_field_architecture.md) — READ before adding field assistant tools. Generic tool architecture: odoo_query+workiz_get+workiz_update, schema-based prompt, full tool list…
- [project_render_conversation_log.md](project_render_conversation_log.md) — GO HERE FIRST when DJ asks "what did Render Claude do/say." Log = ir.config_parameter render.log.YYYY-MM-DD.
- [project_render_cron_jobs.md](project_render_cron_jobs.md) — The 4 Render crons for wsc-field-assistant (A2P Watcher/Daily Sync/Submitted Jobs Scan/HOF Email Check) + what each does + schedules.
- [project_render_deploy_failed_check.md](project_render_deploy_failed_check.md) — Pushed change not live? Check list_deploys for update_failed — Render serves last good build silently.
- [project_render_employee_stats.md](project_render_employee_stats.md) — Stats panel is owner-only on mobile. Future employee stats = toggle button that swaps to a fresh blank screen (not tabs in existing office…
- [project_render_python_pin_incident.md](project_render_python_pin_incident.md) — Render pinned to Python 3.12.8 via .python-version (DO NOT REMOVE).
- [project_render_rolling_deploy_stale.md](project_render_rolling_deploy_stale.md) — Render keeps the old instance briefly during deploy cutover.
- [project_render_session_persistence.md](project_render_session_persistence.md) — 2026-04-26 fix: Render Claude session history now in Odoo (key=render.session.{id}) — survives redeploys.
- [project_render_timer_ui_cumulative.md](project_render_timer_ui_cumulative.md) — Field Assistant timer UI shows elapsed-since-resume instead of total accumulated.
- [project_report_hub_redesign.md](project_report_hub_redesign.md) — STRATEGIC (2026-06-21): "Report Hub + Brain" redesign — owner app feels like add-ons;
- [project_saunders_invoice_send_view.md](project_saunders_invoice_send_view.md) — Saunders HOF invoice mechanics (2026-06-24): SA 1335 "Send Invoice" = REAL send to NBHOF (bhatton@+retailinvoices@baseballhall.org) + silent…
- [project_saunders_printing_pdf_render.md](project_saunders_printing_pdf_render.md) — READ before rendering any Odoo PDF via API. Server action workaround for private _render_qweb_pdf.
- [project_saunders_render_app.md](project_saunders_render_app.md) — New multi-business Render app: repo windowandsolarcare-hash/saunders-render-app, login via res.partner PIN, DJ PIN=8487 role=owner, live at…
- [project_spymuseum_customer.md](project_spymuseum_customer.md) — International Spy Museum = a SAUNDERS PRINTING customer (Odoo company 3;
- [project_submitted_jobs_feature.md](project_submitted_jobs_feature.md) — Submitted future jobs: UUID on sale.order (x_studio_x_studio_workiz_uuid, written by Phase 5).
- [project_system_roadmap.md](project_system_roadmap.md) — "Complete the system" roadmap (DJ 2026-06-17, ~16 items toward end-to-end autonomous ops).
- [project_zapier_to_render_migration.md](project_zapier_to_render_migration.md) — NEAR-TERM: migrate Phases 3/4/5/6 off Zapier. Zapier = just webhook catch + GitHub fetch — easy redirect to Render.
- [reference_render_claude_write_tools.md](reference_render_claude_write_tools.md) — Catalog of all Render Claude write tools + 4-point wiring checklist for adding new ones.
- [reference_render_drive_service_account.md](reference_render_drive_service_account.md) — render-drive service account for Render→Drive. Key backup: C:\Users\dj\Documents\Business\render-drive-service-account.json.
- [reference_render_mcp.md](reference_render_mcp.md) — Official Render MCP added (https://mcp.render.com/sse), needs API key + Claude Code restart to activate
- [reference_render_tools_architecture.md](reference_render_tools_architecture.md) — READ when adding/extending Render Claude tools. Tool definitions live in TOOLS list (line ~1962 in dashboard.py).
- [session_apr25_summary.md](session_apr25_summary.md) — 2026-04-25: Summarized huge chat into 4 memory files, pushed SHARED_MEMORY.md to GitHub, cleaned up test clock-in (4/6-4/18), synced Dan↔Danny…
- [session_apr26_summary.md](session_apr26_summary.md) — 2026-04-26: Analyzed Cheryl transcripts, refined INTERVIEW.md (8 improvements, pushed to GitHub), identified gap between MODELS_SPEC…
- [session_apr30_summary.md](session_apr30_summary.md) — Apr 29-30 evening: PO infrastructure end-to-end (AWP vendor, 33 frame products, draft P00002), 4 new Render Claude write tools, quote workflow…
- [session_may03_summary.md](session_may03_summary.md) — 2026-05-03: activities edit modal, empty-Workiz-Items sync fix, date_order restore after confirm, RENDER_BASE_URL→direct calls, Zelle prefix…
- [session_may08_summary.md](session_may08_summary.md) — 2026-05-08: field.html cache/weather/3-dot, shift_review range revenue fix, 3-dot stop cards, Render cron autoDeploy duplicate-email fix.
- [session_may10_summary.md](session_may10_summary.md) — 2026-05-10: Saunders Printing Step 1 deployed — HOF PO email watcher (IMAP+Claude Haiku+Odoo), /printing/api/check-po manual trigger…
- [session_may14_summary.md](session_may14_summary.md) — 2026-05-14/15: Google Calendar overlay built+deployed, RRULE fix, Render env var wipe+restore, OwnTracks geofence fixes (radius 20m→200m…
- [session_may21_summary.md](session_may21_summary.md) — 2026-05-21: Render Claude rebuild (8 narrow→2 generic tools + schema prompt), nav button in voice chat, theme-aware primary card, voice response…
- [session_may23_summary.md](session_may23_summary.md) — 2026-05-23: timer rewrite (localStorage+ir.config_parameter), crew modal date gate, crew labor cost from hr.employee.hourly_wage, source stamps…
- [project_v2_launcher_duplicated_stale.md](project_v2_launcher_duplicated_stale.md) — Every v2_*.html hardcodes its OWN 🚀 launcher APPS[] (34 stale subsets, 10-20 apps). Canonical = v2_home GROUPS (~35). Command Center fixed; rest stale. Durable fix = shared v2_apps.js.
- [project_payroll_cron_dependency.md](project_payroll_cron_dependency.md) — Payroll specialist rode on the SUSPENDED Daily Sync cron (off since 2026-07-27) → went silent. Fixed w/ dedicated "WSC Payroll" Render cron (crn-d9pfp5m1egvs73fbavug, 0 15 * * *, GET /api/payroll/cron). Daily-safe 5-day freshness guard; ?today future date submits a real card.
- [html_nostore helper](project_html_nostore_helper.md) — shared no-cache helper (routers/owner/shared.py + local mirror in self-contained dashboard.py) on every owner page serve; kills stale-owner-page class. no-store prevents FUTURE stale only; SW-cache separate.
- [project_stripe_webhook.md](project_stripe_webhook.md) — Stripe server-to-server webhook POST /owner/api/stripe/webhook (payments.py): robust card close-out independent of the browser redirect; fail-closed HMAC sig verify; idempotent shared _stripe_record_and_close keyed on payment_intent. INERT until STRIPE_WEBHOOK_SECRET set (Render POST/merge) + endpoint registered in Stripe dashboard. Same cluster de-duped /api/payment shadow.
- [project_auth_enforce_layer.md](project_auth_enforce_layer.md) — App session-auth: routers/authz.py middleware + AUTH_ENFORCE env gates /owner,/tech,/cheryl. Currently OFF (monitor mode) → whole /owner surface answers ANONYMOUS = P0 leak. wsc_session HMAC cookie via /api/login+PIN (role from x_render_role). Make-safe via would-block report GET /owner/api/authz/report; DO NOT flip blind (DJ PWA not reliably cookied).
- [project_artifact_live_watch_hangs_republish.md](project_artifact_live_watch_hangs_republish.md) — An ACTIVE artifact live-watch makes republishes hang for MINUTES; unwatch after the first publish and they take 10-20s. Not file size, not turn position.
- [project_design_canvas_png_export_is_1to1.md](project_design_canvas_png_export_is_1to1.md) — VERIFIED: canvas PNG export is 1:1 with artboard CSS px — author at 300-DPI dims and the export IS the press file (no Upscayl). Photoshop shows 72dpi: relabel via Image Size with Resample OFF.

- [project_memory_mirror_secret_scanning.md](project_memory_mirror_secret_scanning.md) — GitHub secret-scanning BLOCKS memory files with live secrets; redact to placeholders (real value in Render env) before mirroring; never write live tokens into notes.

- [project_cloud_session_env_limits.md](project_cloud_session_env_limits.md) — Cloud CC sessions: NO gh CLI (use GitHub MCP); outbound net is GitHub-only by default (app/Odoo 403) — open env network allowlist to verify live or run Operator-cloud.
- [project_cloud_lead_write_path.md](project_cloud_lead_write_path.md) — ★ CLOUD sessions: no `gh` CLI + api.github.com egress-BLOCKED (403). WRITE = MCP `create_or_update_file` (Contents PUT to main); READ = on-disk clone + `git fetch origin main`. safe_deploy.py absent — gate by hand.
- [feedback_mcp_push_content_is_inline.md](feedback_mcp_push_content_is_inline.md) — MCP `create_or_update_file`'s `content` is the FILE TEXT inline, NOT a path — passing a path silently commits a tiny placeholder over the real file.
- [project_design_canvas_save_slow_after_long_turn.md](project_design_canvas_save_slow_after_long_turn.md) — Design-canvas Artifact saves hang for MINUTES when they trail a long tool-heavy turn; issued alone ~8-14s. Publish as its own step; kill a hang at ~60s and re-issue.
- [project_hr_attendance_unlink_context.md](project_hr_attendance_unlink_context.md) — Deleting/editing hr.attendance over XML-RPC crashes on an enterprise work-entry addon ("unhashable type: 'list'") UNLESS you pass context {'tracking_disable': True}.
- [project_daily_sync_zapier_survivor.md](project_daily_sync_zapier_survivor.md) — The 4am PT "WSC Daily Sync" report emails survive in a ZAPIER zap even though app-side sync is fully retired — the zap runs its own copy. Only DJ can turn it off, in Zapier.
- [project_payment_link_nameerror.md](project_payment_link_nameerror.md) — /api/stripe/payment_link threw NameError '_force_lines_deliverable' for any job with NO existing invoice — killed Send Stripe Link + Charge at Door. Fixed 2026-08-13 (import from field.py).
