---
name: feedback_owner_triggered_endpoint_uses_owner_cookie_not_token
description: "An endpoint a human/Operator triggers from the app must authenticate off the OWNER SESSION cookie, never force a separate server secret (CRON_SECRET) on DJ. Forcing DJ to hand over a token = a plumbing leak that violates 'the app is the UI, DJ never does plumbing.'"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-10-27T06:59:42.024Z
---

DJ (2026-10-26): asked to run the one-time Inbox→Timeline backfill (`GET /owner/api/inbox/backfill_sent`), I asked him to drop CRON_SECRET in a file. DJ pushed back — *"I don't understand, I haven't had to give a token in 6 months, why now?"* He's RIGHT.

**Root cause:** `sms.py:3696` gated the endpoint as `if token != CRON_SECRET: return 403` — it ONLY accepts the CRON_SECRET env secret and ignores the owner cookie. Specialists/Lead described it as "owner-walled," but the code is CRON_SECRET-walled. Every OTHER `/owner/*` endpoint authenticates off DJ's (and Operator's) app-login cookie, which is why in 6 months DJ never handed over a token.

**The rule:** any endpoint a human or the Operator triggers interactively from the app must accept the **owner session cookie** as auth. A `CRON_SECRET`-only gate is correct ONLY for an unattended cron caller. When an endpoint is BOTH cron-fired and owner-triggered, gate it on **EITHER** a valid owner cookie **OR** `token==CRON_SECRET` — never force the token on the owner. Forcing DJ to locate/paste/file a server secret turns him into plumbing — the same failure class as sending him into Odoo ([[feedback_never_send_dj_to_odoo]]).

**How to apply (Operator):** if a peer tells you an endpoint is "owner-walled," VERIFY the code (does it read the owner cookie, or only a token?) before asking DJ for a secret. If it's token-only, DON'T ask DJ for the token — route a fix so the endpoint accepts the owner session, then trigger it from your authenticated owner session. Also honors the secret-relay rule ([[feedback_never_relay_credential_via_session.md]]) — the clean fix removes the need to handle the secret at all. Ties to [[feedback_assistant_use_app_workflow_not_raw_api]].
