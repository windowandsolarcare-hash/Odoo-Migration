---
name: project_confirm_ack_review_first
description: "GOVERNANCE (DJ day-one absolute): NO customer text sends on a one-tap HUD approve. The confirm-ack card (reminders.py _queue_ack_approval) one-tap-fired 'see you then' to a customer unreviewed (Bruce, 2026-09-28) → converted to review-first + send_ack neutralized. Covers the exact HUD mechanism that makes a card one-tap-send vs navigate-only."
metadata:
  node_type: memory
  type: project
  originSessionId: 7f93eb62-ab56-4528-a75a-3a6b108e7612
  modified: 2026-09-28T15:58:24.410Z
---

**Shipped + live 2026-09-28 (deploy 84215bb4, DJ-triggered, Lead QC-hard green). Files: `routers/owner/reminders.py`.** DJ's day-one ABSOLUTE: nothing goes to a customer without DJ SEEING / EDITING / pressing SEND. The confirm-ack card violated it — a one-tap Approve fired the outbound "see you then" text to a customer unreviewed.

## The HUD mechanism (how a card becomes one-tap-send vs navigate-only) — the reusable fact
In `v2_hud.html`: `doApprove` REQUIRES `it.draft.on_approve.href` (else "no approve action"), and the inline ✅ Approve button ONLY renders when `it.draft && it.draft.on_approve.href && !it.draft.editable` (the `inlineOK` check). So:
- A card with **`draft.on_approve` (POST href)** → renders an Approve button → ONE TAP fires that POST. If that endpoint calls `messaging.send`, it's a one-tap customer send = a governance violation.
- A card with **NO `draft.on_approve`**, just **`action:{label, href}`** → `inlineOK=false`, no Approve button → body/action tap NAVIGATES (goAction → the href). This is the review-first / navigate-only shape.

## The FIX (the review-first conversion — the standard pattern, see [[feedback_no_inventing_customer_lines_hud_confirm]])
`_queue_ack_approval` now emits an **attention** card (was 'approval') with `action:{label:'Review & send', href:'/static/owner/v2_inbox.html?open=<partner_id>&draft=<urlencoded body>'}` (fallback `?c=<norm>&draft=` if no partner_id) and **NO `draft`/`on_approve`**. Tapping OPENS the customer thread with the reply PRE-FILLED → DJ reviews/edits and presses Send himself. Mirrors the proven `operator:confirm` card (reminders.py ~2603). No v2_hud change needed — the card SHAPE drives navigate-vs-send.
- **`/api/reminders/send_ack` NEUTRALIZED**: `api_send_ack` no longer calls `messaging.send` — returns `409 {review_first:true}` directing to the thread. Hard-guards a stale/cached card or replay from ever reaching a send. (Verified 0 other callers repo-wide before neutralizing.)
- Trade-off accepted: the review-first card no longer auto-clears on send (old send_ack deleted it; the inbox send doesn't know the card) → it expires in 3 days or DJ ✓-dismisses it. Cosmetic; Lead said do NOT wire auto-clear (would touch the inbox send path).

## RULE (Dispatcher writing into FLEET_GOVERNANCE)
NO HUD card — W&SC OR Cheryl — may send a customer text/email on a one-tap approve. Any card whose approve would send a customer message MUST be review-first (Approve opens the prefilled thread → DJ/Cheryl reviews → presses Send). Record-only cards (schedule/checkin/task/project — e.g. Cheryl's `/cheryl/api/voicenote/execute` = create_task_core/create_goal_core, verified 2026-09-28: no customer send) are fine to keep one-tap. When building/reviewing any `on_approve` card, ask: does its endpoint reach `messaging.send` / an email send? If yes → review-first, no exceptions.

Related: [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_email_draft_first_always]], [[project_feed_ack_terminal_shortcircuit]].
