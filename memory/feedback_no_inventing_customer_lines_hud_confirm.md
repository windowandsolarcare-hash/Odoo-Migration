---
name: feedback_no_inventing_customer_lines_hud_confirm
description: "Never hand-write/invent one-off customer message lines — reschedules & customer-facing changes must AUTO-QUEUE a standardized confirmation card in DJ's HUD that he presses to send. Record-only timeline entries on reschedule are wanted + should be automated."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 90c41229-811c-4085-801e-7475f63f81b9
  modified: 2026-09-23T14:37:46.592Z
---

DJ (2026-09-23): STOP inventing ad-hoc customer message lines. When Operator offered to "draft the 'moved you to Monday 8:30' text," DJ rejected it: *"that's your testimony... a line that you invented... I'm trying to get away from you inventing lines. That doesn't scale up."*

**What DJ wants instead (the scalable pattern):** when a job is RESCHEDULED (or any customer-facing change), the NEXT STEP is for the system to **auto-launch a standardized CONFIRMATION card in DJ's HUD** — he reviews it and presses "yes I agree" to send it to the customer. A normal, repeatable, DJ-approved flow — NOT a session hand-writing a one-off text. (For a job close to its date, DJ just takes the existing 3-day/4-day HUD confirm instead — same principle, he presses to send.)

**Two distinct things — keep them straight:**
1. The record-only TIMELINE entry on reschedule (`source='system'`, label `reschedule`, "Rescheduled to Mon Sep 28") — DJ AGREES this is important and WANTS it, and wants it **automated**. It IS automated: `/api/schedule/reschedule` → `thread_reschedule_result` (append_inbox_event, index=False) auto-creates it. Operator did NOT hand-write it — DJ bet it was automated, and it was. Good. (Its blue-"sent-bubble" styling is a SEPARATE UX bug — flagged: record-only should render as a muted internal log, not a delivered "You" text. See the inbox-thread render fix.)
2. The customer-facing CONFIRMATION text — must come from a standardized HUD-queued, DJ-pressed flow, NEVER a session's invented line.

**★ GOLD STANDARD for ALL HUD approval/confirmation cards (DJ 2026-09-23, applies fleet-wide — "everybody should know this"):** a HUD card's Approve button must **NEVER one-tap-fire the text**. DJ saw a card that "when I press, it does nothing but launch the text — that's not the kind of approval I want." The Approve action must **OPEN the customer's THREAD with the message PRE-POPULATED**, so DJ (a) sees the previous messages / full context, (b) confirms everything is coordinated + in line, (c) can modify it freely, (d) then presses SEND in the thread himself. *Only then* is it sent, and only then does he know it went. *"That's the gold standard of how HUD cards should be made."* The mechanism already exists: the inbox deep-link `/static/owner/v2_inbox.html?open=<pid>&draft=<urlenc>` (Operator's cards already use it — e.g. Glenn's). Every customer-message card must use it; audit existing approve-to-send cards (reminders confirm, offers/send, etc.) to conform — approve OPENS the prefilled thread, never a direct send.

**Why:** scale + trust. Every customer touch must be a standardized, DJ-approved flow, so it works the same every time across the whole business — not dependent on what a session happens to type. And DJ must always review-in-context + edit before anything reaches a customer — a bare "approve = send" gives him no thread context and no edit.

**How to apply (Operator):** never offer to "draft a text" for a customer-facing change. Instead, ensure the change QUEUES the proper HUD confirmation for DJ to press-send; if that flow doesn't exist yet, route it to Lead as a feature. Ties to [[feedback_dj_operating_instincts]] (review-then-send, one-push) and the customer-send governance ([[feedback_email_draft_first_always]], HUD-press rule). Gap routed 2026-09-23: reschedule should auto-queue an immediate HUD reschedule-confirmation card (today it only re-fires the 4-day confirm batch).
