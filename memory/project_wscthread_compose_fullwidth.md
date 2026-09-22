---
name: project_wscthread_compose_fullwidth
description: The shared WSCThread Texts compose box (wsc_thread.js .wsct-reply) squished the message textarea to a ~90-130px one-word-per-line column on a phone because it shared a flex row with fixed-width ✨/Email/Send buttons. Fix = textarea flex:1 1 100% + row flex-wrap so the textarea gets a full-width row and buttons wrap to a row below.
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T03:20:51.213Z
---

**WSCThread compose box full-width fix (2026-09-22, commit 12786208).** DJ hit it on his phone: Command Center → Bruce Karp (SO 265007) → Texts panel → confirmation prefill rendered the message textarea as a tiny ~90-130px column, wrapping one word per line ("Hi Bruce, it's Dan with Wind / ow & Solar Care…").

## Root cause
`static/owner/wsc_thread.js` — the shared `WSCThread` widget (used by v2_command / v2_customers / v2_inbox / v2_reeng_review, embedded via `_job_detail_panel.js`). Its reply row `.wsct-reply` is `display:flex` with four siblings: `<textarea>` + `.wsct-rw` (✨, 52px) + `.wsct-email` (📧 Email, shown only in A29 flow-mode) + `.wsct-send` (Send). Buttons are `flex:0 0 auto`; textarea was `flex:1`. In **confirmation flow-mode** the Email button shows, so the fixed buttons ate ~250px of a 390px phone → textarea got ~90px.
- **NOT `wsc_sendbox.js`** — that's a separate full-screen overlay (the "Launch Confirmation" preview sheet, textarea already width:100%). Dispatcher's report said "Launch Confirmation" but the squished box was the inline WSCThread reply row. Two different compose widgets; don't confuse them.

## Fix (2 CSS changes, lines 61 + 64)
- `.wsct-reply` → add `flex-wrap:wrap`.
- `.wsct-reply textarea` → `flex:1` → `flex:1 1 100%;min-width:0`.
Result: the textarea always takes a full-width row of its own; ✨/Email/Send wrap to a single row below. Browser-verified textarea width at sheet 360/390/620px = 328/358/588px (full-width, all buttons in one row below) at every width.

## General lesson (reusable)
A flex ROW containing a textarea/input (`flex:1`) alongside fixed-width buttons (`flex:0 0 auto`) will squish the input on a phone once the buttons' combined width approaches the viewport. For a phone compose box, put the input on its own full-width row (`flex:1 1 100%` + parent `flex-wrap:wrap`) with the action buttons below — don't rely on `flex:1` to keep it readable. See [[feedback_field_readability_sunlight]].
