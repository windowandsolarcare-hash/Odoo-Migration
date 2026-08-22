---
name: project_field_delete_odoo_only
description: "Field app \"Delete (Odoo only)\"/\"Delete Block\" now HARD-deletes an Odoo-only SO via /api/delete_so; cancel_so is cancel-only (calendar)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

The field app's no-Workiz-UUID delete path (`deleteJobFromMenu` in field.html, "🗑 Delete (Odoo only)" / "🗑 Delete Block") now calls **`POST /api/delete_so/{so_id}`** (dashboard.py, added 2026-07-11 commit fcee600) which **cancel→unlink**s the SO so it's actually REMOVED — refuses if any invoice is linked, deletes linked project.tasks first, uses the tracking-bypass context (see [[reference_odoo19_unlink_tracking_bypass]]).

**Why:** it previously called `/api/cancel_so/{so_id}` which only runs `action_cancel`. An **already-cancelled** Odoo-only SO (e.g. old migration-era names like `S00119`) then couldn't be removed — cancel is a no-op and a cancelled SO STILL shows in the Customer Brain. DJ hit this trying to delete S00119 (Nick Conway) and it silently did nothing.

**How to apply / gotchas:**
- `/api/cancel_so/{so_id}` is UNCHANGED and stays **cancel-only** — `calendar.html`'s "Cancel it in Odoo only?" relies on that (a cancelled SO drops off the calendar, which only shows sale/done). Do NOT make cancel_so unlink. Two copies of cancel_so exist (dashboard.py + submitted_jobs.py); dashboard.py is live.
- Jobs WITH a Workiz uuid still use `/api/delete_job` (full Workiz+Odoo delete).
- **Two res.partner per customer is normal:** a Contact record + a "Name, Street" Property record. SOs attach to the Property (Nick Conway: contact 22986 has 0 SOs; property 24108 holds them). Search SOs by BOTH partner_id and partner_shipping_id in [contact, property] ids.
- Odoo SO names can be old migration format `S00119` (state often `cancel`) OR the current 6-digit `004651` — same customer can have both.
