# Memory Index (TOC)

Detail lives in topic files. This index is sharded by domain — open the sub-index for the area you're working in, or `Grep` the memory dir. 290 topic memories across 11 domains + 47 standing rules.

> **Maintaining this index (read before adding a memory):** put the new one-line hook in the matching `idx_<domain>.md` — NOT here. Keep hooks ≤~145 chars (detail goes in the topic file). Only touch THIS file to add a `feedback_*` standing rule or a brand-new domain shard. This keeps MEMORY.md small enough to fully load every session (the whole reason it's sharded — restructured 2026-07-10 from one 147 KB flat list that only ~1/6 loaded). Re-shard script: `scratchpad/reindex_memory.py`; full pre-split backup: `MEMORY_full_backup_2026-07-10.md`.

## Domain sub-indexes

- [Field app (field.html / job detail)](idx_field_app.md) — 28 — `idx_field_app.md`
- [Scheduling & Command Center](idx_scheduling.md) — 35 — `idx_scheduling.md`
- [Outreach / reactivation / CRM](idx_outreach_crm.md) — 33 — `idx_outreach_crm.md`
- [My Day & tasks](idx_myday.md) — 10 — `idx_myday.md`
- [Vault / Notes / Drive](idx_vault_notes.md) — 28 — `idx_vault_notes.md`
- [Odoo quirks & fields](idx_odoo.md) — 19 — `idx_odoo.md`
- [Workiz / phases / sync](idx_workiz_sync.md) — 35 — `idx_workiz_sync.md`
- [Infra / deploy / GitHub / Render](idx_infra_deploy.md) — 47 — `idx_infra_deploy.md`
- [Saunders Printing (NBHOF)](idx_saunders_printing.md) — 17 — `idx_saunders_printing.md`
- [Business & personal](idx_business.md) — 14 — `idx_business.md`
- [Misc](idx_misc.md) — 24 — `idx_misc.md`

## ★ Standing rules (how DJ wants me to work) — always honor

- [feedback_activity_notes_self_contained.md](feedback_activity_notes_self_contained.md) — Activity notes: embed memory content (no link), but anything with a real URL (Workiz/Odoo/Calendly/GitHub/etc) MUST be a proper <a href> anchor.
- [feedback_agent_handoff_via_doc.md](feedback_agent_handoff_via_doc.md) — Agent handoffs: ALL instructions go in a doc (3_Documentation/*_BRIEF.md); DJ gets only a 1-2 sentence paste paragraph with the doc path.
- [project_agent_mail_channel.md](project_agent_mail_channel.md) — ★ Lead↔specialists comms = 3_Documentation/AGENT_MAIL.md (app repo). DJ's one-word "mail" = go read it. Read at session start + after each task; write there, not through DJ.
- [feedback_agent_mail.md](feedback_agent_mail.md) — Read 3_Documentation/AGENT_MAIL.md at session start + after every task; write cross-session messages THERE. DJ's nudge = "mail". Decisions still via DJ.
- [feedback_agent_mail_autowatch.md](feedback_agent_mail_autowatch.md) — ★ At SESSION START arm a CronCreate ~7-min mail-watcher (if not already, check CronList) so the session self-checks AGENT_MAIL — no manual "mail" nudge. PushNotification DJ only for → DJ entries; push immediately when you post one. Session-local, re-arm each start.
- [feedback_over_status_line.md](feedback_over_status_line.md) — ★ END EVERY REPLY with a status line: `🟢 <Role> — OVER` when idle/open, `🟡 <Role> — working` when not. Watcher ticks included.
- [feedback_repeat_portal_link_every_save.md](feedback_repeat_portal_link_every_save.md) — ★ EVERY "Portal — OVER" sign-off (incl. watcher ticks) must carry the picker link as a markdown [text](url) anchor — bare/backticked URLs don't tap on his phone.
- [feedback_always_paste_preview_link.md](feedback_always_paste_preview_link.md) — ALWAYS paste the clickable URL when referencing anything DJ must open (preview/artifact/report) — every message, not just the first. He's on a phone.
- [feedback_api_keys_via_file.md](feedback_api_keys_via_file.md) — When I need an API key, DJ puts it in a dedicated FILE and tells me the path — NEVER paste in chat (he pasted his Render + live Stripe keys…
- [feedback_bash_tmp_not_persistent.md](feedback_bash_tmp_not_persistent.md) — /tmp resets between Bash calls. Pipe gh download→python edit→save to /c/Users/dj/ in ONE call.
- [feedback_bidirectional_creation_links.md](feedback_bidirectional_creation_links.md) — STANDING RULE (DJ 2026-07-06): anytime ANYTHING creates something, build BOTH-direction tappable links (origin↔created), not just a provenance…
- [feedback_brand_dark_blue_accents.md](feedback_brand_dark_blue_accents.md) — DJ loves DARK BLUE accents (#1e5aa8) on generated docs/PDFs/UI — make it the default brand accent (blue, not plum).
- [feedback_call_opens_dialer_never_dials.md](feedback_call_opens_dialer_never_dials.md) — STANDING RULE: no Call button may dial on tap; every Call opens v2_dialer.html PREFILLED (?to=/?name=/?partner_id=). Only the dialer's own Dial button posts /owner/voice/dial. DJ misfires taps + must dial on the business line.
- [feedback_chatter_format.md](feedback_chatter_format.md) — All chatter message_post calls must use pipe-separated plain text — no HTML tags (Odoo escapes them in both server actions and Zapier JSON-RPC)
- [feedback_company_name_no_a.md](feedback_company_name_no_a.md) — Company name is "Window & Solar Care" — folder has "A" prefix but that is NOT part of the brand name.
- [feedback_confirmation_policy.md](feedback_confirmation_policy.md) — When to ask DJ for confirmation vs. just act (routine tasks: never ask;
- [feedback_disable_pull_to_refresh.md](feedback_disable_pull_to_refresh.md) — BANNED: mobile pull-to-refresh on every page (it reloads the SPA + wipes state — DJ hates it).
- [feedback_done_jobs_definition.md](feedback_done_jobs_definition.md) — "Done jobs" always = x_studio_x_studio_workiz_status = 'Done' on sale.order.
- [feedback_wsc_email_from_domain.md](feedback_wsc_email_from_domain.md) — CRITICAL: W&SC customer emails MUST set email_from='windowandsolarcare@gmail.com' — Odoo has 2 send servers (W&SC + Saunders dan@scenicartprint.com), routes by from-match; a blank/wrong from leaks out under scenicartprint.com.
- [feedback_email_draft_first_always.md](feedback_email_draft_first_always.md) — ALWAYS prepare emails as Gmail DRAFTS for DJ to review + send himself — NEVER send directly via SMTP, even if he says "yes/send" to a "want me…
- [feedback_email_via_odoo.md](feedback_email_via_odoo.md) — Always send emails via Odoo mail.mail JSON-RPC — Gmail MCP can only draft, not send
- [feedback_field_html_js_syntax_check.md](feedback_field_html_js_syntax_check.md) — ALWAYS run node --check on field.html JS before pushing.
- [feedback_field_readability_sunlight.md](feedback_field_readability_sunlight.md) — DJ has limited vision + works outdoors in bright sun → ALL field/owner UI must be large-text + high-contrast with a genuinely sunlight-readable…
- [feedback_gh_push_empty_file_guard.md](feedback_gh_push_empty_file_guard.md) — Before any raw gh api PUT, verify b64 length (<1000 → abort) — a missing/empty local file silently pushes EMPTY and crashes app boot (new_job.py…
- [feedback_github_deploy_from_bash.md](feedback_github_deploy_from_bash.md) — GitHub deployment from Claude Code requires powershell -Command wrapper, not raw bash/Python
- [feedback_github_deploy_python_fallback.md](feedback_github_deploy_python_fallback.md) — When bash+powershell base64 returns "Problems parsing JSON" HTTP 400, switch to Python (base64.b64encode + json.dump).
- [feedback_github_deployment_bash.md](feedback_github_deployment_bash.md) — CANONICAL: Use bash + base64 + temp file for GitHub deployments.
- [feedback_hist_modal_activejob_null.md](feedback_hist_modal_activejob_null.md) — Never setTimeout-clear activeJob after openNoteModal() — submitNote() checks it first and silently fails.
- [feedback_ios_date_input_appearance.md](feedback_ios_date_input_appearance.md) — iOS bug: a styled <input type=date> with -webkit-appearance:none won't open/change.
- [feedback_local_vs_deployed_drift.md](feedback_local_vs_deployed_drift.md) — 2026-04-27: Local Saunders Render App copy can lag deployed.
- [feedback_multiagent_collision_field_html.md](feedback_multiagent_collision_field_html.md) — Real 2-agent collision on field.html: a small card-wrapper change got silently reverted by a bigger concurrent push (the line-count guard misses…
- [feedback_never_send_dj_to_odoo.md](feedback_never_send_dj_to_odoo.md) — ★ GOVERNING: DJ/users NEVER touch Odoo (backend DB, invisible). The Render app is THE UI; every field needs a Render pathway. "Go into Odoo" = a bug to fix, never an answer.
- [feedback_assistant_use_app_workflow_not_raw_api.md](feedback_assistant_use_app_workflow_not_raw_api.md) — ★ GOVERNING: when DJ asks me AS ASSISTANT to DO an op with an app workflow (create customer/job, schedule, send, pay), CALL the app's own endpoints (same routes the phone uses) — never raw Odoo writes, which bypass scheduling logic/naming/defaults/confirmation. Raw RPC only for read/diagnosis/cleanup. No computer-use needed — call the HTTP endpoints.
- [feedback_never_remove_working_code.md](feedback_never_remove_working_code.md) — NEVER comment out or delete existing working code without DJ's explicit approval — adding is fine, removing requires asking first
- [feedback_no_guessing_on_fields.md](feedback_no_guessing_on_fields.md) — NEVER guess Odoo field names. Verify in CLAUDE.md, memory files, or query Odoo first.
- [feedback_no_mutating_smoketest_payroll.md](feedback_no_mutating_smoketest_payroll.md) — Never POST a mutating payroll endpoint to test it exists — use Render deploy status / read-only routes.
- [feedback_no_re_listing.md](feedback_no_re_listing.md) — Don't re-print tables/lists/buckets across turns. Write to a working file (typically 4_Reference_Data/), reference by name, keep chat terse.
- [feedback_odoo_verify_content_not_status.md](feedback_odoo_verify_content_not_status.md) — ★ On Odoo HTTP 200 ≠ success (denied /web/image serves placeholder.png 200; reserved routes serve an error page 200). Verify by CONTENT, never status alone.
- [feedback_odoo_html_field_colors.md](feedback_odoo_html_field_colors.md) — How to create colored status indicators using HTML field type + Bootstrap classes (text-success/text-danger/text-warning).
- [feedback_odoo_reserved_variable_names.md](feedback_odoo_reserved_variable_names.md) — NEVER use response or result as variable names in Odoo 19 server actions — they are reserved eval context vars (causes Response object crash)
- [feedback_odoo_rpc_write_pattern.md](feedback_odoo_rpc_write_pattern.md) — READ before writing any odoo_rpc write() call. vals dict must be INSIDE args list: [[id], {vals}] — NOT as 4th kwarg arg.
- [feedback_ported_means_twilio.md](feedback_ported_means_twilio.md) — "ported"/"ported numbers" ALWAYS = Twilio ported phone numbers (never a generic 'port the data over' concept). Reactivation is TEXT via Workiz until ported.
- [feedback_planning_constraints.md](feedback_planning_constraints.md) — Filter ALL architecture suggestions through 4 constraints: no new Odoo seats, no custom models, one Odoo instance, must scale across businesses
- [feedback_proactive_inefficiency_capture.md](feedback_proactive_inefficiency_capture.md) — I own responsibility to recognize trial-and-error patterns and save solutions immediately — no asking DJ, no waiting for end of session.
- [feedback_python_patch_escaping.md](feedback_python_patch_escaping.md) — NEVER use '\\n' in Python patch replacement strings — embeds actual newlines → SyntaxError.
- [feedback_regression_guard_pushes.md](feedback_regression_guard_pushes.md) — READ before any push to dashboard.py or other large files.
- [feedback_question_when_big_picture_wrong.md](feedback_question_when_big_picture_wrong.md) — ★ MOST IMPORTANT judgment rule: repetition across files = STOP and ASK, don't grind. When a task's shape looks structurally wrong (same edit in N places), ask DJ before executing — don't mechanically duplicate NOR unilaterally refactor working code. (34-launcher incident.)
- [feedback_reuse_canonical_endpoint.md](feedback_reuse_canonical_endpoint.md) — Don't duplicate existing logic for a new UI entry point — call the canonical endpoint (extend it if missing something), so there's ONE place to maintain.
- [feedback_removing_element_leaves_dangling_ref.md](feedback_removing_element_leaves_dangling_ref.md) — Removing an HTML element but leaving a JS getElementById('X').prop ref crashes init → whole app stuck/error screen.
- [feedback_render_claude_number_options.md](feedback_render_claude_number_options.md) — Render Claude must ALWAYS present choices as a NUMBERED list (customers/services/statuses) so DJ replies with a number — he's on a phone, won't…
- [feedback_render_cron_autodeploy.md](feedback_render_cron_autodeploy.md) — Render cron autoDeploy=yes fires on every commit push → duplicate emails.
- [feedback_render_env_var_patch_not_put.md](feedback_render_env_var_patch_not_put.md) — NEVER PUT Render env-vars (wipes all unspecified keys). Use POST per-var or fetch+merge+PUT.
- [feedback_render_put_env_vars.md](feedback_render_put_env_vars.md) — CRITICAL: Render PUT /env-vars wipes ALL vars. Always GET first, merge, then PUT full list.
- [feedback_report_gray_lines.md](feedback_report_gray_lines.md) — Every P&L/financial report emailed to DJ needs a light-gray line under EVERY line item (phone readability).
- [feedback_route_work_to_claude_code.md](feedback_route_work_to_claude_code.md) — Default ALL work to Claude Code (me = flat Max sub, no marginal $).
- [feedback_mirror_memory_to_github.md](feedback_mirror_memory_to_github.md) — ★ When you write/edit ANY memory, ALSO mirror it to GitHub Odoo-Migration/memory/<name> via `gh api` Contents PUT (fetch sha first) — NEVER git push (main is protected). In addition to the SHARED_MEMORY dual-write.
- [feedback_save_filter.md](feedback_save_filter.md) — DJ wants auto-saves (no slash command). Filter SHARED_MEMORY writes — only runtime-relevant facts go there;
- [feedback_script_insertion_anchor.md](feedback_script_insertion_anchor.md) — Never use rfind('</script>') — finds last external script tag.
- [feedback_send_email_with_attachment.md](feedback_send_email_with_attachment.md) — Full pattern for sending email + PDF attachment via Odoo JSON-RPC.
- [feedback_status_update_format.md](feedback_status_update_format.md) — When DJ asks for a "status update"/"what's open"/"update me": condensed recap of just the last ~3-4 hrs, grouped Shipped / Waiting-on-you / Open. Not long-term, not how-solved detail.
- [feedback_spoken_friendly_responses.md](feedback_spoken_friendly_responses.md) — DJ has his phone READ replies aloud while working, so default to a PLAIN spoken-friendly style: short sentences, no bold/tables/symbols/emoji…
- [feedback_test_like_real_app_before_delivering.md](feedback_test_like_real_app_before_delivering.md) — When building an app that mimics a known product (Vault=Evernote), TEST it against that product's core behaviors…
- [feedback_use_sonnet_for_routine.md](feedback_use_sonnet_for_routine.md) — Model choice: OPUS for Render-app edits + accounting structure (regression/financial risk);
- [feedback_workiz_no_job_all.md](feedback_workiz_no_job_all.md) — NEVER use Workiz job/all/ endpoint. DJ's explicit rule (2026-05-04).
- [feedback_saunders_printing_never_send.md](feedback_saunders_printing_never_send.md) — NEVER send any Saunders Printing invoice/email without DJ explicitly approving (a prior session sent to a vendor early).
