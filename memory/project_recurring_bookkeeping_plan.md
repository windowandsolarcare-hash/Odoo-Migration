---
name: project_recurring_bookkeeping_plan
description: The agreed plan for recurring (weekly/monthly) automated bookkeeping + the cash-expense gap. Approved design, NOT yet built — DJ said wait/review first (2026-06-08).
metadata:
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Recurring Bookkeeping Automation — agreed plan (2026-06-08, NOT yet built)

DJ wants the bookkeeping (categorize + reconcile) to run on a schedule so he doesn't have to say "go do it." Reviewed but **not built** — DJ chose "wait, I'll review first." See master plan [[project_accounting_master_plan]].

## Run mechanism: Claude Code wake-up, NOT Render
DJ chose the **Claude Code self-scheduled wake-up** so the recurring run gets real reasoning (not a deterministic Render script).
- **Laptop is ALWAYS ON** (2026-06-08) — DJ runs CC from the road via remote control, so the machine stays up. This removes the "wake-up only fires if machine is on" worry.
- Still make every run **catch-up based** (process EVERYTHING since last successful run via a `last_run` marker) and self-renew the schedule each run, as a safety net.
- **MODEL: run on Sonnet, not Opus** — DJ is cost/subscription conscious (2026-06-08). The recurring runs are where ongoing token spend lives → use Sonnet. See [[feedback_use_sonnet_for_routine]].

## Weekly deliverable — "Bookkeeping — week of …" email (NOT a P&L)
DJ explicitly does NOT want a weekly P&L. He wants a "what I worked on this week" report:
- ✅ **Auto-categorized:** count + $ (the obvious, already done by `categorize_engine.py`)
- ⚠️ **Needs your decision:** unmatched / ambiguous, one line each with the ask
- 🔴 **Flags:** dupes, missing invoices, fee mismatches
- The ⚠️ queue is the "auto for obvious, ask on unclear" loop turned recurring — DJ just answers the weekly list; I clear it with judgment in-session/next wake-up.

## Monthly deliverable — P&L + written analysis
- P&L with gray separator lines [[feedback_report_gray_lines]], emailer `5_Accounting/pl_2024_2025.py`.
- PLUS a written analysis: this month vs last month, YoY same month, what drove the change.

## CASH — corrected by DJ (I had it backwards)
- **Cash INCOME is already handled.** Door payments processed as "cash" in the Render app already create the invoice + a cash payment in Odoo. No need to involve Workiz. Only tidy-up = ensure these post to **Cash on Hand (101406)** (one-time journal config — Cash journal id 18 → 101406), NOT a recurring job.
- **Cash EXPENSES are the real gap** — this is what DJ was actually asking about. Expenses he pays out of pocket in cash never hit any bank feed, so today they're invisible. Only source = DJ telling us.
  - The "cash cron" = a **recurring prompt: "any expenses paid in cash since last time?"** → book each as `Dr <expense account> / Cr 101406 Cash on Hand`. This also draws the till down so 101406 stays real.
  - **DECIDED (2026-06-08):** DJ logs cash expenses **in the Render field app as he spends** ("render for sure"). I book each from those entries as `Dr <expense> / Cr 101406`. Needs a small cash-expense entry form/endpoint in the field app.

## Status
APPROVED DESIGN, NOT BUILT. When DJ says go: (1) wire the Claude Code wake-up w/ catch-up marker, (2) weekly report builder, (3) monthly P&L+analysis, (4) cash-expense capture per his (a)/(b) choice, (5) confirm Cash journal 18 → 101406.
