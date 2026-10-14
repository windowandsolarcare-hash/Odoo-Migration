---
name: project_wsc_cash_revenue_undeposited_funds
description: "★ No reliable 2025 CASH figure exists. QB UF growth was +$37,157 (12/31/24 $113,441.83 → 12/31/25 $150,598.84) but DJ says that's WAY too high → the Undeposited Funds account is a JUNK DRAWER (stray unmatched non-cash items), NOT a clean cash number. Real cash lives with DJ/the safe. DECISION (DJ 2026-10-13): do NOT clean up retired QuickBooks — it corrupted nothing in the Odoo migration (income is correct; only payment-method didn't carry, unfixable now), so zero upside. Real cash-on-hand gets set up in ODOO before the 2027 balance sheet. No tax impact."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-14T06:07:59.176Z
---

**2026-10-13 — answered DJ's standing question "how much 2025 revenue was CASH" (W&SC), using the newly-granted QuickBooks MCP connector (read-only).**

## The answer: ~$37,157 cash revenue in 2025
- Odoo CAN'T answer it — the 2025 invoices were migrated from QuickBooks and the **payment method did NOT carry over** (only ~$13,500 of tagged account.payment records, all Chase Checking). The CURRENT app DOES ask check/card/Zelle/cash per payment, so 2026-forward is answerable in Odoo. See [[project_2025_qb_vs_odoo_reconciliation]].
- QB MCP has **no "sales by payment method" report**. Derived it from the balance sheet instead: **Undeposited Funds** (cash basis) = **$113,441.83 @ 12/31/2024 → $150,598.84 @ 12/31/2025 = +$37,157.01 in 2025.**
- **Why that ≈ cash:** DJ's cash receipts go to a **home safe and are NEVER deposited to the bank**, so when recorded in QB they land in Undeposited Funds and never clear. Checks/cards/Zelle that WERE deposited clear out of UF. So the 2025 UF growth ≈ cash received + recorded in 2025. ~$37K of ~$80K gross ≈ ~46% cash (plausible for residential service work).
- **Caveats:** assumes the ONLY thing left undeposited was cash (a stray undeposited check would overstate it); and it's GROSS cash received, not net of any cash spent directly out of the safe. Confirm against DJ's own sense of the safe.

## ★ DECISION (DJ 2026-10-13): do NOT clean up QuickBooks
- DJ says ~$37K cash is **way too high** → the $150,598.84 Undeposited Funds balance is a **junk account** (stray unmatched non-cash items piled up over years), not real cash. So it's NOT a usable cash proxy.
- **QB is RETIRED/obsolete — nobody files from it, and the 2027 balance sheet will be built in ODOO, not QB. So scrubbing QB now buys nothing.**
- **It did NOT corrupt the Odoo migration:** what migrated = invoices + payments + paid status, and the INCOME totals are verified correct. The UF mess never made Odoo income wrong. The only thing that didn't carry = payment-method detail — and **cleaning QB now would NOT fix that** (migration already happened; can't re-migrate). → **zero upside to touching QB. Leave it.**
- **The ONLY real cleanup lives in ODOO, going forward (small, ~2027 setup):** before the 2027 balance sheet, set up a **"Cash on Hand / Safe" asset in Odoo** carrying the ACTUAL cash balance — **the honest number comes from DJ/the safe** (QB can't tell us). Accounting owns keeping Odoo's ducks in a row so 2027 is clean. See [[project_wsc_scorp_election_status]] (why 2027 balance sheet matters) + [[project_2025_turbotax_entry_status]].
- Tax impact: NONE — income is fully reported (all jobs invoiced/on the books).

## Other QB observations (2026-10-13 pull, cash basis)
- QB 2025 Net Income (cash) = **$23,755.45** — ties closely to the W&SC Schedule C net ($24,417) on the return. 2024 was $28,632.
- QB still carries the stale **Ford Transit 250** as a fixed asset ($28,576.50) + its loan ($13,367.88) alongside the real business vehicle **Toyota Tacoma** ($44,567.80) + Toyota Loan ($28,126.13 @ 2025; note this is QB's number — the AUTHORITATIVE 2025 interest is the Navy Federal statement $1,981.22, see [[project_2025_turbotax_entry_status]]). QB bookkeeping, not the return.
- Business checking (BUS CHK 9008) shows NEGATIVE on QB cash basis (-$13,262 @ 2025) — likely unreconciled; part of the same cleanup.
- QB connector: DJ explicitly re-enabled access 2026-10-13 for this lookup. Still READ-ONLY; QB remains RETIRED as source of truth (Odoo is) — see [[project_quickbooks_retired]].
