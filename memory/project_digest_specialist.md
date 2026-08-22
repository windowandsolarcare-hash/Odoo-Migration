---
name: project_digest_specialist
description: "Second AI specialist LIVE 2026-07-26: routers/owner/specialist_digest.py = weekly 'chief of staff'. Read-only. Mondays it drops ONE attention card in the HUD summarizing money/jobs/needs-you/customers/goals/payroll; card → GET /owner/api/digest/view (full brief page). Fires via cron.py daily_sync (Monday guard)."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T20:45:58.686Z
---

**2026-07-26 — second specialist ([[project_operating_system_vision]], seam [[project_attention_feed_contract]]).** `routers/owner/specialist_digest.py` (registered in main.py, prefix /owner). DJ approved the section list as-is.

**What it does:** READ-ONLY "chief of staff." `build_digest(today)` computes 6 sections (each guarded), stores the brief JSON in `ir.config_parameter wsc.digest.brief`, and submits ONE **`attention`** card `id=digest:<ISO-week>` to the feed (title e.g. "Your week: $790 last week, 5 jobs ahead"; why_now = highlights; expires next Tue; action → the brief page). Attention cards carry no body, so the full brief is a separate PAGE. Sections + sources (all reused/audited):
- **Money** — `_rev(start,end)` = Done jobs (company 1, workiz_status Done, amount>0) summed; last week vs prior week vs YTD toward the goal. Goal = `ir.config_parameter wsc.digest.revenue_goal` (default $100k, DJ-editable).
- **Jobs** — count of confirmed SOs (state sale/done, company 1) with date_order this week.
- **Needs you / Unpaid** — confirmed SOs NOT Done/Canceled, amount>0, **date_order in [today-21d, today]** (MUST bound to past — an unbounded query counted 95 future scheduled jobs; bounded = 11/$1,885, correct).
- **Customers** — read cached `analytics_customer_cache` base (active/lapsed/leads); no expensive recompute.
- **Goals** — project.project (Goal tag) with x_goal_target_date + days-left countdown.
- **Payroll** — next biweekly period close via `specialist_payroll._period_for`.

**Endpoints (my lane):** `GET /owner/api/digest/view?week=` renders the full brief as a self-contained themed HTML page (big text, high-contrast, dark-aware — DJ readability). `POST /owner/api/digest/prepare {today?}` = manual/test trigger. **Trigger:** `run_weekly_trigger()` (Monday-only guard) hooked into `cron.py _run_daily_sync` (guarded), alongside the payroll trigger — fires every day, acts only Mondays.

**Verified live** (today=2026-07-27 Monday): brief correct — last week $790/5 jobs ▼, prior $1,905, YTD $46,286 of $100k (46%), 5 scheduled, unpaid 11/$1,885, active 364 / lapsed 180, office-move 5 days / hire 42 days, payroll next close. App booted after the main.py edit. Card appears in HUD (v2_hud.html) among payroll + the lead's myday card.

**FOLD-IN 2026-07-26 (DJ: "fold in"):** added the deferred rows + charts. **Needs-you** now also shows **Overdue to schedule** + **Upcoming to schedule** — `_maintenance(today)` counts Submitted next-jobs (`x_studio_x_studio_workiz_status='Submitted'`, company 1, state!=cancel, uuid set) via search_count: overdue = date_order in [today-365, today), upcoming = date_order >= today (same filter as api_scheduled_sos / the Submitted-jobs overdue scope). Live: overdue **156**, upcoming 15 (156 is real — matches the app's existing Submitted-overdue backlog). **Charts** (via shared **WSCChart** `v2_charts.js`, per the use-it-for-all-charts rule — it self-injects its wc-CSS on load): `_rev_trend(ref_mon,6)` → 6-week revenue horizontal `WSCChart.bars({money:true})`, and a `WSCChart.donut` goal ring (center "46%", Earned/To-go legend). Brief page includes `<script src="/static/owner/v2_charts.js">` + an inline render script fed `__REV__`/`__GOALY__` JSON; added `--ink-2/--ink-3/--sunk` vars (light+dark) so charts theme-match. Verified both charts render. Overdue count also added to the card's why_now highlights.

**Notes / open:** the `/api/digest/view` page is a stopgap I built in my lane; the lead's "briefing delivery" surface may fold it in later — repoint the card href then. Deferred to v2: overdue-maintenance / needs-scheduling section, charts (WSCChart), reactivation "ready" count (vs raw lapsed). Touched shared files: main.py + cron.py (both additive/guarded) — flag to lead. See [[project_payroll_specialist]], [[project_analytics_audit_base]].
