# Payment Entry: What to Revert and What to Use

**Purpose:** Clarify what the previous chat changed, what to turn off, and what minimal setup to use so payment entry lives in Odoo (SO → Invoice → Collect Payment) with as little custom code as possible.  
**Date:** February 2026

---

## 1. Your goal (recap)

- **Stop** entering payments in Workiz (type, reference/check number, date, amount → balance zero → mark Done).  
- **Start** entering payments in Odoo: from a Sales Order, create an invoice, then use a **Server Action** that opens a form where you choose **journal (bank)**, **payment method** (Check/Cash/Credit), **amount**, **today’s date**, and **reference (check number)**.  
- You want to **remove or simplify** as much of the code that was added to make payment work, and you want to know how Server Actions work (one copy, backup/duplicate before edit).

---

## 2. What the previous chat did (and why it’s messy)

In `0_One_Off_Scripts/` there are **dozens** of payment-related scripts. In summary they:

| Category | What was done | Problem |
|----------|----------------|---------|
| **Payment register wizard** | Many scripts tried to “fix” the **Register Payment** wizard (`account.payment.register`): currency_id visibility, required fields, payment method filters, etc. | The wizard is standard Odoo; changing it with view inheritances and one-off fixes is fragile and hard to reset. |
| **Payment method names** | Renamed Odoo payment method lines (e.g. “Manual Payment” → “Cash”, “Checks” → “Check”). | Not necessarily wrong, but if something breaks you have to remember what was renamed. |
| **“Collect Payment” Server Action** | Created an action that opens the payment form with defaults. Then “fixed” it multiple times: `fields.Date.today()` (forbidden in sandbox), then `from datetime import date` (also forbidden), then changed to **creating the payment in code** and posting it (no form — so you can’t enter check number or confirm details). | Each “fix” added more code and moved further from your desired flow (form where you enter journal, method, amount, date, ref). |
| **View inheritances** | Added views for currency on wizard, “check number” on payment form, memo position, payment method domain, etc. | Multiple custom views; hard to know which are safe to disable. |
| **Extra Server Actions** | “Post Payment”, “Apply Payment to Invoice”, etc. | More moving parts; standard flow only needs one “open payment form” action. |

So: a lot of one-off changes, and the **Collect Payment** action was “fixed” in a way that **removed** the form and your ability to enter reference/check number.

---

## 3. What to do: simplify and use one action

**Principle:** Use **standard Odoo** as much as possible. One **minimal** Server Action that only **opens** the standard payment form with defaults. No wizard hacks, no creating payment in code.

### Step 1: Disable the customizations (optional but recommended)

The repo has a script that disables the custom Server Actions and view inheritances that were added:

- **File:** `0_One_Off_Scripts/reset_to_odoo_original.py`

It disables:

- Server Actions: “Collect Payment” (674), “Post Payment” (675), “Apply Payment to Invoice” (677)
- View inheritances (by ID): memo, check number, currency, payment method domain

**Run it** if you want to clear the old customizations. That will also disable the current “Collect Payment” action (so the button disappears until you re-add it).

### Step 2: Add back only the minimal “Collect Payment” action

After reset (or if you didn’t reset), you want **exactly one** Server Action:

- **Name:** e.g. “Collect Payment”
- **Model:** Invoices (`account.move`)
- **Binding:** Form (so it appears in the Action menu on an open invoice)
- **Code:** The minimal code in **Collect_Payment_Action_Minimal.md** (opens `account.payment` form with context; no `import`, no creating payment in code)

So you are **not** re-enabling the old “Collect Payment” that might create payment in code; you are **creating or overwriting** it with the minimal version that only opens the form.

### Step 3: Reference (check number) on the payment form

- Standard Odoo payment form usually has a **Memo** or **Reference** or **Communication** field. Use that for the check number.
- If it’s missing, add **one** field (Reference/Communication) to the payment form via **Studio**. Do **not** re-run the old “add check number” scripts that may create custom fields or multiple view inheritances.

### Step 4: Don’t re-run the one-off payment scripts

The 70+ scripts in `0_One_Off_Scripts/` for payment/invoice were exploratory and fix-on-fix. For the **live** flow we only need:

- Standard: **Create Invoice** from SO, **Confirm** invoice.
- One Server Action: **Collect Payment** (minimal code from Collect_Payment_Action_Minimal.md).
- Standard: **Payment** form (with Ref/Memo/Communication visible), then **Create** and **Validate**.

No wizard fixes, no “fix_currency_id”, no “fix_payment_ref_field” (that one replaced the form with code), no “create_payment_direct”, etc.

---

## 4. How Server Actions work (backup / copy)

- There is **only one copy** of each action in the database; editing it changes the live behavior.
- **Before editing:** Copy the action’s Python code to a file in this repo (e.g. in `Phase 6 Handoff/backups/` or `1_Active_Odoo_Scripts/`), or duplicate the action in Odoo and disable the duplicate.
- **After editing:** Update that file with the new code so the repo stays the source of truth and you can reset by pasting back.

Details: **Odoo_Server_Action_Backup_and_Edit.md**.

---

## 5. Summary table

| Do this | Don’t do this |
|---------|----------------|
| Use one Server Action that **opens** the payment form with defaults | Use an action that **creates** the payment in code (no form for ref/date/method) |
| Rely on standard payment form (Journal, Method, Amount, Date, Ref/Memo) | Re-run scripts that change the register wizard or add many view inheritances |
| Back up action code in the repo before editing | Edit the only copy in Odoo without a backup or duplicate |
| Add Ref/Communication via Studio if missing on payment form | Run the old “add check number” / “fix payment ref” scripts |
| Run `reset_to_odoo_original.py` if you want to clear old customizations | Re-enable all disabled actions and views without checking what they do |

---

## 6. Files in this handoff

| File | Use |
|------|-----|
| **Odoo_Server_Action_Backup_and_Edit.md** | How Server Actions work; backup and copy-before-edit. |
| **Collect_Payment_Action_Minimal.md** | Exact minimal code for “Collect Payment” and how to use it. |
| **Payment_Entry_What_to_Revert_and_Use.md** | This file: what to revert, what to use, what to avoid. |

After you apply the minimal action and ensure the reference field is on the payment form, your flow is: **SO → Create Invoice → Confirm → Actions → Collect Payment → fill journal, method, amount, date, ref → Create → Validate.** No extra procedures; Phase 6 (sync to Workiz) can be added later.
