---
name: project_wsc_signature_on_every_text
description: "EVERY outbound text signs off with DJ's stacked block (Dan Saunders / Window & Solar Care / 855-245-2273). Applied centrally in sms.py _send_sms — don't add sign-offs in templates/AI prompts; they're auto-normalized."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T21:13:49.445Z
---

**DJ's sign-off (2026-08-07):** he wants his stacked signature on **every single text** (he confirmed "every single text", not just formal ones):
```
Dan Saunders
Window & Solar Care
855-245-2273
```

**Where it's applied — ONE place:** `sms.py` **`_send_sms(to, body)`** — the single Twilio funnel that `messaging.send` AND `inbox_send` both call. Added `WSC_SIGNATURE` + `_apply_signature(body)`: strips a trailing casual sign-off (`_SIGN_STRIP` = `\s*[–—-]\s*(?:Dan|Window & Solar Care)\s*$`), then appends `\n\n` + the block. **Idempotent** (skips if body already has `Dan Saunders` + `855-245-2273`). So every reminder/confirm/inbox-reply/booking/reactivation/ETA/Zelle text gets it, regardless of what the templates or AI drafters produce — **do NOT also add sign-offs in templates/prompts** (they still say "– Dan" and that's fine; it gets stripped + replaced). Quiet-hours holds get signed on release (they re-enter _send_sms).

**Note:** the signature is added at SEND time, so DJ's preview/send-box shows the draft WITHOUT the block — the customer still gets it. That's intentional (consistent, can't be accidentally deleted).

Also updated the branded booking page (`booking.py _SCHED_HTML`) on-screen "You're booked / Request received" confirmations to show the same stacked block (via `<br>`), for brand consistency (those are web cards, not texts, so not covered by _send_sms).

If a NEW outbound-text path is ever added, route it through `_send_sms` (or call `_apply_signature`) so it's signed too. See [[feedback_company_name_no_a.md]] (brand = "Window & Solar Care").
