---
name: project_2025_turbotax_entry_status
description: "★ 2025 TurboTax return — Accounting entered BOTH Schedule Cs + owner W-2 + $4k fed extension pmt via computer-use 2026-10-13/14 (DJ said 'fill it out, we review at end'). W&SC net $24,417 + Saunders $25,868 = $50,285 business net. Running meter after W-2+$4k: Fed $5,890 / CA $1,966. NOT filed — draft. Open: SEP, SE health, CA est pmts. FLAG: owner W-2 issued by Saunders Printing but $2,700 wage deducted on W&SC Sch C."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-14T05:22:15.676Z
---

**2026-10-13 — Accounting filled out DJ's 2025 TurboTax Online ("Do It Yourself Premium") via Claude-in-Chrome, at DJ's explicit direction ("fill this out as best you can and then you and me review it at the end"; he confirmed Premium handles both Schedule Cs; 2024 return WAS transferred in, which created both businesses).** NOT filed — saved as draft pending DJ review. Figures are from the finalized builds in [[project_2025_schedule_c_categorized]] (W&SC) + [[project_saunders_qb2010_export_findings]] (Saunders), with the mileage corrected to DJ's 2026-10-13 odometer. Entry worksheet: `Financial_Statements/Tax_2025/2025_TurboTax_entry_worksheet.md`.

## What's ENTERED and VERIFIED
- **W&SC ("Exterior Home Services", code 999000): net $24,417.** Gross $79,877; expenses $55,460 incl. Vehicle $15,879, Home office $650 (simplified 130 sq ft), Wages $4,950, Contract labor $4,425, Meals $2,837 (TT halves the $5,674), Supplies $7,031, Office $8,342, Utilities $2,780, Rent $2,647, Advertising $1,409, Repairs $1,288, Interest $1,805 (Citi card only), Taxes&lic $745, Insurance $223, Other $449. Ties to TurboTax ("taxable income $55,460 lower" → $24,417). Audit check = LOW risk.
- **Saunders Printing (code 323100): net $25,868.** Gross $39,725; expenses $13,857 = Supplies/printing 8,536 + Rent/storage 2,452 + Utilities 1,344 + Interest(Amex) 680 + Office 622 + Other 223. Audit check = LOW. No vehicle/home-office/wages (matches 2024 return).
- **Combined SE net = $50,285.**
- **★ VEHICLE FULLY VERIFIED:** 2022 Toyota Tacoma (VIN 3TMDZ5BN5NM139672), standard mileage 19,854 mi × $0.70 = $13,898 (2024 used std mileage → allowed) + Navy Federal auto-loan interest $1,981.22 (entered in the vehicle section, NOT on the Sch C interest line) = $15,879 vehicle deduction. The $1,981.22 is CONFIRMED to the penny off the Navy Federal Dec-2025 statement ("Current Year Interest Paid"). Dealer 0% contract was a placeholder; real loan = Navy Federal "Used Vehicle Loan 5787", 5.99% APR, orig $44,473.18, opened 01/08/2024. See [[project_dj_2024_return_schedule_c]] + the Tacoma purchase record + statement in `Financial_Statements/Window_Solar_Care/Vehicle/`.

## ★ UPDATE 2026-10-14 — W-2 + $4k extension payment ENTERED (via computer-use, DJ said "enter the W-2 and the $4,000 payment")
- **Owner W-2 ENTERED** (Income → Wages & income summary → Add more income → Wages and Salaries (W-2) → Type it in myself). Source = DJ's actual 2025 W-2 downloaded from Gusto (Taxes & compliance → Tax documents → W-2s → DJ Saunders), archived `Financial_Statements/Tax_2025/W2_2025_DJ_Saunders.pdf` + Drive (My Drive/Financial_Statements/Tax_2025, file id 1DXmfbgBGNo78LbTS9i5SSoZKz0J5TVnh). Values: **Employer = SAUNDERS PRINTING** (EIN 87-3872426), Box1 wages $2,700, Box2 fed WH $207.87, Box3/5 $2,700, Box4 SS $167.40, Box6 Medicare $39.15, Box14 "CA SDI" $32.40, Box15 CA state ID 24190225 (dashes stripped), Box16 $2,700, Box17 CA WH $31.68. SSN was already pre-filled from the return (informational, not editable — I never typed it). Effect: **Fed $9,840 → $9,890** (+$50 net: $2,700 wage income washes the $2,700 Sch C owner-wage deduction, minus $207.87 WH credit, net of SE-tax/QBI interplay); **CA $1,840 → $1,966**.
- **$4,000 FEDERAL EXTENSION PAYMENT ENTERED** (Deductions & Credits → Add more tax breaks → search "estimate" → Estimates and Other Taxes Paid → **Income Taxes Paid** → Payments with Extension → **Payments with 2025 federal extension** → "$4000"). Effect: **Fed $9,890 → $5,890** (exactly −$4,000). Now shows "Revisit".
- **New car-loan-interest deduction (OBBB 2025) — DECLINED** in the guided D&C flow: Tacoma interest is already a BUSINESS deduction in the Sch C vehicle section (double-dip), and the truck is USED + bought 2024 so it doesn't qualify anyway.
- **★ NAVIGATION NOTE:** "Deductions and credits summary" submenu dumps you into the guided "find tax breaks" walkthrough (moving → student loan → education → car loan int → educator → 1095-A health ins → then the "Your tax breaks" summary page). From that summary → **Add more tax breaks** → search box → the category groups appear with Start buttons. The top "Ask AI anything" search opens a HELP panel, not a jump-to. W-2 auto-fill by EIN failed (payroll import) → used "Type it in myself".

## Running tax meter (as entered NOW, after W-2 + $4k)
**Federal due $5,890 · CA due $1,966.** (History: $14,649 fed at start → $9,840 after both Sch Cs → $9,890 after W-2 → $5,890 after $4k extension pmt.) Standard deduction kept ($15,750).

## ★ DJ DECISIONS 2026-10-13 (draft now essentially FINAL)
- **Solo 401(k): SKIP for 2025.** DJ decided NOT to fund — needs the cash for the tax bill, no extra funds. So no retirement deduction. (Mechanics confirmed to DJ: a 401(k) is a deduction not a credit → saves ~18-20¢/$ income tax only, and NEITHER employee nor employer side cuts SE tax for a sole prop.)
- **Home office $650 — KEEP, it's worth ~$186 combined tax** (≈$92 SE + ~$58 fed + ~$36 CA). It's a Sch C deduction so it DOES cut SE tax (unlike the 401k). Simplified method ($5 × 130 sqft), no receipts/depreciation, zero added cost → clear keep.
- **→ Draft is FINAL pending review: Federal $5,890 · CA $1,966. File by the Oct 15, 2026 extension deadline.**

## OPEN — still to confirm at final review
1. **★ FLAG — W-2 employer mismatch:** the owner W-2 is issued by **Saunders Printing** (EIN 87-3872426), but the $2,700 owner-wage DEDUCTION sits on the **Window & Solar Care** Sch C (L26). Dollars wash on the 1040 either way, but ideally the deduction belongs on the Saunders Printing Sch C. Also a sole-prop issuing a W-2 to its own owner is non-standard — DJ + CPA to confirm. (Going fwd, W&SC payroll should move to the new LLC EIN 42-3461012 — see [[project_wsc_scorp_election_status]].)
2. **SE health insurance** — none assumed (DJ said none); confirm.
3. **CA (FTB)** — $1,966 shown; confirm any CA estimated payments made (would reduce it).
4. **Sanity-check W&SC gross $79,877** — 2024 Odoo ran ~$15K higher than the filed return gross; verify 2025 gross isn't overstated.

DRAFT — DJ reviews + files. See [[project_dj_tax_filing_2025]].
