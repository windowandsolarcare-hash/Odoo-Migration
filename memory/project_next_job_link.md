---
name: project_next_job_link
description: "Phase 5 stores the NEXT maintenance job's Workiz link on the COMPLETED job's invoice (account.move x_studio_workiz_job_link). Field app surfaces it as \"Next job in Workiz\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

# "Next job in Workiz" — link to the Phase-5-created next maintenance job (2026-06-18)

**System behavior (Phase 5, `zapier_phase5_FLATTENED_FINAL.py`):** when a MAINTENANCE job completes, Phase 5 `create_next_maintenance_job` POSTs a new Workiz job, then `update_invoice_with_workiz_link(invoice_id, new_uuid, …)` writes the NEW job's Workiz URL **`https://app.workiz.com/root/job/{new_uuid}/1`** onto the **COMPLETED job's invoice** → `account.move` field **`x_studio_workiz_job_link`** (the "Workiz Link" invoice field). It also writes `x_studio_next_job_date` on the contact and posts to chatter. Phase 5 is triggered by Phase 6 (payment webhook) — i.e. it runs AFTER payment is recorded, asynchronously via Zapier (seconds–minutes).

**DJ's workflow:** record payment on a maintenance job in the field → then go to the NEXT job in Workiz to send it to the customer. The field "Open in Workiz" only opened the CURRENT job; the next job's link was buried on the invoice.

**Shipped (commits 8daa1fc dashboard.py + 527ab48 field.html):**
- **Backend `GET /owner/api/next_job_link?so_id=`** (dashboard.py, next to `api_set_block_status`): reads the SO's `invoice_ids` → first `account.move` with a non-empty `x_studio_workiz_job_link` → returns `{ok, link}`. Empty link = Phase 5 hasn't run yet (or not a maintenance job).
- **Field 3-dot menu item "📋 Next job in Workiz →"** — shown ONLY when the job's status includes 'done' (next job only exists after completion). Handler `openNextJobInWorkiz(btn)` fetches the link live and `window.open`s it; if empty, toasts "Next job isn't ready yet — created right after payment, try again in a minute" (handles the Phase-5 async delay). Double-tap guard `_nextJobPending`, 10s timeout.

## Maintenance to Schedule report SIMPLIFIED (2026-06-18, commits 40d3bb1 + 1f6888f)
DJ asked why a paid maintenance customer (Gayle 004770) wasn't on the report. Root cause: the report (maintenance.html) read a CACHE (`/api/submitted_jobs`, built by `_submitted_jobs_refresh_worker` in dashboard.py) that **excludes any next-job UUID that already has an Odoo SO** (Step 3) — so once Phase 3 syncs the next job to Odoo as a Submitted draft, it dropped off. DJ: "simplify the whole thing — just list all jobs with Workiz status = Submitted in Odoo; tap → launch Workiz preloaded with item + price."
- **`/api/scheduled_sos`** (submitted_jobs.py) is now the report's source: queries `sale.order` where `x_studio_x_studio_workiz_status='Submitted'`, `state != 'cancel'`, `date_order >= today`. **Dropped the old `state in ['sale','done']` filter** (Submitted next-jobs are DRAFT → it hid them all). Returns customer, date, `workiz_link` (or built from uuid), and `lines`. **Line-item fallback:** Phase-5 next jobs often have NO order lines on the SO yet → backend pulls the customer's most recent PAST job's lines (`date_order < today`, by `partner_shipping_id`) as the recurring item+price.
- **maintenance.html** now: simple list of all Submitted jobs; tap → `launchWorkiz(idx)` preloads the clipboard (price then name per item — Duplicate-flow 2-clip paste) + opens the Workiz job. The old slot-picker (`openDetail`/`/api/maintenance/detail`/`set_slot`/map) is LEFT IN PLACE but unused (not deleted). Refresh just reloads.
- **⚠ ITEM SOURCE — use Phase 5's `next_job_line_items`, NOT a naive prior-job lookup (DJ correction 2026-06-18):** Phase-5 next jobs have NO Odoo SO order lines. The correct items live on the **Workiz job's `next_job_line_items`** text field, which Phase 5 (`get_line_items_for_next_job`) computes **alternating-aware**: for an alternating customer (`alternating` Yes), it pulls the line items from the most recent job matching the NEXT job type — i.e. effectively **two jobs ago**, not the immediately previous job. Format: lines `Name: $Price` (or `Name (xN): $Total`) under a `LINE ITEMS TO ADD:` header. New endpoint **`GET /api/maintenance/items?uuid=`** (submitted_jobs.py) does `workiz_get('job/get/{uuid}/')` and parses that block → `[{name, price}]`. `launchWorkiz` calls it FIRST (authoritative), falls back to the SO's own `lines` only if Phase 5 left nothing. My earlier "most recent past job" fallback was WRONG for alternating and was removed. (Gayle JX7W1C verified: `Windows In & Out - Full Service: $175.00`.) Workiz GET on tap = one call, fine.
- ⚠ STILL on the old cache: the separate **"Submitted Jobs"** tile → `/owner/submitted_jobs` → dashboard.py route → submitted_jobs.html (uses `/api/submitted_jobs` cache). Not yet unified with the new simple view. Offer to point it at /owner/maintenance or the new endpoint if DJ wants one report.

**Why live-fetch (not baked into schedule data):** the link only appears after Phase 5 runs post-payment, so fetching on tap (rather than at schedule load) gives the freshest answer and a clear "not ready yet" message. Related: [[project_field_paid_banner]], CLAUDE.md Phase table.
