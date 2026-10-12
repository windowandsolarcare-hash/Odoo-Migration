---
name: project_saunders_invoice_rebuild_plan
description: "★ Saunders (co3) invoice rebuild plan (DJ 2026-10-12). 2025 NBHOF invoices ALREADY in Odoo (automation created them when DJ switched off QB mid-2025) — don't double-count. DJ wants FULL line-item invoice detail rebuilt back to 2024 (not just summary). 2024=clean rebuild; 2025=reconcile the seam; pre-2024=summary P&L JEs only."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T21:02:02.605Z
---

**★★ VERIFIED 2026-10-12 (supersedes the "2025 already in Odoo / reconcile the seam" plan below).** Two facts confirmed by direct query:
1. **QB CSV reconstruction is 100% complete and ties.** Parsed all invoices from the QB Transaction Detail CSV; every one of the 32 present invoices has line detail that sums EXACTLY to its header total (parser: `scratchpad/rebuild_invoices.py`). 2024 = 14 invoices $22,141.26 (#200201–200214); 2025 = 18 invoices $39,724.68 (#200216–200233, #200215 voided/missing). Customers: NBHOF (bulk) + International Spy Museum (1, #200230). Durable output saved to `C:/Users/dj/Documents/Business/Financial_Statements/Saunders_Printing/Invoice_Rebuild/` (saunders_invoice_rebuild.json + _lines.csv).
2. **Odoo co3 existing out_invoices = #200234–200246, ALL dated 2026** (automation set; 200242 is a $0 draft, 200237 gap). So the QB set **#200201–200233 (2024 AND 2025) is NOT in Odoo** and does NOT overlap the automation — they are sequential and disjoint. **There is NO 2025 cutover seam to reconcile** — the earlier belief that 2025 QB invoices already lived in Odoo was WRONG (the automation didn't start until 2026). The rebuild = the full QB set #200201–200233, which slots cleanly right before the automation's #200234. DJ decision (2026-10-12): wants full detailed invoices, NO 2025-shortcut, rejected the 1/1/2025 opening-balance/2024-as-summary cutover.

**REMAINING GATE:** writing the 32 invoices into Odoo co3 (records only, never sent) is a money-write blocked by the Accounting guardrail + Claude Code classifier — same block that stopped the opening-balance JE. Dataset is fully prepped & verified; awaiting DJ's green light on the Odoo write (one-time, additive, reversible).

---
_Original scoping (partially superseded — the 2025 reconcile step is moot per above):_

**DJ 2026-10-12, scoping the Saunders Printing (Odoo company 3) rebuild.** Builds on [[project_saunders_qb2010_export_findings]] (QB export: clean revenue, empty expenses; basis=CASH) and [[project_accounting_next_priorities]] #1.

**★ CRITICAL: Saunders co3 is NOT a blank slate — 2025 NBHOF invoices ALREADY exist in Odoo.** DJ switched off QuickBooks mid-2025 and the Saunders automation (the NBHOF PO watcher, routers/printing/watcher.py — see [[project_nbhof_watcher_reorder_po.md]]) created 2025 invoices directly in Odoo company 3 (AR acct 233, Revenue 266, Sales journal 21 — [[project_saunders_printing_odoo]]). So rebuilding must NOT recreate those = 2025 revenue would double (same trap as the W&SC QB→Odoo dup). 

**★ DJ WANTS FULL LINE-ITEM INVOICE DETAIL rebuilt, at least back to 2024** (each plaque-card line, banding, freight) — NOT just summary totals — because the QB Transaction Detail CSV carries all of it. ("card numbers" = the plaque-postcard product line items, e.g. the C##### sequence per [[project_nbhof_postcard_c_numbers]], not credit-card numbers.) This revises the earlier "summary P&L only" idea: summary-only now applies ONLY to pre-2024 dead years.

**THE PLAN (revenue/invoices):**
- **Pre-2024 dead years:** summary P&L journal entry per year only (DJ won't look at detail; QB P&L accurate only for Cheryl-era years, use filed returns for neglected years). See [[project_saunders_qb2010_export_findings]] scope decision.
- **2024:** rebuild FULL-detail invoices from the QB CSV — CLEAN (none in Odoo yet, zero conflict).
- **2025:** RECONCILE — query Odoo co3 invoices already created by the automation, map them against QB invoice #s 200216–200233, find the CUTOVER seam, rebuild ONLY the gap (pre-cutover QB invoices). Accounting will discover the cutover by querying Odoo directly (don't ask DJ).
- **Expenses/COGS (all touched years):** reconstruct from Chase + Amex (cash basis).

**★ TAXES vs DETAIL — not in conflict:** tax number stays CASH collected (Chase deposits); the detailed invoices are the OPERATIONAL record (additive, no effect on the return). Having full detail in Odoo is fine.

**★ GUARDRAIL — historical invoice rebuilds are RECORDS ONLY, NEVER sent/emailed to NBHOF.** Recreating a 2024 invoice must not fire a confirmation to the Hall of Fame. Ties to [[feedback_saunders_printing_never_send]]. All book writes via Operator/app with DJ ok, never raw RPC ([[feedback_assistant_use_app_workflow_not_raw_api]]).

**SEQUENCE:** taxes first (DJ logs into Chase+Amex → 2025/2026 expense pull); invoice rebuild + 2025 reconciliation scoped in parallel; Accounting returns the exact cutover map BEFORE creating anything. NBHOF QB invoice #s run 200201–200214 (2024), 200216–200233 (2025, #200215 missing); customers seen: National Baseball Hall of Fame (bulk) + International Spy Museum (1, inv 200230).
