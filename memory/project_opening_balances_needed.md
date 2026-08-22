---
name: project_opening_balances_needed
description: Opening-balance plan to bridge Odoo to reality at the Jan 1 2025 cutover. The tool DJ expected to use to make accounts accurate. Needs QB balances + credit card balances.
metadata: 
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Opening Balances — the bridge to reality (cutover Jan 1, 2025)

**This is the accounting tool DJ always intended to use** to make Odoo accounts reflect reality so the books are accurate going forward (confirmed 2026-06-08). QB was accurate through end of 2024; Odoo takes over Jan 1 2025. See master plan [[project_accounting_master_plan]].

**Strategy:** rather than reconcile every pre-2025 transaction by hand, set opening balances at 2025-01-01 from QB/reality, then keep Odoo accurate with real detail forward. This is what resolves the ~$88K Chase gap (real Chase ≈ $1,000 vs Odoo ~$89,410) — together with Stages 2-3 income-duplicate cleanup.

## Accounts needing real balances from QB (as of 2025-01-01)
| Account | Code | What to pull |
|---|---|---|
| Chase Checking (9008) | 101401 | Checking balance at cutover (real ≈ $1,000 currently; need the 2025-01-01 figure) |
| Discover Card | 201200 | Balance owed |
| Discover Card II | 201210 | Balance owed |
| Shop Your Way Mastercard | 201220 | Balance owed |
| Thank You Card | 201230 | Balance owed |
| Ford Transit 250 2019 Loan | 291100 | Remaining loan balance |
| Toyota Loan | 291200 | ✅ KNOWN: $24,252.45 remaining as of 2026-05-20 (NFCU stmt). Loan# 430015945557-87, 5.99%, reg pmt $861.18, DJ pays $900 (overpays principal). |
| Van Shelving Loan | 291300 | Remaining loan balance |
| Notes Payable - Saunders Printing | 291400 | Amount still owed |

Also: QB Fixed Asset List export (vehicles/equipment depreciation), Venmo + Cash on Hand starting balances if any.

## Credit cards — STILL TO HANDLE (DJ has 2 not yet connected to Odoo)
When DJ connects the 2 cards, their feeds will duplicate the QB CC expense entries AND the synthetic "Credit Card | SO" settlements → run a dedupe round (same feed-wins pattern as Chase). The CC *payoff* feed lines from Chase are already parked in review_queue.csv. Card liability accounts already exist (201100/201200/201210/201220/201230).

## ⭐ VERIFIED 2026-06-24 (Stage 2 done, opening balances are NEXT)
- **Stage 2 complete** → Chase 101401 now **$36,081** (from $94,513). Target still ~$1,000; remaining ~$35K is THIS step (opening balance / cutover), NOT Stage 3. See [[project_accounting_master_plan]].
- **DJ's own credit cards (Discover/Discover II/Shop Your Way/Thank You) are NOT linked to Odoo** (no Plaid feed like Chase) and **all 5 card liability accounts are $0 with zero lines** — card debt is entirely absent from the balance sheet.
- **QB import credited Chase 101401 for $260,838 across 3,329 lines = EVERY payment method collapsed into Chase**, including card-paid expenses (0 lines route to any card account). So card *expenses* are in the P&L (via QB, journal 3, runs 2019→2026-05-31) but mis-credited to Chase; the card *liability* must be established via opening balance.
- **DECISION (DJ 2026-06-24): do opening balances BEFORE Stage 3 and BEFORE live-linking cards.** Rationale: live-linking a card feed now would re-import the 2025–mid-2026 card expenses already in via QB → duplicate/dedupe mess, and wouldn't reach back to cutover anyway. Opening balance puts the card debt on the books correctly. Live-linking, IF wanted, is a separate going-forward automation to enable AFTER, with feed start set PAST the QB import (June 2026+) so no overlap.
- **SHOPPING LIST handed to DJ 2026-06-24** (balances as of late-Nov/year-end 2024, closest statement fine): 4 cards (balance owed), Ford Transit 250 loan, Van Shelving loan, Notes Payable-Saunders (Toyota back-calc-able from $24,252 @ 2026-05-20), Chase (derivable from feed). Plus QB Fixed Asset List export for the asset side. Awaiting DJ's numbers.

## How to apply
Once balances are known: one opening-balance JE per account, dated 2025-01-01, debiting/crediting each against **309000 Opening Balance Equity**. BUT first decide cutover mechanics with pre-2025 Odoo activity already present (synthetic deposits + invoices + QB import exist back to 2020): either neutralize pre-2025 detail or compute the opening JE as (real balance − current Odoo balance at cutover) so Odoo ties to reality at 2025-01-01 without double-counting. Reconcile the feed-start overlap (feed begins 2024-11-25, before the Jan-1 cutover) — likely discard/ignore Nov-Dec 2024 feed since QB covers it, OR move cutover to feed start. Resolve next session.

**Why:** this is the final structural step; once opening balances are set and Stages 2-3 done, Odoo Chase ties to the real ~$1,000 and the books are live and accurate forward.
