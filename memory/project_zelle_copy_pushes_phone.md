---
name: project_zelle_copy_pushes_phone
description: "Zelle pay-page Copy-tap (strong \"paying now\" signal) now PUSHES/buzzes DJ's phone via _notify web push (require_interaction + vibrate) in addition to the HUD card. Page OPEN stays quiet (chatter only)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T03:48:02.199Z
---

The customer Zelle pay page (`GET /owner/api/zelle/pay`, routers/owner/payments.py) beacons engagement to `POST /owner/api/zelle/track` (events: open / copy_email / copy_amount / card), stored in ir.config_parameter `wsc.zelle.track.<so_id>` and deduped (first-open, first-copy).

- **OPEN** = SOFT signal (a texted link can auto-preview → could be a bot), so it only writes a quiet SO chatter note ("👀 opened the Zelle pay page"). No HUD card, no push.
- **COPY tap** (email or amount) = STRONG signal (a preview bot never taps a button = a human is paying). It now does THREE things (last one added 2026-08-06, DJ "yes push/buzz"): (1) SO chatter note, (2) HUD glance card `zelle_engaged:<so>` ("💸 <cust> is paying — tapped Copy ($X)"), and (3) a **web PUSH that wakes/buzzes the phone** — `from .sms import _notify(title,body,url,tag,require_interaction=True,vibrate=[300,120,300])`. `_notify` (sms.py) → myday `_get_subs`/`_broadcast` (pywebpush/VAPID, Urgency=high).

Feed cards NEVER push on their own (feed.py is pull-only) — pushing requires an explicit `_notify` call. Push subs live in `myday.push.subs`.

Real-world note: John Bullock (SO 17389) paid 2026-08-06 but the page only logged an OPEN, no COPY — he paid straight from his bank app (saved payee), so no card/push fired. That's expected. See [[project_hud_approve_false_failure_slow_op]].
