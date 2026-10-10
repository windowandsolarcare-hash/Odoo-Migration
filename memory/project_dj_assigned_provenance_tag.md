---
name: project_dj_assigned_provenance_tag
description: "'DJ Assigned' project.tags tag stamped on Cheryl's tasks when DJ assigns them (vs tasks she creates herself) — drives a distinct 'DJ gave you' HUD card. routers/owner/goals.py dj_assigned_tag_id() + myday.py + feed_live.py _cheryl_assigned."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T14:23:25.447Z
---

**DEPLOYED 2026-10-10 to main (DJ "deploy"; QC-GREEN by Lead). Live commit e0e5b824. Part of DJ's one-at-a-time list (item 4).** Provenance so Cheryl's feed distinguishes *tasks DJ handed her* from *tasks she created herself*.

**Field/mechanism (NO schema change):** `routers/owner/goals.py` → `dj_assigned_tag_id()` get-or-creates a `project.tags` tag named **"DJ Assigned"** (module-cached in `_DJ_ASSIGNED_TAG`). It is appended `(4, dj_assigned_tag_id())` to `tag_ids` ONLY at DJ-side assignment points when `owner=='cheryl'`:
- `goals.py` `assign_task` + `create_shared_task`
- `myday.py` `/api/myday/add` cheryl path (`_djt`, alongside the cross-stream `cd` tag)

**Cheryl's own task-writers do NOT add it** (`cheryl/tasks.py` writes tags directly) — so a task she made herself never gets the DJ-Assigned tag. That's the whole point: the tag means "DJ assigned this."

**Feed consumption:** `feed_live.py` `_cheryl_assigned` now requires BOTH the cross-stream `cd` tag AND the `dj_tag` → renders the card title **"🤝 DJ gave you %d task%s"**, why_now **"Assigned to you by DJ…"**. Live HUD producer (self-hides at 0).

**⚠ feed_live cross-branch (RESOLVED at deploy):** both this (item 4) and the review pick-list ([[project_review_request_picklist]]) edited feed_live.py in non-overlapping regions. Deployed together via a 3-way merge (git merge-file, ancestor=live main) → combined file carries BOTH `_cheryl_assigned` (region A) and `_review_requests_ready` (region B). See [[feedback_staged_mirror_stale_base_refetch]].

EOL note: **goals.py is CRLF** (preserved on push); myday.py + feed_live.py are LF. See [[feedback_dj_owns_cheryl_erp_access]].
