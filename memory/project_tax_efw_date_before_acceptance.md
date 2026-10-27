---
name: project_tax_efw_date_before_acceptance
description: "DJ's 2025 fed+CA balances were set as Direct Debit dated 10/15 but returns accepted 10/16 — past-dated EFW likely never pulled; still unpaid."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-27T14:53:31.296Z
---

DJ's 2025 taxes (self-filed TurboTax, re-filed after an AGI-mismatch rejection) were set up to pay the
balances by **Direct Debit / Electronic Funds Withdrawal (EFW) on the e-filed return** — NOT via IRS Direct
Pay or FTB Web Pay. Source of truth = the FULL 59-page TurboTax package
`C:\Users\dj\Downloads\9818aff8-e2ed-4821-92ff-a834555ff35b.pdf` (page 1 federal filing instructions,
page 21 CA) and FTB 8453-OL (page 22 of the 48-page forms-only copy).

- **Federal balance $5,890** + **CA balance $972**, BOTH debited from the SAME Chase checking account
  ending **8356** (routing 322271627), **withdrawal date 10/15/2026**.
- ⚠ **THE GOTCHA:** both returns were **accepted 10/16/2026 — one day AFTER the scheduled 10/15 withdrawal
  date.** A withdrawal date that is in the past relative to the acceptance date generally does NOT auto-pull
  (the IRS/FTB cannot schedule a debit for a date that has already passed). This matches DJ's observation
  that nothing had left the account 10+ days later, and there are NO Direct Pay / Web Pay confirmation emails.
- **Conclusion:** both amounts are LIKELY STILL UNPAID, with late-payment penalty + interest accruing.
  Verify via the bank + the IRS Online Account / MyFTB; if confirmed unpaid, pay manually (IRS Direct Pay for
  $5,890; FTB Web Pay for $972 — FTB direct-debit status line: 1-916-845-0353).
- The 1040 itself does NOT list a payment bank account when you OWE (lines 35b/35c/35d are refund-only). The
  account + EFW election live on the filing-instructions pages and 8453-OL, not on the 1040 face. (Corrected
  an earlier wrong claim that the account "should be on the 1040.")
- When the money finally clears, book it as an **OWNER'S DRAW from Saunders Printing**, not a business expense.

**Why:** DJ was worried the payment method was recorded wrong and that nothing had debited. Diagnosis: the
method was fine (direct debit) but the PAST-DATED withdrawal date vs. a next-day acceptance is the mechanical
reason it likely never pulled.

**How to apply:** Any future e-file where the withdrawal date could fall on/before the acceptance date =
flag it. Safer to date EFW a few business days out. Corrected the QC_BRIEF line that wrongly said
"paid online (IRS Direct Pay + FTB Web Pay)". See [[project_2025_turbotax_entry_status]].
