# Correct Invoice → Paid Workflow (from API testing)

**Date:** February 2026  
**Source:** Script `1_Active_Odoo_Scripts/test_so_to_paid_workflow.py` run against your current Odoo 19 database.

---

## What was tested

1. **Create test Sales Order** – Partner + one product line → SO created and confirmed.
2. **Create invoice from SO** – Tried `_create_invoices`, `action_create_invoices`, `action_create_invoice`, `create_invoice` on `sale.order`. **None of these worked** via API for your Odoo 19 instance (likely uses a wizard or different entry point). Fallback: use an **existing posted unpaid invoice** to test payment.
3. **Post invoice** – Only if state = draft (skip if already posted).
4. **Create payment** – `account.payment` with:
   - `payment_type`: `'inbound'`
   - `partner_type`: `'customer'`
   - `partner_id`, `amount` (= `amount_residual`), `currency_id`, `journal_id`, `date` (today)
   - `invoice_ids`: `[(6, 0, [invoice_id])]` so it’s linked to the invoice
   - `payment_method_line_id`: one from the bank journal
   - **No** `communication` (invalid on Odoo 19)
5. **Post payment** – `account.payment` `action_post`.
6. **Reconcile** – In theory, reconcile the invoice’s receivable line with the payment move’s receivable line (same `account_id`). In our run, invoice and payment had **different account_id** for their lines, so reconciliation was not done. In the **UI**, using **Register Payment** or **Pay** normally creates the payment and reconciles in one go.

---

## Correct procedure (what you should do in the UI)

Until the SO→Invoice step is fixed via API (or you use the UI for that), the **reliable way** to get to **Paid** is:

### Option A: Full flow in UI (recommended)

1. **Sales Order** → Create (or use existing) → **Confirm**.
2. **Create Invoice** → Use the **Create Invoice** button on the SO (standard Odoo). Choose invoice type if asked.
3. **Confirm/Post** the invoice (button on the invoice).
4. **Register payment** – On the invoice, click **Pay** (or **Register Payment**). In the wizard:
   - **Journal**: Bank (e.g. BNK1).
   - **Payment method**: e.g. Check / Manual / Cash (whatever you use).
   - **Amount**: Pre-filled; change if needed.
   - **Date**: Today (or as needed).
   - **Reference** (check number): Enter if applicable.
5. **Create Payment** (or **Validate**) in the wizard.  
   Odoo then creates the payment, posts it, and **reconciles** it to the invoice. The invoice should show **Paid** in the upper right.

### Option B: If you use “Collect Payment” (our Server Action)

1. Same as above for SO and **Create Invoice** and **Confirm** invoice.
2. On the invoice, use **Action → Collect Payment** (our action that opens the payment form).
3. In the form: choose **Journal**, **Payment method**, **Amount**, **Date**, **Reference** (check number).
4. **Create** then **Validate** the payment.  
   If the payment is linked to the invoice (`invoice_ids`), Odoo may auto-reconcile; if not, you may need to **reconcile** manually (Accounting → Reconciliation, or from the invoice/payment) until the invoice shows **Paid**.

---

## What the API test proved

- **SO create + confirm** – Works.
- **Invoice from SO** – No standard method found via API; use **UI “Create Invoice”**.
- **Payment create + post** – Works with `invoice_ids`, journal, `payment_method_line_id`, no `communication`.
- **Reconcile** – Must use **same account** (receivable) on both sides. In the test, payment and invoice had different receivable accounts, so reconciliation was skipped. The **Pay / Register Payment** flow in the UI uses the correct accounts and does the reconcile for you.

---

## Next steps for you

1. **In the UI**: Follow **Option A** (Pay button + wizard) on one invoice and confirm you see **Paid**.
2. **If you prefer Collect Payment**: Use **Option B** and confirm whether the invoice goes to **Paid** after Validate; if not, reconcile once manually and note whether any extra field or link is needed.
3. **Customizations**: Once the correct UI path is clear, we can align Server Actions and any custom fields (e.g. reference/check number, journal default) with that path.
4. **SO → Invoice via API**: If you need this from scripts/Zapier, we’ll need the exact method or wizard your Odoo 19 uses for “Create Invoice” (e.g. from support or from the button’s action in the frontend).

---

## Script reference

- **`1_Active_Odoo_Scripts/test_so_to_paid_workflow.py`** – Run to create a test SO, optionally use an existing unpaid invoice, create and post a payment, and attempt reconcile. Adjust credentials (or point at test DB) as needed.
