---
name: project_maint_confirm_ack_attribution
description: "Maintenance ACK + CONFIRM tracks now attribute WHO acted (customer vs Dan/tech) + WHEN. reminders.py: appt_confirm branches on source; new CONFIRM_BY_KEY stores customer|manual at every confirm set-site; /api/sched/state returns confirmed_by+confirmed_when. v2_field.html: ack-pill + confirm banner show 'by Dan (tech/manual)' vs 'by customer' + Pacific timestamp."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-22T08:19:05.365Z
---

**Fixed 2026-08-22 (DJ caught it): the app said "Customer confirmed" even when DJ (the tech) tapped a Mark button.** Two parallel maintenance tracks on the job-detail (`static/owner/v2_field.html`), handlers in `routers/owner/reminders.py`:

**ACK track** (📩 Send acknowledgement / ✓ Mark acknowledged): state lives in `_maint_state` (key `wsc.maint...`), already stored `via` + `ts`. `appt_confirm(so_id, source)` (state 'ok') is shared by the customer text-reply (`source='text'`), tap-page (`'page'`), and DJ's manual mark (`'manual'`, via `POST /api/maint/mark_ack`). **Bug was:** appt_confirm hardcoded "✅ Customer confirmed … (via {source})" even for `manual`. **Fix:** branch — `source=='manual'` → "✅ Marked acknowledged by Dan (manual)."; else "✅ Customer acknowledged … (via {source})." Read endpoint `GET /api/maint/state` returns `via`+`ts`; client `loadAckState` shows "✓ Acknowledged by Dan (tech) · <time>" (manual) vs "by customer (replied/tapped) · <time>".

**CONFIRM track** (✅ Send confirmation / ✓ Mark confirmed): the confirm flag `CONFIRM_KEY = 'wsc.reminders.confirmed.' + so_id` stored ONLY an ISO timestamp — no WHO. So the green banner always said "Confirmed by customer" even for DJ's manual `POST /api/sched/mark_confirmed`. **Fix (non-breaking):** added a SEPARATE key **`CONFIRM_BY_KEY = 'wsc.reminders.confirmed_by.' + so_id` = 'customer' | 'manual'**, written at EVERY confirm set-site (customer text-reply confirm ~L470, customer approve/book-their-day `approve_request`, DJ `mark_confirmed`) and CLEARED alongside CONFIRM_KEY when a reschedule invalidates it. `GET /api/sched/state` now returns `confirmed_by` + `confirmed_when`. Client `_confLabel(d)` renders "✓ Confirmed by Dan (manual) · <time>" vs "✓ Confirmed by customer · <time>" (used in both `_confBan` and `loadSchedState`). ★ Left `CONFIRM_KEY`'s value format untouched (still a bare ISO string) — `is_confirmed()` + the 4-day auto-confirm skip parse it; the WHO went in the separate key to avoid breaking them.

**Client timestamp helper:** `_fmtStamp(iso)` in v2_field.html formats server UTC ISO (`_now_iso()` emits `...Z`) to a short Pacific stamp. Commits: reminders.py 76f9048, v2_field.html 4526774.

**Same commit-set also:** reordered the job-detail pills (ack→confirm→scheduling-last, Send+Mark grouped per track) and fixed the **Journal date off-by-one** (`routers/owner/journal.py` used `date.today()` server-UTC → stamped tomorrow after ~4-5pm PT; swapped to the canonical `today_pt()` from `routers/owner/shared.py`, commit b4d6f4a). See [[project_second_contact_and_recipient_picker]] (same v2_field messaging/pill area), [[feedback_odoo_verify_content_not_status]].
