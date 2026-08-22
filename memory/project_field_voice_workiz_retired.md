---
name: project_field_voice_workiz_retired
description: "Field VOICE assistant (field.py SYSTEM_PROMPT/HELP_TEXT/TOOLS) de-Workiz'd — it was still advertising + calling dead Workiz tools; now Odoo-only."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-18T15:17:09.688Z
---

**DJ 2026-08-18:** asked the field VOICE assistant "what can you do" and it "talked a lot about Workiz" + risked calling Workiz (retired 2026-08-03). Fixed field.py (commit 48a6bf1):

- **HELP_TEXT** (the hardcoded "Here's what I can do" reply, returned for 'what can you do'/'capabilities' at the trigger list ~line 2964) was the thing DJ saw — it listed "open Workiz jobs", a "CREATE A JOB" voice flow, and "UPDATE WORKIZ JOB FIELDS". Rewritten Odoo-native (schedule/info, navigate, customer profile, payments, log/tasks, email, memory) + a footer noting booking/reschedule/postpone/duplicate are done on the app SCREENS now, not by voice.
- **9 dead Workiz voice tools HIDDEN** via `DEAD_WORKIZ_TOOLS = {workiz_get, workiz_update, update_workiz_field, mark_job_done, create_workiz_job, duplicate_workiz_job, schedule_job, push_quote_to_workiz, delete_workiz_job}` + `TOOLS = [t for t in TOOLS if t['name'] not in DEAD_WORKIZ_TOOLS]` (right after the TOOLS list). Schemas are KEPT defined (don't delete working code) but not exposed to the model, so it can't advertise/call them. Backstop: a guard at the TOP of `execute_write_tool` returns "Workiz is retired…" if any is ever invoked (never hits the dead API). `DEAD_WORKIZ_TOOLS` is defined after execute_write_tool — fine, resolved at call time.
- **SYSTEM_PROMPT** rewritten: added a top "⚠️ WORKIZ IS RETIRED — DO NOT MENTION OR USE IT" banner; WHO YOU ARE = Odoo only; removed workiz_get/workiz_update/schedule_job from PRIMARY TOOLS; "WORKIZ FACTS" → "JOB STATUS + SERVICE TYPES (Odoo)"; SCHEDULING WORKFLOW (all Workiz SubStatus/link stuff) → short "SCHEDULING" = done on app screens, assistant only looks up + points to the screen; New-job + Monthly patterns de-Workiz'd; dropped the `x_studio_x_workiz_link` field line; reframed `ref`/`location_id` as "legacy … id".
- The status field is still `x_studio_x_studio_workiz_status` (a real Odoo CHAR field — the NAME is historical; it's just a label now: Done/Submitted/Scheduled/Postponed/Canceled). Those field-name occurrences are unavoidable and fine — DJ never hears them.

**NOT touched (already safe):** `payments._sync_so_with_workiz` (called by record_check_payment) is guarded — returns early when the SO has no `x_studio_x_studio_workiz_uuid` (every Odoo-native job) and the whole body is under try/except, so old jobs degrade gracefully. No dead-API break on payments. See [[project_status_label_vs_so_state]] [[project_postpone_needs_scheduling]].
