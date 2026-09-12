---
name: project_job_detail_shared_panel
description: "The field job-detail panel (money/timer/photos/so_full/notes/confirm) is now a SHARED component static/owner/_job_detail_panel.js (carved verbatim from v2_field.html), driven by a host CONTEXT via WSCJobDetail.mount(ctx). v2_command opens it IN-PLACE as an iframe overlay of v2_field behind ?inplace=1. Staged build \"B\"."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T18:12:20.590Z
---

**Built 2026-09-12 (staged, "B": Command Center → job detail in-place, kill the "Field Day" page-jump).** Scope doc: `3_Documentation/JOB_DETAIL_INPLACE_SCOPE.md`; gate-1 inventory: `JOB_DETAIL_INPLACE_GATE1_INVENTORY.md`.

## The shared component
- **`static/owner/_job_detail_panel.js`** — the entire job-detail panel JS (openJob/openJobById, all MONEY: doPayment/stripe link+poll+resume/charge-at-door/zelle/send-invoice; TIMER: start/stop/edit/log; PHOTOS; so_full editor; notes; confirm/ack/sched; brain-row) — **carved BYTE-FOR-BYTE** from v2_field.html (Gate 2a; diff-verified byte-identical). Loads via `<script src>` in the SAME global scope as its host (before the inline scripts), so shared globals/helpers resolve.
- **Host CONTEXT (Gate 2b):** the panel's 8 schedule "seams" route through `WSCJobDetail.mount(ctx)`. `ctx = { getScheduleJob(soId), scheduleDays()->[{date,jobs}], refresh(), onReturn(), onPaid(soId), clockedIn(), inplace }`. Helpers `_jdctx()/_jdRefresh()/_jdReturn()/_jdScheduleDays()` centralize access with safe fallbacks. **Money/timer POST logic is byte-unchanged** — only host-coupling (loadField/.jrow/pastDaysData/_returnToOrigin/clock globals) became ctx calls. `.jrow` selection toggles were left (null-safe no-ops off the field page).
- **v2_field.html** mounts a ctx that replicates its original behavior exactly (getScheduleJob = today/future/past array search; onPaid = past_jobs→pastDaysData→_returnToOrigin; clockedIn = _fieldClockedIn||_crewSetToday) → behaves identically. Keeps its own #jobwrap markup + CSS.

## v2_command in-place (Gate 3) = IFRAME OVERLAY (not a DOM merge)
- Why iframe, not inject-the-markup: the panel's CSS uses GENERIC classes (.card/.btn/.sheet/.sheet-bg/.row/.chip/.pill/.dot) that COLLIDE with v2_command's own styles — hand-scoping a money-panel stylesheet was judged too risky. The iframe reuses v2_field natively → zero CSS/markup lift, zero collision (separate document), still single-source.
- **`v2_command.html?inplace=1`**: a job tap opens a fixed overlay (top:36px, z-index 600, allow="camera;microphone", same-origin) containing `<iframe src="v2_field.html?inplace=1&open_so=<id>">`. A's fast-open shows the job instantly; the day-load defers in the iframe; Command Center underneath is untouched (no rebuild). **WITHOUT ?inplace=1 → unchanged navigation to v2_field** (real users until the Gate-5 cutover; one-flag flip, revertible).
- **postMessage protocol (origin-checked, same-origin):** in `?inplace=1`, v2_field's `_returnToOrigin`/`ctx.onReturn`/panel `apBack` post `{type:'wsc-jd-close'}` → parent hides overlay + sets iframe `src=about:blank` (stops timers/camera/polls). `ctx.onPaid` posts `{type:'wsc-jd-paid',so_id}` (after ~1.2s so "✅ Paid" shows) → parent closes + refreshes CC (DATA.on=null + _ccRerender). Phone Back: opening pushes a history state; popstate closes the overlay.

## Gotchas learned
- A mechanical `replace_all('_returnToOrigin();','_jdReturn();')` created an **infinite recursion** in `_jdReturn`'s own fallback (it called itself). node --check passes it (valid syntax) — review caught it. Watch replace_all hitting a helper that contains the replaced token.
- Stale mirror: the read-only clone drifts behind your OWN mid-session pushes — re-fetch live before editing (the inbox pagination was nearly clobbered this way).

## Status / remaining
- Gates 2a (carve), 2b (ctx seam, v2_field identical), 3 (iframe overlay behind ?inplace=1) = LIVE + QC-passed (2a/2b) / awaiting Gate-4 QC (3).
- **Gate 4** (Lead + Auditor): full money/timer/photos walk from `v2_command.html?inplace=1` before cutover.
- **Gate 5** (cutover): make in-place the default (drop the ?inplace=1 gate on rowTap); then v2_field's inline panel markup/CSS could be retired (optional "pure single-DOM" pass). Legacy V1 field.html + ql_panel retirement is separate.

Related: [[project_field_deeplink_return_latch]], [[feedback_never_remove_working_code]].
