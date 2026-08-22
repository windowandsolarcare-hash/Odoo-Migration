---
name: project_workiz_final_export
description: "Final full Workiz data export (2026-08-02, before retirement): 3860 jobs 2019->2027, saved local + GitHub. HOW to bulk-pull job/all incl the offset=page-index gotcha + UA-header requirement."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-03T03:14:38.052Z
---

**A complete final Workiz export was taken 2026-08-02 (day before Workiz retired).** DJ wanted "all data, day 1 to every future job."

## The export
- **3,860 unique jobs**, every field (50 fields: UUID, SerialId, JobName, JobDateTime, JobEndDateTime, CreatedDate, JobTotalPrice, JobAmountDue, item/tech cost, ClientId, Status, SubStatus, Phone, Email, LineItems, FirstName/LastName, full Address, ServiceArea, JobType, JobNotes, JobSource, Tags, Team, pricing, frequency, type_of_service_2, last_date_cleaned, next_job_line_items, ok_to_text, confirmation_method, ...).
- **Date range JobDateTime: 2019-07-16 → 2027-06-08** (2019 = Workiz day-1; re-pulling from start_date=2000 returned the SAME 3860, proving nothing older exists). CreatedDate 2020-02-25 → 2026-07-30.
- Status split: Done 2555, Submitted 884, Pending 387, Canceled 33, done-pending-approval 1.
- **Completeness proof:** the export's open/scheduled count (Submitted+Pending+pending-approval = 1272) EXACTLY matched Workiz's live open-job count (1272) at export time → zero missing. 112 of the jobs are future-dated (30 Submitted + 82 Pending), furthest 2027-06-08.
- **Saved (both):** local `4_Reference_Data/Workiz_Final_Export_2026-08-02/workiz_all_jobs_2026-08-02.json` (+ export_summary.txt), AND pushed offsite to GitHub repo `windowandsolarcare-hash/Odoo-Migration` same path (8.7 MB JSON went through the gh contents API fine as ~11.5MB base64).

## HOW to bulk-pull Workiz (job/all) — the method + gotchas
Endpoint: `GET https://api.workiz.com/api/v1/{TOKEN}/job/all/`
- Params: `auth_secret={SECRET}` (REQUIRED for job/all, unlike job/get), `records=100` (MAX 100 per page; Workiz uses `records` not `limit`), `offset={page}`, `start_date=YYYY-MM-DD` (**if omitted, defaults to last 14 days only** — set early for full history), `only_open=true|false`.
- Response keys: `flag, data (job list), has_more (bool — page cleanly on this), found (per-page count, NOT a grand total), code`.
- ★ **PAGINATION GOTCHA:** `offset` is a **PAGE INDEX 0,1,2,3...** (each page = up to 100), NOT a record-skip count. offset=0→1-100, offset=1→101-200. An OLD doc (AI_Agent_Master_Manual) wrongly called it "jobs to skip" with a `total-depth` formula — that's the buggy interpretation. The tested `export_workiz_full_snapshot.py` overrode it. Loop offset++ while `has_more` is True.
- ★ **User-Agent required:** `urllib.request` with no UA → **403 Forbidden**. `requests` (sends a default UA) or add `headers={'User-Agent':'Mozilla/5.0'}` → 200. (This is why job/get looked "dead" earlier — it was a missing UA, not access being cut.)
- To get EVERYTHING: two passes (`only_open=false` = all/closed, then `only_open=true` = open) deduped by UUID; only_open=false already returned essentially all, open pass added 0. Rate limit was generous (no 429 across ~40 rapid pages at 1.5s spacing) but on 429 sleep ~35s + retry; save incrementally.
- Working script pattern kept in scratchpad during the export; the archived `z_ARCHIVE_DEPRECATED/2_Modular_Phase3_Components/export_workiz_full_snapshot.py` documents the offset-as-interval rule.

Note: this is the sanctioned EXCEPTION to [[feedback_workiz_no_job_all]] (the never-use-job/all rule was for the LIVE sync; a one-time archival export is fine). See [[project_workiz_retirement]].
