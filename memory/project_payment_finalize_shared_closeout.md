---
name: project_payment_finalize_shared_closeout
description: "ONE shared post-payment closeout = payment_finalize.finalize_payment(so_id, method, source, thank). Fixed the card-payment bug: /api/stripe/success called never-defined _stripe_phase6_sync → card recorded $ but never Done/next-visit/thank."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-15T14:00:35.953Z
---

**Shared payment closeout (2026-08-14/15):** `routers/owner/payment_finalize.py` → `finalize_payment(so_id, method='', source='', thank=None) -> {done, next_so, thanked, held}`. Call it AFTER a payment is recorded, from EVERY payment path, so behavior never drifts between methods. It (idempotent, never raises):
1. If the SO is now fully paid + not Done → mark `x_studio_x_studio_workiz_status='Done'`, roll gate/pricing snapshot up to the property master, and `create_next_maintenance_so(so_id)`.
2. Funds-received thank-you for REMOTE methods → `messaging.send('{First}, Funds Received, thank you!', kind='funds_received', idem='funds_received:<so_id>')` — quiet-hours/opt-out/DNC/thread aware, deduped by idem (one thank per payment even if multiple paths fire).
- **CALLER CONTRACT:** pass the REAL method ('zelle'|'venmo'|'card'|'credit'|'check'|'cash'), NOT the journal-mapping method. `REMOTE_METHODS = {zelle, venmo, card, credit, stripe}`. `thank=None`→auto (remote yes, cash/check no). DJ locked: **cash/check get NO thank-you** (handed over in person).

**BUG FIXED (Lead, payments.py commit 51780b9):** `/api/stripe/success` fired `background_tasks.add_task(_stripe_phase6_sync, ...)` but `_stripe_phase6_sync` was **defined NOWHERE** in the repo → NameError swallowed by try/except → **card/Stripe payments recorded the money but NEVER marked Done, created the next maintenance visit, or thanked the customer.** (Zelle via `_execute_payment` did all three, so only card was broken.) Replaced the call with `background_tasks.add_task(finalize_payment, so_id, 'card', 'Stripe')`. Kept as a background task; the payment register runs before finalize so `payment_state` is settled.

**Ownership split (with specialist session):** Lead owns the Stripe wiring (done). Specialist owns `dashboard._execute_payment → finalize` (replace its inline Done+snapshot+next block) + fixing paywatch to pass the REAL method ('zelle'/'venmo' not 'cash') — as of this writing NOT yet wired on their side. Once it is, the field-manual `/api/payment/funds_received` call in v2_field.html doPayment becomes redundant (idem-safe to leave; drop AFTER their wiring + a Zelle/card test). Brief: `3_Documentation/PAYMENT_CLOSEOUT_BRIEF.md`. See [[project_sms_send_paths_quiet_hours]] and [[project_payment_link_nameerror]].
