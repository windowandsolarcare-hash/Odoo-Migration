---
name: feedback_drift_gets_a_bootpack_rule
description: "DJ 2026-10-13: every time we find a process drift, write a rule for it into the right role's boot pack. Fleet asks (anything for several roles) = post to AGENT_MAIL FIRST, then nudge each role directly."
metadata:
  node_type: memory
  type: feedback
  originSessionId: f9d25f0d-f892-4864-829e-2fda94efd70c
  modified: 2026-10-14T04:52:06.449Z
---

DJ (2026-10-13): "every time we come up with a drift we need to come up with a rule in the boot pack." Example drift: DJ's Gemini brief went to Lead by direct message only and was never posted to AGENT_MAIL, so the 8 roles never saw it; Lead then said it would collect inputs but didn't verify the mail post or nudge them. Two breaks of the post-then-nudge rule (2026-09-04): Dispatcher didn't post, Lead didn't check.

**Why:** the hybrid protocol (mail = record, direct message = nudge) only works if both halves happen every time. DJ doesn't care whether roles poll the mail on a timer; the nudge is the primary wake-up. The 20-minute watcher crons are session-local and expire after 7 days (many sessions started ~6 days ago), so they can't be relied on.

**How to apply:** (1) anything meant for several roles: write it to AGENT_MAIL first, then SendMessage each a one-line nudge pointing at it, and say in the visible reply who was nudged. (2) Whoever asks a role to act confirms the mail entry exists before saying "sent." (3) When a drift is found, add one line to that role's boot pack, not a long doc. (4) A durable server-side watcher (Render scheduler, [[feedback_durable_watcher_not_session_cron]]) is the free backup for the expiring session crons; unbuilt.
