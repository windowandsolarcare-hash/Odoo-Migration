---
name: project_task_date_offby1_calendar_vs_myday
description: "Calendar and My Day can place the SAME project.task on different days (off by one). project.task.date_deadline is a DATETIME; My Day converts UTC→PT then takes the date, Calendar slices raw UTC [:10]. Midnight-UTC (00:00:00) tasks disagree by a day."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T05:43:41.361Z
---

**2026-07-24 (DJ: on the calendar, I'm not sure it's putting my tasks correctly).** Confirmed a real off-by-one.

**Mechanism:** `project.task.date_deadline` is a **datetime** field (verified via fields_get), and real values carry a time component (e.g. `2026-11-24 00:00:00`, `2026-07-31 16:00:00`, `2026-12-17 17:00:00`). The two screens interpret it differently:
- **My Day** (`myday.py` ~line 689): `_utc_to_pt(date_deadline).strftime('%Y-%m-%d')` — converts UTC→Pacific, THEN date.
- **Calendar** (`dashboard.py` `/api/todos` ~line 6544): `(date_deadline or '')[:10]` — raw UTC date, no conversion.

For a task stored at **00:00:00 UTC**, Pacific is the *previous day* 5pm, so My Day shows it a day EARLIER than the Calendar. Example: "Buy gorilla tape" `2026-11-24 00:00:00` → My Day Nov 23, Calendar Nov 24. Tasks with a daytime UTC value (12:00/16:00/17:00 → 05–10am PT same day) agree on both screens, which is why only SOME tasks look wrong.

**RESOLVED 2026-07-24 — DJ chose "the day I picked, everywhere."** Fix shipped in `myday.py` (commit caa6210): a to-do due date is now treated as a plain calendar day — read `date_deadline[:10]` (raw date part, NOT `_utc_to_pt`) in the My Day LIST (display `date`), the recurring `_rollforward_recurring`, and `_autopark_stale`. The Calendar already did this, so both screens now land a task on the same day (the stored date part = the picked day). `_utc_to_pt` is still used at line ~687 ONLY for the to-do's `time` display, and for `date_order` (jobs — real instants, keep). Reads-only change; NO write change and NO data migration were needed, because the raw date part already equals the picked day for every real creation path (add stores 09:00 PT→16:00 UTC → raw = picked day; bare-date paths store midnight → raw = picked day). Only the midnight-anomaly tasks visibly move (from a day-early to their correct day). Did NOT touch mail.activity dating (that field IS a pure Date, already sliced right). Left the notification/digest `_utc_to_pt` at ~line 1777 (separate feature, self-contained). Residual: an evening-PT to-do (>~5pm) would raw-slice to the next day — a rare edge; the add default is 09:00 so normal use never hits it.

**Note:** the calendar reads BOTH mail.activity (customer/SO activities) AND project.task to-dos (the reminders DJ creates) via `/api/todos`; personal time + jobs come from `/api/calendar_jobs`; Google events from `/api/gcal_events`. So project.task to-dos DO appear on the calendar — the issue is only the day they land on. See [[project_personal_time_capacity]].
