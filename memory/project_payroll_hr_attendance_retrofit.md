---
name: Payroll hr.attendance Retrofit (2026-04-24)
description: Complete migration from JSON blobs to hr.attendance model with quarter-hour rounding, CA reporting-time pay, Gusto export, Manage Shifts UI, and Playwright automation
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## Overview
Completed major payroll system overhaul: replaced fragile ir.config_parameter JSON storage with Odoo native hr.attendance model. Added comprehensive Manage Shifts UI on Render, Gusto CSV export endpoint, and Playwright automation skeleton for recurring uploads.

**Why:** JSON blobs have 90-day rolling deletion, no audit trail, no filtering, can't sync with payroll providers. hr.attendance is infinite-history, chatter-audited, native Odoo model designed for timesheets.

## Data Model
- **Storage:** Odoo hr.attendance (check_in, check_out, employee_id, worked_hours auto-computed)
- **Calendar:** "W&SC Field Work" (24/7, no lunch break deduction) assigned to DJ (emp 1) and Danny (emp 2)
- **Employees:** DJ=1, Danny=2 in hr.employee
- **Project:** "Payroll" (ID 3, separate from job timer entries)

## Hours Calculation Rules

### Quarter-Hour Rounding (FLSA-Compliant)
- Raw hours: `(check_out - check_in).total_seconds() / 3600`
- Rounding rule: round-half-up at 7.5-min boundary → nearest 0.25
- Formula: `math.floor(hours * 4 + 0.5) / 4`
- Apply at DISPLAY/EXPORT time only, NOT stored
- Example: 4.8253 hours → 4.75 hours (7.5 mins rounds down)

**Why:** FLSA requires rounding to nearest 0.25h. 7-minute neutral rule avoids bias (1-7 min down, 8-15 min up). Storage is raw to preserve audit trail.

### California Reporting-Time Pay (4-Hour Minimum)
- If employee called in and sent home early, minimum 4 hours paid
- Stored as boolean flag `x_reporting_time_pay` on shift (toggle in Manage Shifts UI)
- Export applies minimum: `max(rounded_hours, 4.0)` if flag=true

## Render App Changes (saunders-render-app/routers/owner/dashboard.py)

### New Helper Functions
```python
def _round_quarter_hour_neutral(hours):
    """Quarter-hour rounding to nearest 0.25, FLSA-compliant."""
    if hours <= 0:
        return 0.0
    return math.floor(hours * 4 + 0.5) / 4

def _raw_hours(check_in_str, check_out_str):
    """Raw hours from check_in/check_out timestamps (YYYY-MM-DD HH:MM:SS)."""
    # Returns 0 if either is None/empty; no rounding

def _open_attendance_for(emp_id):
    """Return currently-open hr.attendance for emp_id (check_out IS NULL)."""
    # Used for current shift tracking

def _attendances_in_pt_range(emp_id, start_pt_date, end_pt_date):
    """Return hr.attendance rows in PT date range [start_pt_date, end_pt_date)."""
    # Converts PT boundaries to UTC for Odoo query
```

### New Endpoints

**GET /api/payroll/shifts**
- List shifts for date range (Pacific time)
- Params: employee_id, start_date (YYYY-MM-DD), end_date
- Returns: list of {shift_id, check_in_pt, check_out_pt, raw_hours, rounded_hours, reporting_time_pay}

**POST /api/payroll/shift/update**
- Edit existing shift (check_in, check_out, reporting_time_pay)
- Body: {shift_id, check_in_pt?, check_out_pt?, reporting_time_pay?}
- Validates: check_out > check_in
- Returns: updated shift dict

**POST /api/payroll/shift/create**
- Retroactive shift add (for backfills, corrections)
- Body: {employee_id, check_in_pt, check_out_pt, reporting_time_pay?}
- Returns: new shift dict

**POST /api/payroll/shift/delete**
- Hard delete shift
- Body: {shift_id}
- Returns: {ok: true, deleted_id}

**GET /api/payroll/gusto_export**
- CSV export with daily hour rollups, all active employees
- Params: start_date, end_date, employee_id (optional; omit for all)
- Returns: CSV file (Content-Disposition: attachment)
- Columns: Employee Name, Date, Hours
- Applies: quarter-hour rounding + reporting-time 4h minimum
- Example row: `Dan Saunders,2026-04-20,4.75`

## Frontend UI Changes (timeclock.html)

### Manage Shifts Button & Panel
- Button: light blue (#60a5fa), white text, 13px padding, 15px font, 600 weight, 8px border-radius
- Opens hidden shifts-panel with employee select (owner only), date range pickers
- "＋ Add Shift" button
- shifts-list with day headers and shift rows

### Shift Row Display
- Time: check_in_pt → check_out_pt (Pacific time, 12-hour format with AM/PM)
- Raw hours: gray text (informational only)
- Rounded hours: bold, primary color
- Reporting-time badge: orange pill if flag=true
- Edit button: pencil icon
- Open-flag indicator: amber pill if shift still open (check_out=null)

### Shift Modal (Edit/Add)
- shift-in/shift-out: datetime-local inputs (Pacific time)
- shift-rtp: checkbox for reporting-time pay with explanation text
- Buttons: Cancel, Delete (edit only), Save
- Validation: check_out > check_in, show error hint if invalid

### Gusto Export Section
- Info block: "Download hours for Gusto Smart Import"
- "⬇ Download CSV" button (#10b981 green)
- Exports ALL active employees (ignores employee picker)
- Applies rounding + reporting-time pay

**Why:** Gusto expects one CSV with all employees for "Smart Import" feature. Separate exports per employee is inefficient.

## JavaScript Functions
- `showShiftManager()` - switches to panel, loads employees, sets date range to this week
- `loadShiftList()` - fetches /api/payroll/shifts for selected employee/date range
- `renderShifts(shifts)` - groups by date, renders day headers + shift rows
- `openShiftModal(shift)` - edit (shift provided) or add (shift=null)
- `saveShiftModal()` - POST /shift/update or /shift/create
- `deleteCurrentShift()` - confirmation dialog → POST /shift/delete
- `exportGusto()` - sets window.location.href to trigger CSV download (all employees)

## Playwright Automation (scripts/gusto_upload.py)

### Status
Skeleton created (110 lines), NOT YET TESTED. Needs selector calibration before first use.

### Setup Steps
```bash
pip install playwright
playwright install chromium
setx GUSTO_EMAIL "your-email@gusto.com"
setx GUSTO_PASSWORD "your-password"
```

### Flow
1. Read CSV path from argv[1]
2. Launch browser (Chromium)
3. Navigate to https://app.gusto.com/login
4. Enter email/password (env vars)
5. Navigate to Time Tracking → Import
6. Upload CSV file
7. Confirm import
8. Screenshot + exit

### Calibration
User must run:
```bash
playwright codegen https://app.gusto.com/login
```
Then walk through real login + import flow, copy selectors back into script.

**Why:** Selectors are account-specific and change with Gusto UI updates. Codegen captures them automatically by recording actual interactions.

### Usage (After Calibration)
```bash
python scripts/gusto_upload.py "path/to/wsc_hours_2026-04-20_to_2026-05-03.csv"
```

User approves 2FA prompt on phone. Script handles everything else.

## Migration Execution

### Script
`migrate_payroll_to_hr_attendance.py` (local, already executed)

### Results
- 3 shifts migrated for DJ (4/20: 4.83h, 4/21: 5.83h, 4/22: 3.10h)
- 0 shifts for Danny (only test clicks in old JSON system)
- 4 ir.config_parameter rows deleted (payroll.clockin.1, payroll.clockin.2, payroll.shifts.1, payroll.shifts.2)
- Backup: `payroll_json_backup_2026-04-23.json` saved locally

### Calendar Assignment
"W&SC Field Work" calendar (24/7, no lunch) assigned to both DJ and Danny to avoid Odoo's auto-deduction of break time from worked_hours.

## Documentation Created

### For Danny
- `docs/timeclock_usage_for_danny.md` (105 lines)
- Covers: daily clock in/out, fixing mistakes via Manage Shifts, understanding rounding, reporting-time pay, next steps
- Attached to Odoo Activity #52 on Danny's employee record (due 2026-04-25)

### For DJ (Punch List)
- `docs/timeclock_rollout_punch_list.md` (99 lines)
- 5 remaining action items with descriptions
- Attached to Odoo Activity #53 on DJ's record (due 2026-04-30)

### Odoo Activities
- Activity #52: "Train Danny on time clock — doc attached + backfilled shifts" (hr.employee id 2, due 2026-04-25)
- Activity #53: "Time Clock Rollout — Remaining Actions" (hr.employee id 1, due 2026-04-30, with all 3 docs linked)

## Gusto Integration Status

### CSV Format - TBD
- Currently exports: Employee Name, Date, Hours (rounded)
- Gusto has "Smart Import" feature that claims to auto-match columns
- **Blocker:** Need to confirm Gusto's exact expected columns/headers. User to download template from their Gusto account or test export.
- May need to add: Employee Email (if name is insufficient), or separate Overtime/Time Off columns if Gusto requires categorization

### Button Behavior - TO BE FIXED
- Current: exports one employee at a time (whoever is selected in employee picker)
- Should be: ignore employee picker, always export all active employees in one CSV
- Gusto expects all employees in single CSV for "Smart Import" batch processing
- Fix needed: update exportGusto() JS function to omit employee_id param

### Playwright Readiness - BLOCKED ON USER
- Skeleton ready
- User must run: pip install playwright, playwright install chromium, setx env vars
- User must run: playwright codegen and capture selectors
- After selector calibration: ready for first pay-period upload

## How to Apply

**Editing a shift:** Click Manage Shifts → select employee → click date → click shift row → pencil → change times → Save
**Adding retroactive shift:** Click Manage Shifts → select employee → "＋ Add Shift" → fill times + reporting-time flag → Save
**Exporting to Gusto:** Click Manage Shifts → date range → "⬇ Download CSV" → uploads to Gusto Smart Import (after calibration)

**If timeclock looks wrong:** Check that both DJ and Danny have "W&SC Field Work" calendar assigned (not default calendar). Default calendar deducts 1h lunch even for short shifts.

## Known Quirks

- **Odoo worked_hours field is ignored.** We compute hours ourselves from check_in/check_out to avoid calendar-based deductions.
- **Raw hours are stored, rounding applied at display/export.** This preserves audit trail and allows rounding rules to change without recalculating history.
- **Reporting-time pay is a toggle, not auto-calculated.** DJ must manually mark shifts as RTP in Manage Shifts UI. No rule to auto-detect "called in and sent home."
- **Gusto upload is fully manual after Playwright is calibrated.** No cron job; DJ runs it once per pay period.
