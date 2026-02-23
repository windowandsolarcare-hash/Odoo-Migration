# Pay Button (top bar) vs Pay in Gear (Server Action) — What’s Different

**Purpose:** Explain why the **top “Pay” button** works (same form every time: Journal, Method, Amount, Date, Memo → Paid) and why the **Pay (or similar) option in the gear** can open a different window and show “missing field required”.  
**Date:** February 2026

---

## 1. What the script found (your database)

From **`compare_pay_button_vs_gear_pay.py`** run against your Odoo:

### In the **gear menu** (Server Actions on Invoices) you have:

| ID  | Name             | Module  | What it does |
|-----|------------------|---------|----------------|
| **350** | **Pay**        | account | **Standard Odoo.** Code: `records.action_force_register_payment()`. This **opens the payment register wizard** (Journal, Method, Amount, Date, Memo) — same flow as the top button. |
| **674** | **Collect Payment** | (custom) | **Our custom action.** Opens **`account.payment`** form (direct payment form), **not** the payment register wizard. Different layout and required fields → often “missing field required”. |

So in the gear you have **two** actions:

- **Pay (350)** – standard, same behavior as the top **Pay** button (wizard).
- **Collect Payment (674)** – custom, opens a **different** window (payment form) and is the one that can show “missing field required”.

---

## 2. Why the top “Pay” button works

- The **top bar “Pay”** (after you confirm the invoice) is tied to the **same** logic as the **Pay** server action **ID 350**: it calls `action_force_register_payment()` on the invoice.
- That method **opens the payment register wizard** (`account.payment.register`), which is the form where you choose:
  - Journal (Bank)
  - Payment method (Check, etc.)
  - Amount (defaults to invoice)
  - Date (e.g. today)
  - Memo
- When you submit that wizard, Odoo creates the payment, posts it, reconciles, and the invoice shows **Paid**. So that flow is correct and consistent.

---

## 3. Why the gear can feel “different” and show “missing field required”

- If you use the gear and pick **“Collect Payment”** (ID 674), that action **does not** open the payment register wizard. It opens the **direct payment form** (`account.payment`), which:
  - Has a **different** layout and set of fields,
  - Uses **different** required fields / validation,
  - Does **not** go through the same “register payment” logic as the wizard,
  - So you can get **“missing field required”** even when you think you filled everything.

So the “different window” and “missing field required” match **Collect Payment (674)**, not the standard **Pay (350)**.

- If you use the gear and pick **“Pay”** (ID 350), you should get the **same** wizard as the top button. If you still see a different window or “missing field required” when clicking **Pay** in the gear, it may be due to invoice state (e.g. draft vs confirmed) or view/button configuration; the **code** for 350 is the same as the button.

---

## 4. Recommendation

- **For the flow that works every time:**  
  Confirm the invoice → use the **top “Pay” button** (or the **“Pay”** entry in the gear, **not** “Collect Payment”). That uses the **payment register wizard** and gets you to **Paid** with Journal, Method, Amount, Date, Memo.

- **To avoid confusion and “missing field required”:**  
  Prefer **not** using **“Collect Payment”** in the gear for this flow, unless we change it so it opens the **same** wizard (e.g. open `account.payment.register` with the right context instead of `account.payment`). Then the experience would match the button.

---

## 5. Fix applied (Feb 2026)

The **Collect Payment** (ID 674) Server Action was updated so it **no longer** opens the `account.payment` form. Its code was replaced with the **same** logic as the standard Pay (350):

```python
if records:
    action = records.action_force_register_payment()
```

So now **both** ways to pay use the **exact same workflow**:
- **Top “Pay” button** → payment register wizard → Journal, Method, Amount, Date, Memo → Submit → Paid.
- **Gear “Collect Payment”** → **same** payment register wizard → same fields → Submit → Paid.

The old code (opening `account.payment`) was backed up to **Phase 6 Handoff/backups/collect_payment_674_before_wizard_fix_*.json**. Script: `1_Active_Odoo_Scripts/fix_collect_payment_to_use_register_wizard.py`.

---

## 6. One-line summary

- **Top “Pay”** and **gear “Collect Payment”** now both open the **payment register wizard** (same workflow). The code that opened the `account.payment` form (and caused “missing field required”) was removed and replaced with the standard wizard logic.

---

## 7. Unconfirmed (draft) invoice: Pay from gear used to error

- **Problem:** When the invoice is **unconfirmed (draft)** and you use **Pay** from the gear (server action 350), the payment register wizard could open but then show **“missing required field”** (often **currency**). Standard Odoo code does not always pass `default_currency_id` to the wizard when the move is still draft.
- **Fix:** Both **Pay (350)** and **Collect Payment (674)** were updated to pass `default_currency_id` (and company fallback) in context before calling `action_force_register_payment()`, so the wizard gets the required field even for draft invoices.
- **Script:** `1_Active_Odoo_Scripts/fix_pay_and_collect_payment_for_draft_invoice.py`. Backups: `Phase 6 Handoff/backups/pay_350_collect_674_before_draft_fix_*.json`.
- **Result:** You can use either **Pay** or **Collect Payment** from the gear on **confirmed or unconfirmed** invoices; both open the same payment register wizard and, after Submit, the invoice goes to **Paid** (payment created, posted, reconciled). **Collect Payment** therefore does the full workflow (same as the Pay gear used to do before the error), including reconciliation. If you still see an error, confirm the invoice first then use Pay or Collect Payment.

---

## 8. Next: Phase 6 after payment (sync to Workiz)

After you **submit/confirm** in the **Pay** wizard and the invoice shows **Paid**, the next step is:

- Trigger API calls to **Workiz** with: **payment method** (type), **amount**, **memo/reference**.
- In Workiz: **add payment** and **mark job Done**, so your existing phases (duplicate jobs, etc.) run as today.

That will be implemented separately; this doc only clarifies the difference between the two “Pay”-like actions so you always use the one that works (the wizard).
