---
name: project_wsc_sendbox_shared
description: "wsc_sendbox.js = the ONE shared scheduling/confirmation send-box widget. WSCSendBox.open({so_id,mode}). Every reschedule/confirm entry point should reuse it instead of copying _openSendBox."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T10:11:32.821Z
---

**`static/owner/wsc_sendbox.js`** (created 2026-08-07) — the shared "send a scheduling/confirmation text" preview box, promoted from v2_field's `_openSendBox` so we stop duplicating it (rule #9). Self-contained (own esc/toast/fetch, theme-aware with fallbacks, no deps).

**API:** `WSCSendBox.open({ so_id, mode, toName, onSent })`
- `mode`: `'schedule'` (branded pick-a-time page) | `'confirm'` (branded `?c=1` confirm page).
- It self-fetches the preview from `POST /owner/api/sched/launch {so_id,mode,send:false}`, shows the branded editable preview + **✨ Let AI tailor it** (`POST /owner/api/sched/ai_message {so_id,mode,current}`), and sends via `POST /owner/api/sched/launch {so_id,mode,send:true,message}`. Held→8am aware; `onSent(result)` optional callback.
- Include on the page: `<script src="/static/owner/wsc_sendbox.js?v=1"></script>`.

**Wired so far:**
- **specialist_reschedule.py** (HUD "Jobs to reschedule → Pick the best day" review): `submitJobRs` now, after a successful reschedule, calls `WSCSendBox.open({so_id, mode:_dOut>14?'schedule':'confirm'})` (2-week date-smart). Fixed GAP#2 (that flow used to reschedule + clear with NO send offer).

**STILL TO DO (noted, not urgent):**
- Repoint **v2_field.html** `_openSendBox`/`schedLaunch` to WSCSendBox so there's truly ONE implementation (v2_field still has its own copy = temporary duplication). Deliberate pass + retest (v2_field is a collision-prone file).
- **Lead** owns wiring the HUD 4-day-confirm + night-before approval cards to `WSCSendBox.open` (gives DJ the ✨ AI-tailor send on those cards). Mailed.

Context: the 2-week date-smart rule (`_dOut>14?'schedule':'confirm'`) is the post-reschedule auto-choice; the manual job-detail "✅ Send confirmation" button is explicit confirm. See [[project_sched_lifecycle_one_page]].
