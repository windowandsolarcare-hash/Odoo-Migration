---
name: project_invoiced_guard_posted_only_vs_raw
description: "'Already invoiced' guards: a BENIGN/reversible edit must gate on _has_posted_invoice (POSTED-only), NOT raw invoice_ids (a stranded DRAFT false-blocks with 'already invoiced'). brain.py job_set_service (quote-accept) fixed 2026-10-26 main ae99ce3a; save_job_lines_core fixed 2026-09-14. The dashboard.py siblings (delete_so/delete_job/stripe poll/customer read/invoice_status create) are INTENTIONAL or non-blocks — do NOT loosen (Lead §9 2026-10-26)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-26T16:39:54.519Z
---

**The class:** an endpoint doing a BENIGN, reversible edit (set job-type/service, replace line items) must NOT block on raw `if so.get('invoice_ids'):` — a stranded **DRAFT** invoice (abandoned Stripe checkout, pay-link / plain-send preview) leaves `invoice_ids` non-empty and FALSE-blocks with red "This job is already invoiced -- change the … before it is billed." Gate instead on **`_has_posted_invoice(invoice_ids)`** (brain.py ~464 — `account.move` search `state=='posted'`, limit 1) so only a REAL posted bill blocks. Fail-safe by design: the helper has NO internal try/except → a read error propagates → the route's own try/except → 500 → blocked (conservative for a money-adjacent path).

- **Fixed to posted-only:** `save_job_lines_core` (line edit, brain.py ~485) — 2026-09-14 (Lead-blessed). `job_set_service` (quote-accept sets job-type, brain.py ~587) — 2026-10-26, main `ae99ce3a`, after DJ hit the live false positive ($417 quote / 36 panes at a job site). **No double-bill:** these write a label / SO lines, not an invoice (Audit-proved job_set_service does only reads + one scalar job_type write).
- **DO NOT loosen (analyzed 2026-10-26 under Lead's §9 ruling — assessed per-guard, not swept):**
  - dashboard.py `api_delete_so` (~10474) + `api_delete_job` (~11875): block DELETE on ANY linked invoice incl draft → "cancel/refund first". INTENTIONAL — avoids orphaning accounting on a destructive op. Loosening = data-integrity risk (not double-bill). Leave.
  - `api_stripe_check_payment` (~6829) + the customer/job READ (~5435): NOT blocks — a poll/read that gates on invoice_ids then narrows to `state='posted'` / fetches payment display. Leave.
  - invoice-CREATE path (~12706): gates on `invoice_status == 'invoiced'` (not raw invoice_ids) — this PREVENTS creating a 2nd invoice. Loosening = **DOUBLE-BILL RISK**. MUST stay.
- **Stranded-draft cleanup:** `_create_stripe_tip_link` REUSES an existing unpaid draft, so a stale draft with the OLD amount can bill wrong later — after re-pricing, have Operator delete the stranded draft so the eventual invoice carries the new total.

**How to apply:** a new "refuse if invoiced" guard on a BENIGN/reversible edit → use `_has_posted_invoice`, never raw `invoice_ids`. On a DESTRUCTIVE (delete) or invoice-CREATING action, blocking on any invoice / `invoice_status=='invoiced'` is correct — leave it. See [[feedback_root_cause_not_just_instance]], [[project_v2_job_is_live_job_detail_screen]].
