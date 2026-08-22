---
name: session_jun03_notes_history
description: "2026-06-03: Customer notes system, historical job view, calendar tap-to-open, CLAUDE.md vocabulary addition"
metadata: 
  node_type: memory
  type: project
  originSessionId: a426dd8b-9b75-4779-8f66-583969d0c752
---

## What was built

### Notes system (3-type architecture)
- **To-Do notes** (`project.task`, `project_id=False`, `partner_id` set) — created via "📝 Note" button on job detail screen. Shows in Render Activities tab + Odoo To-do app. Has due date, add/edit/delete.
- **Permanent property note** (`x_studio_x_field_note` on `res.partner`, field ID 20866) — persists forever, always visible on job detail screen as teal "📌 Property Note" card. Shows "NONE" if empty. Edit inline.
- Both tied to the **property partner** (not contact) — loads automatically when any job for that property is opened.

### New Odoo field
- `x_studio_x_field_note` — `ttype: text`, `store: True`, on `res.partner` (model ID 90, field ID 20866). Created 2026-06-03.

### New Render endpoints
- `GET /api/todos/for_partner?partner_id=X` — active project.task notes for a partner (activities.py)
- `POST /api/todos/create` — creates project.task note (activities.py)
- `POST /api/partner/field_note` — saves permanent field note to res.partner (dashboard.py)
- `GET /api/so_history?so_id=X` — returns SO services (line items), payments, photo list (dashboard.py)
- `GET /api/attachment_image?att_id=X` — proxies Odoo binary ir.attachment as image (dashboard.py). Odoo images are not publicly accessible — must proxy through Render. Cache-Control: max-age=86400.

### Historical job view
- Tap a **past** job row → bottom sheet with services, payment, photo grid (3-column thumbnails, tap for lightbox)
- Tap a **future** job row → full live active panel (inherits property context from activeJob or ctx)
- Tap **today's** job → full live panel using exact jobs array object
- This applies from: Job History list, Customers tab, shortcut panel 👤 button, Calendar day sheet

### Calendar tap-to-open
- Calendar job rows are now tappable (cursor:pointer, onclick)
- Navigates to `/owner/field?open_so=X&date_raw=YYYY-MM-DD`
- field.html `openJobById(soId, dateRaw)` detects URL param on load, opens correct view
- SO pill moved from right column (was above 🗑) into the badges row on the left — fixes crowding

### CLAUDE.md addition
- Added **KEY VOCABULARY** section defining "the schedule" = Render field assistant, gate = `state in ['sale','done']` + `date_order` = that day, Submitted = draft (not on schedule), 4 scheduling statuses.

## Key architectural pattern
Notes follow the **customer/property** not the SO — so they appear on every future job automatically. No Workiz dependency.
