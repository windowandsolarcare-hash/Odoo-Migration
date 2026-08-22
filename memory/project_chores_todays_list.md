---
name: project_chores_todays_list
description: "chores.html is the Today's List app (not planner.html). Lives at /static/chores.html in saunders-render-app repo."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b173fd1-b5b7-43e3-ba55-7c216343fb45
---

`chores.html` = the "Today's List" app DJ calls "today's list app" or "chores". URL: `/static/chores.html` in saunders-render-app repo (static/ root, NOT static/owner/).

`planner.html` = the Daily Planner habit tracker with Today/Week/Stats tabs. Completely different app.

**Why:** DJ had to correct me twice — I edited planner.html and activities.html when the actual target was chores.html.

**How to apply:** Any request about "today's list", "chores", or "task list" refers to chores.html. Habit tracking requests → planner.html.

API differences:
- `chores.html` → `/list/data` (GET/POST, no access code)
- `planner.html` → `/owner/api/planner/*` (requires access_code param)
