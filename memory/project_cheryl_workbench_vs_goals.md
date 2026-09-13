---
name: project_cheryl_workbench_vs_goals
description: "Cheryl's Projects/'Workbench' and DJ's 'Goals' run on the SAME Odoo model — the only difference is the renderer; her Plan screen is an imported foreign artifact. Alignment is UI, not data."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-13T23:05:24.677Z
---

**Finding (2026-09-13, from DJ's floating-recorder walkthrough — DJ: "projects being workbench is a struggle... compare to my goals on the ERP side").**

**They are the SAME underlying Odoo model.** Both DJ's "Goals" and Cheryl's "Projects" sit on Odoo-native `project.project` (tagged "Goal", company_id=1, allow_milestones) → `project.milestone` → `project.task`; WOOP/obstacles in `ir.config_parameter` (`wsc.goal.woop.<id>`); goal target date = custom `x_goal_target_date`. No custom models. `create_goal_core` / `create_task_core` in `goals.py` are the shared canonical functions (Cheryl's just stamp a "Cheryl" tag for scoping).

**Why Cheryl's "struggles":** her side is a DIFFERENT RENDERER, not a different engine.
- DJ "Goals" = `static/owner/v2_goals.html` + `routers/owner/goals.py` — ONE screen, strict Goal→Milestone→Task(+loose)→WOOP→capacity forecast, full CRUD. The one he likes.
- Cheryl "Projects/The Plan" = `/cheryl/plan` served by `routers/cheryl/hud.py` → `static/cheryl/plan-views.html`, an **imported artifact from Cheryl's own cloud workspace** ("cheryl-idea-organizer"). 4 tabs (Today/Time/Board/**Ladder**), read-mostly, a different "mission→goals→idea-cards" metaphor, and **sample-data fallback** on the Ladder when the ideas call fails. Foreign feel = the struggle.
- Cheryl "Tasks" = `/cheryl/tasks` (`routers/cheryl/tasks.py` + `tasks.html`) — a good flat task list (progressive disclosure; goal hierarchy hidden). KEEP this.
- "Workbench" is NOT user-visible to Cheryl — only internal (`feed_live.py` `source='workbench'`, `_WORKBENCH_HREF='/cheryl/plan'`) + specs. Her home cards say "Tasks" + "Projects."

**Recommendation given to DJ (his decision):** serve Cheryl a **Cheryl-scoped copy of `v2_goals.html`** (same pattern `hud.py` already uses to reuse `v2_hud.html` via an injected FEED_BASE global), retire `plan-views.html` as her Projects screen, drop the "Workbench" term. Caveat = moderate ADDITIVE work: `v2_goals.html` hardcodes `API='/owner/api/goals'` (:236) so parameterize the API base, and register the goals CRUD suite under `/cheryl` (goals/list,get; milestone/*; task/update; obstacles/save) with Cheryl-tag scoping + IDOR guards like tasks.py. **No schema/data migration.**

Related: [[feedback_recordings_chunk_stream_durable]] (how the recording was captured), [[feedback_dj_owns_cheryl_erp_access]].
