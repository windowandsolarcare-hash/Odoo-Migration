---
name: project_stop_optout_true_count
description: "TRUE stop count = phone.blacklist / x_crm_activity_log 'Opt-Out' (17), NOT x_studio_activelead='Do Not Contact' (74) nor the DEAD x_studio_stop_request_received (0). STOP archives the contact."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**The STOP routine** = Server Action **954 "Workiz STOP Logic"** (Odoo webhook, fires on Workiz SubStatus "STOP - Do not Call or Text"). It: (1) finds contact by `x_studio_x_studio_location_id` then phone; (2) adds phone (E.164 `+1XXXXXXXXXX`) to **`phone.blacklist`**; (3) sets `x_studio_activelead='Do Not Contact'`; (4) posts `[STOP]` chatter; (5) creates an `x_crm_activity_log` **"SMS Opt-Out"** entry (x_campaign_id 1); (6) marks open crm.lead Lost (stage 6); (7) **archives the contact (`active=False`)** — so STOP'd customers vanish from every active-only search/KPI. That archive is WHY the count feels "buried": a normal `search_count` (active=True default) misses them — pass `['active','in',[True,False]]`.

**TRUE number of stops (2026-07-13) = 17** — confirmed two ways that agree: 17 `phone.blacklist` numbers AND 17 `x_crm_activity_log` Opt-Out entries. These are the canonical counters.
- `x_studio_activelead='Do Not Contact'` = **74** (66 active + 8 archived) — a BROADER bucket = the 17 real STOPs + ~57 MANUAL do-not-contacts who never texted STOP. Do Not Contact ≠ STOP.
- ⚠ `x_studio_stop_request_received` (boolean, "Stop Request Received") reads **0** everywhere — SA 954 never writes it. DEAD/misleading field; do NOT use it to count stops.

**Manual STOP button (added 2026-07-13):** outreach.html "Snooze / Remove" sheet (`openPark`) now has a **🛑 STOP** button in the permanent group next to Moved/Deceased/Not interested → `doPark('stop',{})` → `POST /api/outreach/park` action='stop' (outreach.py). It MIRRORS SA 954 (blacklist phone + Do Not Contact + SMS Opt-Out log + cancel re-eng tasks + lead→Lost + archive) so a manual opt-out increments the SAME true counters. Commits outreach.py 26ac98d / outreach.html 95e0d64 (mobile-field fix 5d4a759). ⚠ **res.partner has NO `mobile` field in this Odoo 19** — only `phone` (reading 'mobile' throws `Invalid field 'mobile' on 'res.partner'`). Verified 2026-07-13. See [[project_do_not_contact_forward_looking]], [[project_snooze_scheduled_sos]].
