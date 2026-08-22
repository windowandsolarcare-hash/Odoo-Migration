---
name: project_sms_send_paths_quiet_hours
description: "Two SMS send paths: messaging.send() enforces quiet hours/opt-out/DNC/dedup + threads inbox; sms._send_sms() is raw immediate (bypasses quiet). Signature now 760-334-5355. Zelle auto 'Funds Received' text added."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-14T13:11:59.274Z
---

**There are TWO outbound-SMS paths — this is why some texts hold for quiet hours and some don't:**

1. **`messaging.send(to, body, partner_id, so_id, kind, idem, force_now)`** (routers/owner/messaging.py L306) = the CANONICAL, policy-aware send. It: HOLDS during quiet hours (after 8pm / before 8am PT) and releases at 8am via the hold queue `wsc.msg.holdqueue`; skips opt-out (`is_opted_out`), Do-Not-Contact (`is_do_not_contact`), and dedup (`idem`/`already_sent`); then calls `_send_sms`; then THREADS the message into the inbox conversation + logs to res.partner/sale.order chatter. `force_now=True` bypasses the overnight hold (a text DJ deliberately fires after hours). Automated stuff (reminders, reactivation, re-engagement, photo sends, campaigns, and the new Zelle funds-received) goes through here → honors quiet hours.

2. **`sms._send_sms(to, body)`** (routers/owner/sms.py L54) = RAW immediate Twilio send. NO quiet-hours check, no opt-out/DNC/dedup. Applies the signature, sends now. Used by the STOP handler and the Stripe payment-link `/api/stripe/send_sms`. Originally this was ALSO why manual inbox replies went out immediately at night (answered DJ 2026-08-14: "why did Norman's text go out right away?" — his was a manual reply on this path).

**UPDATE 2026-08-14 — inbox replies NOW honor quiet hours.** DJ asked to change it. `/api/inbox/send` (inbox_send) no longer sends straight through `_send_sms` at night: it now checks `messaging.in_quiet_hours() and not messaging.quiet_paused()` and, if quiet, calls `messaging._hold({...kind:'reply'})` to queue the reply for the 8am `release_holds()` (which re-sends + threads it). Outside quiet hours it still uses the immediate `_send_sms` path (opt-out/DNC behavior on replies unchanged — only quiet-hours holding was added). The endpoint returns `held:True` when queued; the two inbox UIs show it: `wsc_thread.js` (alert) and `v2_inbox.html` sendReply (note) → "🌙 Queued — sends at 8:00 AM (quiet hours)". Override = the global quiet-pause toggle.

**UPDATE 2026-08-14 (part 2) — payment link ALSO honors quiet hours now.** DJ said "hold everything at night." `/api/stripe/send_sms` (payments.py) got the same guard: if `messaging.in_quiet_hours() and not quiet_paused()` → `messaging._hold({...kind:'payment_link'})`, log "💳🌙 …QUEUED — releases 8am" on the SO, return `held:True`; the field UI (v2_field.html doStripeLink) shows "🌙 Payment link queued — sends 8am". Daytime path unchanged (immediate + custom thread record).

**"Automatic STOP" clarified (DJ asked 2026-08-14):** the app does NOT send a STOP/opt-out confirmation text — `reminders.handle_inbound` on `kw=='stop'` just calls `messaging.record_optout()` and returns (no outbound). The "You've unsubscribed" confirmation is sent by **Twilio at the CARRIER level (Advanced Opt-Out)** before it reaches the app — legally required, instant, NOT under app/quiet-hours control. So there is nothing app-side to hold for STOP. Net: EVERY app-originated customer text now honors quiet hours (automated reminders/reactivation/re-engagement/photos, inbox replies, Zelle funds-received, Stripe payment link). The only overnight-immediate text is Twilio's carrier STOP confirmation. "Charge at Door" is unaffected (opens the Stripe page on DJ's own phone — not a customer text).

**Signature (2026-08-14):** `WSC_SIGNATURE` in sms.py changed from `855-245-2273` → **`760-334-5355`** (DJ's main texting line; 855 was toll-free/leftover). `_apply_signature` idempotency now detects EITHER number so old-signed bodies aren't double-signed. Stacked block = `Dan Saunders\nWindow & Solar Care\n760-334-5355`, auto-appended on every outbound text at the send funnel.

**Zelle "Funds Received" auto-text (2026-08-14):** new endpoint **`POST /owner/api/payment/funds_received`** (payments.py) — takes `so_id`, looks up the customer, sends `"{FirstName}, Funds Received, thank you!"` via `messaging.send(kind='funds_received')` (so it HOLDS till 8am at night, threads the inbox, respects opt-out/DNC). Wired into v2_field.html `doPayment()`: fires automatically ONLY when `payMethod==='zelle'` and the payment records ok; toast shows "sent" or "queued — sends 8am". The greeting is the whole body — the 760 signature is auto-appended to match DJ's template. See [[project_stripe_payment_methods]].
