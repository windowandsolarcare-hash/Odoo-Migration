---
name: project_shared_payment_closeout
description: Shared post-payment closeout finalize_payment() (Done + next maint visit + funds-received thank-you). Card (Stripe) path was BROKEN — _stripe_phase6_sync is undefined so card never closed out. Co-plan with lead.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-15T14:44:58.471Z
---

**DJ 2026-08-14:** wants ONE shared payment-closeout logic (not duplicated per method), reusable for the Venmo path coming soon. Coordinate with lead (spans specialist + Stripe).

**★ Real bug found:** `payments.py /api/stripe/success` fires `background_tasks.add_task(_stripe_phase6_sync, ...)` but **`_stripe_phase6_sync` is undefined project-wide** (1 usage payments.py ~L732, 0 definitions; not in field.py/dashboard.py/shared). The NameError is swallowed by the surrounding try/except → the background "Done + Phase 5" step silently no-ops. So **CARD payments record the money (invoice posted+paid, chatter) but NEVER mark the job Done, create the next maintenance visit, or text a thank-you.** The customer sees the on-screen "Payment Received!" page only. Zelle (paywatch → `_execute_payment`) does the full closeout.

**Shared fn built (dormant, commit 69a9575):** `routers/owner/payment_finalize.py` → `finalize_payment(so_id, method='', source='', thank=None) -> {done, next_so, thanked, held}`. Call AFTER a payment records. Idempotent, never raises. (1) paid-in-full → Done + gate/pricing snapshot roll-up + `create_next_maintenance_so`; (2) remote methods → "{First}, Funds Received, thank you!" via messaging.send, idem `funds_received:<so_id>` (one thank per payment across all paths). REMOTE_METHODS = {zelle,venmo,card,credit,stripe}. **Caller must pass the REAL method** (paywatch historically passed 'cash' for Zelle — 'cash'/'zelle' share journal line 6, so switch it to the true method).

**★ WIRED + LIVE (2026-08-14):** Lead OK'd the contract + wired Stripe (`/api/stripe/success` → `finalize_payment(so_id,'card','Stripe')`, commit 51780b9 — card bug FIXED). Specialist wired: `dashboard._execute_payment` closeout → `finalize_payment(so_id, method=raw_method, source)` (commit 329b2d6, so field-manual/paywatch/stale-SO all use it); paywatch now passes REAL method 'zelle'/'venmo' (not 'cash') so finalize thanks + dropped paywatch's own thank-you (commit 8dae014); `payment_finalize` returns `paid_full` too (ce09a49). Field-manual `funds_received` frontend call LEFT for now (idem-deduped harmless; lead drops after joint test). **JOINT TEST pending:** real Zelle (watcher + manual) + real card → each = Done + next maint visit + exactly ONE thank-you.

**Wiring split (brief: 3_Documentation/PAYMENT_CLOSEOUT_BRIEF.md, mailed lead):** ME → wire `dashboard._execute_payment` closeout tail → finalize + fix paywatch method + drop paywatch's separate thank-you. LEAD → wire `/api/stripe/success` → `finalize_payment(so_id, method='card')` (the bug fix) + decide on the redundant field `funds_received` frontend call. Neither wires until the contract's agreed (core money flow). **DJ open Q:** cash/check = no thank-you text (in person) is the default — confirm. Related: [[project_paywatch_auto_tip]], [[project_sms_send_paths_quiet_hours]], [[project_mark_done_refuses_workiz_uuid]].
