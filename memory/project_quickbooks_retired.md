---
name: project_quickbooks_retired
description: "QuickBooks is RETIRED (DJ 2026-09-09). Odoo is the SOLE source of financial truth — revenue, expenses, P&L, AR, cash all from Odoo. Never route financial questions/pointers to QuickBooks."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-09T19:33:15.441Z
---

DJ 2026-09-09: **"QuickBooks is retired."**

**Odoo is now the SOLE source of financial truth for Window & Solar Care.** Revenue, expenses, P&L, accounts-receivable, cash-on-hand — all come from Odoo (`account.move`, journals, `company_id = 1` for W&SC). The QB→Odoo accounting migration is effectively done; Odoo is authoritative.

**How to apply:**
- Financial questions / reports / Memory-Ask "pointers" → **Odoo only**, app-native. Do NOT query QuickBooks or route to it.
- The **QuickBooks MCP connector** (`mcp__claude_ai_Intuit_QuickBooks__*`) is NOT the books anymore — do not use it for W&SC financials.
- This **resolves the old "Odoo may be partial if the QB→Odoo migration isn't complete" caveat** — drop that caveat from financial answers; Odoo is complete/authoritative.
- It also **removes the "app server can't call the QuickBooks MCP (session-only)" boundary** that used to complicate financial pointers — every financial answer is now app-native from Odoo. No QBO REST creds needed.
- Still filter `company_id = 1` (or `in [1, False]` for res.partner) per the multi-company rules — [[feedback_planning_constraints]].

**Open sub-point (surface if hit, don't paper over):** the memory-pointer survey (2026-09-09) is verifying Odoo's EXPENSE/COST side is actually populated (vendor bills = `account.move` move_type='in_invoice', expense-type accounts, journals). Revenue is solidly in Odoo; if the cost side turns out sparse (migration moved revenue but not all expenses), that's a real data-completeness finding for DJ — flag it, don't fabricate a P&L. **Gross-margin-per-service / profit-per-hour** remain unanswerable until a **per-service cost-allocation model** exists (a costing gap, NOT a QuickBooks gap). Related: [[project_workiz_retirement]] (same "X is retired, don't route to it" pattern), [[project_memory_pillar_phase1]].
