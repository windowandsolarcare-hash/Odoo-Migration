---
name: project_tip_on_overpayment
description: "How an over-payment (payment > invoice/SO total) is handled. A shared helper adds a Tip income line (non-taxable WSC-TIP product) so the invoice equals the payment → paid-in-full, zero dangling credit. Owner Pay = editable-preview confirm (not silent); paywatch = auto. Spec 3_Documentation/TIP_OVERPAYMENT_SPEC.md."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T18:28:24.024Z
---

**Tip-on-overpayment (2026-09-22, DJ greenlit; commits 6f55cbf5 backend + 5ebbc741 FE; Lead money-QC PASS on the code).** The gap I verified: recording a payment > invoice total used to park the overage as a **dangling unapplied customer credit** — not a tip, not income, invoice not paid-in-full. Fixed.

## The mechanic
- **Tip product ALREADY existed** and is NON-TAXABLE: `specialist_paywatch._tip_product_id()` → `product.product` default_code `WSC-TIP` (= id 2; also `tech/job.py _TIP_PRODUCT=2`), service, invoice_policy 'order', `taxes_id=[]`. No new product/tax needed (the gratuity-non-taxable requirement was already encoded).
- **Shared helper** `specialist_paywatch._apply_overpayment_tip(so_id, tip_amount)`: adds a `sale.order.line` (WSC-TIP, qty1, price_unit=tip) to the SO **BEFORE** the invoice is created → the invoice (built from SO lines) equals the payment → `account.payment.register` reconciles **paid-in-full, ZERO credit**. Posts SO chatter only (no customer message). **Triple idempotency:** no-op if the SO has a POSTED invoice OR an existing 'Tip' line, and callers gate on `not existing` — so re-record/re-confirm can't double-tip. tip_amount < $0.50 = no-op (rounding).

## Paths (single source via the helper)
- `dashboard._execute_payment(..., tip=None)` — the main owner recorder; adds the tip (via helper) only when a confirmed `tip>0` is passed AND no invoice yet. Default None = today's behavior (byte-identical). `/api/payment` (api_payment) forwards `tip` from the FE.
- `dashboard.api_process_payment_with_sync` — same `+tip` param.
- `dashboard.record_check_payment` (voice tool) — on `ack_mismatch` adds the real Tip line via the helper; the STALE Workiz "add tip manually" reminder is GONE (replaced by an honest "$X added as tip" / "recorded as credit" message).
- `specialist_paywatch` (email-detect, background) — stays AUTO (no live DJ to confirm), routed through the helper (single source).

## The confirm UX (owner Pay = NOT silent)
`static/owner/_job_detail_panel.js doPayment` (the shared owner Pay button): when entered amount > `activeJob.amount`, an EDITABLE-PREVIEW `prompt` — default = exact overage, editable, **CLAMPED to the overage** so the invoice can never exceed the payment (no partial-shortage) — then POSTs `tip`. No overage → no prompt. Owner paths tip only on a DJ-confirmed value (not auto); paywatch is the only auto path (background).

## Edge (acknowledged, inherent)
If the invoice was ALREADY POSTED, a line can't be added (immutable) → the overage stays a credit + the honest "recorded as credit" message fires; that pre-existing-posted case needs manual handling (credit note / manual tip).

## Live $ test = Operator's lane
The gate-2 live reconcile (create test SO → record over-payment → verify invoice==payment/paid/zero-credit → re-record for idempotency → cleanup) is a MUTATING money OPERATION → Operator executes via the app + Lead odoo-read-verifies (like the venmo $1 throwaway). Specialists owns the code, not the live money test. See [[project_payment_journal_routing]], [[feedback_assistant_use_app_workflow_not_raw_api]], [[feedback_no_mutating_smoketest_payroll]].
