---
name: project_reschedule_false_network_error_fix
description: "submitJobRs (_job_detail_panel.js) showed a FALSE 'Network error' on slow reschedules that actually SUCCEEDED (15s AbortController outlived by the day-plan/so-suggest-heavy screen). Fix = 45s + verify-on-timeout. Only submitJobRs had this; sibling writes have no abort."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T07:19:51.426Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy"; Lead QC-GREEN). Operator-reported (Myra SO 17386): "I keep getting error messages but they are going through."**

**Bug:** `submitJobRs()` in `static/owner/_job_detail_panel.js` wrapped its POST (`/owner/api/schedule/reschedule`) in a 15 000 ms `AbortController`. The reschedule screen fires day-plan/so-suggest Odoo calls (~7-10s each) so the POST outlived 15s → client aborted → generic `catch` showed "❌ Network error — try again" while the server FINISHED the write. Side effects: the chained confirm (`schedLaunch('confirm')`) never ran (no customer confirmation) + DJ re-tapped = double-submit risk.

**Fix (surgical, in submitJobRs):**
1. Abort timeout `15000 → 45000` (heavy op).
2. On `AbortError` specifically: re-read the SO via `GET /owner/api/so_history?so_id=&access_code=` and treat as success ONLY if the SO's day actually moved to the requested day (guarded by `_wasDay` captured pre-submit from `activeJob.date_raw`) → then close + `_jdRefresh()` + `openJobById` + `schedLaunch('confirm')`. Otherwise an honest 'inf' toast "Still saving — reopen to check, don't resubmit" (NEVER a false fail, NEVER confirm/text on an unverified write). dup (duplicate_job) path untouched.

**Audit finding (do not re-chase):** the other write buttons Operator suspected (sendApptConfirm, markConfirmed, markAck, schedLaunch, sendTextReply) are plain `await fetch()` with NO AbortController — they can't false-fail-on-success; the bug was UNIQUE to submitJobRs. A LOW-pri hardening (give those a timeout) is GO per Lead but ONLY paired with verify-on-timeout/idempotency (a naive AbortController→"Network error" on a send path would double-text) — see [[feedback_no_ai_offered_dates_use_link]], [[feedback_reuse_function_follow_full_logic]].

Inbox-thread Reschedule entry ([[project_inbox_reschedule_menu]]) deep-links into this same canonical path, so it inherits the fix.
