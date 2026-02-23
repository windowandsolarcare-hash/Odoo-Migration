# Reactivation Workflow and Phase 3/4 Handling

**Context:** You run the **Reactivation Server Action** (Phase 2) on a dormant Sales Order in Odoo. That creates an Opportunity and sends SMS via Zapier/Workiz. When the customer books or a new job is created in Workiz for that lead, Phase 3 and Phase 4 treat it like any other job — no special “reactivation” branch.

---

## 1. What the Reactivation Server Action Does (Phase 2)

- **Trigger:** You select a **dormant Sales Order** in Odoo and run **"LAUNCH Reactivation"** (Server Action).
- **Actions:**
  - Creates a **CRM Opportunity** (stage: Reactivation) with expected revenue and price list.
  - Sends SMS via **Zapier webhook** (Workiz may use a “graveyard” or API job for delivery; status can show as **"API SMS Test Trigger"**).
- **It does NOT:** Create a new Sales Order or a new Workiz job. The *customer* (or you) creates the new job later (e.g. via Calendly booking or manually in Workiz).

**Script:** `1_Active_Odoo_Scripts/odoo_reactivation_launch.py` (pasted into Odoo Server Action).

---

## 2. How the New Job (e.g. 004162) Is Created and Synced

When a **new job** is created in Workiz for that reactivation lead (e.g. after they book or you create it):

| Step | What happens |
|------|-------------------------------|
| 1 | New job exists in Workiz (status often **"Submitted"** or SubStatus **"API SMS Test Trigger"**). |
| 2 | **Phase 3** (Workiz trigger: **New Job Created**) runs → finds or creates Contact/Property → **creates the new Sales Order** in Odoo (e.g. **004162**). |
| 3 | **Phase 4** (Workiz trigger: **Job Status Changed**) may run. It **skips** when status is **"Submitted"** so it doesn’t create a second SO or conflict with Phase 3. |
| 4 | When you later change the job in Workiz (e.g. to **"Send confirmation text"**, **"Scheduled"**, **"Next appointment"**), Phase 4 runs again → updates that same SO (004162), can confirm it and sync tasks. |

So **004162** is the **new** SO tied to the **new** Workiz job that came from the reactivation path. The **old** SO (e.g. **003132** for Art Marbach) stays as the historical/dormant order you launched reactivation from.

---

## 3. “2 rows for 004162” on the Contact

On the Contact (e.g. Art Marbach) you see **two rows** for **004162** with the same details (Feb 20, 11:45 PM, API SMS Test Trigger, $0.00). That usually means:

- **Same SO, shown twice** in the “Quotations and Sales” list (e.g. list view domain or grouping showing the same record twice), **or**
- Two different records (e.g. two SOs with the same number — less likely).

**What to do:** In Odoo, open each row and check **SO id** (and **Workiz UUID**). If both rows open the same SO (same id), it’s a **display/domain issue** in the view, not two separate jobs. If you want, we can add a one-off check script that lists SOs by Contact and flags duplicate `name` (SO number) for the same `id`.

---

## 4. Summary: How We Handle Reactivation Jobs

- **Reactivation Server Action** = Phase 2 only (Opportunity + SMS). No SO or Workiz job creation there.
- **New Workiz job** (from reactivation lead) is handled like any other new job:
  - **Phase 3** (New Job) → creates the new SO (e.g. 004162).
  - **Phase 4** (Status Changed) → skips when status is **"Submitted"**; when status is one of **Next appointment / Send confirmation text / Scheduled**, it updates and can confirm that SO and sync tasks.
- There is **no separate “reactivation” logic** in Phase 3 or Phase 4 — same paths (A/B/C) and same confirm/skip rules.

If you want different behavior for jobs that came from reactivation (e.g. different status or a tag), we’d add a rule based on a Workiz field (e.g. Lead Source = "Reactivation Lead") in Phase 3/4.
