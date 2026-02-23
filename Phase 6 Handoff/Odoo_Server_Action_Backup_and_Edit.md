# Odoo Server Actions: Backup, Edit, and Copy-Before-Edit

**Purpose:** How Server Actions work in Odoo and how to change them safely so you can reset if needed.  
**Date:** February 2026

---

## 1. Is there only one copy? Do I modify the only copy?

Yes. In Odoo, each Server Action is **one record in the database**. There is no separate “file” that Odoo reads. When you edit an action in the UI (Settings → Technical → Automation → Server Actions), you are editing that **only live copy**.

So:
- **Editing** = you change the live action. There is no automatic backup.
- **Backup** = you must create a copy yourself (see below).

---

## 2. How to back up before editing

**Option A: Copy the code to this repo (recommended)**  
1. In Odoo: Settings → Technical → Automation → Server Actions.  
2. Open the action (e.g. “Collect Payment”).  
3. Copy the **Python code** from the “Python Code” field.  
4. Paste it into a file in this project, e.g.  
   `Phase 6 Handoff/backups/Collect_Payment_Action_2026-02-XX.py`  
   or  
   `1_Active_Odoo_Scripts/odoo_collect_payment_BACKUP.py`  
5. Commit that file. Now you have a version you can restore from.

**Option B: Duplicate the action in Odoo**  
1. Open the Server Action.  
2. Use **Duplicate** (or copy the action and give it a new name, e.g. “Collect Payment – Backup”).  
3. **Disable** the duplicate so it doesn’t appear in menus.  
4. Edit the **original** as needed. If something goes wrong, you can disable the original and enable the duplicate, or copy code from the duplicate back into the original.

**Option C: Export (Technical)**  
- Use Settings → Technical → Server Actions → select the action → Export. You get a CSV/XML with the action definition. Keep that file as a backup.

---

## 3. Recommended practice from now on

- **Before changing any Server Action:**  
  - Copy its code into a file in this repo (with a date or version in the name), **or**  
  - Duplicate the action in Odoo and disable the duplicate.  
- **After changing:**  
  - Update the same file in the repo with the new code so the repo always has the “current” version.  
- That way you can **reset** by pasting the backup code back into the action in Odoo, or by re-creating the action from the file.

---

## 4. Where Server Actions live in Odoo

- **Menu:** Settings → Technical → Automation → Server Actions (or, in some versions, Settings → Technical → Actions → Server Actions).  
- **Model:** `ir.actions.server`.  
- **Stored in:** The database. No `import` in the Python code (sandbox restriction).  
- **Binding:** If “Binding” is set to a model and view type (e.g. Invoice, Form), the action appears in the **Action** menu on that form.

---

## 5. Summary

| Question | Answer |
|----------|--------|
| Do I modify the only copy? | Yes, unless you duplicate the action first. |
| Is there an automatic backup? | No. You must back up the code or duplicate the action. |
| How do I back up? | Copy the Python code to a file in this repo and/or duplicate the action in Odoo. |
| How do I reset later? | Paste the backup code back into the action, or enable a duplicated action and disable the broken one. |

Going forward: **always make a copy (in repo or in Odoo) before editing a Server Action.**
