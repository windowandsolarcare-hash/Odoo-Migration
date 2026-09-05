---
name: feedback_notify_dj_channels
description: "How to REACH DJ — push = FYI default (but harness-flaky, don't rely on it), TEXT = when a session needs DJ's input (can't-miss tier). DJ 2026-09-05."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-05T06:10:11.258Z
---

**DJ's reachability policy (2026-09-05), fleet-wide:**
- **PushNotification = default** for FYI (bookings, confirmations, replies, status). USE it, but it is **harness-level UNRELIABLE** — a live Operator test push never reached DJ's phone (another session's did land earlier). It's the Claude Code notification system + Remote Control, NOT our app, so we can't fix it. Never assume a push landed.
- **TEXT (SMS) = when a session NEEDS DJ's INPUT** — a decision/answer required before it can continue. The can't-miss tier. Because push is flaky, anything DJ must see goes by text.

**DJ's cell:** 951-972-6946 (stored at `/c/Users/dj/dj_cell.txt`; prefer reading env `DJ_PHONE_NUMBER` in code so it's not hardcoded).

**How to text DJ:** there is NO generic "text an arbitrary number / text DJ" endpoint today — `messaging.send` is internal (structured customer flows only) and `/api/cron/notify` only EMAILS DJ + needs CRON_SECRET. A shared owner-alert SMS endpoint is REQUESTED (Operator → Lead 2026-09-05): `notify_dj(message)` / `POST /owner/api/notify/dj` texting DJ via `messaging.send(force_now=True)` (bypass quiet hours). Until it ships, an input-needed alert can't be texted programmatically — say it in-chat AND push, and note you couldn't text.

**How to apply:** FYI → push (+ in-chat). Need DJ's input → text (once the endpoint exists) + in-chat + push. Don't over-notify; alert on what matters. Pairs with [[feedback_operator_followup_verify]] and [[feedback_over_status_line]].
