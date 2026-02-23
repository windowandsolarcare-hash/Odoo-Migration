# Collect Payment — Minimal Server Action (Phase 6)

**Purpose:** One simple Server Action that opens the standard Odoo payment form from an invoice so you can enter journal, payment method, amount, date, and reference (check number). No custom wizard, no creating payment in code.  
**Date:** February 2026

---

## 1. Flow you want (aligned with your description)

1. You have a **Sales Order** (from Workiz or otherwise).  
2. You **create an invoice** from that SO (standard Odoo: “Create Invoice” on the SO).  
3. You **confirm** the invoice (standard “Confirm” button).  
4. On the **invoice**, you run a **Server Action** (e.g. “Collect Payment”).  
5. That action **opens the standard payment form** and asks you for:
   - **Journal** (bank account) — can be pre-filled.
   - **Payment method** (Check / Cash / Credit).
   - **Amount** — pre-filled with amount due.
   - **Date** — today (form default).
   - **Reference** (e.g. check number) — you type it.

6. You click **Create**, then **Validate**. Payment is posted and linked to the invoice.  
7. (Later, Phase 6 Zap can sync this payment to Workiz and mark the job Done.)

This doc gives you the **minimal** way to do step 4–6: one Server Action that only opens the payment form with sensible defaults. It does **not** create the payment in code (so you always get to choose method, ref, date).

---

## 2. Minimal Server Action code (sandbox-safe)

Use this **exact** code in a Server Action on **Invoices** (`account.move`). It only opens the payment form; it does **not** use `import`, `fields`, or any forbidden calls.

**Model:** `account.move` (Customer Invoices).  
**Binding:** Form view (so it appears in the Action menu on an open invoice).

```python
action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'default_payment_type': 'inbound',
        'default_partner_type': 'customer',
        'default_partner_id': record.partner_id.id,
        'default_amount': record.amount_residual,
        'default_currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
        'default_journal_id': env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
        'default_invoice_ids': [(6, 0, [record.id])],
    }
}
```

**What this does:**

- Opens the **standard** `account.payment` form in a popup.
- Pre-fills: customer, amount due, currency, bank journal (code `BNK1`), and links the current invoice.
- Does **not** set payment date (form defaults to today).
- Does **not** set reference/check number (you type it in the form).

**Reference / check number:**  
Standard Odoo payment form has a field for this — often **Memo** or **Reference** or **Communication** (label can vary by version). If you don’t see it, use **Studio** to add that one field to the payment form view; do **not** rely on the old one-off scripts that added custom fields or many view inheritances.

---

## 3. Why this is minimal (and what to avoid)

- **No `import`** — allowed in sandbox.
- **No `fields.Date.today()`** — not available in Server Actions; leaving date to the form default avoids the need for it.
- **No creating payment in code** — the previous chat’s “fix” that created the payment in Python and posted it removed your ability to enter check number and confirm details; this keeps the form so you can.
- **No custom wizard** — uses only the standard payment form.
- **No view changes in this action** — only one bank journal is pre-filled by code (`BNK1`); if your bank has another code, change that in the action or in Odoo.

---

## 4. If “Collect Payment” already exists and is broken

1. **Back up:** Open the action in Odoo, copy its Python code to a file in this repo (see `Odoo_Server_Action_Backup_and_Edit.md`).  
2. **Replace** the action’s Python code with the minimal code above.  
3. **Save.**  
4. Refresh the browser and test from an invoice.

If you prefer to start clean: create a **new** Server Action, set Model = Invoices (`account.move`), Binding = Form, paste the code above, name it “Collect Payment”. Then hide or delete the old one.

---

## 5. Reference field (check number) not visible?

- In Odoo, open one **Payment** (Accounting → Payments).  
- Check the form: do you see **Memo**, **Reference**, or **Communication**?  
- If yes: use that for the check number; no change needed.  
- If no: use **Studio** (enable Developer Mode) to add the **Reference** (or **Communication**) field to the payment form. That’s a single field addition; we are not using the old “add check number” scripts that modified multiple views or the wizard.

---

## 6. Summary

| Item | Recommendation |
|------|----------------|
| **Action** | One Server Action: “Collect Payment” on Invoice form. |
| **Code** | Only the snippet above (open payment form with context). |
| **Backup** | Copy current action code to repo before any edit; duplicate in Odoo if you want a quick reset. |
| **Reference** | Use the standard Ref/Memo/Communication field on payment; add via Studio only if missing. |
| **Avoid** | No `import`, no creating payment in code, no reliance on the many one-off payment scripts. |

This gives you the flow: **SO → Create Invoice → Confirm → Collect Payment (action) → fill journal, method, amount, date, ref → Create → Validate**, with minimal code and no custom procedures beyond one action.
