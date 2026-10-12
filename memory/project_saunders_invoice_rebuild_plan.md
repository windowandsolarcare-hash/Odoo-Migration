---
name: project_saunders_invoice_rebuild_plan
description: "★ Saunders (co3) invoice rebuild plan (DJ 2026-10-12). 2025 NBHOF invoices ALREADY in Odoo (automation created them when DJ switched off QB mid-2025) — don't double-count. DJ wants FULL line-item invoice detail rebuilt back to 2024 (not just summary). 2024=clean rebuild; 2025=reconcile the seam; pre-2024=summary P&L JEs only."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T21:17:01.172Z
---

**★★ VERIFIED 2026-10-12 (supersedes the "2025 already in Odoo / reconcile the seam" plan below).** Two facts confirmed by direct query:
1. **QB CSV reconstruction is 100% complete and ties.** Parsed all invoices from the QB Transaction Detail CSV; every one of the 32 present invoices has line detail that sums EXACTLY to its header total (parser: `scratchpad/rebuild_invoices.py`). 2024 = 14 invoices $22,141.26 (#200201–200214); 2025 = 18 invoices $39,724.68 (#200216–200233, #200215 voided/missing). Customers: NBHOF (bulk) + International Spy Museum (1, #200230). Durable output saved to `C:/Users/dj/Documents/Business/Financial_Statements/Saunders_Printing/Invoice_Rebuild/` (saunders_invoice_rebuild.json + _lines.csv).
2. **Odoo co3 existing out_invoices = #200234–200246, ALL dated 2026** (automation set; 200242 is a $0 draft, 200237 gap). So the QB set **#200201–200233 (2024 AND 2025) is NOT in Odoo** and does NOT overlap the automation — they are sequential and disjoint. **There is NO 2025 cutover seam to reconcile** — the earlier belief that 2025 QB invoices already lived in Odoo was WRONG (the automation didn't start until 2026). The rebuild = the full QB set #200201–200233, which slots cleanly right before the automation's #200234. DJ decision (2026-10-12): wants full detailed invoices, NO 2025-shortcut, rejected the 1/1/2025 opening-balance/2024-as-summary cutover.

**✅ DONE 2026-10-12 — ALL 32 INVOICES POSTED to Odoo co3.** DJ chose (AskUserQuestion) "I post directly, now" — straight into Odoo as real invoices with full line items, NOT through the Saunders printing automation code; wants the history + correct P&L revenue. Posted via `scratchpad/post_invoices.py` + `post_drafts.py`: each QB detail line = its own Odoo invoice line (each plaque card, banding, freight), original invoice numbers preserved (#200201–200233, #200215 void), journal 21 (Sales), income account id 266 (Product Sales), fiscal pos 6 (Domestic), no tax, partner NBHOF id 26947 (+ created "International Spy Museum" partner id 27300 for #200230). Provenance stamped in each invoice's narration: "Historical reconstruction from QuickBooks Pro 2010 export (records only - not sent to customer)." NONE were emailed/sent. Final: 2024 = 14 inv $22,141.26, 2025 = 18 inv $39,724.68 (accrual P&L revenue on acct 266 ties exactly by year); 2026 automation set (#200234–246) untouched. No duplicates, no gaps.

**GOTCHAS for next time (Odoo 19 enterprise):** (1) posting out_invoices via XML-RPC intermittently throws `TypeError: unhashable type: 'list'` deep in the account_external_tax/avatax `_post` filter — it is FLAKY/transient; a clean retry of `action_post` succeeds (loop action_post with retries). (2) Setting `name` explicitly on the draft before posting preserved the historical number even though it's LOWER than existing 2026 numbers — no sequence-gap error (co3 has no lock dates). (3) account.move.line `read` must take the id list directly as the positional arg, not wrapped in another list.

**OPEN (minor, balance-sheet only, NOT tax):** these posts created ~$61,866 open A/R in co3 for 2024–2025 (Dr A/R / Cr Revenue) with no payments applied. Taxes are CASH basis so this doesn't affect the return; if DJ wants A/R to clear, apply the historical QB deposits as payments against these invoices later. Accrual P&L revenue (shown above) ≠ cash-basis TAX revenue (2024 cash receipts $29,999.63 collected; 2025 $39,724.68) — keep the two views distinct. See [[project_saunders_qb2010_export_findings]].

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
