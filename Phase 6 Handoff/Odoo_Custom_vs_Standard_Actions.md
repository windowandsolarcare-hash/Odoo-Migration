# How to Tell Custom vs Standard Odoo Logic (Server Actions)

**Purpose:** So you can see what was **created by us** (the project) versus what is **standard Odoo** — and compare code or behavior.  
**Date:** February 2026

---

## 1. How Odoo marks "standard" vs "custom"

In Odoo, records (including Server Actions) can have an **External ID** (also called XML ID). That's stored in the table **`ir.model.data`**:

- **Standard Odoo** actions are loaded from **modules** (e.g. `account`, `sale`). When they're created, Odoo also creates an `ir.model.data` row with:
  - **module** = the app name (e.g. `account`, `sale`)
  - **name** = an internal id (e.g. `action_account_invoice_register_payment`)
  - **model** = e.g. `ir.actions.server`
  - **res_id** = the numeric ID of the action

  So standard actions have an External ID like **`account.action_...`** or **`sale.action_...`**.

- **Custom** actions (created in the UI, by Studio, or by our scripts) usually:
  - Have **no** `ir.model.data` row, so **no** External ID, or
  - Have an auto-generated one like **`__export__.ir_actions_server_674_xxxx`** (from an export), or
  - Live under a generic module (e.g. `base`) with a generic name.

So: **if an action has an External ID that belongs to a real Odoo app (e.g. `account.xxx`, `sale.xxx`), it's standard. If it has no External ID or something like `__export__...`, it's custom (ours or another custom).**

---

## 2. "Collect Payment" is custom (created by us)

The **Collect Payment** Server Action was created by our script (`create_collect_payment_action.py` in `0_One_Off_Scripts`). It is **not** part of standard Odoo. Standard Odoo for "pay an invoice" is usually:

- A **button** that runs an action (e.g. "Register Payment" / "Pay") which opens the **payment register wizard** (`account.payment.register`), not a custom "Collect Payment" that opens the payment form directly.

So:

- **Standard:** "Register Payment" / "Pay" → opens wizard `account.payment.register`.
- **Ours:** "Collect Payment" → Server Action that opens `account.payment` form with context (created by us).

---

## 2b. The "Pay" action may have been modified by us

We may have **modified** the standard **"Pay"** action (the one that opens the payment register wizard). If so:

- It will **still show as "Standard"** in the list script (module = `account`), because the script only checks **origin** (External ID / `ir.model.data`). It does **not** detect whether the record was **edited** after install.
- So: **Standard (by origin) ≠ unchanged.** An action can be from the `account` module and yet have custom code or context that we changed.

**Implication:** Treat the **"Pay"** action as **possibly modified by us**. To see what it looks like now, back up its current definition (see §5). To compare with true standard Odoo, you'd need a clean Odoo database or the Odoo source for the `account` module.

---

## 3. How to see what's custom vs standard in Odoo

**Option A: In the Odoo UI (Developer Mode)**

1. Enable **Developer Mode** (Settings → Activate the developer mode).
2. Go to **Settings → Technical → Automation → Server Actions** (or Actions → Server Actions, depending on version).
3. Open an action (e.g. "Collect Payment").
4. In the form, look for **External ID** (sometimes at the bottom, or in "Technical" / "Developer" section).  
   - If it shows something like **`account.action_...`** → standard.  
   - If it shows **`__export__.ir_actions_server_674_...`** or **nothing / "—"** → custom (likely ours or from UI/Studio).

**Option B: List actions and their origin (script)**

Use the script we added: **`1_Active_Odoo_Scripts/list_invoice_actions_custom_vs_standard.py`**.

It:

- Finds Server Actions (and optionally window actions) that are bound to **Invoices** (`account.move`).
- For each action, looks up **`ir.model.data`** to see if it has a **module** and **External ID**.
- Prints a short table: **ID, Name, Module, External ID, Custom?** and (for server actions) a **code preview**.

So you can see at a glance:

- **Collect Payment** → no module / `__export__` → **Custom (ours)**.  
- **Register Payment** or **Pay** with **module = account** → **Standard by origin** — but the **"Pay"** action may have been **modified by us**, so it might not be unchanged Odoo logic (see §2b).

That gives you "what code looks like" (our custom action's code) versus "what Odoo standard logic is" (the standard action, which is usually a window action or server action defined in the `account` module and not editable as "Python code" in the same way — often it's "open wizard" with no custom Python).

---

## 4. Comparing "our code" vs "standard logic"

- **Our custom action:** You can see the exact code in:
  - The Server Action form in Odoo (Python Code field), or
  - The minimal version we documented: **Phase 6 Handoff/Collect_Payment_Action_Minimal.md**, or
  - A backup file you saved (e.g. in **Phase 6 Handoff/backups/**).

- **Standard "Pay" / "Register Payment":** That's usually an **ir.actions.act_window** (or a small server action) that opens the wizard. Its "code" is not a big Python block — it's a definition like "open this wizard with this context." You can see it in Odoo by finding the action (e.g. search Server Actions / Window Actions for "Pay" or "Register Payment" on `account.move`) and checking its definition. Standard one often has **module = account** and an External ID like **`account.action_...`**.

So:

- **Custom (ours):** identifiable by **no standard module** / `__export__` and by the **Python code** we wrote (open `account.payment` form with context).  
- **Standard:** identifiable by **module = account** (or another core app) and by the fact it usually opens the **payment register wizard**, not the payment form directly.

---

## 5. Backing up the current "Pay" action (to see what we have vs standard)

Because the **"Pay"** action may have been modified, it helps to **dump its current definition** so you can:

- Keep a backup of what's in the database now.
- Compare later to standard Odoo (e.g. from a clean install or Odoo source).

Use the script **`1_Active_Odoo_Scripts/dump_pay_action_for_backup.py`**. It finds the "Pay" action (server or window) bound to Invoices and writes its full definition (including code if it's a server action) to a file in **Phase 6 Handoff/backups/** (create the folder if needed). Run it whenever you want a snapshot of "what Pay looks like now."

---

## 6. Summary

| Question | Answer |
|----------|--------|
| Is "Collect Payment" standard Odoo? | No. It was created by us (script in the project). |
| Is "Pay" standard Odoo? | It **originated** from Odoo (module `account`), but we may have **modified** it — so it can show as "Standard" in the list but still contain our changes. |
| How do I see what's custom vs standard by origin? | Check **External ID** in Odoo (Developer Mode) or run **list_invoice_actions_custom_vs_standard.py**. |
| Standard (by origin) = | Has **module** like `account` / `sale` in **ir.model.data** (External ID like `account.xxx`). |
| Custom (ours) = | No such module, or External ID like `__export__.ir_actions_server_674_...`. |
| How do I see what "Pay" looks like now? | Run **dump_pay_action_for_backup.py** to save its current definition to a file for backup/comparison. |
| Where is our Collect Payment code? | In the Server Action in Odoo; minimal version in **Collect_Payment_Action_Minimal.md**; backups in repo if you saved them. |

Using the list script, you see which actions are custom vs standard **by origin**. Remember: the **"Pay"** action can still be standard by origin but **modified by us**; use the dump script to capture its current state for comparison or revert.
