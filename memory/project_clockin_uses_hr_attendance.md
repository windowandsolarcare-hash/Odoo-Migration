---
name: Render clock-in writes to hr.attendance, not ir.config_parameter
description: Live Render timeclock stores shifts in Odoo's built-in hr.attendance model, contradicting the local app.py/dashboard.py code which references payroll.* config parameters
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
The Render app's clock-in/out system stores data in Odoo's built-in `hr.attendance` model — NOT in `ir.config_parameter` under `payroll.clockin.{id}` / `payroll.shifts.{id}` keys as the local code in `5_Mobile_Interface/app.py` and `Saunders Render App/routers/owner/dashboard.py` suggests.

Verified 2026-04-24: queried `hr.attendance` and found 15 records matching DJ's screenshot (Dan Saunders emp_id=1, Danny Saunders emp_id=2). Queried `ir.config_parameter` for `payroll.*` and found zero rows.

Key fields on `hr.attendance`:
- `employee_id` — [id, name] tuple
- `check_in` — UTC datetime string
- `check_out` — UTC datetime string (False if still clocked in)
- `worked_hours` — float

The screenshot showed an admin "+ Add Shift / Week of / raw" UI with edit buttons and weekly groupings — this UI does NOT exist in either local codebase. It must live in a newer/separate payroll admin page (possibly deployed on Render but not yet pulled down locally, or in a sibling repo not yet surveyed).

**Why:** Local code is stale. Before editing clock-in/out logic, pull the deployed version from GitHub or the running Render service. Don't assume ir.config_parameter is the storage.

**How to apply:** When asked about clock-in/out data, query `hr.attendance` first (filter by `employee_id` and date range on `check_in`). Remember DJ emp_id=1, Danny emp_id=2. Times are UTC — convert to Pacific for display. Before editing the clock-in code path, verify the live source — check GitHub repos `windowandsolarcare-hash/Odoo-Migration` and `windowandsolarcare-hash/saunders-render-app` for the currently deployed version and look for the "Add Shift" admin UI.

**CRITICAL: ignore Odoo's `worked_hours` field.** The deployed app (`saunders-render-app/routers/owner/dashboard.py` lines 2638–2642) computes hours from raw `check_in`/`check_out` timestamps and applies `_round_quarter_hour_neutral()` (FLSA 7-min rule) at display time only. Odoo auto-populates `worked_hours` with calendar-based break deductions (e.g., 8 wall-clock hours → `worked_hours = 7.0` due to a 1-hour lunch deduction) but the UI/Gusto export both bypass this. When creating attendance records via API for DJ to use, DO NOT try to compensate for the lunch deduction by extending check_out — the wall-clock duration is what shows. Verified 2026-04-26 by creating 3 × 15:00→23:00 UTC shifts (worked_hours=7.0 each); they display as 8.00h in Manage Shifts.
