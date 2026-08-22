---
name: project_v2field_deeplink_open_flash
description: v2_field.html deep-link open (from Command Center card) flashed the ⭐ next-visit banner ~3x and jumped scroll to top — openJob ran multiple times (skeleton + so_history). Guarded both.
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-23T06:57:55.215Z
---

**2026-07-22 (DJ, customer Kristen, on the NEW screens).** Tapping a job card in Command Center (`v2_command.html` → `rowTap` → `location.href=/static/owner/v2_field.html?open_so=<id>`) landed on the job detail and the big ⭐ "Heads up for this visit" banner appeared → flashed gone → came back ~3 times, each cycle yanking scroll back to the TOP while DJ read info further down.

## Why (this is a DIFFERENT path than [[project_field_refresh_rerenders_open_job]])
That earlier fix covered the 5-min **refresh** path (`_applyFieldData`, which already does a surgical repaint, NOT full openJob). This bug is the **deep-link OPEN** sequence in `boot()`:
1. Line ~3034 `openJob(_ho,false)` — instant SKELETON paint from the Command Center sessionStorage handoff (`wsc_job_handoff`).
2. Line ~3037 `openJobById(so0)` — at boot `jobs` is empty (loadField runs AFTER, ~3041), so it falls to the `so_history` fetch branch (~L1807) and calls `openJob(...)` AGAIN with full data.

Every `openJob()` unconditionally: (a) calls `loadNextVisitNote(pid)` (~L1727) which does `display:none; innerHTML=''` → fetch → show = the visible FLASH; and (b) `jb.scrollTop=0` (~L1777) = the jump to top. So skeleton→full = 2+ openJob = banner flash + scroll reset each time.

## Fix (two surgical guards, commit 8e3385d)
1. **`loadNextVisitNote(pid)`** — added module var `_nvPid`; early-return `if(pid && String(pid)===String(_nvPid)) return;` before the hide/refetch, set `_nvPid=pid` after. Same customer opened again (skeleton→full, or a background repaint) no longer re-flashes the ⭐ banner. A DIFFERENT partner still reloads.
2. **`openJob(job,scroll)`** — capture `var _wasSo=activeJob&&activeJob.so_id;` at the top (before `activeJob=job`), then only `jb.scrollTop=0` when `String(_wasSo)!==String(job.so_id)`. New job → scrolls to top (fresh open, openNextJob). Same-job re-render (skeleton→full) → preserves scroll.

## How to apply
Any screen that opens a detail via an instant skeleton THEN a fuller fetch must not let the second render re-flash banners or reset scroll. Guard per-partner banner loads and gate scroll-reset on "is this actually a new entity?". The `scroll` param on `openJob` is effectively dead at the scrollTop line — the `_wasSo` guard is what governs it now.
