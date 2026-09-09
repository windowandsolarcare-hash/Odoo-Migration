---
name: feedback_escalate_to_dj_sparingly
description: "Only reach out to DJ (→ DJ mail / PushNotification / \"needs you\" alert / in-chat question) when it's REALLY needed; otherwise make the call yourself. Raise the bar on session→DJ interruptions."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-09T14:43:12.863Z
---

DJ 2026-09-09: "it should only reach out to me if it's really needed. otherwise you make the call."

**The rule:** default to DECIDING, not asking. A session reaches DJ only when the thing GENUINELY requires him:
- a decision only he can make (priorities, business facts/content only he knows, a real fork with no sensible default),
- money-touching or customer-facing actions,
- something truly BLOCKED that no session can resolve.

Everything else — routine choices, things with an obvious default, cross-stream/architecture/QC calls — the session makes the call itself (Lead owns cross-stream + architecture; each role decides within its scope). This is a HIGHER bar than the old "ask DJ directly" reflex: asking-directly is still right *when the question is really his*, but most things aren't, and each interruption has a cost.

**Applies to:** the `dj_alerts`/`notify_dj` "needs you" banner (sessions posting questions to DJ), `PushNotification`, `→ DJ` AGENT_MAIL entries, and in-chat questions. Prefer to act + report briefly over stopping to ask. When you DO decide something that was borderline, say so in one line ("made X call, flag if wrong") rather than asking first.

**Why:** DJ is often in the field and doesn't want a stream of prompts; a needless interruption annoys in a way that accumulates. He explicitly trusts the sessions to run things and only wants the genuinely-needs-DJ items to surface. Pairs with [[feedback_never_idle_waiting_on_dj]] (park non-blocking DJ items, keep building) and [[feedback_notify_dj_channels]] (how to reach him when it IS needed). Do NOT relitigate a decision once DJ has made it ([[feedback_dj_owns_cheryl_erp_access]]).

**How to apply:** before posting a → DJ alert or asking DJ a question, ask "can I decide this myself with a sensible default?" If yes, decide, do it, report in one line. If it's truly his (money/customer-facing/only-he-knows/hard-blocked), then surface it — concisely.
