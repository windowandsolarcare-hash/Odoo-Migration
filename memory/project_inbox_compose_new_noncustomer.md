---
name: inbox-compose-new-noncustomer
description: "Inbox has a ✎ New text compose sheet to text an ARBITRARY typed-in number (non-customer). POST /owner/api/inbox/compose → messaging.send(), which threads a non-customer into an 'Unknown' conv so the reply lands in the Inbox."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-23T23:48:58.151Z
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
---

**Feature (shipped 2026-10-23, §15 Audit+Lead GREEN):** the Inbox (`static/owner/v2_inbox.html`) has a **✎ New text** button in the list header → a compose bottom-sheet (To = typed phone number + Message + Send). DJ texts anyone, customer or not ("where I enter the number"). Commits: sms.py `98ccb495`, v2_inbox.html `4dfddd01`, ENDPOINT_MAP `84662755`.

**The reusable pattern — `messaging.send()` already threads an arbitrary number into the Inbox.** `messaging.send(to, body, partner_id=None, kind='manual', idem=…, force_now=…, source='text')` (messaging.py:614) is the canonical low-level sender and does EVERYTHING for an ad-hoc send: `_sms._norm(to)` → `+1`+norm E.164 (10-digit handled), `is_opted_out(to)` by PHONE (so STOP blocks a non-customer too), DNC, quiet-hours hold, Twilio fire, **AND threads it** — `_sms._conv_get(norm)`; if none, `_sms._conv_new(norm, to, 'Unknown', None)` keyed by the normalized phone (messaging.py:668-689). The inbound webhook `/owner/api/sms/incoming` threads a reply by that same norm → a NON-customer's reply lands in the Inbox under the outbound, never downgraded. If the number already has a thread, `_conv_get(norm)` reuses it (no 'Unknown' shadow). So to text an arbitrary number from anywhere: just call `send()` — don't roll a new sender ([[feedback_reuse_canonical_endpoint]]).

**Why a NEW owner endpoint (not the existing `/api/messaging/send`):** that HTTP wrapper is **CRON_SECRET-guarded** (backend/test only), so the owner UI can't call it. `inbox_compose` (`POST /owner/api/inbox/compose`, sms.py:3855) is a thin owner-authed entry point onto `send()`. It's owner-cookie gated by inclusion under `prefix="/owner"` (same surface as `inbox_send`), see [[project_owner_api_auth_enforced]].

**Quiet hours:** staged `force_now=False` → a compose typed 8pm–8am PT HOLDS for the 8am release like an inbox reply (Lead/DJ confirmed; quiet-pause toggle overrides). One-kwarg flip to `force_now=True` if DJ wants night sends to fire immediately.

**Client reuse:** the compose Send goes through `window.wscSend` (`/static/owner/wsc_send.js`) — lost-signal-safe: injects a `client_msg_id` keyed (threadKey=norm, bodyhash), which `inbox_compose` forwards as `send()`'s `idem` (atomic CAS claim + `_confirm_sent`); on a transient it re-queries `/owner/api/inbox/send_status` (reads `sent_status(client_msg_id)`) + idempotent retry → never a false "not sent", never a double-text (rule 13). On ok → `openThread(norm, true)` (the conv was just seeded). jpost fallback if the shared script is absent.
