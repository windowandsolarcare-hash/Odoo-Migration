---
name: feedback_customer_sends_through_dj_hud
description: "★ NOTHING goes out to a customer until it's in DJ's HUD and DJ presses send — never direct/auto-send, even when DJ says \"get the payment\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-19T04:38:50.783Z
---

★ **Nothing gets sent to a customer without going through DJ's HUD first — DJ reviews it there and DJ presses send.** No session (Operator included) may direct-send OR auto-queue a customer-facing text/email/link to actually fire on its own. The correct pattern is always: stage it as a **pending approval card in DJ's HUD**, and DJ sends it.

**Why:** DJ 2026-09-18. Operator was routed to "re-send Bob Lis his working $200 card link" and queued it to auto-release at 8am (night-hold). DJ: "I'm surprised Operator or anybody sent that out to Bob. Nothing gets sent out to the customer without going through my HUD, and then I send it out." A queued auto-send is still a send DJ never pressed — same violation.

**How to apply:**
- **EDITABLE PREVIEW, always (DJ 2026-09-19):** every customer-facing send must present the message in an **editable box DJ can modify, then Send** — NEVER a bare Send / Send-all with no way to change the text. "That should never say send by itself... I always have the ability to modify it in a preview box, then hit send." A send-only card (e.g. the MAINT_CONFIRM 'Confirmations to send' card, A29) is a bug.
- Any customer-facing send (SMS via messaging/stripe send, email, payment/booking link) → **queue it in DJ's HUD as an approval card**, never `send` directly and never schedule it to auto-fire.
- This holds **even when DJ says "get the payment" / "send it"** — that authorizes PREPARING it for his HUD, not bypassing his press-send. When in doubt, stage → HUD.
- Dispatcher lesson: don't route "send X to the customer" as a direct send; route it as "stage X in DJ's HUD for his approval."
- Related: [[feedback_email_draft_first_always]] (emails as drafts, DJ sends), [[feedback_dj_operating_instincts]] (review-then-send), [[feedback_assistant_use_app_workflow_not_raw_api]].
