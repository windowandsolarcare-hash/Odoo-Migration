---
name: project_field_paid_banner
description: "Field payment card — confirm dialog includes method+check#; green Paid banner (method/ref/amount/date) replaces button when SO already paid. Backend _paid_detail_by_so maps payment→invoice→SO via account.payment.reconciled_invoice_ids."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-09: Field assistant (`field.html`) payment card upgraded two ways.

**1. Confirm dialog now names the method.** `doPayment()` builds a label from `payMethod` + the memo/check field: `Record $160 Check #1234 payment for Bill Nancy Ward?` (check → "Check #<memo>"; others with a ref → "Zelle (ref)"). So DJ is OK-ing the method, not just the amount.

**2. Green "Paid" banner replaces the button when already paid.** When `job.paid`, `_setPaidUI(job)` hides `.amount-row`, `.method-btns`, `.memo-input`, and `#pay-btn`, and shows `#pay-paid-banner` = `_paidBannerHTML(job.paid_detail)` → "✓ Paid" + "$160 · Check #1234" + formatted date. Not-paid restores all inputs. Replaces the old "✓ Already Paid" greyed-button behavior.

**Backend data (`dashboard.py`):** new `job.paid_detail = {method, ref, amount, date}` added to all three job-build sites: `tool_get_schedule` (today, powers `/api/dashboard`), the `/api/upcoming` builder, and `/api/past_jobs` builder. Source helper **`_paid_detail_by_so(sos)`** (next to `_paid_status_by_so`).

**KEY API FACT — how to map a payment back to its SO in Odoo 19 SaaS:** `account.payment` has a stored, *searchable* field **`reconciled_invoice_ids`** (m2m to the invoices it paid). Pattern: SO.invoice_ids → filter account.move to posted + payment_state in (paid,in_payment) → `account.payment.search_read([['reconciled_invoice_ids','in',paid_inv_ids],['payment_type','=','inbound'],['state','in',[posted,paid,in_payment]]], fields=[date,amount,payment_method_line_id,memo,reconciled_invoice_ids])` → map each payment's invoices back to so_id. Method via existing `_detect_payment_method(payment)` (reads `payment_method_line_id` + memo). Whole helper wrapped in try/except so it never blocks schedule render.

**Why:** DJ wants to confirm the payment *method* at OK time, and wants a job that's been paid to clearly show it's paid + how/when/how-much (not just a dead button). **How to apply:** extend the banner via `_paidBannerHTML`; the per-SO payment detail is already on every field job object as `paid_detail`. See [[project_predeposit_paid_cache]], [[project_phase4a_sync.md]].
