# Memory Index (TOC)

Detail lives in topic files. Sharded by domain — open the matching `idx_<domain>.md` or `Grep` the memory dir. 288 topic memories / 11 domains + 82 standing rules.

> **Maintaining:** new hooks go in the matching `idx_<domain>.md`, NOT here. Touch THIS file only for a `feedback_*` standing rule or a new domain shard — keep it <17 KB so it fully loads every session (≈24.4 KB hard cap). Re-shard: `scratchpad/reindex_memory.py`.

## Domain sub-indexes

- [Field app (field.html / job detail)](idx_field_app.md) — 28
- [Scheduling & Command Center](idx_scheduling.md) — 35
- [Outreach / reactivation / CRM](idx_outreach_crm.md) — 33
- [My Day & tasks](idx_myday.md) — 10
- [Vault / Notes / Drive](idx_vault_notes.md) — 28
- [Odoo quirks & fields](idx_odoo.md) — 19
- [Workiz / phases / sync](idx_workiz_sync.md) — 35
- [Infra / deploy / GitHub / Render](idx_infra_deploy.md) — 47
- [Saunders Printing (NBHOF)](idx_saunders_printing.md) — 17
- [Business & personal](idx_business.md) — 14
- [Misc](idx_misc.md) — 24

## ★ Standing rules (how DJ wants me to work) — always honor

- [feedback_notify_dj_channels.md](feedback_notify_dj_channels.md) — Reach DJ: PushNotification=FYI (flaky, don't assume delivered); TEXT/SMS=when INPUT needed (can't-miss). Cell in /c/Users/dj/dj_cell.txt.
- [feedback_raise_bar_on_dj_alerts.md](feedback_raise_bar_on_dj_alerts.md) — ★ Reach DJ ONLY when REALLY needed; else decide-and-proceed (park nice-to-haves), escalate only true blockers/DJ-only; cross-stream→Lead.
- [feedback_alert_dj_when_input_needed.md](feedback_alert_dj_when_input_needed.md) — ★ When DJ's input is genuinely needed, ALERT him (banner/HUD/text) — never ask then wait silently; keep working meanwhile.
- [feedback_dj_operating_instincts.md](feedback_dj_operating_instincts.md) — ★ DJ's instincts: WORDS warm/personal/one-push; DATES batch-by-geography, tight slots; ACTIONS 2 quote types, review-then-send, tap-to-book, price-TBD-till-seen, one-pass.
- [feedback_operator_followup_verify.md](feedback_operator_followup_verify.md) — ★ Operator: any action with an expected OUTCOME gets a CONCRETE scheduled follow-up (CronCreate one-shot) to VERIFY — never a vague "I'll watch for it".
- [feedback_activity_notes_self_contained.md](feedback_activity_notes_self_contained.md) — Activity notes: embed memory content; any real URL must be a proper <a href> anchor.
- [feedback_agent_handoff_via_doc.md](feedback_agent_handoff_via_doc.md) — Agent handoffs: instructions in a doc (3_Documentation/*_BRIEF.md); DJ gets a 1–2 sentence paste + the path.
- [project_agent_mail_channel.md](project_agent_mail_channel.md) — ★ Cross-session comms = 3_Documentation/AGENT_MAIL.md (app repo). DJ's "mail" = go read it. Read at start + after each task; write there.
- [feedback_lead_roster_restamp.md](feedback_lead_roster_restamp.md) — ★ Lead MUST re-stamp its SESSION_ROSTER row (ref+UTC) at start, every tick, + a heartbeat cron — a churned ref once left a DEAD Lead address.
- [feedback_agent_mail_autowatch.md](feedback_agent_mail_autowatch.md) — ★ At session start arm a mail-watcher cron (offset minute; check CronList) so the session self-checks AGENT_MAIL. Session-local, re-arm each start.
- [feedback_render_design_before_presenting.md](feedback_render_design_before_presenting.md) — ★ Never present a math-built design: render to PNG, LOOK, send the IMAGE. Never hardcode a session ref in a heartbeat.
- [project_eddm_mailing_rules.md](project_eddm_mailing_rules.md) — ★★ EDDM: W&SC size 9×6.5 in (Zoo EDDM). 9×6 NOT eligible. Address block TOP HALF. Indicia rules. Design owns.
- [project_wsc_print_build_pipeline.md](project_wsc_print_build_pipeline.md) — `_design_build.py`: .dc.html → guide proofs + Zoo CMYK press PDFs (2775×2025, SWOP, crop marks, TrimBox/BleedBox).
- [feedback_design_end_to_end_workflow.md](feedback_design_end_to_end_workflow.md) — ★ "design X" → Design does it all → hand back ONE Google Drive link per piece. Dev proofs carry trim/safe guides; "my Zoo files" = clean CMYK PDFs, no guides.
- [feedback_over_status_line.md](feedback_over_status_line.md) — ★ END EVERY REPLY with a status line: `🟢 <Role> — OVER` idle / `🟡 <Role> — working`. Watcher ticks included.
- [feedback_repeat_portal_link_every_save.md](feedback_repeat_portal_link_every_save.md) — ★ Every "Portal — OVER" sign-off carries the picker link as a markdown [text](url) anchor — bare URLs don't tap on his phone.
- [feedback_always_paste_preview_link.md](feedback_always_paste_preview_link.md) — ALWAYS paste the clickable URL for anything DJ must open — every message, not just the first. He's on a phone.
- [feedback_api_keys_via_file.md](feedback_api_keys_via_file.md) — API keys: DJ puts them in a dedicated FILE + tells me the path — NEVER paste in chat.
- [feedback_bash_tmp_not_persistent.md](feedback_bash_tmp_not_persistent.md) — /tmp resets between Bash calls. Pipe gh download→python edit→save to /c/Users/dj/ in ONE call.
- [feedback_bidirectional_creation_links.md](feedback_bidirectional_creation_links.md) — Anything that CREATES something builds BOTH-direction tappable links (origin↔created).
- [feedback_brand_dark_blue_accents.md](feedback_brand_dark_blue_accents.md) — DJ loves DARK BLUE accents (#1e5aa8) on docs/PDFs/UI — default brand accent (blue, not plum).
- [feedback_call_opens_dialer_never_dials.md](feedback_call_opens_dialer_never_dials.md) — No Call button dials on tap; every Call opens v2_dialer.html PREFILLED. Only the dialer's Dial button posts /owner/voice/dial.
- [feedback_chatter_format.md](feedback_chatter_format.md) — chatter message_post = pipe-separated PLAIN text, no HTML tags (Odoo escapes them).
- [feedback_company_name_no_a.md](feedback_company_name_no_a.md) — Brand = "Window & Solar Care" — the folder's "A" prefix is NOT part of the name.
- [feedback_confirmation_policy.md](feedback_confirmation_policy.md) — When to ask DJ vs act: routine never ask; only irreversible/destructive/visible-to-others.
- [feedback_disable_pull_to_refresh.md](feedback_disable_pull_to_refresh.md) — BANNED: mobile pull-to-refresh (reloads the SPA + wipes state).
- [feedback_done_jobs_definition.md](feedback_done_jobs_definition.md) — "Done jobs" = x_studio_x_studio_workiz_status='Done' on sale.order.
- [feedback_wsc_email_from_domain.md](feedback_wsc_email_from_domain.md) — CRITICAL: W&SC emails set email_from='windowandsolarcare@gmail.com' — Odoo routes by from-match; blank/wrong leaks under scenicartprint.com.
- [feedback_email_draft_first_always.md](feedback_email_draft_first_always.md) — ALWAYS prepare emails as Gmail DRAFTS for DJ to send himself — never SMTP-send directly, even on "yes/send".
- [feedback_email_via_odoo.md](feedback_email_via_odoo.md) — Send emails via Odoo mail.mail JSON-RPC — Gmail MCP only drafts.
- [feedback_field_html_js_syntax_check.md](feedback_field_html_js_syntax_check.md) — ALWAYS `node --check` field.html JS before pushing.
- [feedback_field_readability_sunlight.md](feedback_field_readability_sunlight.md) — DJ has limited vision + works in bright sun → all field/owner UI large-text, high-contrast, sunlight-readable.
- [feedback_gh_push_empty_file_guard.md](feedback_gh_push_empty_file_guard.md) — Before any raw gh api PUT, verify b64 len (<1000→abort) — an empty push crashes app boot.
- [feedback_github_deploy_from_bash.md](feedback_github_deploy_from_bash.md) — GitHub deploy from Claude Code needs a `powershell -Command` wrapper, not raw bash/Python.
- [feedback_github_deploy_python_fallback.md](feedback_github_deploy_python_fallback.md) — If bash+powershell base64 gives "Problems parsing JSON" 400, switch to Python (base64.b64encode + json.dump).
- [feedback_github_deployment_bash.md](feedback_github_deployment_bash.md) — CANONICAL: bash + base64 + temp file for GitHub deploys.
- [feedback_hist_modal_activejob_null.md](feedback_hist_modal_activejob_null.md) — Never setTimeout-clear activeJob after openNoteModal() — submitNote() checks it first, silently fails.
- [feedback_ios_date_input_appearance.md](feedback_ios_date_input_appearance.md) — iOS: a styled <input type=date> with -webkit-appearance:none won't open/change.
- [feedback_local_vs_deployed_drift.md](feedback_local_vs_deployed_drift.md) — The local Saunders Render App copy can lag deployed — fetch the live file before a push.
- [feedback_multiagent_collision_field_html.md](feedback_multiagent_collision_field_html.md) — Real 2-agent field.html collision: a small change reverted by a bigger concurrent push (the line-count guard misses it).
- [feedback_never_send_dj_to_odoo.md](feedback_never_send_dj_to_odoo.md) — ★ GOVERNING: DJ/users NEVER touch Odoo. The Render app is THE UI; every field needs a Render pathway. "Go into Odoo" = a bug.
- [feedback_assistant_use_app_workflow_not_raw_api.md](feedback_assistant_use_app_workflow_not_raw_api.md) — ★ GOVERNING: DO ops via the app's OWN endpoints, never raw Odoo writes (they bypass logic/naming/defaults). Raw RPC only for read/diagnosis/cleanup.
- [feedback_never_remove_working_code.md](feedback_never_remove_working_code.md) — NEVER comment out/delete working code without DJ's explicit OK — adding is fine.
- [feedback_no_guessing_on_fields.md](feedback_no_guessing_on_fields.md) — NEVER guess Odoo field names — verify in CLAUDE.md/memory, or query Odoo first.
- [feedback_no_mutating_smoketest_payroll.md](feedback_no_mutating_smoketest_payroll.md) — Never POST a mutating payroll endpoint to test it exists — use deploy status / read-only routes.
- [feedback_no_re_listing.md](feedback_no_re_listing.md) — Don't re-print tables/lists across turns. Write to a working file (4_Reference_Data/), reference by name.
- [feedback_odoo_verify_content_not_status.md](feedback_odoo_verify_content_not_status.md) — ★ Odoo HTTP 200 ≠ success (denied serves placeholder/error page at 200). Verify by CONTENT, not status.
- [feedback_odoo_html_field_colors.md](feedback_odoo_html_field_colors.md) — Colored status indicators = HTML field type + Bootstrap classes (text-success/danger/warning).
- [feedback_odoo_reserved_variable_names.md](feedback_odoo_reserved_variable_names.md) — NEVER name a var `response`/`result` in Odoo 19 server actions — reserved eval vars (Response crash).
- [feedback_odoo_rpc_write_pattern.md](feedback_odoo_rpc_write_pattern.md) — odoo_rpc write(): vals dict INSIDE the args list — [[id],{vals}] — not a 4th kwarg.
- [feedback_ported_means_twilio.md](feedback_ported_means_twilio.md) — "ported"/"ported numbers" = Twilio ported phone numbers (not a generic "port the data over").
- [feedback_planning_constraints.md](feedback_planning_constraints.md) — Filter all architecture through 4 constraints: no new Odoo seats, no custom models, one Odoo instance, must scale across businesses.
- [feedback_proactive_inefficiency_capture.md](feedback_proactive_inefficiency_capture.md) — I own catching trial-and-error patterns + saving the fix immediately — no asking, no waiting.
- [feedback_python_patch_escaping.md](feedback_python_patch_escaping.md) — NEVER use '\\n' in Python patch replacement strings — embeds real newlines → SyntaxError.
- [feedback_regression_guard_pushes.md](feedback_regression_guard_pushes.md) — READ before any push to dashboard.py / large files (stale-overwrite guard).
- [feedback_push_compare_and_swap.md](feedback_push_compare_and_swap.md) — PUT with the sha you READ at, never a fresh one — concurrent change 409s instead of clobbering.
- [feedback_question_when_big_picture_wrong.md](feedback_question_when_big_picture_wrong.md) — ★ TOP judgment rule: repetition across files = STOP and ASK. Don't mechanically duplicate NOR unilaterally refactor working code (34-launcher incident).
- [feedback_reuse_canonical_endpoint.md](feedback_reuse_canonical_endpoint.md) — Don't duplicate logic for a new UI entry — call the canonical endpoint (extend if needed).
- [feedback_removing_element_leaves_dangling_ref.md](feedback_removing_element_leaves_dangling_ref.md) — Removing an HTML element but leaving a JS getElementById('X').prop ref crashes init.
- [feedback_render_claude_number_options.md](feedback_render_claude_number_options.md) — Render Claude presents choices as a NUMBERED list (DJ replies with a number — he's on a phone).
- [feedback_render_cron_autodeploy.md](feedback_render_cron_autodeploy.md) — Render cron autoDeploy=yes fires on every push → duplicate emails.
- [feedback_render_env_var_patch_not_put.md](feedback_render_env_var_patch_not_put.md) — NEVER PUT Render env-vars (wipes unspecified). POST per-var, or fetch+merge+PUT the full list.
- [feedback_report_gray_lines.md](feedback_report_gray_lines.md) — Every emailed P&L/financial report needs a light-gray line under every line item (phone readability).
- [feedback_route_work_to_claude_code.md](feedback_route_work_to_claude_code.md) — Default ALL work to Claude Code (flat Max sub, no marginal $).
- [feedback_mirror_memory_to_github.md](feedback_mirror_memory_to_github.md) — ★ Writing/editing ANY memory → also mirror to Odoo-Migration/memory/<name> via gh api Contents PUT (fetch sha first). Never git push (main protected).
- [feedback_save_filter.md](feedback_save_filter.md) — DJ wants auto-saves (no slash command). Filter SHARED_MEMORY writes to runtime-relevant facts only.
- [feedback_script_insertion_anchor.md](feedback_script_insertion_anchor.md) — Never rfind('</script>') — it hits the last external script tag.
- [feedback_send_email_with_attachment.md](feedback_send_email_with_attachment.md) — Pattern for sending email + PDF attachment via Odoo JSON-RPC.
- [feedback_status_update_format.md](feedback_status_update_format.md) — "status update"/"what's open" = condensed last-~3–4 hr recap grouped Shipped / Waiting-on-you / Open.
- [feedback_spoken_friendly_responses.md](feedback_spoken_friendly_responses.md) — DJ has replies read aloud → default PLAIN spoken style: short sentences, no bold/tables/symbols.
- [feedback_test_like_real_app_before_delivering.md](feedback_test_like_real_app_before_delivering.md) — An app mimicking a known product (Vault=Evernote): TEST against that product's core behaviors before delivering.
- [feedback_verify_limits_before_declaring.md](feedback_verify_limits_before_declaring.md) — Before telling DJ "I can't do X" (esp. cloud reach), TEST the call first — don't declare a limit from a stale doc.
- [feedback_use_sonnet_for_routine.md](feedback_use_sonnet_for_routine.md) — Model: OPUS for Render-app edits + accounting (regression/financial risk); Sonnet for routine.
- [feedback_workiz_no_job_all.md](feedback_workiz_no_job_all.md) — NEVER use the Workiz job/all/ endpoint (DJ's rule).
- [feedback_saunders_printing_never_send.md](feedback_saunders_printing_never_send.md) — NEVER send any Saunders Printing invoice/email without DJ's explicit OK.
- [feedback_auditor_user_perspective_gapfinder.md](feedback_auditor_user_perspective_gapfinder.md) — ★ Auditor = USER-perspective gap-finder: uses the app as a real person, hunts what the PLAN missed (edit/delete/edge/missing Add). Run before calling user-facing work done.
- [feedback_dj_owns_cheryl_erp_access.md](feedback_dj_owns_cheryl_erp_access.md) — ★ GOVERNANCE: DJ progressively grants Cheryl more owner/ERP access as HE chooses. Surface a scope concern ONCE, don't relitigate. company_id fails-open holds.
- [feedback_drop_link_table.md](feedback_drop_link_table.md) — ★ DROP the end-of-reply link TABLE (fed Cheryl's "too many interfaces"). Keep ONE relevant link + the OVER line.
- [feedback_hud_cards_live_not_inbox.md](feedback_hud_cards_live_not_inbox.md) — ★ HUD/status cards must be LIVE-DERIVED every render (a dashboard), never a stored inbox that goes stale. Persist only STATUS.
- [feedback_escalate_to_dj_sparingly.md](feedback_escalate_to_dj_sparingly.md) — ★ Reach DJ only when REALLY needed (only-he-can-decide/money/customer-facing/blocked); else make the call + report in one line.
- [feedback_check_endpoint_map_first.md](feedback_check_endpoint_map_first.md) — ★ Any endpoint lookup/build/review → CHECK 3_Documentation/ENDPOINT_MAP.md FIRST (method/path/LIVE-vs-DEAD/file:line/auth), not router code. Kept living by push-gate + backstop.
- [feedback_durable_watcher_not_session_cron.md](feedback_durable_watcher_not_session_cron.md) — ★ Durable must-always-run work = SERVER-SIDE Render APScheduler, NEVER a session cron (7-day expiry + dies on exit). Session crons only for a session's own presence (heartbeat/mail-watcher; self-re-arm).
