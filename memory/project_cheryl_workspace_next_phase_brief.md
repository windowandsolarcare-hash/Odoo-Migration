---
name: project_cheryl_workspace_next_phase_brief
description: "DJ's 2026-09-06 design direction for the Cheryl/DJ workspace's next phase: build the Projects/PM pillar now (Cheryl tweaks after, don't wait), mission-first Ideas, in-app documented comms (no email), and above all a GRAPHICAL organizing model beyond sorted/filtered lists — all moving to app-stage (server-side)."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-06T08:54:05.779Z
---

**DJ's design direction for the workspace's next phase (2026-09-06), after touring the built pieces.** Five threads:

1. **PROJECTS (pillar 4) — BUILD IT NOW, don't wait for Cheryl.** ★ DJ CORRECTED the earlier "parked pending Cheryl" rule: *"all I said was Cheryl will LIVE this. She still needs it built by us, then she can tweak or change it."* So the fleet BUILDS the projects/PM layer; Cheryl adjusts after — it is NOT wait-for-Cheryl. (Supersedes the "get Cheryl in a session before building the PM layer" framing in [[project_cheryl_workspace_next_phase_brief]]/earlier notes.) Base it on a solid PM: DJ's **"goals app" = OUR OWN ERP app** (RESOLVED 2026-09-06): `routers/owner/goals.py` + `static/owner/v2_goals.html` (🎯 on the v2 launcher), backed by Odoo **project.project/project.task** — "Goal Board: goals → milestones → tasks → WOOP obstacles" + capacity/slot awareness (`/api/goals/day_capacity`, `next_slots`, `overloaded_days`). So the projects pillar = **EXTEND Goals** (app-code = Specialists), NOT from scratch. DJ's two gaps: **task dependencies** and **more views — Gantt especially** (+ board/timeline = the graphical direction). ★ Goals is project.task-backed and the **task-surface pillar was also "a view of project.task"** — so projects + tasks are ONE project-data spine surfaced through Goals extended, design them together, not two builds.

2. **IDEAS — "ok, not great," needs work.** Reframe **mission-first**: a mission/vision at the top; ideas LADDER UP from it / build toward it, not a flat pile.

3. **COMMS — the DJ↔Cheryl communication piece lives IN THE APP, NOT email.** DJ: don't want to use email; want everything CAPTURED in the app, everything DOCUMENTED. Design an in-app, fully-logged comms surface.

4. **★ THE HEADLINE THEME — GRAPHICAL, NOT LISTS.** DJ: *"lots of what we do are lists which is ok... wish we could introduce something cooler or fancier than sorted/filtered lists. something graphical... need something that organizes outside of a list."* So the workspace needs a VISUAL/SPATIAL organizing metaphor (boards/canvas/map/timeline/graph — not rows), ideas especially. This is the biggest single direction.

5. **APP-STAGE — DJ greenlit the server-side move.** *"need to move this along to app stage."* The workspace graduates from standalone published artifacts to REAL APP SCREENS (Specialists builds server-side). Design targets server-side.

**How to apply:** Lead routed this to Cheryl's cloud as a DESIGN BRIEF — draft a PLAN (deps+Gantt+views projects, mission-first ideas, in-app documented comms, and above all the graphical organizing model, all targeting app-stage), calling out Specialists (server-side) vs Cheryl's-cloud design + a recommended order. **DJ approves the plan before anyone builds.** See [[project_cheryl_workspace_hud_pattern]] (HUD front door), [[project_agent_dj_banner_channel]], [[project_idea_board]] (the current list-based Idea Board this reworks).
