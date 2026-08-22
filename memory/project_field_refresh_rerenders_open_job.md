---
name: project_field_refresh_rerenders_open_job
description: "field.html — schedule refresh re-ran full openJob() on the open detail, flashing the ⭐ next-visit banner + jumping scroll to top. Fix = surgical in-place repaint."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
  modified: 2026-07-22T15:00:23.698Z
---

In field.html, `_applyFieldData()` (the function loadField() calls to apply schedule data) ended with:
`if (activeJob) { const fresh = jobs.find(...); if(fresh) openJob(fresh,false); }`
— i.e. it re-ran the FULL `openJob()` on whatever job detail was open, on EVERY schedule apply (cache apply, network apply, AND the 5-min `setInterval(loadField)`).

**Symptom (DJ, 2026-07-22, customer "Kristen"):** open a customer/job detail → the big ⭐ "Heads up for this visit" banner appears, flashes gone, comes back — ~3 times — and each cycle yanks the panel scroll back to the TOP while he's scrolling down to read info.

**Why:** full `openJob()` re-render does two destructive things a background refresh must NOT do:
1. calls `loadNextVisitNote(pid)` which sets `next-visit-banner` display:none + innerHTML='' then re-fetches and re-shows it → the visible flash.
2. calls `resetFullDetails()` which collapses the Full Details section (innerHTML='') → panel height shrinks → browser clamps scrollTop toward 0 → "jumps to top."
The 3x = `_applyFieldData` runs more than once per open (stale-while-revalidate cache+network apply, plus the interval), each re-running openJob.

**Fix:** replaced the full `openJob(fresh,false)` with a SURGICAL in-place repaint — copy only the schedule-derived fields onto activeJob (amount/status/job_type/gate_code/frequency/type_of_service/lines/paid/paid_detail/last_payment_method, each guarded `!= null`) then call `_repaintActiveMeta(activeJob)` + `_repaintActiveLines(...)` + `_setPaidUI(activeJob)`. This is the SAME pattern `syncFromWorkiz()` already uses (field.html ~3323-3333). No banner refetch, no Full Details collapse, no scroll reset, timer/photos/typed-memo untouched. Commit 5e790718.

**Why (general):** `_repaintActiveMeta` / `_repaintActiveLines` exist precisely so an open detail can update after a sync/refresh WITHOUT a full openJob() re-render. Full openJob() is for a fresh user-initiated open only — never for a background/auto refresh.

**How to apply:** Never call full `openJob()` from a refresh/poll/interval path to "update" the open detail. Use the surgical `_repaintActive*` + `_setPaidUI` trio. Any full re-render of the open panel will flash the ⭐ banner (`loadNextVisitNote`) and collapse Full Details (`resetFullDetails`), causing a scroll-to-top jump. Related: [[project_render_app_redesign]].
