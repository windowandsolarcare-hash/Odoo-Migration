---
name: project_wsc_cash_revenue_undeposited_funds
description: "2025 CASH revenue (W&SC) ≈ $37,157 — DERIVED from the QuickBooks Undeposited Funds growth (12/31/24 $113,441.83 → 12/31/25 $150,598.84 = +$37,157). DJ's cash goes to a home safe, never deposited, so it piles up in Undeposited Funds. Caveat: assumes ONLY cash stayed undeposited. ★ BIG FLAG: $150K stuck in Undeposited Funds = a QB bookkeeping cleanup needed (overstates assets; part of why payment-method didn't migrate to Odoo). None of this affects the tax return (income all reported)."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-14T06:02:50.109Z
---

**2026-10-13 — answered DJ's standing question "how much 2025 revenue was CASH" (W&SC), using the newly-granted QuickBooks MCP connector (read-only).**

## The answer: ~$37,157 cash revenue in 2025
- Odoo CAN'T answer it — the 2025 invoices were migrated from QuickBooks and the **payment method did NOT carry over** (only ~$13,500 of tagged account.payment records, all Chase Checking). The CURRENT app DOES ask check/card/Zelle/cash per payment, so 2026-forward is answerable in Odoo. See [[project_2025_qb_vs_odoo_reconciliation]].
- QB MCP has **no "sales by payment method" report**. Derived it from the balance sheet instead: **Undeposited Funds** (cash basis) = **$113,441.83 @ 12/31/2024 → $150,598.84 @ 12/31/2025 = +$37,157.01 in 2025.**
- **Why that ≈ cash:** DJ's cash receipts go to a **home safe and are NEVER deposited to the bank**, so when recorded in QB they land in Undeposited Funds and never clear. Checks/cards/Zelle that WERE deposited clear out of UF. So the 2025 UF growth ≈ cash received + recorded in 2025. ~$37K of ~$80K gross ≈ ~46% cash (plausible for residential service work).
- **Caveats:** assumes the ONLY thing left undeposited was cash (a stray undeposited check would overstate it); and it's GROSS cash received, not net of any cash spent directly out of the safe. Confirm against DJ's own sense of the safe.

## ★ BIG BOOKKEEPING FLAG (not tax) — Undeposited Funds pile-up
- **$150,598.84 sits in Undeposited Funds @ 12/31/2025** — years of payments marked "received" but never reconciled to actual bank deposits. Overstates assets; a real QB hygiene problem and part of why payment data didn't migrate cleanly. **Cleanup project:** match historical deposits + move the genuine cash-in-safe portion into its own **"Cash on Hand / Safe" asset account**, and record cash as income-when-received into that account going forward.
- Tax impact: NONE — income is fully reported (DJ confirmed all jobs are invoiced/on the books). This is purely bookkeeping. See [[project_2025_turbotax_entry_status]].

## Other QB observations (2026-10-13 pull, cash basis)
- QB 2025 Net Income (cash) = **$23,755.45** — ties closely to the W&SC Schedule C net ($24,417) on the return. 2024 was $28,632.
- QB still carries the stale **Ford Transit 250** as a fixed asset ($28,576.50) + its loan ($13,367.88) alongside the real business vehicle **Toyota Tacoma** ($44,567.80) + Toyota Loan ($28,126.13 @ 2025; note this is QB's number — the AUTHORITATIVE 2025 interest is the Navy Federal statement $1,981.22, see [[project_2025_turbotax_entry_status]]). QB bookkeeping, not the return.
- Business checking (BUS CHK 9008) shows NEGATIVE on QB cash basis (-$13,262 @ 2025) — likely unreconciled; part of the same cleanup.
- QB connector: DJ explicitly re-enabled access 2026-10-13 for this lookup. Still READ-ONLY; QB remains RETIRED as source of truth (Odoo is) — see [[project_quickbooks_retired]].
