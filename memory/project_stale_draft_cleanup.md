---
name: project_stale_draft_cleanup
description: "Stale Draft Cleanup feature — v2_residue.html review screen + tappable Catch-up Submitted rows. 3 new dashboard.py endpoints residue_drafts/cancel/restore; selector = AGE (old date_order) not $0; SOFT action_cancel + in-app action_draft restore; per-row DJ approval. Deployed 2026-10-11."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T02:03:05.820Z
---

**DEPLOYED 2026-10-11 to main (DJ "Deploy now" §12 picker; Lead QC-GREEN @ branch feee2298; Audit §15 stamped + post-live walk). Cleans up the migration-leftover draft quotes (e.g. Gregg's 2023-24 drafts created 2026-02-12 by the import — residue, not dups).**

**New endpoints — in `routers/owner/dashboard.py` LIVE copies** (NOT submitted_jobs.py — those @router twins are DEAD; dashboard.py is included first at main.py:1042 and shadows them; submitted_jobs.py still imported by catchup.py for HELPERS only):
- `GET /owner/api/residue_drafts` — age-based Odoo list, paginated ("Load more").
- `POST /owner/api/residue_cancel` — SOFT `action_cancel` (reversible, state→cancel, NEVER unlink), one batched call (not a per-SO loop → avoids 429), KV-logged. **Server re-check uses the FULL domain**: `safe_set = search(_residue_domain(_age) + [['id','in',ids]])` with `_age=int(body.get('age') or 120)` — re-validation == the list filter (denylist/company/age all re-enforced; a stale/cross-page/wrong id can't slip through). [[feedback_architect_server_revalidate_bulk_mutations]]
- `POST /owner/api/residue_restore` — `action_draft`, **guarded to state='cancel'** (409 if none) so it never un-confirms a live SO.

**`_residue_domain(age)`:** `state='draft'` AND workiz_status NOT in Done/Canceled AND `company_id in [1,False]` (rule 8) AND `date_order < today-age` AND `job_type NOT IN ['Reactivation Lead','Personal Time','Dr. Appointment']` (denylist = the only 3 non-residue draft types; residue spans Quote/False/services so NO service-type exclusion). **Discriminator = AGE, never $0** (a fresh unpriced quote is also draft+$0, so $0 is info-only).

**Frontend:** `static/owner/v2_residue.html` (NEW "Stale Draft Cleanup" review screen — age filter, select-all, bulk soft-cancel w/ confirm + "Undo last", paginated; passes `age:age()` in the cancel body). `routers/owner/catchup.py` submitted-row payload += so_date/so_service/so_price. `static/owner/wsc_catchup.js` makes Submitted rows tappable (Open=v2_job?open_so / Schedule=open_so&rs=1 / Cancel=soft + Undo via `sCancel`/`sRestore`). `static/owner/v2_apps.js` launcher tile `🧽 Stale Draft Cleanup → /static/owner/v2_residue.html`.

**Safety model:** nothing cancels without DJ's PER-ROW approval with the customer NAME visible; cancel is soft + in-app reversible (no "go into Odoo"). 3 new routes → ENDPOINT_MAP regenerated + pushed with the deploy. See [[project_submitted_jobs_shadow]] (dead-twin cleanup parked), [[feedback_staged_mirror_stale_base_refetch]].
