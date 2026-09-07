---
name: project_job_type_autoderive
description: "job_type (x_studio_x_studio_x_studio_job_type) auto-derives from the line mix in POST /owner/api/job/lines so it never goes stale when a service is dropped from a combination; + /owner/api/job/set_job_type alias of set_service. CONSERVATIVE overwrite; values data-driven (windows-only='Windows Inside & Outside Plus Screens')."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-07T01:24:32.915Z
---

**Built 2026-09-06 (brain.py, commits after b79fdad).** DJ's very common workflow: a customer drops one service from a Combination job (e.g. Clark Argeris dropped solar, kept windows) and the Studio "Job Type" field `x_studio_x_studio_x_studio_job_type` (a **selection** on sale.order) then reads STALE ('Combination of Services' when it's now single-service).

**Fix — auto-derive inside `POST /owner/api/job/lines`** (`brain.py job_lines_save`): after the order_line replace succeeds, `_derive_job_type(names)` maps the resulting line mix to a label and writes it. Helpers: `_job_type_category(name)` (keyword→ solar/windows/gutter/pressure/cobweb, else None=add-on), `_windows_label(names)` (inside-only / outside-only / else 'Windows Inside & Outside Plus Screens'), `_JT_PRIMARY=('windows','solar','gutter','pressure')`.
- **Combination requires 2+ PRIMARY services.** Add-ons (cobweb) NEVER force Combination. 1 primary → that service's label; only-add-on single → its label; nothing confident → None (leave label alone).
- **CONSERVATIVE overwrite (never clobber a hand-picked label):** only writes when `(not cur) OR derived=='Combination of Services'(2+ primary) OR (cur=='Combination of Services' AND collapsed to <2 cats)` AND derived!=cur. A routine price-edit on an unchanged single-service job does NOT relabel it.
- Validated against the **LIVE selection** (fields_get) before writing; the whole derive is wrapped in try/except so a miss can never fail the line-save. Response gains `job_type` when it applied one. Unit-tested 11/11.

**`POST /owner/api/job/set_job_type {so_id, job_type}`** = thin ALIAS of the already-live `job_set_service` (brain.py) — one validated single-field handler, no duplication (Lead requested the name). Manual override / correction path.

**★ VALUES ARE DATA-DRIVEN, never guessed (Rule 1 + Lead + Operator all stressed):** tallied 397 live SOs carrying a "Windows In & Out - Full Service" line → single-line ones are **'Windows Inside & Outside Plus Screens' 238/274**. That's what DJ uses for a full in&out windows job, so windows-only maps to it. There is NO literal "Windows In & Out - Full Service" job_type value. Clark SO 16952 (004202) relabeled live Combination→that (single windows $250 line, no solar, not invoiced).

**Open business call for DJ:** which services count toward "Combination" — currently PRIMARY = windows/solar/gutter/pressure, cobweb = add-on. One-line map change if he wants it different. See [[project_cadence_engine]] (also touches job_type via PRODUCT_TO_JOB_TYPE) and [[feedback_no_guessing_on_fields]].
