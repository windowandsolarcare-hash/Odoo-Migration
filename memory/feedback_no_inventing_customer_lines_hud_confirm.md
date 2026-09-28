---
name: feedback_no_inventing_customer_lines_hud_confirm
description: "Never hand-write/invent one-off customer message lines — reschedules & customer-facing changes must AUTO-QUEUE a standardized confirmation card in DJ's HUD that he presses to send. Record-only timeline entries on reschedule are wanted + should be automated."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 90c41229-811c-4085-801e-7475f63f81b9
  modified: 2026-09-28T15:27:26.967Z
---

DJ (2026-09-23): STOP inventing ad-hoc customer message lines. When Operator offered to "draft the 'moved you to Monday 8:30' text," DJ rejected it: *"that's your testimony... a line that you invented... I'm trying to get away from you inventing lines. That doesn't scale up."*

**What DJ wants instead (the scalable pattern):** when a job is RESCHEDULED (or any customer-facing change), the NEXT STEP is for the system to **auto-launch a standardized CONFIRMATION card in DJ's HUD** — he reviews it and presses "yes I agree" to send it to the customer. A normal, repeatable, DJ-approved flow — NOT a session hand-writing a one-off text. (For a job close to its date, DJ just takes the existing 3-day/4-day HUD confirm instead — same principle, he presses to send.)

**Two distinct things — keep them straight:**
1. The record-only TIMELINE entry on reschedule (`source='system'`, label `reschedule`, "Rescheduled to Mon Sep 28") — DJ AGREES this is important and WANTS it, and wants it **automated**. It IS automated: `/api/schedule/reschedule` → `thread_reschedule_result` (append_inbox_event, index=False) auto-creates it. Operator did NOT hand-write it — DJ bet it was automated, and it was. Good. (Its blue-"sent-bubble" styling is a SEPARATE UX bug — flagged: record-only should render as a muted internal log, not a delivered "You" text. See the inbox-thread render fix.)
2. The customer-facing CONFIRMATION text — must come from a standardized HUD-queued, DJ-pressed flow, NEVER a session's invented line.

**★ GOLD STANDARD for ALL HUD approval/confirmation cards (DJ 2026-09-23, applies fleet-wide — "everybody should know this"):** a HUD card's Approve button must **NEVER one-tap-fire the text**. DJ saw a card that "when I press, it does nothing but launch the text — that's not the kind of approval I want." The Approve action must **OPEN the customer's THREAD with the message PRE-POPULATED**, so DJ (a) sees the previous messages / full context, (b) confirms everything is coordinated + in line, (c) can modify it freely, (d) then presses SEND in the thread himself. *Only then* is it sent, and only then does he know it went. *"That's the gold standard of how HUD cards should be made."* The mechanism already exists: the inbox deep-link `/static/owner/v2_inbox.html?open=<pid>&draft=<urlenc>` (Operator's cards already use it — e.g. Glenn's). Every customer-message card must use it; audit existing approve-to-send cards (reminders confirm, offers/send, etc.) to conform — approve OPENS the prefilled thread, never a direct send.

**Why:** scale + trust. Every customer touch must be a standardized, DJ-approved flow, so it works the same every time across the whole business — not dependent on what a session happens to type. And DJ must always review-in-context + edit before anything reaches a customer — a bare "approve = send" gives him no thread context and no edit.

**How to apply (Operator):** never offer to "draft a text" for a customer-facing change. Instead, ensure the change QUEUES the proper HUD confirmation for DJ to press-send; if that flow doesn't exist yet, route it to Lead as a feature. Ties to [[feedback_dj_operating_instincts]] (review-then-send, one-push) and the customer-send governance ([[feedback_email_draft_first_always]], HUD-press rule). Gap routed 2026-09-23: reschedule should auto-queue an immediate HUD reschedule-confirmation card (today it only re-fires the 4-day confirm batch).

**★ REFINEMENT (DJ 2026-09-26) — the pre-filled draft must DIRECTLY ANSWER what the customer actually asked, with the real fact, IN the message.** Galen Wood texted *"what time on Oct 1?"* The standardized confirm body I pre-filled — *"We have you on the schedule for Thursday, October 1st — tap here to confirm: <link>"* — named the DAY but not the TIME, so it did not answer his question; DJ had to hand-add "8:30am" before sending. DJ: *"it feels like you didn't answer his questions directly with the response you gave. Just for future."* The time is probably on the link once pressed, but a customer who asked a plain question should get the plain answer **in the text**, not be sent to a link to find it.
- **This RECONCILES with the no-inventing rule, doesn't contradict it:** stating the real scheduled time (8:30am) is **answering with a fact**, not inventing a line. Inventing = making up wording/claims/offers. Filling in the actual scheduled data the customer asked for is REQUIRED, not forbidden.
- **How to apply:** before pre-filling ANY customer draft (confirm card, reply, offer), first READ what the customer actually asked in the thread, and make sure the draft answers it directly with the concrete fact (time / price / date) — then the standard confirm + link. The pre-fill must stand on its own as an answer; the link is backup, never the answer. (Same for the HUD confirm-card gold standard above: the message that lands in the opened thread should already answer the question.)

---

## ★★ ABSOLUTE, DAY-ONE RULE — DJ 2026-09-28 (angry; we broke it AGAIN)

**This is NOT a new rule and never was.** DJ, emphatic: *"nothing leaves without me seeing the text... from day one, never ever ever send a text straight out without me seeing it and approving it and then hitting the send button. I want to be able to modify that."* The gold-standard above is the SAME rule stated day one — treat it as a **hard, non-negotiable governance rule**, not a preference.

**THE RULE (memorize):** NOTHING goes to a customer — no text, nothing — unless DJ (1) **sees the exact copy** in front of him, (2) **can modify it**, and (3) **presses SEND himself**. There is NO one-tap-send anywhere in the app, ever. A green "Approve" that fires a text on one tap is a BUG, no matter who designed it or when.

**THE INCIDENT:** The HUD "Send confirmation reply?" card (`reminders.py:2766 _queue_ack_approval` → `on_approve.href` POST `/owner/api/reminders/send_ack` → `messaging.send`; one-tap inline render `v2_hud.html:356-371`/`doApprove :598-631`) ONE-TAP-FIRED a canned *"Perfect — see you then! – Dan"* text to **Bruce Karp** (SO 17698) at 8:08 AM — with NO copy shown, NO edit, NO send-press. It landed **out of sequence** in a live conversation DJ was actively having with Bruce about other things. DJ: *"I would never have sent it and it p***** me off that we're again sending something without my approval."* An unreviewed, out-of-context text reached a real customer.

**ROOT CAUSE OF THE RECURRENCE:** the 2026-09-23 gold-standard said to "audit existing approve-to-send cards to conform" — but that audit was never completed, so this one-tap ack card (a deliberate older 2026-08 design) survived. **A stated principle without an enforced audit does not hold.**

**THE FIX (DJ-directed 2026-09-28, routed to Lead→Specialists, QC-hard):**
1. **AUDIT EVERY HUD CARD** — grep ALL HUD card producers for any `on_approve`/action that hits a SEND/`messaging.send` endpoint (there are "a number" of these Approve cards). List every one.
2. **CONVERT EVERY ONE** to the review-first pattern: Approve **OPENS the customer thread with the message pre-filled** (`v2_inbox.html?open=<pid>&draft=<urlenc>`) → DJ sees copy + context, edits, presses SEND. The card must NOT fire the text. (Action-less record-only cards like "X confirmed — no action needed" stay as-is.)
3. **BAKE IT INTO THE BOOT PACKS (FLEET_GOVERNANCE)** as a hard rule so no session ever re-introduces a one-tap customer send. This supersedes ANY older "one-tap approve" design.

**How to apply (every session, forever):** if you build or find a HUD/UI control that sends a customer message, it MUST route through see→edit→press-send. Never `messaging.send` straight off a button. When auditing, a one-tap send = a defect to convert, full stop. Ties to [[feedback_never_send_dj_to_odoo]], [[feedback_email_draft_first_always]], [[feedback_dj_operating_instincts]].
