---
name: session_may23_summary
description: "2026-05-23: timer rewrite (localStorage+ir.config_parameter), crew modal date gate, crew labor cost from hr.employee.hourly_wage, source stamps on project.task creates, follow-up context prompt, gate code in timer card, past due section in calendar, cron failure emails"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

## Session 2026-05-23

### Timer Rewrite (field.html + timeclock.py)
- **Old**: task-based timer writing to `account.analytic.line` — wrong model (billable hours), tasks got deleted
- **New**: client-side localStorage timer → single API call on Stop
- `wsc_timer` localStorage key: `{so_id, start_ms, employee_id}` — instant start, survives network loss
- Stop calls `POST /owner/api/timer/log` → writes to `ir.config_parameter` key `timer.so.{so_id}` (JSON array)
- Also posts chatter note on the SO
- `GET /owner/api/timer/records?so_id=X` — reads records back for display
- Timer-start-label shows "▶ Started 10:40 AM" when timer is running
- Restores running timer on job open (reads localStorage)
- `renderTimerBtns('idle'|'running'|'none')` controls Start/Stop/disabled states

### Crew Labor Cost
- `/api/timer/log` reads `crew.today.YYYY-MM-DD` ir.config_parameter (set by clockin_crew on "Let's Go")
- Reads `hr.employee.hourly_wage` for EACH crew member (Odoo standard field — DJ=$30, Danny=$25)
- Calculates cost per person, sums total
- Response includes `crew[]` array with per-person breakdown + `total_labor_cost`
- `employee_id` is now optional — falls back to crew list first member, then employee ID 1 (DJ)
- **Why fallback needed**: DJ logs in with access code `owner` (dashboard code), `whoami` returns no `employeeId`, so `_fieldGpsEmpId=null` → `employee_id=0` stored in localStorage → backend rejected it

### Crew Modal Date Gate (field.html)
- **Old gate**: `if (_fieldClockedIn || !_fieldGpsEmpId)` — OwnTracks auto-clocks DJ in on home departure so crew modal never fired
- **New gate**: `localStorage.getItem('crewSetDate') === new Date().toISOString().slice(0,10)` — date comparison
- `_markCrewSet()` writes today's ISO date to localStorage after "Let's Go" is tapped
- Self-resets at midnight, no cron needed
- Voice nav also goes through same gate via `openNavVoice(url)` + `_pendingNavUrl`
- `doCrewClockIn()` overwrites existing `check_in` time for already-clocked-in employees (so pay starts from navigate-to-job, not OwnTracks home departure)

### Gate Code in Timer Card (field.html)
- `#timer-gate-hint` span in timer card header (right-aligned, inline with "Timer" label)
- Amber `🔑 1234` when code exists; red `⚠ NO GATE` when empty
- Populated by `openJob()` alongside the existing `#ap-gate` display
- Stays visible while timing without scrolling up

### Source Stamps on project.task Creates
All 5 places that create `project.task` records now stamp `description` with exact source:
- `field.py → create_todo` — voice To-Dos via Render Claude
- `field.py → schedule_job` — "Review before sending" task
- `zapier_calendly_booking → fallback_todo` — can't-find-customer fallback
- `zapier_phase4 → backfill_task` — task backfill
- `zapier_phase5 → re-engagement` — re-engagement cycle task
Anything without a stamp was created natively in Odoo.

### Follow-Up Context Prompt (field.py system prompt)
- Added rule to `create_todo` tool description: always ask "What do you want to follow up about?" before calling the tool if the user hasn't provided a specific note
- Prevents vague To-Dos like "Follow up with Nick" with no actionable context

### Past Due Section in Calendar (calendar.html)
- New `#pastdue-section` at bottom of calendar page (after undated section, before voice modal)
- Red header `⚠ Past Due (N)` — only appears when items exist
- Filters `allActivityTodos` for `t.date && t.date < today` (today = ISO date string comparison)
- Uses `actItemHtml()` so each item has ✓ done button
- `markActDone()` now also removes from `allActivityTodos` and re-renders past-due + undated sections
- 8 past-due items as of 2026-05-23 (Tom Kelly, Joan Flickinger, Barbara Rago x2, Bruce Johnson, Nick Follow-up, stale next job date, review task)

### Cron Failure Emails (main.py)
- `_cron_failure_email(job_name, error)` sends to windowandsolarcare@gmail.com via Odoo mail.mail
- Wraps both `_scheduled_daily_sync` (4:17am) and `_scheduled_check_hof_emails` (every 30min)
- Email subject: `⚠️ Cron Failure: {job_name}`, body includes timestamp + first 2000 chars of traceback

### Deploy Bug Fix: Embedded Newlines in Python Patches
- **Problem**: patching Python source files with `\n` in replacement strings embeds actual newlines → SyntaxError "unterminated string literal"
- **Fix**: use `chr(92)` (backslash character) to build `\n` escape sequences: `chr(92) + 'n'` writes `\n` to file (2 chars: backslash + n) which Python parses as newline escape
- `repr()` of a correctly patched line shows `\\n` (double backslash); broken line shows `\n` (single) — easy diagnostic
- See [[feedback_python_patch_escaping]]
