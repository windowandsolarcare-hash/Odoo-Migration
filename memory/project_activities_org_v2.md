---
name: Activities tab — sections + type filter + search + snooze (v2 2026-04-29)
description: Organization layer DJ asked for after the activities list became "an out-of-control inbox". Open sub-tab now has search bar with X clear, type filter (All/Follow-Ups/To-Dos), 4 date-based collapsible sections (Overdue/Today/This Week/Later), and a Snooze row in the detail modal with 4 chips (+1d/+3d/+1wk/+1mo).
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when editing /owner/activities open-list rendering or detail-modal action area.**

## What's there

The Open sub-tab of `/owner/activities` (`activities.html`) renders a filtered, grouped list:

```
[Search bar with X clear]
[All] [Follow-Ups] [To-Dos]              ← type filter pills

🔴 Overdue (3)              ▾
  [activity card]
  [activity card]
🟠 Today (2)                ▾
  [activity card]
🔵 This Week (4)            ▾
  ...
⚪ Later (12)               ▾
  ...
```

All sections start expanded. Tapping a section header collapses/expands it; the choice persists for the rest of the browser session (in-memory `_collapsedSections` Set, not localStorage).

## Detail modal Snooze row

Added between the body and the action row:

```
SNOOZE: [+1 day] [+3 days] [+1 week] [+1 month]
[Close] [Open Follow-Up Editor →] [Mark Done]
```

Tap a snooze chip → calls `/api/todos/snooze` with `{activity_id, days}` → backend bumps `date_deadline` by N days → modal closes → list reloads.

## Backend endpoint

`POST /owner/api/todos/snooze`
- Body: `{activity_id: int, days: int (positive)}`
- Reads current `date_deadline`. If it's in the past, **clamps to today** before adding (so a 30-day-overdue activity snoozed 1 week becomes 1 week from today, not 23 days from yesterday).
- Returns `{ok: true, date_deadline: 'YYYY-MM-DD'}`.

## Frontend state

```javascript
let _allTodos = [];                // full list from /api/todos
let _searchQuery = '';             // current search text
let _typeFilter = 'all';           // 'all' | 'followup' | 'todo'
const _collapsedSections = new Set();  // section keys collapsed by user
```

`renderOpen()` is called whenever filter state changes. It filters `_allTodos` through `passesFilters(t)` then groups by date proximity via `classifyBucket(t, today, weekEnd)`.

## Type filter logic

- `all` — no filter
- `followup` — only those where `isFollowupTodo(t)` returns true (partner_id set + summary/type contains "follow up", "follow-up", "followup", "reactivation", or "reach out")
- `todo` — everything else

The `isFollowupTodo()` predicate is the same one that surfaces the "Open Follow-Up Editor" button in the detail modal — so toggling "Follow-Ups" shows exactly the activities that have that button.

## Search filter

Case-insensitive substring match across `summary` + `record` + `type` + `note`. Empty search = no filter.

## Date-based bucket classification

```javascript
function classifyBucket(t, today, weekEnd) {
  if (!t.date) return 'later';
  if (t.date < today)   return 'overdue';
  if (t.date === today) return 'today';
  if (t.date <= weekEnd) return 'week';
  return 'later';
}
```

`weekEnd = today + 7 days` (calendar days). Activities with no date_deadline land in 'later'.

## Filter bar hides on Done sub-tab

`showSubTab(which)` toggles `#todo-filter-bar` visibility based on `which === 'open'`. The filter bar is only meaningful for open activities.

## When adding new activity types or filters

Add the predicate alongside `isFollowupTodo(t)`. If you add a new pill (e.g. "Calendly"), add a `data-type` value, the predicate match in `passesFilters`, and a button in the type-pills div. Don't refactor the whole bucket structure — sections are date-based and the type pills are orthogonal.

## Related memory

- `project_activities_module.md` — broader Activities module reference (READ FIRST)
- `project_activities_unified_flow.md` — detail-first routing pattern (the reason snooze chips live IN the detail modal, not on the cards)
- `feedback_activity_notes_self_contained.md` — note-authoring rule
- `session_apr29_summary.md` — context for why this was built
