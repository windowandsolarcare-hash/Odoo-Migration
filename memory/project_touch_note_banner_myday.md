---
name: project_touch_note_banner_myday
description: "The 'touch' note sheet: undated notes stay OFF My Day (user_ids=[]), dated → My Day task, ⭐ next_visit → x_next_visit_note banner. Rule: only DATED touches hit My Day."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**The "touch" feature** (DJ's note-logging sheet, bottom of the job/Brain — `outDoLog` in field.html → `POST /owner/api/touch`, `reactivation.py` L1587 `api_touch`). Body `{partner_id, kind, text, date?, next_visit?}`. Does up to 3 things:
1. **Timeline** — ALWAYS: chatter `message_post` + `x_crm_activity_log` create on the parent customer.
2. **project.task** — created when `kind=='note'` OR a `date` is given. **DATED** → `user_ids=[(6,0,[ODOO_USER_ID])]` = assigned to DJ = **shows on My Day** (Action Items). **UNDATED note** → `user_ids=[(6,0,[])]` = unassigned = **OFF My Day** (lives as a job/customer note in the field Notes list). ⚠ Odoo re-adds the creator to user_ids AFTER create, so the code re-writes `[]` right after (L1641-1643) — this strip is THE mechanism that keeps undated notes off My Day.
3. **⭐ next-visit banner** — if `next_visit`, writes `x_next_visit_note` (res.partner, single text field on the parent/commercial customer). Renders as the `next-visit-banner` in field.html ("pops up at their door until you clear it"). NOT a task.

**THE RULE (DJ 2026-07-12):** only DATED touches belong on My Day. An undated note = a job/customer note (off My Day); a ⭐ star = a banner (off My Day). My Day is dated items only. The touch endpoint already enforces this via the user_ids strip — verified working (a note flagged ⭐ with no date today landed unassigned/off My Day correctly).

**Field-app Notes list (2026-07-13 upgrade):** the per-customer Notes card (field.html `loadPartnerNotes` → `GET /owner/api/todos/for_partner`, activities.py) now: (1) shows each note's **creation date** (🕘 create_date, always kept) plus due date (📅) only when set; (2) **keeps DONE notes** — "✓" calls new `POST /api/todos/complete` (state=1_done, active stays True) instead of the old `/api/todos/delete` (active=False archive) that made them vanish; for_partner returns done notes too (domain `state != 1_canceled`) with a `done` flag + `created`; (3) done notes render struck-through under a collapsed **"Show completed (N)"** toggle (`toggleDoneNotes`), Undo = `POST /api/todos/reactivate` (state back to 01_in_progress, same record — no dup). (4) **Clearing the ⭐ banner** (`POST /owner/api/customer/next_visit_note` with empty note, outreach.py `api_next_visit_note_set`) now marks the underlying note DONE via best-effort text match (`name == old_banner[:80]` across parent+children partners) so it lands as a checked note. Commits: activities 0e9c00d, outreach 716d60b, field.html 250c999.

**Legacy leak cleaned 2026-07-12:** notes created BEFORE the user_ids-strip fix still had user 2 → leaked onto My Day. Found 6 undated user-2 tasks: 3 customer (1203 Kristin→converted to ⭐ banner; 1048 Curtis "Husband is Miles"→kept as plain note, both user_ids stripped off My Day; 1224 Carlos phone# left for DJ) + 3 personal/no-customer (785, 999, 1005 = DJ's own, left to handle). NOTE: "Hisband is Miles" was ONLY on the task, never on Curtis's job/chatter — verify before deleting any such note. Separately, Vault/Notes `/api/notes/create_todo` (notes.py L572) also makes project.tasks and does NOT strip user_ids — a possible secondary undated-leak path if used without a date. See [[project_myday_organizing_system]], [[project_reengagement_no_myday_task]].
