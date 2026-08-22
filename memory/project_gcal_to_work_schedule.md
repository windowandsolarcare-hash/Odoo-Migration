---
name: project_gcal_to_work_schedule
description: "Reflect select Google Calendar events on the WORK/field schedule. Phase 1 DONE (2026-06-17): '📅 Add to schedule' button on each gcal event in the calendar day-sheet → creates a Personal Time block. Phase 2 (auto-mirror via a dedicated calendar) NOT built."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ (2026-06-17): the Schedule Calendar already shows Google Calendar events; he wants SELECT ones ("sometimes, for certain events") to also appear on his actual WORK/field schedule (the daily job list he routes by).** Chose **"both — tap now, auto-mirror later."**

## DIRECTION — Schedule Calendar = the forward-planning HUB (DJ 2026-06-17)
The field/job schedule is short-range (~2-3 wks, a do-the-work list). The **Schedule Calendar (/owner/calendar)** has no range limit → it's where DJ looks ahead (book a Thanksgiving job, plan a vacation). It already shows Jobs + Google Cal + Activities + Planner(habits). Vision = make it both the look-ahead AND the launch point.
- **"My Day stuff is missing" was a LABELING issue, NOT a data gap.** The calendar's activities layer is fed by `/owner/api/todos`, which ALREADY returns BOTH mail.activity AND My Day project.task to-dos (source 'activity' vs 'task'); dated ones plot on the day, undated go to a collapsible section.
- **DONE 2026-06-17 — removed BOTH planner remnants from the calendar:** (a) the Planner toggle chip, and (b) the **"Today's List" iframe embed** (`/static/chores.html?embed=1`) — both commented out (reversible; chores.html + toggleTodaysList untouched). DJ: planner is gone, use My Day.
- **DONE 2026-06-17 — MIGRATED the 6 planner habits → My Day recurring to-dos** (project.task, x_myday_recur, x_myday_type='task', ids 984-991). Planner held only personal life habits (Meditate/Workout/Walk Dogs/Watch TV/Date Night/Visit Parents), NOT work chores — those were always My Day tasks. Mapping: daily habits→daily; Date Night→weekly(Fri); Visit Parents→weekly(Sun); **Workout M/W/F → 3 separate weekly tasks** (My Day recur has no multi-weekday). Planner source params `personal.planner.8487.template`/`.history` left PARKED (not deleted; UI hidden so no duplication). My Day recurring = spawn-on-done (won't auto-advance days unless checked off — inherent to the model).
- **DONE 2026-06-17 — relabeled "Activities" → "☀️ My Day" on the calendar** (legend, day-sheet section headers, undated section header) + added a **My Day layer toggle** (`let showActs=true`; `toggleLayer('acts')`; gates the day-cell dot + both day-sheet sections; toggle chip next to Jobs/Planner, default on, pink #f472b6 dot). Internal fn/var names (renderUndatedActivities, allActivityTodos, etc.) left as-is — only user-facing text changed. The undated/past-due TOP sections are NOT gated by the toggle (they're standalone helper sections).
## SHIPPED 2026-06-17 — recurring-to-do expansion + completed-history on the calendar
DJ asked for BOTH. Backend `/api/todos` (dashboard.py) is shared by 5 files → changes are OPT-IN + additive:
- **`?include_done=1`** (calendar passes it) ALSO returns completed personal To-dos (`project.task state='1_done'`, last 365d) tagged **`done:true`**. **Excludes auto system tasks** (`name not ilike 'Re-engagement:'` / `'[Render] Follow-up:'`) — those are automated, not "what DJ did", and would flood the look-back. Always adds a **`recur`** field (`x_myday_recur`) + `done` flag to every todo item (harmless to other callers).
- **Completed-history (calendar.html):** done items render on their day as `act-done` (✓, strikethrough, dimmed, no action button); **excluded from the Undated + Past-Due helper sections** (`!t.done` guard) so a done item never shows as "past due". Past days now show what DJ checked off. Verified: 22 real done to-dos (auto ones filtered out).
- **Recurring expansion (calendar.html):** `indexActivities` → `expandRecurring(todos)` paints PROJECTED future occurrences of any to-do with a `recur` rule onto each repeat day (today→+365d, cap 200/item), marked `_projected:true` (NOT added to allActivityTodos, so they stay out of undated/pastdue). `advanceRecur(d, recur)` mirrors `_advance_recur` (daily/weekdays/weekly/biweekly/monthly w/ month-end clamp). Projected items render as `act-projected` (🔁 "repeats", faded, not actionable). Day-key built from LOCAL components (`_dkOf`) to avoid TZ shift. **NOTE: DJ currently has 0 recurring to-dos, so nothing projects yet — feature is wired and waiting.**
- Both respect the ☀️ My Day toggle (they flow through actsByDate which is gated by showActs).
- ⚠ data gotcha: completed `project.task` for DJ is DOMINATED by auto reactivation/followup tasks (the "Re-engagement:" / "[Render] Follow-up:" prefixes) — always filter those out of any "what DJ did" view.
- Future ideas (not built): surface My Day distinctly; "block off a vacation" = multi-day Personal Time.

## SHIPPED 2026-06-17 — "➕ Book a job" from the calendar (future-date booking)
DJ's "someone wants to book around Thanksgiving" → the booking entry point is now ON the calendar. Day-sheet action bar (next to GPS Stops / + Google Cal) has a green **"➕ Book a job"** pill → `/owner/new-order?date=<dayKey>`. The date threads through the existing front door:
- **calendar.html**: `bookPill` in `topLinks`.
- **new_order.html**: `const BOOK_DATE = URLSearchParams date`; `njHref(qs)` appends `&date=` to ALL New Job redirects (new=1, contact=ID, warnContinueNew). (Reactivation-Book route does NOT carry the date — it has its own date logic.)
- **new_job.html**: init reads `?date=` → `S.bookDate`; `loadStep3` sets `job-date = S.bookDate` (so `loadDateSuggestions` won't auto-pick over it) + calls `onDateChange(S.bookDate)` to load that day's schedule + suggested time + route map. So New Job opens prefilled to the chosen future day; DJ still picks customer/property/items.
- New Order remains the correct front door for ANY future job (it already supported any date via the day picker); this just launches it from where DJ is looking.
- ⚠ DEPLOY NOTE: 3 rapid pushes → Render COALESCED the burst and skipped the head commit (new_job never deployed; served old). Fix = one more trivial commit to force a clean deploy of HEAD. When pushing several files, expect coalescing — verify the LAST file actually serves, and bump if not.

## Architecture (why this is the design)
- Google Calendar events come in via **read-only iCal feeds** (`GCAL_*_URL`), parsed by `GET /owner/api/gcal_events` (dashboard.py L10362). Event shape: `{summary, time:"1:30 PM", all_day, location, link}` — NO end time, NO stable id.
- The **work/field schedule is built from sale.order** (jobs). The bridge already existed: **"Personal Time" blocks are SOs** (partner 23054, type 'Personal Time') that DO render on the field schedule — created by `POST /owner/api/schedule/add_block {name,date,time,notes}` ([[project_schedule_add_block]], [[project_personal_time_schedule_desc]]).
- So "reflect a gcal event on the work schedule" = **turn it into a Personal Time block.**

## PHASE 1 SHIPPED 2026-06-17 — tap-to-promote (`static/owner/calendar.html`)
In the calendar **day-sheet**, every Google Calendar event now has a green **"📅 Add to schedule"** button next to "Open in GCal" (added to BOTH render blocks: all-day events + timed events). Tap → `gcalToSchedule()`:
- Converts the event's `time` "1:30 PM" → "13:30"; **all-day events default to 09:00** (DJ adjusts on the schedule).
- `confirm()` then `POST /api/schedule/add_block {name:title, date:dayKey, time:HHMM, notes:location}` → Personal Time block.
- New helpers in calendar.html: `_enc` (encodeURIComponent + manual `'`→%27 so apostrophe titles don't break the single-quoted onclick), `_addToSchedBtn(e,dk)`, `gcalToSchedule(...)`. Backend unchanged (reuses add_block).
- VERIFIED: promoting "Therapist Appointment 1:30 PM" created a confirmed Personal Time block at 1:30 PM PT (partner 23054), title+location in notes. One-time COPY — if the gcal event later moves, the block does NOT follow (delete/re-add).

## PHASE 2 (NOT built) — auto-mirror
A dedicated Google Calendar (e.g. "WSC Work Blocks") OR a title tag (`[WORK]`): a periodic sync auto-creates/updates/removes Personal Time blocks for matching events, keyed by the gcal event UID stored on the block (so moves/cancellations reflect). Needs: store the gcal UID on the block (new field or in notes), a sync loop, dedup/lifecycle. iCal feeds refresh on Google's delay (not instant).
