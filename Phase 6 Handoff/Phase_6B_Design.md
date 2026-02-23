# Phase 6B: Workiz → Odoo Sync (No Schedule — Invoice-Time + Status-Change)

**Purpose:** Keep Odoo in sync with Workiz so invoicing in Odoo matches what was done, **without** running a heavy “get all jobs” sync every 4 hours.

**Status:** Preferred approach is **no 4-hour schedule**. Use (1) **invoice-time refresh** and (2) **status-change** triggers instead.

---

## Why Not a 4-Hour Schedule?

- **GET /job/all** returns a lot of data and isn’t meant to be run every 4 hours just to sync.
- We **do** have the job **UUID** when we need it: from the Sales Order (`x_studio_x_studio_workiz_uuid`) when you’re about to invoice. So we can refresh **that one job** from Workiz right before invoicing.

---

## Two Ways to Keep Things Mirrored (No Schedule)

### 1. At invoice time — “Refresh this job, then invoice”

When you click the button to create the invoice (in the Phase 6 / invoicing workflow):

1. **Before** creating the invoice, the system takes the current SO’s Workiz UUID.
2. Calls Workiz API to get the **latest job** for that UUID (`get_job_details(uuid)`).
3. Runs the same “update SO + property” logic as Phase 4 for **that one job** so Odoo is up to date.
4. Then continues with the rest of the invoicing workflow.

So **right before invoicing**, both systems are mirrored for that job. No “get all jobs”; we only need the one UUID we already have on the SO.

**To implement:** Options (user is open to either):
- **Option A:** New button **“Update Workiz”** that runs the one-job refresh (Phase 4 for that SO’s Workiz UUID); then user clicks **“Create Invoice”** as today. No change to the existing Create Invoice button.
- **Option B:** Hook the refresh into the existing Create Invoice flow (e.g. server action or webhook before invoice creation).  
Once we know which option and where the invoice action lives, we can implement.

---

### 2. When you change something in Workiz — use a status like “Upload Data 2OD”

- In Workiz, create a **new status** (e.g. **“Upload Data 2OD”** or “Sync to Odoo”).
- Whenever you make a change in Workiz and want it in Odoo, change the job’s status to that (e.g. to **Upload Data 2OD**).
- Workiz fires **“Job Status Changed”** → your existing Zap runs **Phase 4** with that job’s UUID → Odoo SO (and property) get updated.
- You can flip back to **Submitted** (or whatever) and later flip again to **Upload Data 2OD**; **each status change** runs Phase 4. So: Submitted → Upload Data 2OD → Submitted → Upload Data 2OD is fine; each time Phase 4 runs and updates Odoo.

No new Zaps needed for this — Phase 4 is already triggered by **any** status change. You only need the new status in Workiz and to use it when you want to push data to Odoo.

---

## What you need to do (no dry run required for normal use)

- **Dry run (`PHASE6B_DRY_RUN=1`):** Only for **testing** the bulk “list open jobs” script (e.g. to see how many open jobs you have). You do **not** need to run it for normal operation.
- **Day to day:**
  - **When you want Workiz changes in Odoo:** Change the job status to your “Upload Data 2OD” (or similar) status so Phase 4 runs. You can go back to Submitted and back to Upload Data 2OD as many times as you want; each change triggers an update.
  - **When you invoice:** We’ll wire “refresh this job from Workiz, then create invoice” into your invoice button/workflow (once we know where that is).

---

## One-time mass backfill (all open jobs → Sales Orders)

**Purpose:** Bring **all current open jobs** from Workiz into Odoo **once** (create or update SO per job) so Odoo has present/future jobs, not only historical.

**Script:** `2_Modular_Phase3_Components/phase6b_sync_open_jobs_to_odoo.py`

**What it does:**
1. Calls Workiz `GET /job/all?only_open=true&start_date=...&records=100&offset=...`.
2. **Pagination:** Fetches 100 jobs at a time. Offset is **page index 0, 1, 2, 3, 4...** (increment by 1; each page = 100 records, per Workiz support). When a page returns **fewer than 100 jobs**, there are no more pages and the loop stops (no “there’s more” message from the API — we just stop when the page is short).
3. Collects all job UUIDs from every page.
4. For each UUID, runs **Phase 4 in this Python process** (no Zapier — one run = one process): find SO by UUID; if not found, Phase 3 creates it; then update all SO/property fields from Workiz. So each open job gets an SO in Odoo (created or updated).
5. At the end it prints a summary: total jobs, success count, failed count, and any errors.

**Command (when you’re ready):**  
From `2_Modular_Phase3_Components`:  
- Test (first 5 jobs): `python phase6b_sync_open_jobs_to_odoo.py 2024-01-01 5`  
- Full run: `python phase6b_sync_open_jobs_to_odoo.py 2024-01-01`  
(Or omit start_date for default 1 year ago.)

**Important:** Do **not** run the full mass sync until you give **explicit permission**. The assistant will run it only after you say to go ahead. Optional: you can ask for a small test first (e.g. first 5 jobs only) to confirm behavior before the full run.

---

## Summary

| Item | Choice |
|------|--------|
| 4-hour schedule | **No** — too much data; not desired. |
| Sync at invoice time | **Yes** — refresh **one** job (by UUID from SO), then run invoicing. |
| Sync when you change Workiz | **Yes** — use status e.g. “Upload Data 2OD”; each status change runs Phase 4. |
| Phase 4 on status change | Already in place; works for any status, including your new one. |
| Dry run | Only for testing the bulk script; not required for normal use. |
