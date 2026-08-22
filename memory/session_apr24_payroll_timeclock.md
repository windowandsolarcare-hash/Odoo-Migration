---
name: Payroll System Migration & Timeclock UI — Apr 24 Session
description: Complete payroll system overhaul from JSON to hr.attendance; Manage Shifts UI; Gusto Smart Import with CA OT; multi-week display; task timer coupling
type: project
originSessionId: d6e26f3b-5c8f-43bd-ac5f-1af57a73c01b
---
## Completed Work — Apr 24

### 1. Payroll JSON → hr.attendance Migration (LIVE)
- Migrated payroll.shifts and payroll.clockin JSON blobs → Odoo hr.attendance records
- Cleaned up 4 old ir.config_parameter rows (backed up to ~/wsc-render/payroll_json_backup_2026-04-23.json)
- hr.attendance is now sole source of truth; no more dual-write to JSON
- Dan: 5 attendance rows (4 migrated + 1 test); Danny: 3 rows backfilled to match Dan's work

### 2. Manage Shifts UI (LIVE at /timeclock)
- New "✎ Manage Shifts" button on timeclock card → opens modal interface
- Date range picker (defaults to current week, editable)
- Employee picker (owner/DJ only) — view/manage Dan or Danny's shifts
- **+ Add Shift button** — retroactive entry modal (clock-in/out times + RTP checkbox)
- **Edit Shift** — modify existing shifts (employee, times, RTP flag)
- **Delete Shift** — remove shifts with confirmation
- Visual hierarchy: shifts grouped by date, with per-day subtotals
- RTP badge and "CURRENTLY OPEN" flag for live clock-ins

### 3. Gusto Smart Import CSV Export (LIVE)
- **Backend**: `/owner/api/payroll/gusto_export` endpoint produces Gusto-compatible CSV
- **Format**: one row per employee for entire pay period (not per-day)
- **Columns**: last_name, first_name, title, gusto_employee_id, regular_hours, overtime_hours, double_overtime_hours, [rest blank]
- **CA Overtime Rules** (now implemented):
  - Daily: ≤8h → regular, 8–12h → overtime, >12h → double_overtime
  - Weekly: if regular hours >40 in a week, excess becomes overtime
  - Applied per-employee, per-week; no double-counting
- **Gusto Custom Fields** added to hr.employee (4 new fields):
  - x_gusto_employee_id (the 6-char code; Dan=a5f5da, Danny=1bacc2)
  - x_gusto_first_name, x_gusto_last_name, x_gusto_title
- Download button always exports **all active employees** (ignores picker), one CSV for entire range

### 4. Multi-Week Display (LIVE)
- When range spans >1 week: "Week of 4/13 – 4/19" headers appear before each week's day groups
- Week headers: solid blue (#1e3a8a) background + right-aligned week subtotal + left accent bar
- Day headers and shift rows indent under week headers for visual nesting
- Single-week range: same as before (no week headers, just day groups)
- Grand total row at bottom shows full range sum

### 5. UI Polish
- **Time Format**: All times now 12h (7:30 AM – 2:08 PM) instead of 24h
- **Font Sizes**: Bumped smallest text from 10–11px → 12–14px (readability on mobile)
- **Manage Shifts Button**: Light blue (#60a5fa) background, white text, larger padding/font
- **Modal Backdrop**: Darker overlay (rgba(0,0,0,0.85)) + blur(4px) for clarity
- **Removed**: Raw hours subtext under each shift row (info still in day header)

### 6. Task Timer Coupling (LIVE)
- Starting a task timer now auto-clocks in user for the day if not already clocked in
- Surfaces the auto-clock-in in UI: "▶ Timer running — also clocked you in for the day"
- No blocking if auto-clock-in fails (graceful degradation)
- Stopping task timer does NOT clock out (they remain independent; stopping one task ≠ end of workday)

### 7. Multi-User Employee Resolution (LIVE)
- Removed hardcoded ODOO_EMPLOYEE_ID = 1
- New `_employee_id_from_access_code(code)` helper: 8487 → Dan, 0708 → Danny
- Timer start/stop endpoints extract access_code from request → look up correct employee
- Attendance and timesheet entries now correctly attribute to whoever is using the app
- Voice path (Render Claude) still uses DJ_EMPLOYEE_ID as fallback (single-user context; doesn't need code)

### 8. Playwright Gusto Uploader (SCAFFOLD READY)
- scripts/gusto_upload.py — skeleton for logging in → navigating → uploading CSV → capturing screenshot
- scripts/README.md — full setup guide (pip install playwright, env vars, codegen calibration)
- **Issue discovered**: Google OAuth blocks Playwright's bundled Chromium as "automation"
- **Options**: (1) try real Chrome with channel='chrome', (2) use direct Gusto password (no Google SSO), (3) persistent browser profile, (4) semi-automate (you do SSO, script clicks upload), (5) Anthropic Computer Use
- Awaiting confirmation: does your Gusto account support direct email+password, or Google SSO only?

---

## Architecture Notes

**Payroll Data Flow**:
- Clock in/out on Render app → creates hr.attendance in Odoo
- Manage Shifts UI allows retroactive edits (add/edit/delete shifts)
- /owner/api/payroll/gusto_export sums hr.attendance → Gusto Smart Import CSV
- Every employee has 4 Gusto metadata fields; export uses them for matching

**Weekly OT Logic**:
- Per-day thresholds applied first (8/12h rules)
- Then weekly 40h cap checked — if regular >40, excess → overtime
- Works for single or multi-week exports; no overlap

**Multi-User Tracking**:
- Every API call (timer, shifts, exports) derives employee from access_code in request
- Voice tools default to DJ (env var DJ_EMPLOYEE_ID)
- Timesheet/attendance entries always have correct employee_id

---

## Open Items

1. **Playwright OAuth**: Try real Chrome vs. Gusto direct password vs. persistent profile
2. **First Gusto Upload**: Once Playwright is calibrated, do real end-of-pay-period upload
3. **Test Data Cleanup**: Delete 3 test shifts (4/6, 4/8, 4/10) and Saturday 4/18 test shift (id 18) once you confirm UI works

---

## Files Deployed

**Render App** (saunders-render-app):
- routers/owner/dashboard.py — all new endpoints + Gusto export logic + multi-user timer coupling
- static/owner/timeclock.html — Manage Shifts UI + multi-week display + 12h time format
- scripts/gusto_upload.py, scripts/README.md — Playwright skeleton

**GitHub Repos**:
- saunders-render-app/docs/timeclock_usage_for_danny.md — user guide
- saunders-render-app/docs/timeclock_rollout_punch_list.md — 5-item rollout checklist (live on Odoo activities)

**Odoo Activities**:
- Activity #53 (Dan's record, due 4/30): master punch list with links
- Activity #52 (Danny's record, due 4/25): training walkthrough

---

## Why: Reasoning

- **JSON → hr.attendance**: Single source of truth simplifies future queries, auditing, and integrations
- **Manage Shifts UI**: Retroactive entry crucial for "forgot to clock in" scenarios; owner can backfill for employees
- **Gusto Smart Import format**: Gusto's time-import is one row per employee per payroll; daily CSVs require concatenation
- **CA OT rules**: California law requires both daily (8/12h) and weekly (40h) OT calculation
- **Multi-week display**: Visual week grouping makes it clear when payroll periods cross week boundaries
- **Task timer coupling**: Prevents the case where you start timing a task but forget to clock in (payroll would miss the day entirely)
- **Employee ID from access_code**: Multi-user system requires knowing who is making the request; hardcoding breaks Danny's usage

---

## How to Apply

- Use Manage Shifts to retroactively fix any missed clock-ins (ideal with employee's input on times)
- Download CSV for your pay period (week or biweekly, depending on your Gusto schedule), import to Gusto
- If Playwright calibration succeeds, automate the final upload step per punch-list item #3
- Monitor task timer auto-clock-in behavior — should be silent if already clocked in, verbal notification if it auto-clocked
