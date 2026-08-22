---
name: project_job_note_vs_task
description: "Field job 'Note' button = a JOB note (shows under the Notes card, Odoo-stored) that becomes a My Day task ONLY if you give it a date. Workiz is being retired so notes live in Odoo."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce7b153f-3bb6-4e33-a982-35d4d7a9f4ba
---

**DJ 2026-07-06 (Workiz is dropping, so notes must live in Odoo; DJ dislikes the ⋯ menu for notes):** the field job-detail **"📝 Note" button** (bottom of the open job → `openNoteModal`/`submitNote`) is the note flow. Rule:
- **No date → job-only note.** Shows under the "📝 Notes" card on the open job detail (`loadPartnerNotes` → `/api/todos/for_partner`, which filters by **partner_id only**). Does NOT appear in My Day.
- **With a date → also a My Day task** with that due date.

**Mechanism (all in `routers/owner/activities.py`):** notes are `project.task` (project_id=False, partner_id set). My Day pulls `project.task` where `user_ids in [2]`; `for_partner` pulls by partner_id (no user filter). So the lever is the ASSIGNEE:
- `/api/todos/create`: dated → `user_ids=[(6,0,[2])]` + `date_deadline`; undated → leave unassigned.
- `/api/todos/update`: adding a date → `user_ids=[(4,2)]` (promote to My Day); clearing the date → `(3,2)` (demote to job-only).

**★ GOTCHA that cost several deploys:** Odoo's project module **force-adds the creator (user 2) to `user_ids` AFTER create**, so setting `user_ids:[(6,0,[])]` in the create vals does NOT stick — the new task still lands in My Day. FIX = a **post-create write** `write [[task_id],{'user_ids':[(6,0,[])]}]` for undated notes (a WRITE clears it reliably; the create-time value is overridden). Verified: undated → on job card True / My Day False; dated → My Day True.

The old "25 panels" task (id 1222, Sheela Havas) that triggered this was converted to a job-only note (unassigned). "Add Workiz Note" (⋯ menu, writes Workiz JobNotes) is the legacy path being retired. See [[project_customer_brain_job_actions]].

## THIRD note type — NEXT-VISIT NOTE (distinct from the two above)
A separate flow DJ often forgets the name of: an at-the-door **instruction/agreement to remember for NEXT time** ("clean their solar panels next time", "add screens", "gate code changed"). Stored in **`res.partner.x_next_visit_note`** (customer-level, NOT a task). Endpoints: `GET/POST /api/customer/next_visit_note` (outreach.py) — both resolve property→parent via `_nvn_partner`, so set and read always land on the same customer.
- **SURFACES** as a gold "⭐ Heads up for this visit" banner (`#next-visit-banner`, `loadNextVisitNote`) at the top of the field job detail whenever ANY job for that customer is opened; a "✓ Done — clear this" button clears it (`clearNextVisitNote`).
- **SET from two places:** (1) the Customer Brain "📞 Log a touch" sheet (`outShowLog`) has a "⭐ Flag this for the next visit" checkbox; (2) **NEW 2026-07-09** — the field job **📝 Note modal** (`openNoteModal`/`submitNote`) now has a "⭐ Flag for next visit" checkbox too, so DJ can set it right from the job he's working (he couldn't find the Log-a-touch button on the job detail — it was only on the Customer Brain). Checking it writes `text` to `x_next_visit_note` after the note saves.
So on the job: 📝 Note (no date=job note / date=My Day task) + optional ⭐ flag = surfaces next visit. Three behaviors, one modal.

## ★ UNIFIED "Log a touch" — one component, one endpoint (2026-07-09)
DJ: merge Note + Log-a-touch into ONE thing, on the job (replacing the 📝 Note button) AND in the customer brain, with all 4 kinds getting the same 3 outcomes. Built + verified E2E on Chuck McBride (23215).

**NEW `POST /api/touch` (reactivation.py)** — Body `{partner_id, kind:'call'|'reply'|'inperson'|'note', text, date?, next_visit?}`. One call does up to 3 things for ANY kind:
1. **ALWAYS → timeline**: chatter message_post + `x_crm_activity_log` (logged_<kind>). Same write as `/api/outreach/log`.
2. **project.task** created when `kind=='note'` OR a `date` is given: undated note → unassigned (`user_ids [(6,0,[])]` + post-create write to beat Odoo's creator re-add) = shows in the Notes list, OFF My Day; dated → `date_deadline` + `user_ids [(6,0,[ODOO_USER_ID])]` = My Day + Action Items (a non-note dated touch is named "📞 Call: <text>").
3. **⭐ next_visit → `x_next_visit_note`** (the banner).
★ The task lands on the **raw partner_id** (matches `/api/todos/for_partner`'s exact-id query so it shows in the Notes list); timeline + next-visit resolve property→parent via `_followup_customer_id`. Also bumps `x_last_communication` for call/reply.

**Frontend (field.html):** the job's History-card "📝 Note" button → **"📣 Log a touch"** (`outShowLog(activeJob.partner_id)`). The shared `outShowLog` sheet gained a **date field** (`#out-log-date`) + the ⭐ checkbox; `outDoLog` now makes ONE `/api/touch` call (was outreach/log + a separate next_visit call). After save it refreshes the outreach strip and, if the open job is that customer, `loadPartnerNotes` + `loadNextVisitNote`.
**Notes card → collapsed button + count:** `#notes-section` is now a "📝 Notes (N)" toggle button (`toggleNotesList`), list hidden by default (no clutter at the door); `loadPartnerNotes` sets `#notes-count` and keeps it collapsed. Verified: note→off My Day, dated→on My Day/Action Items, ⭐→banner set.

## ★ Action Items = DATED only (2026-07-09)
`/api/customer_jobs` "actions" query (dashboard.py) now requires `['date_deadline','!=',False]` — undated notes were cluttering the customer-brain Action Items ("things I owe" = dated to-dos only). Undated notes live in the Notes list + timeline instead. See [[project_booking_portal_display_rules]] for the internal-vs-customer distinction pattern.
