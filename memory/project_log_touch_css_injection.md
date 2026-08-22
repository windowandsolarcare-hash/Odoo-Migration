---
name: ""
metadata: 
  node_type: memory
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

The "📣 Log a touch" button on the **field.html job-detail screen** (History card, bottom-right of the row at ~L1135, `onclick="if(activeJob)outShowLog(activeJob.partner_id)"`) appeared to do nothing when tapped.

**Root cause:** the outreach sheet's CSS (`.out-ov`, `.out-sheet`, `.out-kind-row`, `.out-btn`, etc.) is injected lazily by `_outInjectCSS()` (guards on `#out-css`). That function was ONLY called from `loadOutreachStrip()` (the Customer Brain outreach strip). `outShowLog()` → `_outSheet()` never called it. So opening the sheet from the job detail created `<div class="out-ov show">` with **no matching CSS** → no `position:fixed`, no z-index, no background → the modal was effectively invisible. It "worked" from Customer Brain only because `loadOutreachStrip` had run there first and injected the CSS as a side effect.

**Fix (2026-07-10, commit e87c5a1):** call `_outInjectCSS()` at the top of `_outSheet()` — the single choke point every outreach sheet passes through. Idempotent, so safe.

**Why:** the same unified "Log a touch" sheet (`outShowLog`/`_outSheet`, POST `/owner/api/touch`) is reachable from two entry points; only one injected its styles.

**How to apply:** any feature that lazily injects its CSS/DOM via a helper must call that injector at the modal-open choke point, NOT only from one render path. If a modal "does nothing" from one screen but works from another, suspect side-effect-injected CSS that never ran on the broken screen. See [[project_job_note_vs_task]].
