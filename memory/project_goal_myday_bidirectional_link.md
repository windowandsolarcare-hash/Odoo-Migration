---
name: project_goal_myday_bidirectional_link
description: "Goal tasks pinned to My Day now link both ways: My Day row → tappable 🎯 goal chip opens the goal (and highlights the task); the goal task shows a ☀️ My Day link. Honors the bidirectional-creation-links standing rule."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T08:06:04.525Z
---

**2026-07-24 (DJ: tasks created in Goals that appear in My Day should link back and forth).** Applies [[feedback_bidirectional_creation_links]].

**Surfacing (updated 2026-07-25, myday.py de91c89):** DJ expected milestone tasks to appear in My Day but none did — they were pin-only. He chose **auto-show**: any goal task with a `date_deadline` now surfaces in My Day on its day, alongside normal reminders + pinned. My Day task domain widened to `OR(project_id=False, x_myday_pinned=True, AND(project_id in <goal project ids>, date_deadline!=False))` — goal ids = project.project with tag "Goal", company 1. Pin now just controls top placement. (Consequence: dated tasks from ALL goals show, incl. far-off ones in the Later group — DJ picked full auto-show over the due-soon middle option.)

Goal tasks are `project.task` with `project_id` = the goal. Both directions are tappable:

**My Day → Goal:** `myday.py` task payload adds `goal_id` + `goal_name` (from the `project_id` many2one, which already returns `[id, name]` — no extra query). `v2_myday.html` `card()` renders a brand-colored chip `🎯 <goal> ↗` (class `a.m.goalchip`) linking to `/static/owner/v2_goals.html?goal=<gid>&task=<tid>`.

**Goal → My Day:** `v2_goals.html` `taskHtml` shows a `☀️` link (`.myday-lk`) whenever the task is actually IN My Day — i.e. **`t.pinned || t.due`** (updated 2026-07-25 from pinned-only, since dated goal tasks now auto-surface; a pinned-only gate hid the link on DJ's dated-but-unpinned tasks). It links to `/static/owner/v2_myday.html?task=<tid>`. In My Day, cards carry `data-tid`; the init reads `?task=` and `highlightTask(tid)` scrolls to `.it[data-tid=...]` + flashes a brand outline, and if the card isn't found (task sits in a collapsed group) it expands all groups (view-only, not persisted) and retries.

**My Day → Goal:** (also `?task=` in the other direction) `openGoal(id, taskId)` reads `?task=` and `scrollToTask(tid)` highlights `.task[data-tid=...]` in the goal.

Files: myday.py c0fa75e, v2_myday.html 0874d2b, v2_goals.html 5a78a58. See [[project_goal_board]], [[project_goal_target_date_phaseA]].
