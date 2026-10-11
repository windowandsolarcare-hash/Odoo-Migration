---
name: project_needsyou_banner_dismiss_and_overlap
description: "Thumbtack-leads banner (v2_needsyou_banner.js): bar ✕ with >1 lead used to only OPEN the list (never dismissed → 'kept coming back'). Fixed: ✕ now persistently banner-dismisses (localStorage wsc_ny_bardismiss). Also v2_job offsets its fixed panel below the banner (body.wsc-ny-shown)."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T07:20:20.182Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy"; Lead QC-GREEN). DJ via Dispatcher (screenshot, Myra Lane job screen): "2 Thumbtack leads" banner covered the job header + ✕ wouldn't stick.**

**Root cause (X doesn't stick):** `onBarX` in `static/owner/v2_needsyou_banner.js` — with >1 lead the bar ✕ did NOT dismiss, it only toggled the list open (`OPEN=!OPEN`). DJ's banner read "2 leads" so every ✕ tap acked nothing → always back. (Per-lead dismiss persists fine: the TT LEAD card's `created` = stable lead-arrival time, and `_merge_live_card` honors terminal 'done' by id — server side was correct.)

**Fix (client-only):** added a localStorage-backed BANNER-level dismissal `wsc_ny_bardismiss` (`_supGet/_supSet/_vis/_supPruneToLive/_supDismissShown`). Bar ✕ with >1 lead → `_supDismissShown()` suppresses the banner for the leads SHOWN — they STAY in the HUD (NOT a terminal lead-dismiss; honors "never silently drop a real lead"), bar stays gone across refreshes, and returns when a genuinely NEW lead id appears (`_supPruneToLive` drops suppressions for leads no longer live, run each refresh). Single-lead ✕ = unchanged true-dismiss (`op:'done'`); ⏰ snooze + per-row list ✕ unchanged. paint/paintList/onBar* operate on `_vis()` (ALERTS minus suppressed).

**Overlap fix (DJ picker "also move the job screen down"):** banner `paint()` toggles `body.wsc-ny-shown` while shown. `v2_job.html` adds a class-gated CSS rule `body.wsc-ny-shown #jobwrap, body.wsc-ny-shown #wsc-opening{top:80px}` (banner top:36px + height:44px = 80px). The job detail is `position:fixed; inset:0` so body-padding can't move it — offsetting the fixed panel's top is the fix; ZERO offset when the banner is absent. The shared banner's position is NOT changed (Lead ruling: don't fragment the shared include / re-open the top:36px class fleet-wide). Cosmetic non-blocker: on v2_job the clock-in bar is at the BOTTOM, so the banner floats ~36px below the top edge.
