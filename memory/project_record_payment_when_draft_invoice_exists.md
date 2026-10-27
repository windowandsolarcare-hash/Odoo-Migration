---
name: project_record_payment_when_draft_invoice_exists
description: "To record a customer payment via the app when a DRAFT invoice already exists on the SO (invoice was SENT before payment), use POST /owner/api/payment — NOT /owner/api/record_zelle_payment (its duplicate guard refuses when any non-cancelled invoice exists)."
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-10-27T08:15:10.601Z
---

**Context (2026-10-27, Sue Garcia SO 265036 / id 17770, $515 Zelle):** Sue's invoice was SENT first (draft `account.move` 12112 created by `/owner/api/job/send_invoice` when the invoice email went out), THEN she paid. Recording the payment had to use the right endpoint.

**The two Zelle-payment HTTP paths differ:**
- `POST /owner/api/record_zelle_payment {so_id, zelle_amount, zelle_date}` (dashboard.py:11572) has a **duplicate guard** (≈:11582) that REFUSES (`already_paid:true`) if the SO has ANY non-cancelled invoice — a pre-existing DRAFT (state!='cancel') trips it. It's built for the stale-SO matcher on jobs NOT yet invoiced. **Do NOT use it when a draft/sent invoice already exists.**
- `POST /owner/api/payment {so_id, amount, payment_method, memo, payment_date}` (dashboard.py:7112) is the **main Payments-button endpoint**. It calls `_execute_payment` directly with NO HTTP-layer invoice guard. `_execute_payment` (dashboard.py:5116) handles every case idempotently: existing **draft** → sets invoice_date=payment_date, `action_post` (assigns the INV/2026/xxxxx number), then registers the payment; existing **posted+unpaid** → pays against it; **posted+paid** → no-op success; **no invoice** → creates one from the SO. So use `/owner/api/payment` for a job that already has a sent/draft invoice.

**Params used:** `{so_id:17770, amount:515, payment_method:'zelle', memo:'Zelle', payment_date:'2026-10-23'}`. Result: `INV/2026/02595 | paid in full — job Done`. payment_date set to the ACTUAL Chase deposit date (not today) so it lines up for bank reconciliation.

**Journal routing (confirmed live):** `_execute_payment` books Zelle → **Chase journal 6** (NOT j19); only Venmo breaks out to journal 29. Matches [[feedback_times_in_pacific]]-era correction that Zelle deposits straight to Chase.

**Side effects to know:** `_execute_payment` → `finalize_payment` marks the SO Done, rolls gate/pricing to the property master, spawns the **next maintenance SO only if the job is Maintenance type** (Sue's was "Unknown" → none spawned), calls `_billing_settle` (drops it from the collect/awaiting trackers so the HUD "awaiting payment" card clears — it's live-derived), and posts a standard "💵 Payment received $X by <method>" receipt line into the customer thread. `send_thanks` defaults True but `/api/payment` doesn't expose it.

**Bank-side reconciliation is SEPARATE:** registering the payment makes the INVOICE paid, but the Chase bank statement line (the actual Zelle deposit) stays unreconciled until matched in Odoo bank-rec — route to Accounting so the deposit line isn't an orphan. Also: a Zelle `payment_ref` may show a BUSINESS name (Sue paid as "FLE, LLC") — confirm with DJ before assuming a non-matching name is/ isn't the customer ([[💳 payment lookup rule]] / don't record a phantom).
