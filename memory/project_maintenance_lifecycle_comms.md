---
name: project_maintenance_lifecycle_comms
description: "★ SPEC (DJ 2026-08-01): replicate Workiz's maintenance comms lifecycle in Odoo/Render, transparent to the customer. 3 stages + an advance heads-up, HUD-approved first then automated. Reuse reminders.py. URGENT — DJ has jobs to inform."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-01T16:48:26.660Z
---

**DJ, 2026-08-01: replicate the Workiz maintenance-comms flow so it's transparent to the customer (what he's used to), then improve later. URGENT — he has jobs to notify now.** Build on the EXISTING reminders.py (confirm + night-before via messaging.send/Twilio already exist). Keep Phase 5/6 running for now (invoice → generate next job by frequency).

## The lifecycle DJ wants (per maintenance job)
**Trigger:** a maintenance job is INVOICED → Phase 5/6 generate the NEXT job in the future at the frequency interval (keep as-is for now).

**Stage 0 — Advance heads-up (at the far-out point, e.g. ~6 months, when DJ is ready to deal with it):**
- Surfaces in the HUD ("you need to send this to the customer"). DJ-approved at first; automate later (this is the "flip the switch" payoff — Workiz forced manual intervention).
- DJ picks from a **dropdown of what to send** (text / email / [other]) — the message = "You've got a job on <date> (~6 months out). Put it on your calendar. If you'll be away, get back to me; otherwise reply OK." Give the customer options to **OK / request another date / cancel**.
- Customer replies **OK** → must be **RECORDED automatically** (a field/tag = "advance-OK'd"). In Workiz DJ had to manually flip a tag — he wants that auto. OK = "this future date looks good."

**Stage 1 — Confirmation (3–4 days before the job):**
- Reads the advance-OK tag. If OK'd, send a **confirmation** text: ask the customer to confirm (again gives them a chance to back out if their schedule changed).
- Customer **confirms** → recorded (a "confirmed" field, triggered/timestamped).
- **Cancel must also be an option** at this stage (and arguably in Stage 0's initial text too — a "this date doesn't work, I need another" reply path).

**Stage 2 — Night-before reminder:**
- IF confirmed → "I'll be there tomorrow — gate code / guard list / anything I should know, let me know."

## The HICCUP DJ most wants solved (Workiz's limitation)
When the customer **doesn't reply** at a stage, Workiz dead-ended. DJ wants NO dead-end:
- Non-confirmers should STILL get a night-before reminder, but a **different message**: "You didn't confirm but didn't cancel — so I'll be there tomorrow. This is your reminder…"
- So the flow branches on state at each stage (OK'd? confirmed? no-reply? cancelled?) and always stays communicative.

## Approval model
Everything runs through the **HUD with DJ's approval at first**; once he trusts it, it **automates** (per-stage or global auto toggle). "Flip the switch now" = build it approval-gated, with a path to auto.

## Reuse map (what exists vs new)
- **EXISTS (reminders.py):** Stage 1 confirm ("reply YES to confirm") + Stage 2 night-before, via messaging.send (Twilio), YES→handle_inbound marks CONFIRM_KEY, review-before-send cards to HUD. `build_batch('confirm')` targets jobs exactly today+3d; `'eve'` targets today+1.
- **NEW / to build:**
  1. **Stage 0 advance heads-up** = a new reminder kind (e.g. 'advance') fired when DJ is ready (HUD), with the send-option dropdown (text/email) + OK/reschedule/cancel replies.
  2. **State fields** for advance-OK'd and confirmed + cancel/reschedule — decide the Odoo field(s) (was Workiz tags). Record automatically on inbound reply.
  3. **Inbound handling** beyond YES: add OK (advance), CONFIRM, CANCEL, RESCHEDULE-request parsing in handle_inbound.
  4. **Non-confirm night-before branch** — a second eve template for un-confirmed-but-not-cancelled jobs (currently eve has one template).
  5. **Email channel** option in the dropdown (Odoo mail.mail) alongside text.
  6. Short-notice confirm (job booked <3 days out misses the today+3 window) — send confirm at schedule time.
- **KEEP:** Phase 5/6 (invoice → next job by frequency) for now.

## Files
`routers/owner/reminders.py` (extend), `messaging.py` (send layer — reuse), the HUD feed (approval cards), inbound webhook (sms.py handle path). See [[project_reminder_texts_build]], [[project_hud_followups_surface]], [[feedback_ported_means_twilio]].
