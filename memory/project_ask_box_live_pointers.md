---
name: project_ask_box_live_pointers
description: Memory Ask box answers money/customer/history questions from LIVE Odoo data via routers/owner/memory_pointers.py (keyword/intent map → reused analytics/dashboard fns). QB retired = Odoo authoritative. Built 2026-09-09.
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T20:05:55.278Z
---

The 🧠 Memory Ask box (`/owner/api/memory/ask`, v2_memory.html) answers FINANCIAL + CUSTOMER/JOB-HISTORY questions from **live Odoo data**, alongside the stored-decision search. Built 2026-09-09 (Specialists, Lead-QC'd). **QuickBooks is RETIRED — Odoo is the authoritative books** (all financials company_id=1, no QB path, no migration caveat).

**Architecture — `routers/owner/memory_pointers.py`:** `ask_pointer(q)` = an ordered **keyword/intent map** (NO LLM — deterministic + debuggable), each intent → an EXISTING data source, returns a plain-English `live` dict `{source_label:'Live — from Odoo', answer, detail, intent, ...}` or `None`. `memory_store.ask()` calls it and returns `live` in the response; v2_memory.html renders a **"⚡ Live — from Odoo"** card ABOVE the stored hits (None → falls through to the stored search). All READ-ONLY. Intent order matters (specific first; AR before whos_due so "who is past due"=money not visits).

**REUSE (no rebuild):** revenue → dashboard `tool_get_sales`/`tool_get_sales_week`/`tool_get_sales_month`/`tool_check_unpaid_jobs`; YTD → `memory_store.financials_ytd(year)` (extracted; the /financials endpoint delegates); aggregates (active/lapsed/top-N/retention/new-vs-lost/LTV) → `analytics.compute_analytics()` (base/leaderboard/years); per-customer → `tool_search_customers` (name-resolve, "which one?" if ambiguous) + `tool_get_job_details`; did-X-pay → account.move `payment_state` (the reliable signal) + Stripe-gap note; last-service → sale.order `workiz_status='Done' AND date_order<=today` (NOT the next scheduled job).

**v1.5 P&L (Odoo IS the books):** net_profit / expenses(top categories) / cash-on-hand / fuel via `account.move.line read_group` on account-type accounts (expense/asset_cash), company 1. Deferred (costing-model gap, NOT QB): gross-margin-per-service, profit-per-hour.

**★ DATA-COMPLETENESS FINDING (surfaced to DJ 2026-09-09):** Odoo has revenue (~$53,738 YTD), operating expenses (~$11,760 across 15 categories, booked via **journal entries** not vendor bills — only 1 vendor bill all year, so query `account.move.line` on expense accounts, not `in_invoice`), and cash (~$66,655). **But PAYROLL/LABOR has ZERO postings** (Salaries/Wages accounts exist in the chart, empty). So "net profit" excludes the biggest cost → the net_profit answer is labeled **"Operating margin BEFORE labor … ⚠️ excludes payroll"** in the HEADLINE (not just detail). True net profit needs payroll booked into Odoo — DJ's call.

**★ TWO DEBUGGING LESSONS:**
1. **A wrong Odoo field/model in a handler behind a broad `try/except` presents as "no live answer," not an error** — `ask_pointer` swallows handler exceptions and returns None → the intent silently falls through. whos_due was dead because it queried `x_studio_next_job_date` on **sale.order**, but that field is on **res.partner** (CLAUDE.md field table — don't guess the model). When a pointer intent "matches but returns nothing," suspect a raising handler, not the keyword match. Repro the keyword match in Python AND run the handler's Odoo query directly (via the local `_odoo_key_val.txt` key) before trusting a fix.
2. Can't cookie-verify an owner-gated endpoint myself (never mint an owner cookie — Lead's QC domain); verify the two failure points instead — intent-match (pure Python) + the Odoo query (direct RPC).

See [[project_render_coalesces_rapid_pushes]], [[feedback_no_guessing_on_fields]], [[feedback_reuse_canonical_endpoint]], [[project_memory_pillar_phase1]].
