---
name: Next Job Date field - COMPLETE
description: New res.partner field x_studio_next_job_date to exclude contacts with future scheduled jobs from reactivation filter
type: project
---

Add a Date field `x_studio_next_job_date` to `res.partner` so the reactivation filter can exclude customers who already have a future job scheduled.

**Why:** Kevin Hile (SO 003912, Apr 23 2026) appeared in the reactivation candidate filter even though he already has a job coming up. Need a way to automatically exclude these customers without manual tagging.

**How to apply:** This work is NOT done yet. Pick it up at the start of the next session.

## Steps remaining (in order):

1. ~~**Create field via Odoo API**~~ — DONE. `x_studio_next_job_date`, ttype `date`, field ID 18764 on `res.partner` (model ID 90)
2. ~~**Add to contact form view**~~ — DONE. View ID 728, placed below `x_studio_last_reactivation_sent`
3. ~~**Phase 3**~~ — DONE. Calls `write_next_job_date_to_contact(contact_id, job_datetime)` at end of paths A, B, C
4. ~~**Phase 4**~~ — DONE. Calls `clear_next_job_date_on_contact(contact_id)` when status is Done or Canceled
5. ~~**Phase 5**~~ — DONE. Calls `write_next_job_date_to_contact(contact_id, scheduled_datetime)` after successful job creation
6. ~~**Reactivation filter**~~ — DONE. DJ needs to add to filter: "Next Job Date is not set" OR "Next Job Date is before today". Backfill script run 2026-04-02, populated 48 contacts. Field `x_studio_x_studio_workiz_status` used as filter (not just state='sale') — only SOs with scheduling statuses count.

## Context:
- Reactivation filter lives on `res.partner` in Odoo (custom filter DJ built)
- Current filter already has: exclude Dan Saunders/Window & Solar Care, Record Category = Contact, Last Visit All Properties < 01/01/2025, Last Reactivation Sent < date, Active/Lead = Active, Has Solar/Window Service
- The new condition slots in alongside those existing rules
