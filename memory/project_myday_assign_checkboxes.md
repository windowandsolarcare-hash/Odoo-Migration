---
name: project_myday_assign_checkboxes
description: "My Day 'Assign to' = two CHECKBOXES Dan+Cheryl (replaced single Me/Cheryl pills). Both-checked = SHARED task via new 'Shared Both' tag + x_owner=Cheryl (canonical) so her list/auth/HUD stay unchanged; Dan-side reads widened. goals.make_personal is the ONE unshare helper for both to-Dan paths. Deployed 2026-10-11."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T02:59:51.860Z
---

**DEPLOYED 2026-10-11 to main (DJ "Deploy now" §12 picker; Lead QC-GREEN; Audit §15 COMPLETE). Branch specialists/myday-assign-checkboxes @ f5228da8. 4 files, no route change.** Replaces the single-choice Me/Cheryl pills on My Day with TWO checkboxes (Dan default-checked, Cheryl optional).

**3 states (DJ Q1/Q2/Q3 2026-10-11):** Dan-only = his PERSONAL task; Cheryl-only = hers (he sees via "With Cheryl" pill = section 2c); **BOTH = shared, shows on both plates.** Unchecking Dan = hand fully to Cheryl; either can delete a shared task; tick-done = done for both (one record). A task must belong to someone → UI re-checks Dan if both unchecked.

**The "both" problem + design:** `x_owner` is a single M2O (Dan=3 / Cheryl=23243), so Dan-actionable (x_owner=3) and Cheryl-actionable (x_owner=her) are mutually exclusive — "both" needs a marker beyond x_owner. Solution = new get-or-create tag **"Shared Both"** (`goals.shared_both_tag_id()`, cached, NO schema) + **canonical x_owner=Cheryl** for a both-task. Why x_owner=Cheryl: her list/edit-auth (`cheryl/tasks.py _her_*_domain`) + HUD tile (`feed_live._cheryl_assigned`) are IDOR/auth-sensitive and all x_owner-based → a both-task is naturally hers with ZERO change there. Only Dan-side READS widen: My Day **section 2b** + **Command Center `/api/cheryl_dan/hud`** domain = `cd_tag AND (x_owner=3 OR Shared-Both)`; **section 2c** excludes Shared-Both (dedup — it shows via 2b); 2b item carries a `shared_both` flag for the UI.

**ONE shared tag-move helper (goals.py) — no drift (Lead/Audit gate):** `make_personal(task_id)` = UNSHARE (x_owner=Dan, strip cd+dj+both via (3,id) unlink) — called by BOTH owner-side `assign_task(id,'dan')` AND Cheryl-side `cheryl_tasks_reassign` to='dan'. `assign_task(id, owner, add_provenance=True)`: 'dan'→make_personal; 'cheryl'→x_owner=Cheryl +cd +dj(unless add_provenance False=PULL-BACK of her own task→keep cd/dj, no forced DJ-Assigned) and STRIP both; 'both'→x_owner=Cheryl +cd +dj +both. Cheryl pull-back calls `assign_task(id,'cheryl',add_provenance=False)` so her reclaimed task isn't mislabeled "DJ gave you". Only ONE caller of assign_task existed (myday.py update) so the contract change was safe.

**UI (v2_myday.html):** checkboxes on ADD + EDIT sheet (edit was hidden before → now shown = §13 CRUD parity) + ⋯ menu 3-state quick set (Just me / Cheryl only / Both). `edOwnerVal()` derives dan|cheryl|both; send-on-change (new: default dan sends nothing; edit: only on change). **NUANCE (flagged to DJ):** Cheryl's hand-to-Dan now UNSHARES (per Q1), so her legacy "watch handed-to-Dan" view (tasks.py:242) won't catch newly-handed tasks. **MINOR accepted:** `cheryl/goals.py` capacity (:195) counts a both-task's FULL hours against Cheryl. goals.py is CRLF; others LF. See [[project_dj_assigned_provenance_tag]], [[project_cheryl_task_checklist]], [[feedback_existing_odoo_field_build_ui_dont_ask]].
