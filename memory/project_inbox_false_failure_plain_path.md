---
name: project_inbox_false_failure_plain_path
description: "Inbox 'You lost signal — nothing was sent' shown AFTER a real delivered text — the PLAIN reply path never re-queried the server before declaring failure (only the CONFIRM path had the Linda fix). Fix = shared window.wscSend helper: per-(thread,body) client_msg_id + re-query /owner/api/inbox/send_status before ever reporting a non-send + outcome beacon. Phase 1 server + Phase 2 client ship as ONE unit."
metadata:
  node_type: memory
  type: project
  originSessionId: 8a97aa73-5f27-4f02-a0f6-64f2dd10d242
  modified: 2026-10-02T06:15:29.538Z
---

**Symptom (proven, 2026-10-01):** DJ saw red "You lost signal for a moment — nothing was sent. Tap Send to try again." on Desiree Wesson's thread at 7:55 PM PT, but Twilio DELIVERED the text at 7:49:46 PM PT (SM673886…). A FALSE failure on a genuine success → invites a re-tap → double-text risk.

**Root cause (code-proven):** the three PLAIN inbox senders declared failure on ANY transient (timeout/abort/network/5xx) WITHOUT asking the server whether the send went through:
- `v2_inbox.html sendReply()` — the CONFIRM branch already re-queried `/owner/api/reminders/confirm_status` (the 2026-09-28 "Linda Elliott" fix), but the **PLAIN branch** (`jpost('/owner/api/inbox/send')`) went straight to `_sendFailMsg(null)` on a transient null → the exact red copy, no re-query.
- `wsc_thread.js send()` plain branch + `_job_detail_panel.js sendTextReply()` — raw `fetch` + `alert/showToast('Network error')` on throw, no re-query either.

**Danger window:** server `inbox_send` was idempotent only for the current + previous minute (`reply:<thread>:<bodyhash>:<minute>`). The false error persists on screen, so a re-tap at +6 min is OUTSIDE that ~2-min window → `already_sent` false → it WOULD double-text.

**Fix (Phase 1 server + Phase 2 client ship TOGETHER as ONE unit):**
- **Phase 1 (server, sms.py/messaging.py/slot_offers.py):** `client_msg_id` any-time dedup (kills the ~6-min double-text), a 10-min thread+bodyhash TTL, a `mark_sent`/`sent_status`/`recent_sent_at` ledger, and a NEW read-only `POST /owner/api/inbox/send_status`. Backward-compatible (no client_msg_id ⇒ old behavior). slot_offers maps `already_sent`→success.
- **Phase 2 (client):** ONE shared `static/owner/wsc_send.js` → `window.wscSend({url,payload,threadKey,body,statusIdem?})`. It persists a per-`(threadKey,djb2(body))` `client_msg_id` in localStorage, injects it as the server idem, and on a transient **RE-QUERIES `/owner/api/inbox/send_status` before ever reporting a non-send** (green/"already" if the ledger says sent; red only if truly not sent). Fires a guarded `window.wscBeacon('inbox_send',{outcome})` → the plain path's first real failure RATE. **Fail-safe:** an unconfirmable transient KEEPS the id (re-tap reuses it → server dedups → no double-text) and NEVER claims a false "sent". Wired the 3 plain senders; helper loaded on all 5 host pages (v2_inbox/command/customers/reeng_review/job). Every caller is `if(window.wscSend){…}else{<original fetch>}` = zero regression if a host lacks the script.

**How to apply / lessons:**
1. **A send UI must confirm with the server before ever reporting a non-send.** A client timeout ≠ a non-send; the server almost always delivered (Twilio logs 200/delivered even when the client aborted). Re-query the authoritative ledger first.
2. **When one fix (the Linda confirm-path re-query) lands, grep for SIBLING paths with the same gap.** The plain path, wsc_thread, and job-detail all had the identical bug; fixing only the confirm path left 3 live false-failure surfaces.
3. **Shared helper, not N copies** (repetition rule) — `wsc_send.js` is the single source; graceful fallback keeps un-migrated hosts safe.
4. **Beacon the outcome** so a "sporadic" UX bug gets a real RATE instead of single-case guessing ([[feedback_sporadic_bugs_repeat_test]]).
5. The **MESSAGE-THREAD** staleness (Leonard Karp's night-before text missing from the thread view while the server had it) is a SEPARATE path (thread render/refresh, not the send path) — do not fold it into this fix. `wsc_thread.load()` fetches `thread_by_partner` fresh per open, so that staleness is elsewhere; queued as its own investigation.

Staged (2026-10-01) at `3_Documentation/review/inbox_false_failure_fix/` (Phase 1 `*_built.py` + Phase 2 8 `_built` files + BUILD_NOTE). Related: [[feedback_reuse_function_follow_full_logic]], [[project_inbox_reply_double_send_guard]], [[feedback_sporadic_bugs_repeat_test]].
