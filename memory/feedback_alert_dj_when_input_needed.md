---
name: feedback_alert_dj_when_input_needed
description: "When a session genuinely NEEDS DJ's input mid-task (a real decision / a question awaiting his pick+submit), ALERT him via the needs-you banner/notify — never just pose the question and wait silently. DJ 2026-09-09."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-09T22:50:11.721Z
---

DJ 2026-09-09: the exact moment a session is waiting on him to pick from options and hit submit (e.g. an AskUserQuestion-style 4-option prompt) is the moment the **needs-you banner** was built for — so DJ isn't the silent bottleneck. He gets pinged in a banner, taps it, it takes him back to that session to answer + submit, to EXPEDITE things so the session isn't stalled. In the incident that prompted this, a session left him waiting at a decision point and fired NO banner.

**Why:** DJ is in the field; a question posed in-chat with no alert can sit unseen for a long time while the session idles. The point of the alert is to close that gap and keep work moving.

**How to apply (Operator):** when I hit a point where I genuinely need DJ's decision to proceed (a real fork I can't resolve — see [[feedback_raise_bar_on_dj_alerts]]: only for things I truly can't decide), don't just ask and go quiet — surface a **needs-you alert** (a HUD attention card via feed/submit, and/or text him for a must-see input per [[feedback_notify_dj_channels]]) so he's pinged and can jump back to answer. This does NOT conflict with the raise-the-bar rule: that governs WHETHER to involve him (rarely); THIS governs, once I legitimately do, making it VISIBLE instead of a silent wait. And keep working other tasks while waiting ([[feedback_never_idle_waiting_on_dj]]). The banner→back-to-session→answer+submit flow is the product mechanism DJ wants for this; until it's fully wired, a HUD card + text is the stand-in.
