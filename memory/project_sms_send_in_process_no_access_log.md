---
name: project_sms_send_in_process_no_access_log
description: "★ SMS sends (reminders/confirmations) fire IN-PROCESS (APScheduler tick inside the web service) → there is NO access-log line for the send. So 'no POST in the access logs' ≠ 'not sent', and a client-side error ('Could not send') ≠ 'the customer didn't get it'. Verify sends via the ledger (wsc.msg.sent) + Odoo chatter ('Sent SMS'), NOT access logs. Also: the app tracks NO SMS delivery receipts (no Twilio StatusCallback) — only send-accepted is knowable in-app; true delivered/failed lives only in Twilio."
metadata:
  node_type: memory
  type: project
  originSessionId: 9ac29974-fb57-4885-a75e-8f19050d109b
  modified: 2026-09-28T02:36:35.089Z
---

**Discovered 2026-09-27 — a diagnosis reached a WRONG "never sent" conclusion; DJ caught it.**

**The trap:** Dianne Hourscht's reschedule-confirmation screen showed a red "Could not send the confirmation," and a first code+log diagnosis concluded the send NEVER happened (no `POST /owner/api/sched/launch` access-log line, ~80s of DJ's requests missing = his phone dropped signal). **That conclusion was wrong.** The confirmation HAD sent (ledger key `confirm:17443:2026-11-24` @ 02:03:52Z, chatter "📤 Sent SMS [confirm_offer]"), and the customer CONFIRMED it (she tapped the confirm link from her own IP minutes later).

**Why the first read was wrong — TWO reasons, both reusable:**
1. **In-process send = no access log.** The reminder/confirm SMS fires from the APScheduler tick running INSIDE the web service (there is no separate worker). So the actual Twilio send produces **no HTTP access-log line**. "No POST logged for the send" therefore does NOT mean "not sent." (What DID show in the logs was only DJ *loading the draft* + a *separate* manual tap that dropped — not the authoritative send path.)
2. **A client error ≠ customer didn't get it.** DJ's manual tap dropped on his signal and showed "Could not send" — but a *different* code path (the in-process offer/confirm send) had already texted her. Idempotency (`confirm:<so>:<date>`) means even both firing = only one send.

**How to verify an SMS send correctly (do THIS, not access logs):**
- **Idempotency ledger** `wsc.msg.sent` (ir.config_parameter) — one key per send, e.g. `reminder_eve:<so>:<date>`, `confirm:<so>:<date>`; the value is the send timestamp. One key = one send (structurally prevents dupes).
- **Odoo chatter** on the SO — a "📤 Sent SMS [<type>]: …" line per send.
- The `reason:'sent'` + SID in `messaging.send()` is set only AFTER `_send_sms` returns a real SID (sms.py:56) — trustworthy for send-accepted.
- **NOT** `wsc.reminders.batch.*` `sent[]` — it gets cleared/rebuilt by a HUD rebuild after the send (a red herring; can read empty even though sends happened).

**Delivery is NOT tracked.** `sms._send_sms()` posts to Twilio Messages.json and reads only the `sid` — it sets **no StatusCallback**, and there is no SMS status-callback endpoint or delivered/failed store anywhere (the only StatusCallback in the app is for VOICE in voice.py). So in-app you can only know "Twilio accepted it," never "it hit the handset." True delivery = Twilio console/API (by number + timestamp). A delivery-tracking build (add StatusCallback + a status store) is the durable fix to answer "did they get it?" on-screen — offered to DJ 2026-09-27.

**Ties to** [[feedback_no_conclusion_from_single_test_sporadic]] (one diagnosis with a plausible story ≠ truth — DJ's ground knowledge overrode it), [[feedback_reiterate_then_handoff_never_guess]], and [[project_stripe_payments_not_reconciled_to_odoo]] (same shape: a client/UI state disagreeing with what actually happened server-side).
