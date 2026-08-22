---
name: project_money_decision_allowlist
description: "Any \"does this customer owe us?\" / bill-the-customer decision MUST use an ALLOWLIST (enumerate the states that OWE), never a denylist — a denylist fails OPEN and bills already-paid customers."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-21T01:38:44.587Z
---

**Discovered 2026-08-20 (Blair Becker portal double-charge).** The customer portal balance card showed Blair **INV/2026/00001 · "$85.00 due · Pay now"** for an invoice she'd already paid. Root cause: the "is this owed?" filter was a **denylist** — `payment_state NOT IN ('paid','reversed')`. Her invoice was `payment_state='in_payment'` (paid but unreconciled — a migration lag, `amount_residual` still 85), a state nobody enumerated, so it **defaulted to bill the customer**. A denylist on money **fails OPEN**.

**Rule (Portal fix, portal.py 55c58c45): enumerate what OWES, never what doesn't.** Allowlist:
`payment_state IN ('not_paid','partial') AND amount_residual > 0`. An unfamiliar/future state then defaults to **NOT** asking for money — the safe direction. Do NOT rely on `amount_residual > 0` alone (Blair's was 85 while already `in_payment`).

**This is the SAME shape as the cross-company leak** ([[project_company_filter_fails_open]] / [[project_company_guard_enforce_at_resolver]]): a guard that lists the bad cases fails open on every case it forgot. For money + access decisions, always allowlist the permitted/positive set.

**How to apply / verify:** any code deciding a customer balance, "Pay now" button, dunning, or auto-charge must allowlist owed states. Verify against the WHOLE book, not one record: Portal swept all **2,520** posted W&SC customer invoices — old denylist billed 4 ($341), new allowlist bills 3 ($256), dropping exactly Blair's stray and adding nothing (dist: paid 2514 / in_payment 3 / not_paid 3). Household balance sums `child_of` the contact (person **+** all children), so a stray on the person record (23046) and jobs on the property record (24169) are both in scope; `search_read` returns each invoice once (no dedupe gap — address-dedupe collapses only *display* rows).

**Underlying data issue still open:** INV/2026/00001 is a migration invoice whose payment is a **stub with no journal entry** (`account.payment` 24, `move_id=False`) — income booked, cash side never recorded. Clearing it needs the Bank-Suspense/opening-balance cleanup (don't fabricate a payment → risks double-counting the Feb cash if it's already in suspense). See [[project_accounting_master_plan]].
