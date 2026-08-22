---
name: project_myday_done_button_stuck
description: "My Day task \"Done\" button showed \"…\" instead of \"✓ Done\" — static loading button only reset on error, fixed by resetting in openTask"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Bug:** the My Day task editor's green **Done** button (`#tkDone`, myday.html) showed **"…"** (and was disabled) instead of "✓ Done". Cause: `tkDone()` sets `btn.textContent='…'; btn.disabled=true` on click, then on SUCCESS only calls `closeTask()`/`load()` — it never resets the button (only the ERROR branch resets to "✓ Done"). `#tkDone` is a STATIC HTML button that persists across editor opens, so after one successful mark-done it stayed "…"+disabled for every subsequently-opened task.

**Fix (commit ecf0295, 2026-07-11):** reset it in `openTask` alongside the display-restore — `$('tkDone').disabled=false; $('tkDone').textContent='✓ Done';`. (The Skip button `#tkSkipBtn` doesn't have this bug — it's re-created fresh in `renderActionZone` each open.)

★ **Reusable gotcha:** any STATIC button that shows a transient loading label (`'…'`, `'Saving…'`) and only resets on error will get stuck after a success-path that closes/navigates instead of resetting. Reset such buttons when the container/editor (re)opens, or reset on both success AND error. Dynamically-recreated buttons are immune.
