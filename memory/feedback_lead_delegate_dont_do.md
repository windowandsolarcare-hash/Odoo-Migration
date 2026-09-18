---
name: feedback_lead_delegate_dont_do
description: "★ Lead must DELEGATE the investigate→diagnose→fix to the owning session immediately, not go heads-down doing it — DJ waits on Lead's serial digging while builders sit idle. Lead stays the interface + QC gate, hands off in one move, uses background agents for quick facts."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fc82158e-3491-40c5-9546-2c3dcd81a09b
  modified: 2026-09-18T15:37:12.373Z
---

**DJ 2026-09-18 (standing correction):** "I'm waiting around for you a lot, and it's because you're choosing to do the activity rather than delegate it. They're sitting idle, I'm sitting waiting on you. I need you to delegate so it frees you up to take on the next thing, so we move through these things faster."

**The failure:** Lead was going heads-down on every reported issue — grepping code, querying Odoo, curling live checks, tracing the exact bug — and only THEN handing a polished spec to Specialists. That makes Lead the **serial bottleneck**: DJ waits on Lead's digging while the owning builder sits idle. The diagnosis quality was good, but the cost (DJ's wait + idle builders) wasn't worth it.

**The rule — Lead HANDS OFF, doesn't DO:**
1. When DJ reports an issue, identify the owner (Specialists=app code, Web=site, Portal=portal) and hand them **"diagnose AND fix"** in ONE move — they own that code and can investigate it themselves. Do NOT pre-chew the diagnosis. Turn right back to DJ for the next thing.
2. **QC is where Lead's value lands, and it's NON-BLOCKING to DJ** — it happens when the fix is ready, while DJ is already several things ahead. (Proven 2026-09-18: Lead's post-build QC still caught the sendAll double-send gap + corrected a wrong photos-fix approach — without DJ waiting on the diagnosis.)
3. **Need a quick fact** (which file is this screen, is the data intact)? Spin a **background Agent** (fork inherits Lead's context incl. screenshots; or Explore/general-purpose) so DJ isn't waiting while Lead looks — never go silent digging.
4. **No "assistant-to-Lead" session needed** — that just adds a hop between DJ and Lead. The fix is behavioral: Lead delegates the doing, stays DJ's interface + the QC gate.

**Restrictions (who can take what):** only **Operator** (execute-only, DJ's hands) and **Cheryl's cloud** (her domain) are hard-limited. Web owns the marketing site, Portal owns the customer portal, but **Specialists takes app work broadly** — route to whoever is free + capable, don't be precious about "whose place" it is (DJ explicitly OK'd this).

**Net:** DJ talks to Lead; Lead hands off in one move and is instantly free for the next thing; builders work in parallel; Lead QCs when each lands. Do not make DJ wait on Lead's keyboard. See [[feedback_escalate_to_dj_sparingly]], [[feedback_never_idle_waiting_on_dj]], [[feedback_agent_mail_autowatch]] (post-then-nudge).
