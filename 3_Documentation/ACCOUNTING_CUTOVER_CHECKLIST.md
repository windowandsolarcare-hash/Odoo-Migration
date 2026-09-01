# Jan 1 Cutover Checklist — QuickBooks → Odoo (Window & Solar Care, company 1)
**Rebuilt 2026-09-01 by cloud Lead** from memory: [[project_accounting_master_plan]],
[[project_opening_balances_needed]], [[project_bank_feed_qb_double_booking]],
[[project_recurring_bookkeeping_plan]], [[project_missing_invoice_audit]], [[user_accounting_knowledge]].
**Live interactive version (DJ ticks items off):** https://claude.ai/code/artifact/29b0c82e-502b-4e34-9c25-083bd5fc534c

⚠ **All dollar figures below were last verified 2026-06-24 — TEN WEEKS STALE.** Run Stage 0 before acting.

## Where it stands
Odoo Chase `101401` = **$36,081** (2026-06-24) · real Chase ≈ **$1,000** · gap ≈ **$35,081**.
The gap is NOT a mystery — it is pre-cutover synthetic inflows still sitting on Chase by design
(Check $143,560 + Zelle $43,184 + CC $33,905), netted vs expenses, to be trued at the cutover.
**Opening balances are the lever, not Stage 3.**

## STAGE 0 — re-verify (Claude, ~10 min)
- [ ] Today's Odoo balance for Chase `101401`
- [ ] Re-count unreconciled lines in Outstanding Receipts `101403` (was 30 residuals / $4,830)
- [ ] Confirm card liability accounts still $0 (`201100/201200/201210/201220/201230`)
- [ ] Check what the Chase feed imported since June (new uncategorized suspense)

## STAGE 1 — balances only DJ can get (as of 2025-01-01; nearest year-end-2024 statement is fine)
| Account | Code | Needed |
|---|---|---|
| Discover Card | 201200 | balance owed |
| Discover Card II | 201210 | balance owed |
| Shop Your Way Mastercard | 201220 | balance owed |
| Thank You Card | 201230 | balance owed |
| Ford Transit 250 2019 Loan | 291100 | remaining balance |
| Toyota Loan (NFCU) | 291200 | ✅ KNOWN $24,252.45 @ 2026-05-20, 5.99%, pmt $861.18 (DJ pays $900) — back-calculable |
| Van Shelving Loan | 291300 | remaining balance |
| Notes Payable — Saunders Printing | 291400 | amount still owed |
| Venmo | 101405 | starting balance if any |
| Cash on Hand | 101406 | starting balance if any |
| Chase Checking (9008) | 101401 | statement balance (derivable from feed, DJ's is better) |

Plus: **QuickBooks Fixed Asset List export** (vehicles/equipment depreciation).

## STAGE 2 — three decisions from DJ
1. **Cutover date conflict.** Opening balance anchors to **2025-01-01** but the Chase feed starts
   **2024-11-25**, so Nov–Dec 2024 exists twice. Recommendation: ignore Nov–Dec 2024 feed lines
   (QB covers them), keep Jan 1. Alternative: move cutover to feed start.
2. **Fixed assets:** full depreciation schedules per asset, or current book value as one lump.
3. **7 SOs paid with no bank trace** → likely cash DJ kept → book as owner's draw (same as the
   $60,847 Stage-1 cash): `003362` $450 · `003476` $85 · `003489` $100 · `003578` $65 ·
   `003740` $250 · `003659` $110 · `003732` $250.

## STAGE 3 — Claude builds the opening balances (one session)
- [ ] One JE per account dated 2025-01-01 vs Opening Balance Equity `309000`, computed as
      **(real balance − current Odoo balance at cutover)** so pre-2025 Odoo detail isn't double-counted
- [ ] Tie Odoo Chase `101401` to the real bank balance (~$1,000)
- [ ] Point Cash journal (id 18) at Cash on Hand `101406` — config, one-time
- [ ] Produce a balance sheet + plain-English walkthrough for DJ

## STAGE 4 — cleanup that can wait (deliberately AFTER opening balances, DJ 2026-06-24)
- [ ] Credit-card settlements (old "Stage 3"): 22 post-cutoff synthetics $3,635 vs 50 Workiz batch
      deposits $10,921; fee plug → `650100`
- [ ] Outstanding Receipts residuals: Bucket A lump deposits (Brenda Williams 2×$150, Hennessy Group,
      batched checks), Bucket C possible dup (Patti Martel two $140 Zelles, one $140 deposit)
- [ ] DECIDE: link card feeds at all? Only after opening balances, feed start PAST the QB import (June 2026+)

## STAGE 5 — recurring bookkeeping (approved design, NOT built)
- [ ] Weekly "what I did" email (auto-categorized / needs your call / flags) — explicitly NOT a weekly P&L
- [ ] Monthly P&L + written analysis (`5_Accounting/pl_2024_2025.py`, gray separator lines)
- [ ] **Cash EXPENSES have no capture path** — invisible today, overstates profit. Agreed: DJ logs in the
      field app as he spends → `Dr <expense> / Cr 101406`. Needs a small entry form.

## DONE — do not redo
795 QB↔feed duplicate expenses retired (feed wins) · 105 orphan expenses categorized · 18 NFCU→Toyota ·
Stage 1 cash 407/$60,847→owner's draw + Venmo 74/$14,654→`101405` (Chase $164,911→$89,410) ·
144 income dups via Outstanding Receipts · Stage 2 Check/Zelle 327 re-pointed, 297 auto-reconciled
(Chase $94,513→$36,081) · 73 missing invoices created 2020–2024 (Stephen Hatch `001803` flagged, overpaid $5) ·
Toyota interest split (2024 $187.84 / 2025 $1,981.22 / 2026 YTD $657.42) · revenue `400000` verified clean.

## FLAGS
- **`5_Accounting/` is LOCAL-ONLY on DJ's Surface Pro** — the categorizer, Stage 2 engine, P&L mailer and
  every audit CSV are in neither repo. Same unbacked exposure the memory files had; same fix (mirror it).
- **Card spending is on the P&L but the card DEBT is not on the balance sheet.** QB credited Chase
  $260,838 across 3,329 lines including card-paid expenses; all 5 card accounts read $0. P&L fine,
  balance sheet understates liabilities until Stage 3.

## KEY ACCOUNTS
`101401` Chase · `101402` Bank Suspense · `101403` Outstanding Receipts · `101405` Venmo ·
`101406` Cash on Hand · `121000` AR · `400000` Product Sales · `312000` Owner's Pay & Personal ·
`650100` Merchant/CC Fees · `309000` Opening Balance Equity. Chase journal id 6; Misc Operations = QB import.
