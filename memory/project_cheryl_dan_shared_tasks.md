---
name: project_cheryl_dan_shared_tasks
description: The Cheryl & Dan shared-task stream (Cheryl Tasks edit/delete/reassign + My Day section + Command Center HUD tile) and the view_plan role-by-mount-prefix fix — how each piece works + the field/id facts.
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T23:46:42.951Z
---

DJ-directed feature shipped + Lead-QC-passed 2026-09-09 (repo saunders-render-app). Two related builds in one deploy (tip d580530).

**Owner/assignee facts:** `project.task.x_owner` (field id 21398) is a many2one → res.partner, the ONE owner per task. **Cheryl = 23243, Dan (DJ) = 3.** `project.project` has NO owner field. The "Goal" project.tags id = **25** (this is the TAG id, not to be confused with project id 25 "Not sorted yet"). The "Cheryl & Dan" project.tags id = **27** (get-or-create).

**1) Cheryl Tasks edit/delete/reassign** (`routers/cheryl/tasks.py`, UI `static/cheryl/tasks.html`): new endpoints `/cheryl/api/tasks/edit` (id,name?,due?), `/delete` (id → SOFT cancel `state='1_canceled'`, reversible, shown to her as "Delete"), `/reassign` (id, to:'cheryl'|'dan'). ALL IDOR-guarded via `_her_domain(pid)` (default-deny; task must be in her set = her x_owner OR the project-25 unsorted pool). UI: assignee chip, inline Edit, **two-tap Delete** (guards mis-taps, no browser dialog), "Give to Dan/Cheryl" toggle. list now returns `assignee`. Reassign→Dan writes x_owner=3 (drops it off her active list) + x_myday_type='task'; preserves the tag.

**2) Durable identity = the "Cheryl & Dan" tag.** `goals.cheryl_dan_tag_id()` (cached get-or-create, mirrors `_goal_tag_id`). Auto-applied on her every `/cheryl/api/tasks/add` and preserved on reassign — so the shared-stream identity survives the x_owner change. My Day + the HUD key off tag + x_owner, NOT x_myday_type.

**3) My Day section** (`routers/owner/myday.py api_myday` + `static/owner/v2_myday.html`): a dedicated query block ("2b") returns tasks tagged Cheryl&Dan + x_owner=3 + open with `kind='cheryl_dan'`, and dedups them out of the main task loop (`if t['id'] in cd_ids: continue`). Frontend: `KINDMETA.cheryl_dan`, its own "🤝 Cheryl & Dan" section at the TOP of the default date-bucket view (pulled out of `act` so it doesn't also land in date buckets) + in the type-sort. HUD count endpoint = `/owner/api/cheryl_dan/hud` ({count, items}).

**4) Command Center HUD tile** (`static/owner/v2_home.html`): WORK array idx 6, rose `.t-rose`, goes `.hot` when >0 (added 6 to the hot set in setWork), count from `/owner/api/cheryl_dan/hud`, href `v2_myday.html#cheryl_dan`.

**5) DJ reassign-back:** `goals.task_update` now accepts `owner:'cheryl'|'dan'` → writes x_owner (so the My Day section/HUD can kick a task back to Cheryl).

**view_plan role-by-mount-prefix fix** (`goals.py`, DJ-decided "safe fix"): the SAME `view_plan` is served at BOTH `/owner/api/view/plan` (owner_goals.router) AND `/cheryl/api/view/plan` (cheryl_hud.py `add_api_route`). Role signal = **`request.url.path.startswith('/cheryl')`** → `_build_view_plan(..., cheryl_only=True)` sets gids=[] + days=[] → Cheryl's Plan is EMPTY (she owns no goals; project.project has no owner field) = clean "No projects yet", which ALSO ended the old sample-data fallback. `/owner` unchanged with DJ's full goals. NO goals deleted/unlinked. This mount-prefix role check is a reusable pattern for any endpoint shared across /owner and /cheryl. See [[feedback_reuse_canonical_endpoint]], [[feedback_never_send_dj_to_odoo]], [[project_cheryl_plan_views_sync]].
