---
name: Session summary — 2026-04-20 (truck / remote control day)
description: What was done today across W&SC and Cheryl projects; open items to revisit
type: project
originSessionId: 545d601c-e5c6-46c0-aca1-5a8081a73ec9
---
**Context:** DJ was remote-controlling from his truck all day. One session name: WSC-Auto. Worked across W&SC and Cheryl projects from the single W&SC session using absolute paths.

## W&SC FIXES TODAY

**Balser orphan task — fixed.** SO 15916 had no project.task despite tasks_count=1. Recreated task 297, linked to order line 17478. Root cause: Phase 4 task re-entry bug (see `project_phase4_task_reentry_bug.md`).

**Jose Merelies tech-gate — diagnosed, not auto-fixed.** SO 17113 failed Phase 6 tech gate because `x_studio_x_studio_workiz_tech` was blank. DJ handled tech assignment from the truck. Invoice was created twice (INV/00114, INV/00116 both paid $150) because payment button fired twice — Phase 6 correctly refused to close Workiz on both attempts.

**Timer UI bug confirmed as UI-only.** Backend timesheets are clean (see `project_render_timer_ui_cumulative.md`). 7 jobs today, 7 single timesheet lines, zero duplicates.

**Orphan SO sweep — 1 real orphan found.** SO 17066 (Wayne Geringer, Aug 20 2026) still needs task recreation. Low urgency.

## CHERYL PROJECT — SHIPPED TODAY

Project was split out of W&SC repo into its own:
- Local: `C:\Users\dj\Documents\Business\A Cheryl Real Estate`
- Repo: `windowandsolarcare-hash/cheryl-real-estate`

Built and deployed:
- `/cheryl/` dashboard (5 tiles, dark/light toggle)
- `/cheryl/clients` list view + stage picker modal
- Odoo schema: "Cheryl's Clients" tag (id 249) + 4 custom fields on res.partner (x_cheryl_stage, x_cheryl_last_use, x_cheryl_onehome_visit, x_cheryl_onehome_ref)
- 314 contacts imported from her OneHome CSV

CSV gotcha: Google Sheets CSV export had data rows shifted one column right of header row. Solved with positional-extraction parser (`@` = email, `"Last, First"` = name, MM/DD/YYYY = date, trailing digits = ref). Import script: `A Cheryl Real Estate\1_Production_Code\import_cheryl_clients.py`.

Still blocked on Cheryl: checklist items per stage, business name (for Odoo company), CRMLS Spark API access via broker.

## INFRASTRUCTURE NOTE

**PowerShell deploy script gotcha:** When pushing files inside subfolders of a new repo, the old gh-api-via-powershell script failed with a nested-JSON error (404 mixed into the SHA var). Python subprocess wrapping gh worked. If DJ hits the same shell-out-via-PowerShell issue again, switch to Python subprocess. Detail in `project_cheryl_repo_split.md`.

## SCHEDULED (SESSION-ONLY, WILL DIE IF SESSION ENDS)

At 2026-04-20 18:42 local, DJ asked for "remind me soon" about pending items. Cron job 7c3d96b9 scheduled to fire at 19:27 local — one-shot, session-only. If DJ starts a new chat before 19:27, that reminder dies. All items are already captured in memory files (pending_sync_before_payment, odoo_upsell_activity, reactivation_attempt2, pending_cursor_history_review, plus the two new memories from today), so starting fresh doesn't lose the list — just loses the automated nudge.

## NEXT SESSION SHOULD ASK

- Did Cheryl give feedback on the client list view (she tests it tonight)?
- Did DJ disable the Odoo Upsell toggle yet?
- Does DJ want to recreate SO 17066 Wayne Geringer's task now or defer?
- Does DJ want to start on the Phase 4 sync re-entry permanent fix?
