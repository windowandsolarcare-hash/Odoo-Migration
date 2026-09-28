---
name: project_inbox_reply_double_send_guard
description: "The plain inbox reply (inbox_send) now claims-before-fire through the atomic PG CAS ledger so a lost-signal re-tap can't double-text"
metadata:
  node_type: memory
  type: project
  originSessionId: 430559b0-9410-47a6-ae47-0dc126d75711
  modified: 2026-09-28T21:48:59.305Z
---

Shipped 2026-09-28 (main HEAD f535badb, DJ deploy trigger). `POST /owner/api/inbox/send` → `inbox_send` (LIVE `routers/owner/sms.py:3136`, not shadowed) previously called `_send_sms(phone, text)` **directly with zero idempotency** — a lost-signal RE-TAP (request reached server, fired the SMS, response lost → client "tap to retry" → DJ re-taps) or a numInstances=2 concurrent double-tap **double-texted the customer**.

**Fix (surgical, +20 lines, no behavior change beyond dedup):** wrapped the fire in the SAME atomic PG CAS ledger the confirm path proved (`messaging.already_sent` / `_claim_send` / `_confirm_sent` / `_release_claim`; `UNIQUE(idem)` table `wsc_msg_sent`). See [[project_messaging_idempotency_cas]].
- **idem = `reply:<c>:<sha1(body)[:10]>:<YYYYMMDDHHMM>`** — body-hash so two DIFFERENT replies in the same minute BOTH go (keying on `c`+minute alone would wrongly block the 2nd); minute bucket so a genuine repeat in a later minute goes too.
- **Checks current AND previous minute** (`already_sent(idem) or already_sent(idem_prev)`) so a retry crossing the minute boundary is still caught (~1–2 min dedup window). Residual: a manual re-tap >~2 min later is treated as intentional and goes.
- Claim BEFORE fire; `_confirm_sent(idem, sid)` on success; `_release_claim(idem)` on Twilio failure so a legit retry can go. Crash between claim and confirm leaves the row `claimed` = at-most-once (never a double-text; `stuck_claimed()` surfaces those).

**Why NOT routed through `messaging.send()`:** that would newly apply opt-out/DNC blocking to manual replies (DJ replying to someone who texted in) = a regression. Only the dedup was added; opt-out/DNC/quiet-hours behavior of the reply path is UNCHANGED (quiet-hold is still the pre-existing branch above the fire).

**No client change:** 3 live callers (v2_inbox.html, wsc_thread.js, _job_detail_panel.js) — a server guard covers all by construction. v2_inbox.html already renders `{ok, already:true}` as green "✓ Already sent (delivered)" (built for the confirm path); the reply path reuses that UX for free. `hashlib` was NOT imported in sms.py — added to line 15 (`import os, json, re, datetime, html, threading, hashlib`); miss it → `hashlib.sha1` NameErrors the reply path at runtime (py_compile won't catch it).
