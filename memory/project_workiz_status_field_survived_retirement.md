---
name: project_workiz_status_field_survived_retirement
description: "x_studio_x_studio_workiz_status is STILL the live job-status field after Workiz retirement (2026-08-03) — Odoo-native now, legacy name. Verified populated on 22/23 SOs since. Do NOT \"clean it up\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-19T01:17:51.412Z
---

Workiz was retired 2026-08-03, but **`x_studio_x_studio_workiz_status` on `sale.order` is still the
live, actively-written job-status field.** The name is legacy; the field is now Odoo-native and
maintained by the app's own flows (new_job.py, Customer Brain, the status dropdown that also
`action_confirm`s — see [[project_status_scheduled_now_confirms]]).

**Verified 2026-08-18** (direct Odoo query, company_id=1, SOs dated 2026-08-03 → 2026-08-18):
23 SOs, status distribution `Done: 13, Scheduled: 4, Submitted: 4, Postponed: 1, EMPTY: 1`. Both
blank ones were non-customer records ("Personal Time" time-block, "ZZ PDF Test") — **no real
customer job is missing a status.**

**Why this matters:** the Workiz-retirement banner in CLAUDE.md marks every Workiz-shaped section
LEGACY, which invites a session to conclude this field is dead too and rip it out or replace the
"Done" gate. It isn't dead. CLAUDE.md rule 2 still holds: **a completed visit is
`x_studio_x_studio_workiz_status == 'Done'`**, not `state`, not `invoice_status`, not `invoice_ids`.

**How to apply:** keep reading/writing this field. Note the two DIFFERENT senses of "done" now in
play — don't conflate them:
- **Service happened** (what the customer portal's history, last-visit and due math use) = `workiz_status == 'Done'`.
- **Job closed out / money collected** = paid in full (Lead's 2026-08-18 note). That is a billing
  lifecycle question, not a "did we clean their windows" question.

Also seen: post-retirement SOs carry Odoo-default names like `S00192`/`S00218` alongside the
migrated 6-digit `003575` format, so **never assume the 6-digit shape when parsing an SO name** —
match exactly (e.g. `invoice_origin` → `sale.order.name`) rather than zero-padding a guess.

Related: [[project_customer_portal]], [[feedback_done_jobs_definition]], [[project_workiz_retirement]]
