---
name: feedback_use_sonnet_for_routine
description: DJ is cost/subscription conscious — use Sonnet for routine accounting work, reserve Opus only for high-blast-radius judgment (opening balances / cutover).
metadata:
  node_type: memory
  type: feedback
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

**UPDATE 2026-06-08 (after checking `/usage`): use OPUS for Render-app edits + accounting structure; Sonnet only for genuinely mechanical low-risk work.** DJ's usage data showed a heavy Opus-dominated day (regression recovery, $53.64 API-equiv value) was only **10% of his weekly Max limit** — he has ample headroom; Opus will not push him into limits at his volume. The real cost drivers per the dashboard are **session length / >150k context (84%), subagent-heavy sessions (79%), and 8h+ sessions (79%)** — NOT model tier. So the bigger lever is session hygiene: `/compact` mid-task, `/clear` when switching tasks, keep sessions focused, spawn subagents deliberately. The 2026-06-08 regression (made under Sonnet — stale local + raw `gh api` bypassing the guard) is exactly the kind of high-blast-radius slip that justifies Opus on Render-app edits. NOTE on billing: the dollar figure in `/usage` is retail API-equivalent value, NOT money drained from the $100/mo Max plan — limits are %-based, not a dollar wallet. See [[feedback_regression_guard_pushes.md]].

**Original guidance (still valid for the cost ratio):** Default to Sonnet for routine accounting work; reserve Opus for the few high-blast-radius judgment calls. (DJ, 2026-06-08: "id rather not chew through my subscription if I can.") Opus ≈ 5× Sonnet per token, but DJ's absolute volume is low enough that this doesn't threaten his limits.

**Why:** DJ is cost-conscious about the CC subscription. Most remaining accounting work is pattern-execution with mechanics already documented in memory — Sonnet handles it. Opus's value is concentrated in subtle one-time structural decisions where a wrong assumption mis-states the whole balance sheet.

**How to apply:**
- **Sonnet is good enough for:** Stage 2 & 3 reconciliation (Check/Zelle/Credit Card → Outstanding Receipts), credit-card dedupe, categorization, the recurring weekly report, and the monthly P&L + analysis. See [[project_recurring_bookkeeping_plan]] / [[project_accounting_master_plan]].
- **Keep / flip up to Opus only for:** the **opening-balance / cutover design** ([[project_opening_balances_needed]]) — one-time, low token cost, high blast radius. We already had a near-miss (the date bug that doubled ~$97K of expenses before it was caught), which is exactly the kind of subtle trap to spend reasoning on.
- When I hit something I think genuinely warrants Opus, say so explicitly ("I'd flip to Opus for this one") and let DJ decide — don't silently burn Opus.
- Regardless of model, lean hard on verification (per-year P&L checks, audit-log CSVs) so a cheaper model never means looser books.
