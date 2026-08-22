---
name: project_goal_layer3_bump
description: "Layer 3 (must-do bump) — mark a to-do 'must happen this day'; if that day is over 8h, list the movable to-dos/goal work on it and bump ONE to its next open day. Single-level, DJ decides."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T04:47:27.081Z
---

**2026-07-24 — Layer 3, the must-do bump engine (built on the Goal Board capacity rails).**

**The problem it solves:** Layer 1/2 handle "does this fit? if not, when's the next open day for THIS task." Layer 3 is the opposite: the to-do MUST be that day, so instead of moving it, move something ELSE off the day to make room.

**Backend (routers/owner/goals.py):**
- `GET /api/goals/day_items?date_str=YYYY-MM-DD` → the FLEXIBLE (movable) things committed that day: project-less to-dos + goal tasks (project has Goal tag). **Jobs are deliberately excluded** — customer appointments don't move. Returns `{ok, items:[{id,name,hours,kind:'todo'|'goal',pinned?,goal?}]}`. Both are `project.task`, filtered `state not in ['1_done','1_canceled']` and `date_deadline` within the day.
- `POST /api/goals/reschedule_task {id, to_date}` → `project.task write date_deadline=to_date`. Works for both to-dos and goal tasks (both project.task).

**Frontend (v2_myday.html reminder editor):**
- New toggle `#e-must` "📌 Must happen on this day" (reset off in openAdd + openEditor; NOT stored — it's a live planning aid at edit time only).
- `_doFit()` now BRANCHES when the day doesn't comfortably fit (`after<1`):
  - **must ON** → fetch `day_items`, render each movable item as a `.fit-move` button "↦ name · Nh (goal)/📌". Tapping = `bumpDayItem(id,dt,hours,btn)`: finds that item's own next open day via `next_slots` (after the crowded day), calls `reschedule_task`, toasts "↦ Moved to Mon 07-27", re-runs `checkDayFit()` (now fits) + `boot()`.
  - **must OFF** → the old Layer 2 "Next open" chips (move THIS task).
  - If nothing movable ("it's all jobs") → tells DJ he'd have to move a job or a goal date.

**Design guardrails (DJ's rules, honored):**
- SINGLE-LEVEL consequence — bump X to its next open day; that day has room by definition (next_slots only returns days with ≥dur free), so NO cascade. Never auto-reshuffle a chain.
- DJ makes the ACTIVE decision — he sees the movable list and picks which one to bump. The app never auto-picks or silently moves anything.
- Jobs never move here. Only flexible to-dos/goal work.

**Flip side — job-landing warning (built 2026-07-24, same session):** instead of hooking every job-creation path, a PASSIVE scan on My Day boot.
- `GET /api/goals/overloaded_days?days=21` (goals.py) → scans upcoming days; buckets jobs (fixed) + flexible work (to-dos + goal tasks) by day like next_slots. Flags a day when `job_hrs>0 AND items nonempty AND (job_hrs+flex_hrs) > DAY_CAP_HRS`. Returns `{ok, cap, days:[{date,weekday,job_hrs,todo_hrs,over,items:[...]}]}`. Jobs win (customer appts), so the flexible items are what's "at risk."
- Frontend v2_myday.html: `#job-warn` div between cap-strip and list; `renderJobWarn()` (called in boot after renderCapStrip) renders a `.jw-card` per overloaded day — "⚠️ Thu 7/30 is overloaded · Xh jobs + Yh to-dos in an 8h day, over by Zh · Jobs win, so these are at risk" + each at-risk item as a `.fit-move` "↦ move …" button → reuses `bumpDayItem` (finds its next open day, reschedule_task, boot re-renders the card). DJ decides which to move; nothing auto-moves.

See [[project_goal_board]], [[project_myday_save_slow_boot]].
