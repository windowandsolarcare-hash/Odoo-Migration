---
name: project_stripe_sms_bypasses_stop_dnc
description: FIXED 2026-09-19 (commit 56f14676) — /stripe/send_sms used to send via raw _send_sms (skipping STOP/DNC); now routed through messaging.send so opt-out is enforced. Kept as the record + the "customer SMS must go through messaging.send" rule.
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-20T00:54:29.020Z
---

**✅ FIXED 2026-09-19 (commit 56f14676, Lead-QC'd).** `api_stripe_send_sms` now routes through `messaging.send(..., kind='payment_link', idem='stripe_sms:{so}:{5min-bucket}')`, which enforces `is_opted_out`(STOP) + `is_do_not_contact` + quiet-hold + threading + comms-log. A STOP'd customer now correctly FAILS with a friendly reason ("Customer opted out (texted STOP) — not sent"), no text. Raw `_send_sms` + manual `_hold` + manual thread-append removed (−25 lines). The record of the original gap + the general rule follows.

**The gap (was):** The Stripe payment-link SMS path **bypassed the STOP/DNC opt-out check.**

- `POST /owner/api/stripe/send_sms` → `api_stripe_send_sms` (routers/owner/payments.py, ~:545) gates ONLY on `messaging.in_quiet_hours()` (manual quiet-hold via `messaging._hold`), then calls **`sms._send_sms(to, body)` directly** (sms.py:54).
- `_send_sms` is the RAW Twilio egress — it posts straight to the Twilio Messages URL and does **NOT** check opt-out. The STOP/DNC check (`is_opted_out`) lives in **`messaging.send`** (messaging.py:345), which this path SKIPS.
- **Result:** a customer who texted STOP can still receive a Stripe payment-link text = a real TCPA/compliance risk (not just a consistency nit). Quiet-hours IS honored; STOP/DNC is the miss.

**Why:** the Stripe path predates / sidesteps the `messaging.send` funnel (the funnel is the single place STOP/DNC/quiet/threading/idempotency are applied). `_send_sms` is meant to be BELOW the funnel, not called directly for customer sends.

**How to fix (the "route Stripe SMS through the funnel" follow-up):** replace `_send_sms(to, body)` + the manual `_hold` in `api_stripe_send_sms` with a single `messaging.send(to, body, partner_id=, so_id=, kind='payment_link', idem=<real key>)` call — that one call applies `is_opted_out`(STOP) + DNC + quiet-hours + thread-write + idempotency, collapsing the special-case into the funnel. Payments/customer-facing → deepest QC (preserve the link, the SO chatter note, and the inbox thread-append the current path does). Related: [[feedback_ported_means_twilio]].

**General rule this reinforces:** any customer SMS must go through `messaging.send` (the STOP/DNC/quiet/idem funnel), NEVER `_send_sms` directly. A direct `_send_sms` for a customer-facing text is a red flag. (The photos-send path was similarly missing idempotency — fixed 2026-09-19 with a bucketed idem — see the A29/follow-up work.)
