---
name: project_system_roadmap
description: "DJ's prioritized 'complete the system' roadmap (2026-06-17). ~16 build items toward an end-to-end autonomous ops system. CHECK alongside project_open_tasks at session start when DJ asks 'what's next'."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ asked (2026-06-17) for a dozen+ things to make the system 'complete' and said to keep this where future Claude Code sessions can find it.** Vision = end-to-end autonomous business ops: intake → schedule → execute → pay → bookkeep → retain → grow, automated with approve-first human gates, run from his phone. This is the canonical roadmap; pair with [[project_open_tasks]] (running task list) and [[project_accounting_master_plan]].

## Reliability (system runs the business → fragility = lost money)
1. **Finish Zapier → Render migration (Phases 3/4/5/6).** Highest leverage. Zapier is just a webhook catcher that fetches GitHub; Render does it better, no per-task cost, faster. Prereq for #7 and cleaner #5. ~½ day. [[project_zapier_to_render_migration]]
2. **Health/monitor surface.** `/owner/health` tile: last deploy status, last Phase-4 poll, APScheduler last-tick per job, Odoo+Workiz reachability + daily push if stale. Kills silent `update_failed`/502 forensics. [[project_render_deploy_failed_check]] [[project_render_502_uptime_fixes]]
3. **Kill Notes OAuth fragility.** Google OAuth token dies ~7 days (app still "Testing") → every note 500s. Publish to Production + auto-refresh. [[project_notes_google_oauth]]
4. **Test/staging path.** Everything is prod (why a mistimed /act snoozed a live customer, a smoke-test clocked out a real shift). Staging Render service or `?dry_run=1` convention on mutating endpoints. [[feedback_no_mutating_smoketest_payroll]]

## Growth (close the revenue loop)
5. **Review engine after Done jobs (Twilio A2P).** Biggest unbuilt growth lever. Needs A2P 10DLC Standard Low-Volume under Saunders EIN — START PAPERWORK NOW (long approval). `Done` event → review-request text → Google review. [[project_twilio_a2p_and_entity]] [[project_ai_growth_seo_website]]
6. **WordPress → Odoo Website + SEO.** Website module already installed (no new cost). Migrate w/ 301 redirects, then AI-assisted SEO/content. Compounding.
7. **Employee referral program.** Text + $250 incentive + webhook tracking already designed; needs #1 first. [[project_employee_referral_program]]

## Financial closure (books match reality)
8. **Opening balances + finish accounting bridge.** Opening balances + 2 credit cards still pending; validation target real Chase ≈ $1,000. Until done, P&L isn't trustworthy. [[project_accounting_master_plan]]
9. **Recurring auto-bookkeeping.** Weekly worked-on report + monthly P&L + cash-EXPENSE capture (cash income already handled). Claude Code wake-up, not Render cron. [[project_recurring_bookkeeping_plan]]
10. **Fix Stripe abandoned-checkout stranded invoice.** Link flow posts invoice before payment → abandoned checkout = posted/unpaid invoice that blocks sync + re-invoicing. Fix ordering + add test mode. [[project_stripe_abandoned_checkout_strands_invoice]]

## Data integrity (trust the data)
11. **Workiz ↔ Odoo reconciliation sweep + tool.** Recurring audit flagging Workiz-only jobs, orphaned future jobs, posted-invoice-blocked deletes; finish pending Bev Hartin cleanup. [[project_workiz_jobs_not_in_odoo]]
12. **Finish at-source job provenance.** 15-min scanner covers forward; precise at-source stamp in reactivation/New Job/duplicate/Phase 3 still TODO. [[project_job_creation_provenance]]

## NEW — DJ additions 2026-06-17
13. **AI answers inbound TEXTS and PHONE CALLS (AI receptionist).** ★ DJ-requested.
    - **Inbound SMS auto-answer:** customer texts the business number → AI reads it, answers (pricing/scheduling/"are you coming today"), books or reschedules using the shared scheduler brain (`rank_days`/day-plan to offer REAL open slots), or escalates to DJ. Also handles reactivation replies (today DJ books those by hand from the Sent tab).
    - **Inbound VOICE:** AI voice receptionist for missed / after-hours calls — answer, qualify, book or take a message, text a booking link. Twilio Voice + realtime voice model.
    - Depends on/overlaps #5's Twilio A2P (SMS) + a Twilio Voice number. Start approve-first (draft reply → DJ taps send), graduate to autonomous. MUST honor Do-Not-Contact/STOP [[project_do_not_contact_forward_looking]].
14. **Revisit Render Claude — make him better.** ★ DJ-requested. The field assistant (API $, phone). Audit + upgrade: tighten SYSTEM_PROMPT, review his tool set + close capability gaps (give him the customer "brain", `rank_days`, etc.), enforce numbered-list UX everywhere [[feedback_render_claude_number_options]], reconsider model/cost, reliability. Folds in #15. [[feedback_route_work_to_claude_code]]

## Smaller polish
15. **Unify the last scheduler fork** — point phone `find_next_opening` at `rank_days` so there's ONE scheduling brain. [[project_shared_scheduler]]
16. **Reactivation `initialized` field** — stop brand-new customers surfacing on the reactivation report before they've ever lapsed. [[project_reactivation_initialized_field]]

## DJ's "start with three"
#1 Render migration (unlocks #5/#7, removes a platform), #5 A2P paperwork (start today — long pole on reviews AND on #13), #8 opening balances (makes the money real).
