# Misc — memory index

- [project_odoo_200_not_success.md](project_odoo_200_not_success.md) — On Odoo, HTTP 200 ≠ success: denied attachments serve placeholder.png (200), broken /terms serves an error page (200). Verify permission/route/access changes by response CONTENT (bytes/content-type), never status alone.
- [project_company_filter_fails_open.md](project_company_filter_fails_open.md) — ★ SECURITY: company_id FAILS OPEN (W&SC customers mostly False) → enforce `company_id in [1,False]` at the RESOLVER/chokepoint, never per-caller, never bare "≠ me". Real portal leak (Saunders customer on W&SC portal) 2026-08-19. Backs CLAUDE.md rule 8.

- [project_thumbtack_automation.md](project_thumbtack_automation.md) — Thumbtack lead automation: Thumbtack HAS a partner-gated Pro API (OAuth2, webhook leads + two-way messaging → reply in-thread, no phone/A2P). Quick win = built-in auto-responder set up via computer-use when DJ's at desk. API access = must apply, solo-pro eligibility TBD. Parked.

- [project_portal_link_as_text_ps.md](project_portal_link_as_text_ps.md) — DJ's framing: the portal link is "a P.S. to every text I send someone" — rides the sms.py signature rail, resolved per recipient. Specialists owns sms.py; segment cost is the open question. NOT approved to build.

- [project_customer_portal.md](project_customer_portal.md) — Customer portal = wscare.pro/p/<token>, magic link, no password. portal.py + portal.html (Portal session owns). No-prefix router = public by construction, zero authz edits. Photo link ONLY when `wsc.job.photos_sent.<so_id>` exists.

- [reference_app_ai_prompts.md](reference_app_ai_prompts.md) — Inventory of EVERY AI persona/prompt in the Render app + house philosophy (comprehensive prompt >> many tools; inject facts not fetch-tools; same full prompt on all model tiers). Engine = field.py `_agent_loop` (Haiku→Sonnet, REUSE it). Read before writing/tuning any in-app Claude prompt.

- [project_idea_board.md](project_idea_board.md) — Idea Board: DJ+Cheryl shared idea capture, in-app group chat Claude turns into a live DECAYING dashboard (NOT an inbox). **ALL 4 phases LIVE 2026-08-17**: ideas.py (blob `ideaboard.data`, /owner/api/ideas/*), ideas.html (Chat + Board + Card-detail views, reuses Library dclib_user identity), 💡 launcher tile + global capture FAB in v2_apps.js. P1=chat/capture; P2=decaying dashboard (Claude proposes cards, one-tap promote, heat half-life 5d, stale nudge 4d); P3=per-card sub-threads (resume-in-context) + HUD "Ideas" lane (pushes source=ideas into canonical feed via feed.submit_item; v2_hud.html separate section) + deep-link /owner/ideas#card=<id>; **P4=🎙️ Record button → MediaRecorder → /api/ideas/record → hosted Whisper (reuses myday `_vm_whisper` + existing OPENAI_API_KEY, NO new key) → brainstorm session (audio as ir.attachment, Range-streamed) → idea-scan**. ★ blob is load-save no-lock — don't hammer writes; DJ actively uses it, preserve msgs when testing. ★ Windows curl `-F @` uploads need `C:/` path not `/c/`. Brief=app repo 3_Documentation/IDEA_BOARD_BRIEF.md. Library pattern, breakable to ideas.wscare.pro.

- [project_button_color_inherit_darkmode.md](project_button_color_inherit_darkmode.md) — GOTCHA: text in a <button> doesn't inherit color/font — defaults to black, invisible in dark mode. Fix: color:var(--ink);font-family:inherit on the button. Hit v2_analytics KPI numbers. Test dark mode. 2026-07-25.

- [project_dan_cheryl_library.md](project_dan_cheryl_library.md) — Dan & Cheryl's Library /owner/library (library.py+library.html): Cheryl saves self-help videos/screenshots, Dan browses. Odoo-backed shared store (ir.config_parameter dclib.data + ir.attachment images), server-side Anthropic Verify/Truth Meter. Built into Render app, not standalone. Launcher + Cheryl hub links.
- [project_ask_ai_router.md](project_ask_ai_router.md) — Ask AI page /owner/ai + /api/ask (myday.py): Haiku routes a question → answers easy ones or escalates to Opus (deep) / Opus+web-search (current info). One-tap override. Anthropic-only, DJ declined Gemini. Model list = config array _AI_MODELS.
- [project_feature_consolidation.md](project_feature_consolidation.md) — DJ's 6-bucket consolidation model (Orders/Inputs/Output/CRM/AI/3rd-party); front doors that list CHOICES and route (like New Order). Inputs front door /owner/inputs BUILT 2026-07-13; Activities tile hidden; home "My Day" group → 1 Inputs tile.

- [project_api_search_company_filter.md](project_api_search_company_filter.md) — Home /api/search: added company_id in [1,False] filter (was missing, not a regression). Cheryl(2) contacts lack Workiz ref so already excluded; "foreign" results like Active Window Products = unstamped company=False strays matching mid-word ("pRODucts"). A/B-names screenshot = deploy transient, not lost code.

- [project_calendly_mcp.md](project_calendly_mcp.md) — Calendly MCP connected via claude.ai connector (authorized 2026-04-12).
- [project_cheryl_interview_refinements.md](project_cheryl_interview_refinements.md) — 2026-04-26: Template improvements based on transcript analysis (8 changes, 60→90 min);
- [project_cheryl_interview_to_plan_workflow.md](project_cheryl_interview_to_plan_workflow.md) — 2026-04-26: Interview = gather current-state data (what she does).
- [project_chores_todays_list.md](project_chores_todays_list.md) — chores.html = "today's list" app (/static/chores.html). planner.html = habit tracker.
- [project_clockin_bar_customer_overlay.md](project_clockin_bar_customer_overlay.md) — Clock-in bar = fixed,top:0,36px,max z-index. ANY full-screen position:fixed overlay on an owner page MUST start at top:36px not inset:0 or the…
- [project_gusto_integration_status.md](project_gusto_integration_status.md) — 2026-04-24: CSV export endpoint done, button done but scope wrong (exports 1 emp, should be all), Playwright skeleton done but selectors need…
- [project_hiring_ats.md](project_hiring_ats.md) — Hiring ATS: grouped view (yes/maybe/no/follow-up/unreviewed), screening answers, candidate notes.
- [project_hiring_interview_tracker.md](project_hiring_interview_tracker.md) — Interview tracker: per-candidate status chip + Interviews day-view.
- [project_hiring_screening_messages.md](project_hiring_screening_messages.md) — Approved screening message + graceful rejection message for Indeed.
- [project_invoice_qty_delivered_gate.md](project_invoice_qty_delivered_gate.md) — READ when touching any invoice-creation code. sale.advance.payment.inv refuses when qty_delivered<qty_ordered on delivered-policy products.
- [project_open_tasks.md](project_open_tasks.md) — CHECK AT SESSION START. Running task list with dates. Customer tab work pending.
- [project_opening_balances_needed.md](project_opening_balances_needed.md) — The opening-balance bridge to reality — NOW THE ACTIVE NEXT STEP (2026-06-24).
- [project_owntracks_setup.md](project_owntracks_setup.md) — OwnTracks Android: DJ's settings, clock-in/out logic, waypoint name must contain "home", radius must be 200m+, checkbox = monitoring on/off.
- [project_pending_cursor_history_review.md](project_pending_cursor_history_review.md) — REMIND DJ: review old Cursor chat history to extract historical bug fixes into CLAUDE.md (when time permits)
- [project_predeposit_paid_cache.md](project_predeposit_paid_cache.md) — WSCPaid (paid-cache.js): mark SO paid in localStorage on payment → pre-deposit lists hide it offline via pageshow, no network refresh.
- [project_pwa_launch_to_dashboard.md](project_pwa_launch_to_dashboard.md) — PWA icon now always launches to dashboard hub (login.html), not last-visited page.
- [project_pwa_manifest_on_every_page.md](project_pwa_manifest_on_every_page.md) — PWA showing Chrome shortcut icon = manifest link missing from install page.
- [project_recurring_bookkeeping_plan.md](project_recurring_bookkeeping_plan.md) — Agreed plan for weekly/monthly auto-bookkeeping (NOT built — DJ reviewing).
- [project_session_apr20_summary.md](project_session_apr20_summary.md) — What was done Apr 20 (Balser fix, Jose Merelies diagnosis, timer UI verification, Cheryl dashboard + client list shipped, 314 contacts imported).
- [project_shift_review_source_of_truth.md](project_shift_review_source_of_truth.md) — shift_review.html authoritative source is AppData temp file, NOT local repo path.
- [project_timer_architecture.md](project_timer_architecture.md) — READ before touching timer code. localStorage start → POST /api/timer/log → timer.so.{so_id} ir.config_parameter.
- [session_apr24_payroll_timeclock.md](session_apr24_payroll_timeclock.md) — Apr 24 payroll system migration: JSON → hr.attendance, Manage Shifts UI, Gusto Smart Import with CA OT, multi-week display, task timer coupling…
- [session_jun01_hiring_ats.md](session_jun01_hiring_ats.md) — 2026-06-01: ZIP import, 64 candidates, DJ batch scoring, email incident, Cheryl setup, PWA fixes (icon+resume partial)
- [user_profile.md](user_profile.md) — Full name is Dan Saunders (goes by DJ). Never "DJ Sanders." Documents/emails/signatures = Dan Saunders.
- [project_open_items_2026-07.md](project_open_items_2026-07.md) — ★ BACKLOG (July 2026): open/unhandled items DJ & I discussed but did not close out — working list to revisit.
- [project_memory_index_structure.md](project_memory_index_structure.md) — How the memory index works: MEMORY.md is a sharded TOC, detail in idx_<domain>.md. To add a memory, append the hook to the matching idx_ file, NOT MEMORY.md.
- [project_split_view.md](project_split_view.md) — Split View (2026-08-03): two owner screens side by side in iframes for the folding phone. v2_split.html reuses window.WSCApps; embed guards in v2_apps.js + clockin-bar.js.

- [project_voice_call_forwarding.md](project_voice_call_forwarding.md) — Twilio voice forwarding (biz# caller ID = looks like self-call), screening whisper; dead-air fix + block-list→VM endpoints (voice.py 1ad7c59).
- [project_marketing_site_odoo.md](project_marketing_site_odoo.md) — Public marketing site = Odoo website module (site 1). ONE shared wsc.page/wsc.styles + component views; pages are body-only. Re-runnable build script.
- [project_odoo_website_page_api.md](project_odoo_website_page_api.md) — Odoo website API: website.page _inherits ir.ui.view (one-call create); COW header/footer views by key+website_id; /terms is a RESERVED route that silently errors.
- [project_wsc_address_do_not_publish.md](project_wsc_address_do_not_publish.md) — W&SC = service-area business, NO public street address. Odoo company addr (Palm Desert) is STALE; the real one is DJ's HOME. Never publish/schema it.
- [project_thumbtack_proxy_numbers.md](project_thumbtack_proxy_numbers.md) — Thumbtack proxy/masked customer numbers ARE a usable permanent channel (DJ's Twilio number is registered to the Thumbtack account) — store the proxy as the customer's phone.
