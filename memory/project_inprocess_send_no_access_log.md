---
name: project_inprocess_send_no_access_log
description: "Diagnosis pitfall (2026-09-28): SMS/reminder sends fire IN-PROCESS (an APScheduler tick inside the web service), so they leave NO web access-log line. 'No POST logged = never sent' is WRONG. Verify a send via the SMS ledger (wsc.msg.sent / confirm:<so>:<date>) + Odoo chatter ('Sent SMS [...]'), NOT access logs."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-28T02:37:10.113Z
---

**The pitfall (caused a wrong 'never sent' verdict twice — Dianne, 2026-09-28):** a first diagnosis read "no POST in the access log → the send never fired." Wrong. The night-before reminder + confirm sends run **in-process** on the APScheduler tick *inside* the web service (not via an inbound HTTP request), so there is **no access-log line for the send** even when it succeeded. Dianne's confirm HAD sent (ledger `confirm:17443:2026-11-24`, chatter "Sent SMS [confirm_offer]") and she'd even confirmed (tapped the link, sched state=accepted) — the "no access log" reading missed all of it.

**Why:** an access log only records inbound HTTP requests. An in-process scheduled send is a server-side function call — nothing hits the router — so absence from the access log says nothing about whether the SMS fired.

**How to apply — verify a send by the SOURCE OF TRUTH, not a proxy signal:**
- Did the SMS fire? → check the **SMS ledger** (`wsc.msg.sent`, key like `confirm:<so>:<date>` / `reminder_eve:<so>:<date>`) + the **Odoo chatter** ("Sent SMS [...]" with a Twilio SID). NOT the access log.
- Did the customer act? → their inbound tap DOES hit the access log (from their IP) + flips sched state (accepted).
- Access-log *absence* ≠ not-sent for anything in-process. (Access-log absence over a window DOES still indicate a client-side signal drop for a MANUAL user tap — that's a real inbound request that never arrived — so the two cases differ: manual tap = inbound = access-logged; scheduled send = in-process = not.)

Same family as the payment-lookup rule (verify a payment via Stripe/`payment_state`, never Odoo-`account.payment`-alone): confirm the effect against the authoritative store, not an incomplete proxy. Related: [[feedback_verify_collection_and_live_pipe]], [[feedback_no_conclusion_from_single_test_sporadic]].
