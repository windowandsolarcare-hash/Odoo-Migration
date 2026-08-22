---
name: feedback_over_status_line
description: "End EVERY reply with a walkie-talkie status line — 🟢 <Role> — OVER when idle, 🟡 <Role> — working when not."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1cb095a1-10e5-4519-903e-c06b100b873a
  modified: 2026-08-20T08:08:30.416Z
---

**The very last line of every reply must be a status line** (DJ 2026-08-18, via Lead):

- Done and idle, channel open for DJ → `🟢 <Role> — OVER` (a few words of context are welcome:
  `🟢 Web — OVER (waiting on photo pairs)`).
- Still working, a background task is running, or more output is coming without DJ → `🟡 <Role> — working`.

`<Role>` is the session's role from the roster — Lead / Specialists / Web / Portal (see
[[project_agent_mail_channel]]).

**Why:** DJ runs several Claude sessions at once and wants to tell at a glance which ones are idle
and worth talking to, like a walkie-talkie "over". Without it he has to read a whole reply to work
out whether that session is still busy.

**How to apply:** every reply, always the last line, **including watcher ticks and one-line
answers**. 🟢 = channel open, 🟡 = stand by. Do not put anything after it.

**★ Web session only (DJ 2026-08-20): put the live site URL in the OVER line, every single
time — as a real clickable markdown link, never bare text.** Format:

`🟢 Web — OVER · [window-solar-care.odoo.com](https://window-solar-care.odoo.com/)`

DJ is on a phone and wants to tap straight through to the site without scrolling back for the
address — same reason as [[feedback_always_paste_preview_link]]. Swap the URL for
`https://wscare.pro/` once Lead completes the DNS cutover (see [[project_marketing_site_odoo]]).
