---
name: Payroll Tracker — DJ + Danny
description: Plan for clock-in/out payroll tracking for DJ and Danny via Render, storing hours in Odoo, syncing to Gusto
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Payroll Tracker

**Decided:** 2026-04-18
**Status:** Ready to build. No blockers.

---

## REQUIREMENTS

- **Workers:** DJ + Danny, both hourly
- **Clock in/out:** Via Render app (their own screen/route)
- **Storage:** Odoo timesheets (account.analytic.line) — same model the timer already uses
- **Payroll processing:** Gusto for now. Odoo tracks hours, DJ manually enters into Gusto.
- **Future:** Switch to Odoo payroll completely if Claude can automate enough of it

---

## ACCESS / PERMISSIONS

- Danny: sees only his own hours, clock in/out for himself only
- DJ: sees everything — both workers, daily hours, weekly totals, what's owed to each

---

## RENDER SCREEN (Danny's view)

- Simple clock in / clock out button
- Shows today's hours running
- Shows week total
- No other access

---

## RENDER SCREEN (DJ's view — within existing app or new tab)

- Both workers side by side
- Hours per day this week
- Weekly total hours each
- Dollar amount owed at their hourly rate
- Status: currently clocked in or out

---

## ODOO STORAGE

- Uses existing account.analytic.line (timesheet) model
- Each entry: employee, date, hours, description "[Payroll] Clock in/out"
- Separate from job timer entries (those use task_id, payroll entries use employee_id only)
- Project: create a "Payroll" project in Odoo to house these entries

---

## GUSTO SYNC (for now)

- Manual: DJ runs weekly report from Render, enters hours into Gusto
- Future: Gusto has API — could automate hours submission when ready

---

## HOURLY RATES

- Store as Render env vars (DANNY_RATE, DJ_RATE) — easy to update without code change
- Never hardcoded

---

## BUILD ORDER

1. Create Payroll project in Odoo
2. Add Danny as employee in Odoo (if not already)
3. Build /danny and /payroll-admin routes in Render app
4. Clock in/out API endpoints in app.py
5. DJ's payroll summary view
