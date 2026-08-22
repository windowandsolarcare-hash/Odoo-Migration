---
name: project_followups_job_detail_button
description: "Follow-ups page cards each have a \"Job detail\" button that deep-links to v2_field (?open_so=) — the one screen with every per-job action; Done still removes the follow-up."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T07:38:13.978Z
---

**DJ 2026-08-04:** follow-up cards (followups.py view) that need an action (e.g. Dick Palomba's reschedule) had no way to actually DO the action — only Send-text/Call/Done/Snooze. The follow-up ITEM only carries text (`name/phone/do/draft/last/cat/pid` in `wsc.followups.data`) — NO structured job data (no so_id/date), so a real inline reschedule button couldn't execute. DJ's decision: don't build a per-intent button or duplicate the reschedule engine — instead **each card gets one "🗂️ Job detail" button that opens the customer's job detail (v2_field), the single screen where reschedule/cancel/send-confirmation/call all already live and work on real job data.** Keep ✓ Done to clear the follow-up after.

**Implementation (followups.py):**
- Every card's resolve row now: `🗂️ Job detail` + `✓ Done` + `⏰ Snooze 3d`.
- `openJobFU(phone)` (JS) → `GET /api/followups/job_link?phone=` → `{ok, so_id}` → `location.href='/static/owner/v2_field.html?open_so='+so_id`.
- `/api/followups/job_link` resolver: `_resolve_pid(phone)` → soonest UPCOMING non-Done/Canceled job (`partner_id child_of pid`, date_order>=today) else most-recent job. Returns so_id.
- v2_field `?open_so=<id>` (its existing deep-link, boot L1015) → `openJobById` opens it even if the job isn't in the current day view (it falls back to fetching via `/owner/api/so_history?so_id=`). Verified: Rod Hahn 3233695008→so 17462, Dick 9253371000→so 17485; button renders on all 35 cards.

**Billing cards target a different job (2026-08-04):** a billing follow-up ("Record her Venmo payment") is about a PAYMENT = work already DONE, so opening the future scheduled job was wrong. The button now passes `cat` → `openJobFU(phone, cat)` → `job_link?phone=&cat=`. For `cat=='billing'` the resolver picks: (1) newest POSTED unpaid/partial `account.move` (`company_id=1`) → its `invoice_origin` SO, else (2) newest `x_studio_x_studio_workiz_status='Done'` SO, else most-recent. Non-billing keeps soonest-upcoming. Verified: Kristin Acker → billing opens 004577 (last Done), action opens 004928 (upcoming Submitted).

**Why this shape:** avoids a second copy of the reschedule/cancel engine (DJ's "one call not multiple looks"). The follow-ups page and the inbox_ai HUD cards both surface the same reschedule/cancel replies — job detail is the shared action surface. Related: [[feedback_call_opens_dialer_never_dials]], [[project_shared_text_thread_component]].
