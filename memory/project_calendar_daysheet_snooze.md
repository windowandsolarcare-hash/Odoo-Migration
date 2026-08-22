---
name: project_calendar_daysheet_snooze
description: "Calendar day-sheet My Day rows now have a ⏰ move/snooze menu: Quick (Tomorrow/+3/Next week), capacity-aware 'Days with room' (reuses /api/goals/next_slots — shows free hrs/day), and Pick-a-date. Moves via existing /api/myday snooze + bulk-date. No new backend."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T19:15:59.255Z
---

**2026-07-25 (DJ: "need a way to snooze (full options) when I'm looking at this list [the calendar day-sheet ☀️ My Day list]. snooze (move) should factor in capacity for that day. I think we have this logic somewhere and would like to call it rather than create new logic.")**

**Reused existing logic (no new backend endpoints):**
- Capacity-aware target days = `GET /owner/api/goals/next_slots?duration=<hrs>&after=<date>&count=4&span=30` (goals.py) → returns the next days with `free >= duration`, each `{date, weekday, free}` where free = work-hours `_day_cap` − jobs − to-dos − goal work. Exactly the "which days actually have room" logic already built for goal scheduling / Layer 2.
- The move = existing My Day endpoints (myday.py): relative `POST /owner/api/myday/snooze {id, source, days}` (Tomorrow/+3/Next week) and exact-date `POST /owner/api/myday/bulk-date {ids:[{id,source}], date}` (handles both task + activity sources, preserves a task's time-of-day). Same endpoints v2_myday.html already uses.

**Built (v2_calendar.html only, commit 3df3d95):**
- `actRowHtml(t,{sheet:true})` now renders a brand-tinted `⏰` button (`.act-ck.snz`, `data-k="actsnooze"`) beside the existing `✓` done button. Only in the day-sheet variant (not the undated/past-due lists).
- Delegated `#sheet-body` click handler gets an `actsnooze` case → `openSnz(SHEET_CTX.acts[i])`.
- New bottom-sheet `#snz-bg` (z-index 60, above the day sheet at 50) with `openSnz / loadSnzSlots / snzRel / snzTo / snzPick / _snzMove / closeSnz`. Menu sections: **Quick** (Tomorrow/In 3 days/Next week → snooze), **Days with room (fits Nh)** (next_slots list, each row "Wed, Jul 29 · 6h free" → bulk-date), **Pick a date** (`<input type=date min=today>` → bulk-date). `_snzPending` guards double-tap.
- After a successful move: `_extraLoaded={}` (moved item may land in another month — force refetch, see [[project_calendar_day_ondemand_load]]), `await Promise.all([load(), loadActivities()])`, then re-`openDay(currentSheetDay)` so the item disappears from the day it left.
- Task duration for the capacity query = `a.hours || a.allocated_hours || 0.5` (0.5 matches the to-do default in the capacity model).

**Verified live:** ⏰ present on all 17 My Day rows for today; menu opens with 3 sections; next_slots returned Sun 7/26 (1h)/Mon 7/27 (0.5h)/Tue 7/28 (1.5h)/Wed 7/29 (6h); snooze sheet fits viewport. Did NOT mutate real to-dos in testing (bulk-date/snooze already battle-tested by v2_myday). Only wired into the calendar day-sheet (where DJ asked); v2_myday's own snooze menu still uses the simpler 1/3/7-day options — could get the same capacity-aware "days with room" list later if wanted. See [[project_workhours_capacity_model]], [[project_goal_forecast_daywalk]], [[feedback_reuse_canonical_endpoint]].
