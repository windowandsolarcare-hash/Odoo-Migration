---
name: project_cheryl_task_checklist
description: "Cheryl Tasks screen now shows + ticks the My Day checklist (x_myday_checklist). list returns checklist/chk_total/chk_done; new POST /cheryl/api/tasks/checklist persists the whole [{t,d}] array to the SAME field My Day uses = auto DJ↔Cheryl sync, no schema."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T17:57:52.007Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy" via §12 picker; Lead QC-GREEN). DJ via Dispatcher: a task he assigned Cheryl had a checklist in his My Day, but it didn't show on her Tasks screen.**

**Root cause:** the checklist lives in custom field `x_myday_checklist` on project.task (JSON `[{t:'step', d:bool}]`, written/read by My Day — `routers/owner/myday.py`). Cheryl's pipeline had ZERO awareness of it: `/cheryl/api/tasks/list` (routers/cheryl/tasks.py) didn't read the field, there was no persist endpoint, and `static/cheryl/tasks.html` had no checklist UI. Not broken — never built on her side.

**Fix (2 files, additive):**
- `routers/cheryl/tasks.py`: `list` FIELDS now includes `x_myday_checklist`; `_row` parses it → returns `checklist`/`chk_total`/`chk_done` (mirrors myday.py shape exactly). NEW `POST /cheryl/api/tasks/checklist` {id, checklist:[{t,d}]} → IDOR-guarded via `_her_any_domain` (same as /edit), items sanitized to `{t:str[:300], d:bool}` capped 100, writes `x_myday_checklist=json.dumps(clean)`, returns chk_total/chk_done.
- `static/cheryl/tasks.html`: renders the checklist TICKABLE inline on the row (not buried in edit) + a "✓ done/total" chip (`chkChip`/`chkBlock`); `toggleChk` sends the whole array (authoritative), optimistic strike w/ revert-on-fail.

**Why it auto-syncs:** both Cheryl's side and DJ's My Day read/write the ONE field `x_myday_checklist` — a tick on either surfaces on the other. No schema change (field already existed → [[feedback_existing_odoo_field_build_ui_dont_ask]]). She can only TICK (items are authored in DJ's My Day); no add/remove on her side. See [[project_dj_assigned_provenance_tag]], [[feedback_reuse_canonical_endpoint]].
