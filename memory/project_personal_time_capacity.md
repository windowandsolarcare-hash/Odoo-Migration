---
name: project_personal_time_capacity
description: "Personal Time blocks used to count as 0 hrs in ALL capacity math (a doctor's appt didn't reduce free time). Fixed by storing a real duration in x_job_length_min on add/move so _job_minutes counts it everywhere."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T05:12:12.469Z
---

**2026-07-24 (DJ: does layer 1/2/3 account for personal time I mark on my schedule?).** It did NOT — verified against live data.

**Root cause:** Personal Time blocks are Odoo-only `sale.order`s (partner "Personal Time", `x_studio_x_studio_x_studio_job_type='Personal Time'`, state sale/done, name format `S00xxx` — a different sequence from real 6-digit SOs). Every one had **`x_job_length_min = 0`** and no end/duration field (checked S00191: commitment_date/expected_date/date_deadline all False). And both the schedule renderer (scheduler.py:213 `dur = int(x_job_length_min or 0) or _job_block_min(jt)`) and the capacity math (goals.py `_job_minutes`:44 real-length-wins, else `_job_block_min`) return **0 for 'personal time'** when length is 0. The old `add_block` (dashboard.py) created the block with NO length, and the v2_field.html block modal had **no duration input**. So a doctor's appointment occupied 0 hours in cap strip, day_capacity, next_slots, overloaded_days, and layers 1/2/3.

**Fix (all deployed 2026-07-24):**
- `dashboard.py` `/api/schedule/add_block`: parse `length` (minutes) from body, default **60** if missing/≤0, write `x_job_length_min` on create AND on the post-confirm date_order write-back (action_confirm doesn't touch it, but belt-and-suspenders).
- `/api/schedule/move_block`: optional `length` → writes `x_job_length_min` when >0.
- `/api/schedule/block_info`: now returns `length` (x_job_length_min) so the edit form prefills it.
- `v2_field.html` block modal: added a **"How long"** `<select id="block-dur">` (30m/1h/1½/2/3/4/6/8h, default 1h); `submitBlock` sends `length`; `openBlockModal`/`moveBlockFromMenu` prefill it.

**Why it works with zero capacity-layer changes:** `_job_minutes`/scheduler both already use real `x_job_length_min` FIRST. Writing a real length makes personal time count automatically everywhere. No edits to goals.py capacity endpoints.

**Existing blocks:** 37 old Personal Time SOs still have length=0, but only **1 is upcoming** (S00192, 2026-08-26) — left as-is; DJ can open it and set a duration (prefills to 1h now). Did NOT backfill/guess durations on the rest.

See [[project_goal_layer3_bump]], [[project_goal_board]].
