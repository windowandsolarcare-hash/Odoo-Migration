---
name: feedback_post_then_nudge_every_bootpack
description: "POST-THEN-NUDGE is standing procedure for EVERY role/boot pack — write to mail, then directly nudge the agent to read it."
metadata:
  node_type: memory
  type: feedback
  originSessionId: e025c990-f5b0-4a94-874c-5016d12b0b5a
  modified: 2026-10-20T17:19:39.713Z
---

DJ 2026-10-20: POST-THEN-NUDGE is **how the whole fleet operates, every time** — not a Dispatcher-only or occasional step. For any cross-session handoff: **(1) write the item in `AGENT_MAIL.md` (durable record), then (2) IMMEDIATELY nudge the target agent(s) with a direct `SendMessage` telling them to go read their mail NOW** — do not wait for their next watcher tick. The mail is the system of record; the direct nudge is the wake.

DJ's words: "we write things in the mail, and then we nudge the fleet to look at their mail — make sure everybody is clear on that."

**Why:** idle sessions don't take a tool round until woken; a mail entry alone can sit unread for a full watcher interval (or forever for a watcher-less on-demand role). The direct nudge converts "eventually" into "now." DJ saw the old Dispatcher lock up / items stall waiting on ticks.

**How to apply:** this must be codified VERBATIM into EVERY role boot pack (`3_Documentation/roles/*.md`) + `FLEET_GOVERNANCE.md` — a rule that lives only in mail/memory DIES at spin-up (FLEET_GOVERNANCE principle). Routed to Lead 2026-10-20 to propagate. On name collision in `SendMessage`, use the on-this-machine `[ref]`. Ties to [[feedback_agent_mail_autowatch]] (post-then-nudge + roster) and [[feedback_drift_gets_a_bootpack_rule]] and [[project_agent_mail_channel]].
