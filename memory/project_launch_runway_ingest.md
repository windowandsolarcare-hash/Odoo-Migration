---
name: project_launch_runway_ingest
description: "Launch-Runway ingest (2026-09-08, DONE+LIVE): Cheryl's 'Launch Runway' Claude artifact (90 tasks/5 phases, linked off Odoo task 1675) → 77 project.task on the Gantt (hiring phase SKIPPED — existing 20-task 'Hire a Lead Technician' goal 13 covers it). New goal 'Launch Runway' (id 26, Goal-tagged 25), phase→milestone (20-23), tag 'Launch Runway' (26), idempotent per NEW field project.task.x_source_id='lr:<id>'. GUARDED: snapshot→additive-ingest→diff, 0 drift on the 45 existing tasks. Reversible: delete x_source_id like 'lr:%'."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T20:35:14.775Z
---

**Built 2026-09-08 (DJ greenlit via Lead; DJ hands-off "you do it safely"). The last thing parked on DJ for Launch-Runway.**

**Source:** the "Launch Runway" is **Cheryl's Claude artifact** `https://claude.ai/code/artifact/7f9369ac-85d9-4e13-be2d-a088b300b46d` (linked in the description of Odoo **project.task 1675** "Review 'Launch Runway' — Cheryl's artifact"). NOT a Drive doc, NOT in any repo — it's a published artifact. Its data lives in a `<script type="application/json" id="data">` block: **90 tasks** across 5 phases (`pricing` 9, `reviews` 8, `gbp` 17, `hiring` 13, `launch` 43) + non-task reference sections (drops/budget/decisions/flags/roi — NOT ingested). Each task: id (p1..), phase, t(title), who, st(done/doing/todo), p(progress 0-100), note, up(deps — only 1 task has any). Parsed to `_lr_data.json`.

**Ingest (77 tasks — Lead's 3 forks):**
- **A HIRING SKIPPED:** the artifact's 13 hiring tasks re-frame the SAME domain as the existing 20-task **"Hire a Lead Technician" goal (project 13)** — ingesting = a duplicate parallel hiring list (the "two things for one idea" anti-pattern). Kept the existing detailed 20; ingested the other 77.
- **B GANTT SCAFFOLD:** artifact tasks have NO dates/hours → invisible on the Gantt (the blocker). Fix: ladder 1/day from today, 2h each, 2-day seam between phases → biggest phase (Launch 43) naturally gets the longest span. Every description carries "[Launch Runway] this Gantt date is a STARTING GUESS — drag to set."
- **C OWNERS:** single→`x_owner` (Dan/DJ→partner 3, Cheryl→23243); shared("Cheryl+DJ"/"Dan&Cheryl")/blank→unassigned (only 22 of 77 have a single owner).

**Odoo objects created:** goal **project.project "Launch Runway" id 26** (company 1, tag_ids=[25] so the plan reads it as a Goal); phase **milestones** Pricing 20 / Reviews 21 / GBP 22 / Launch 23 (task.milestone_id); **project.tags "Launch Runway" id 26**; ★ **NEW custom field `project.task.x_source_id`** (Char, indexed, store) = the idempotency key, value `lr:<artifact-id>`. Mapping: name=t, description=note+scaffold-note, x_manual_progress=p (0-100 scale confirmed), state=`1_done` if done else `01_in_progress`, date_deadline=laddered, allocated_hours=2.

**★ THE GUARD (DJ's method — export→ingest→restore→diff):** SNAPSHOT all 45 existing goal-project tasks (projects 10/9/13/3/1/25) id/name/date_deadline/allocated_hours/x_manual_progress/x_owner → `_planbak_<ts>.json` + `ir.config_parameter wsc.planbak.latest` BEFORE. Ingest is **ADDITIVE** — new tasks under a NEW goal (26), the code NEVER writes a task without an `lr:` source id — so existing tasks are structurally untouched. Re-read all 45 FRESH after: **drift = 0 fields**. Independently re-verified (fresh read vs the backup file): CLEAN.

**★ Lead independently QC-verified (2026-09-08): re-read wsc.planbak.latest + all 45 tasks fresh → 0 drift himself (not on report); 77 tasks match on both x_source_id lr:% AND tag 26. Lead blessed this snapshot→additive→restore→diff pattern as THE TEMPLATE for any future ingest** — reuse it (snapshot the protected set, only ever write records carrying your ingest key, re-read + diff to prove 0 drift, keep it reversible by key/tag/project).

**★ Idempotent + REVERSIBLE:** re-running updates the 77 in place (search by x_source_id), never duplicates. To UNDO: delete `project.task` where `x_source_id like 'lr:%'` (or by tag 26 / goal 26), then optionally the goal/milestones/tag/field. Script: `C:/Users/dj/_lr_ingest.py` (EXECUTE flag; DRY-RUN default). Helper gotchas hit: xmlrpc `read` takes the ids list bare (not wrapped), `write` needs ids+vals as TWO args, `set_param` needs two positional args, `create([{}])` returns `[id]` (unwrap). See [[project_plan_task_add_owner]] (x_owner + the plan's goal/Gantt model) and [[feedback_never_send_dj_to_odoo]] (why this went straight into the Gantt, not asked of DJ).
