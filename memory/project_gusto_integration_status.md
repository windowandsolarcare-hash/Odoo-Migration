---
name: Gusto Integration Status (2026-04-24)
description: CSV export endpoint partially complete; blockers = Gusto CSV format confirmation, button scope fix, Playwright selector calibration
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## Current State

### What's Done
✅ Render endpoint `/api/payroll/gusto_export` created
  - Fetches hr.attendance for date range
  - Applies quarter-hour rounding + CA 4-hour reporting-time pay minimum
  - Outputs CSV with columns: Employee Name, Date, Hours
  - Example: `Dan Saunders,2026-04-20,4.75`

✅ Download CSV button in Manage Shifts UI
  - Green button (#10b981), placed in gusto-export section
  - Currently wired to export single employee (whoever is selected in employee picker)
  - File downloads as attachment

✅ Playwright skeleton created
  - Path: `saunders-render-app/scripts/gusto_upload.py`
  - 110 lines, handles: browser launch, login, file upload, confirmation
  - Uses env vars: GUSTO_EMAIL, GUSTO_PASSWORD
  - Outputs screenshot on success
  - **Selectors are TODOs** (need calibration)

### What's Blocked

#### Blocker 1: Gusto CSV Format - INFORMATION NEEDED
**Status:** Waiting on DJ confirmation

Gusto's "Smart Import" feature claims to auto-match columns, but exact expected format unknown.

Current export: `Employee Name, Date, Hours`

**Possible requirements:**
- Does Gusto need `Employee Email` instead of/in addition to name?
- Does Gusto need separate columns for Overtime, Regular Time, PTO?
- Does Gusto need date in specific format (MM/DD/YYYY vs YYYY-MM-DD)?
- Are hours expected as decimal (4.75) or minutes (285)?

**How to Resolve:**
1. DJ logs into Gusto account
2. Goes to Time Tracking → Import
3. Downloads CSV template or sample file
4. Provides first row (headers) and 1-2 sample rows
5. We update `/api/payroll/gusto_export` endpoint to match exact format

**Impact:** Without correct format, Playwright upload fails or imports incorrectly (wrong hours recorded).

#### Blocker 2: Download Button Scope - CODE FIX PENDING
**Status:** Ready to fix once Gusto format is confirmed

Current bug:
```javascript
// Current behavior: exports only selected employee
const empId = currentSmEmpId();  // returns selected employee
window.location.href = `/api/payroll/gusto_export?start_date=${start}&end_date=${end}&employee_id=${empId}`;
```

Should be:
```javascript
// Fixed behavior: exports ALL employees, ignores picker
window.location.href = `/api/payroll/gusto_export?start_date=${start}&end_date=${end}`;
// Endpoint default: if employee_id omitted, query all active hr.employee records
```

**Backend logic (unchanged):**
```python
def gusto_export():
    emp_id = request.args.get('employee_id')  # optional param
    if emp_id:
        employees = [int(emp_id)]  # single employee
    else:
        # All active employees
        employees = [e['id'] for e in odoo_rpc('hr.employee', 'search_read', 
            [[['active', '=', True]]], {'fields': ['id']})]
    
    # Rest of logic fetches hr.attendance for all in list, groups by employee + date
```

**Why:** Gusto expects one CSV with all employees for batch Smart Import. Separate exports per employee is inefficient.

**Fix effort:** 2 lines of JavaScript + 3 lines of backend logic.

#### Blocker 3: Playwright Selector Calibration - USER ACTION REQUIRED
**Status:** Skeleton ready, selectors are TODOs

Current skeleton:
```python
# TODO: fill in selectors via playwright codegen
async def login(page):
    await page.goto('https://app.gusto.com/login')
    # await page.fill('[TODO_EMAIL_SELECTOR]', email)
    # await page.fill('[TODO_PASSWORD_SELECTOR]', password)
    # await page.click('[TODO_LOGIN_BUTTON_SELECTOR]')

async def upload_csv(page, csv_path):
    # await page.goto('[TODO_IMPORT_PAGE_URL]')
    # await page.fill('[TODO_FILE_INPUT_SELECTOR]', csv_path)
    # await page.click('[TODO_CONFIRM_BUTTON_SELECTOR]')
```

**How to Calibrate:**
1. Install Playwright: `pip install playwright && playwright install chromium`
2. Set env vars: `setx GUSTO_EMAIL "email@gusto.com" && setx GUSTO_PASSWORD "password"`
3. Run codegen: `playwright codegen https://app.gusto.com/login`
4. Browser opens, user logs in → import flow → selects file → imports
5. Codegen auto-generates selector code; copy into `gusto_upload.py`

**Why:** Selectors are account + UI-version specific. User's account interface may differ from mine. Codegen records the exact path through their UI.

**Effort:** ~10 minutes to walk through once; one-time setup.

**Usage (After Calibration):**
```bash
python scripts/gusto_upload.py "/path/to/wsc_hours_2026-04-20_to_2026-05-03.csv"
# User approves 2FA on phone; script finishes upload
```

## Implementation Checklist

```
[ ] DJ downloads Gusto CSV template (or sample import file)
[ ] DJ provides column headers + sample row
[ ] Claude updates /api/payroll/gusto_export endpoint (column names)
[ ] Claude fixes Download CSV button (omit employee_id, query all)
[ ] Claude deploys both changes to main
[ ] DJ installs Playwright deps (pip install playwright && playwright install chromium)
[ ] DJ runs playwright codegen + walks through login/import
[ ] DJ provides selectors (copy/paste from codegen output)
[ ] Claude updates gusto_upload.py with real selectors
[ ] Claude deploys to main
[ ] At next pay period: DJ runs gusto_upload.py, approves 2FA, done
```

## How to Apply

**Until blockers are resolved:**
- Continue using manual clock in/out on Render
- Manage Shifts UI is ready for edits + retroactive adds
- CSV export button works but exports only one employee (not useful yet)

**After Gusto format confirmed + code fixed:**
- Download CSV → all employees + all hours for date range
- Send to Gusto via button (opens CSV) or manually

**After Playwright calibrated:**
- Fully automated: `python scripts/gusto_upload.py "path.csv"` + 2FA approval = done

## Known Gotchas

- **Gusto Smart Import may have rate limits.** If uploading frequently, watch for throttling.
- **Gusto deletes prior data on import.** Each upload overwrites that pay period (good for corrections, bad if you double-submit).
- **2FA may block headless automation.** Playwright script will pause and wait for user approval — phone gets push notification.
- **CSV format mismatch = silent failure.** Gusto may accept the file but map columns wrong (hours go to OT, names become notes, etc.). Always spot-check first import in Gusto UI.

## Email References
- Gusto support email: none yet (DJ to provide if needed)
- Playwright docs: https://playwright.dev/python/

## Related Files
- `/api/payroll/gusto_export` endpoint — saunders-render-app/routers/owner/dashboard.py (lines 2900–2951)
- Download CSV button — saunders-render-app/static/owner/timeclock.html (exportGusto function)
- Playwright script — saunders-render-app/scripts/gusto_upload.py
