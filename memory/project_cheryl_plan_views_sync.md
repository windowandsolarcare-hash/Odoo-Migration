---
name: project_cheryl_plan_views_sync
description: "/cheryl/plan serves Cheryl-cloud's Phase-2 renderer (Gantt/board/ladder). It's her artifact FRAGMENT (plan-views.html) pulled from cheryl-workspace, stored at static/cheryl/plan-views.html, wrapped-at-serve by cheryl/hud.py cheryl_plan(). When she posts 'sync' → re-pull the fragment from her branch + redeploy the static file (do NOT fork/edit it)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-07T02:01:36.444Z
---

**Built 2026-09-06 (Phase-2 #1); synced 2026-09-06 to a "TODAY" front door.** Current version (48,768 bytes) opens on a **Today** tab (tabs Today → Timeline → Board → Ladder; bare `/cheryl/plan` lands on Today; deep links `?view=time|board|ladder`). DJ/Cheryl open the project views at **`/cheryl/plan`** — a real Render app route (NOT a claude.ai artifact: an artifact origin's CSP blocks the live `/cheryl/api/view/*` fetch; served same-origin under /cheryl, her `canFetch()` does the real fetch).

**How it's wired:**
- Her renderer is an **artifact-style FRAGMENT** (no doctype/html/head/body) named `plan-views.html`, authored in repo **cheryl-workspace**, branch **`claude/cheryl-idea-organizer-yzv19x`** (root). The exact serve-wrapper is in a comment block at the TOP of the file.
- It's stored verbatim in the app at **`static/cheryl/plan-views.html`** (the synced copy).
- **`routers/cheryl/hud.py` `cheryl_plan()`** (`@router.get('/plan')`) reads that file and WRAPS it at serve time (`<!doctype html>…<body style="margin:0">` + fragment + `</body></html>`) — **never fork the file to add the wrapper**, so the artifact and the app route stay one source of truth. Tabs / deep-links `?view=board` / `?view=ladder` are handled client-side.

**★ SYNC CONVENTION (when Cheryl-cloud posts "sync"):** re-pull `plan-views.html` from cheryl-workspace@claude/cheryl-idea-organizer-yzv19x → overwrite `static/cheryl/plan-views.html` (verbatim) → redeploy. That's the whole update; the route + wrapper don't change. Before pushing, `node --check` her inline `<script>` (one block, ~27KB) so a broken renderer never ships. She owns the visual layer; Specialists owns pulling + serving it.

**The payload it reads** (Specialists-owned, goals.py): `/cheryl/api/view/plan?from=&to=&goal_id=` → {tasks[{id,name,goal_id,due,scheduled_start,hours,progress,milestone_id,owner,done,pinned}], links[{from,to,kind}], days[{date,capacity,jobs,committed}], critical[], goals[], milestones[]}; and `/cheryl/api/view/ideas` (cards-only ladder). `progress` = **x_manual_progress** (native project.task.progress recomputes off hours — see [[project_cadence_engine]] discipline of behavioral verification). See [[project_voice_tool_add_pattern]] for the /cheryl delegation pattern (cheryl/hud.py add_api_route → owner handlers).
