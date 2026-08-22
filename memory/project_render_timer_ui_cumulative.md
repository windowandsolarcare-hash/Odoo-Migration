---
name: Render timer UI resets display on reopen (data is clean)
description: Field Assistant timer LOOKS like it starts over when DJ leaves a job and comes back — UI-only bug, backend correctly updates the single timesheet line with cumulative hours
type: project
originSessionId: 545d601c-e5c6-46c0-aca1-5a8081a73ec9
---
**What DJ sees:** Starts timer on a job, navigates away (to check another job, look at something), comes back — timer display shows 00:00 again, not cumulative elapsed time.

**What actually happens in the backend (verified 2026-04-20 across all 7 jobs today):** Every task has exactly ONE account.analytic.line (timesheet). Resuming doesn't create duplicates — the backend finds the existing line and adds to `unit_amount`. Timesheet math is 100% accurate.

**Proof:** Barbra Balser task showed `write_date` 12 minutes after `create_date` with total = 1.0 hour, while display name range only captured the first session ("9:34–9:46 AM"). That's the backend correctly accumulating hours while the display name only reflects the first start/stop.

**Two separate display bugs inside the single UI issue:**
1. **Timer face** shows elapsed-since-last-resume instead of total accumulated seconds.
2. **Task name time range** (e.g. "Customer - Service (9:34 AM - 9:46 AM)") only reflects the first session, not the updated end on subsequent resumes.

**How to apply:**
- When DJ asks "does the timer actually restart or just look like it?" — answer: looks only, data is correct.
- Fix when building this: 
  - Timer face: on reopen, compute elapsed from `unit_amount * 3600` + (now - last-start-timestamp if running), not just (now - this-session-start).
  - Task name: strip the "(HH:MM AM - HH:MM AM)" suffix and regenerate it from actual line data on every save, OR stop auto-writing the time range into the name entirely.
- Not urgent — invoicing and payroll both pull from `unit_amount`, which is correct. This is purely cosmetic/confidence.

**Today's 7 jobs, 1 timesheet line each, zero duplicates detected.**
