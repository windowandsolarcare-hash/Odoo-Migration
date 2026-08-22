---
name: feedback_disable_pull_to_refresh
description: "EVERY page/app must disable mobile pull-to-refresh and have a manual refresh button — a stray pull reloads the SPA and wipes state, which DJ hates."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3bc8d84-66ee-4ee9-b6c2-8cd69a165d04
---

**RULE (DJ, emphatic, 2026-06-22): mobile pull-to-refresh is BANNED on every page/app, and every page needs a manual Refresh button instead.**

**Why:** DJ works one-handed on a phone in the field. Pulling down to scroll to the top of a screen triggers Chrome's pull-to-refresh → the single-page app fully reloads → all in-memory state is lost and he's dumped back to the previous screen mid-task. He called it "a ball buster… awful" and wants it stopped permanently going forward, not page-by-page after he hits it.

**How to apply (do this on EVERY new owner/field/cheryl/HR page, no exceptions):**
1. CSS: `html, body { overscroll-behavior: none; }` — kills pull-to-refresh (and overscroll glow). `overscroll-behavior-y: contain` also works but use `none` to be safe (DJ still hit it with `contain` once).
2. Add a manual **Refresh button** (↻) in the header that RE-RUNS THE CURRENT VIEW'S DATA LOAD (e.g. re-call the loader for whatever view is open) — NOT `location.reload()` (that's the very full-reload we're avoiding and also loses state). Pattern: a `refreshView()` that branches on the current view state and calls the right loader.

**Status (2026-06-22):** field.html had it (`contain`, now upgraded to `none`); common.css now has it (covers command center/schedule_hub + all report/owner pages that link it); hr.html has it + a refresh button + sheet `max-height:92vh;overflow-y:auto` (a too-tall bottom sheet pushed the first field off-screen — always cap sheet height + internal scroll). NEW pages NOT using common.css must add the rule themselves.

**2026-07-20 update:** `overscroll-behavior-y:contain` on body is NOT enough — DJ's Samsung browser still fired pull-to-refresh (killed the Job history sheet on the Job Screen, reloaded to the wrong view). The only proven pattern is v1's: `html,body{overscroll-behavior:none}` — BOTH elements, value `none`. All 39 v2 pages swept 2026-07-20. Inner scrollers keep their own `overscroll-behavior:contain` (that part is fine/desired).
