---
name: project_hiring_interview_tracker
description: Hiring page interview tracker — per-candidate status chip + Interviews day-view. Stored in ir.config_parameter hiring.interviews (NOT applicant_notes).
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-07: Added interview tracking to the Hiring ATS (`routers/owner/hiring.py` + `static/owner/hiring.html`) so the Render page keeps up with the interview process while DJ schedules the actual interviews in Indeed.

**Storage (deliberately isolated from the fragile applicant_notes marker chain):** one `ir.config_parameter` key **`hiring.interviews`** = JSON `{ "<applicant_id>": {"date":"YYYY-MM-DD","time":"10:00 AM","status":"invited"} }`. Read/write via `odoo_rpc('ir.config_parameter','get_param'/'set_param', ...)`.

**Backend endpoints (hiring.py):**
- `GET /owner/api/hiring/interviews` → the full map.
- `POST /owner/api/hiring/interview` → body `{app_id, date?, time?, status?}` merges one entry; `{app_id, clear:true}` removes it. Helper `_load_interviews()`.

**Front-end (hiring.html):**
- Global `INTERVIEWS = {}` fetched in `loadApplicants()`.
- **Interviews tab** (`tab-interviews`, filter `'interviews'`): `renderList()` short-circuits to `renderInterviewDay()` — rows grouped by date, sorted by time, name + status badge, tap → openDetail.
- **Per-candidate chip:** `#interviewBox` rendered by `renderInterviewBox(id)` inside `openDetail` (right after the stage row). Date input + time text + 5 status chips. Saves via `saveInterview(id, patch)` (optimistic local update then POST).
- Statuses: invited(gray ○) / confirmed(green ●) / done(blue ✓) / declined(red ✗) / noshow(orange ⚠) — `INTV_STATUSES`.
- **Confirmed auto-advances stage to Phone Screen (id 2)** — `setIntvStatus` calls `commitStage(id,2)` only if current stage < 2 (never demotes). Added 2026-06-08.
- **Stage move (2026-06-09 rewrite):** `updateStage(appId,stageId,btn)` is now a **two-tap confirm** (tap arms button → text "Confirm ✓" + `.stage-btn.confirm` amber; tap again commits; auto-cancels 3.5s via `_resetStageConfirm`; tapping current stage is a no-op). Actual write is `commitStage()` which refreshes the stage row FROM DATA and calls renderList + renderInterviewDay. **Root-cause fixed:** old `updateStage` did `event.target.classList.add('active')` AFTER an `await` — global `event` is cleared post-await → threw every time → "Update failed" alert + skipped renderList, so moves saved server-side but inconsistently showed. RULE: never reference the global `event`/`event.target` after an `await`; pass `this` from the onclick and re-render from data instead.

**Decision/data model recap:** candidates = `hr.applicant`, `job_id=1`. Decision (yes/maybe/no/follow-up) lives in `applicant_notes` markers — `===DECISION===` is Cheryl's, `===DJ_DECISION===` is DJ's. Stages: 1 Reviewing / 2 Phone Screen / 3 Interview / 5 Offer / 6 Hired. The 7 "Yes" = Cheryl decision yes.

**Seeded 2026-06-08:** the 7 Yes candidates (ids 151,145,136,102,141,156,109) with Wed 2026-06-10 slots 10:00–1:00, status 'invited'. See [[project_hiring_screening_messages]], [[project_hiring_ats]].

**Why:** keeps the Render hiring page in sync with the Indeed-driven interview process without touching the brittle notes parser. **How to apply:** extend statuses or day-view here; never store interview state in applicant_notes (use the config param).
