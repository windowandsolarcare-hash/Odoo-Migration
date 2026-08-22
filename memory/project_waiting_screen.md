---
name: project_waiting_screen
description: "The Waiting-on-Reply screen (/owner/waiting) — 2 tabs (Re-engagement Sent | Reactivation Sent) unifying both outreach 'awaiting reply' lists with the same cards + actions. Cockpit 'Awaiting reply' points here."
metadata:
  node_type: memory
  type: project
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

**Built 2026-07-09** (DJ: the cockpit "Awaiting reply" should point to a new 2-tab screen; "the sends of both need the same" → chose **same cards + actions**).

## The screen: `/owner/waiting` → `static/owner/waiting.html`
Two tabs, unified card renderer, IDENTICAL actions on both:
- **Left = Re-engagement Sent**, **Right = Reactivation Sent**.
- Card: name · city · service · "Sent <date>" · **🧹 Last visit: <date> (X ago)** amber badge · age badge (fresh ≤7d / aging ≤21d / stale).
- **Last visit (added 2026-07-09, DJ req):** both `/sent` endpoints now return `last_visit` (fmt "May 27, 2025") + `last_visit_rel` ("1 yr 2 mo ago") from partner **`x_studio_last_visit_all_properties`** (verified to match last Done SO date exactly across 12 samples; the twin `x_studio_x_studio_last_property_visit` is EMPTY — don't use it). Reactivation does a batch res.partner read keyed on lead partner_id; re-engagement adds the field to its existing partner read. Formatter = `_fmt_last_visit(raw)` in reactivation.py. Frontend renders `.lastvisit` amber badge; "none on file" grey variant when absent.
- Actions (dispatch by `r.kind` = 'reeng' | 'react'):
  - **📅 Book** → deep-links the PROVEN existing book sheets: react `/owner/reactivation?book_lead=<lead_id>`; reeng `/owner/reactivation?book_reengage=<partner_id>`. (No re-implementation.)
  - **💬 View text** → modal, `GET /owner/api/customer/crm_activity?partner_id=` (the real logged outreach = x_crm_activity_log; `x_description` is the message). Same for both.
  - **🕓 Not ready** → 3mo/6mo → `POST /owner/api/outreach/defer`. react = `{kind:'lead', id:lead_id, partner_id, months}`; reeng = `{kind:'partner', partner_id, months}`.
  - **🚫 Not interested** → react `POST /api/reactivation/decline {lead_id}` (lead→Lost); reeng `POST /api/reengagement/decline {partner_id}` (clears parked uuid).
  - **📣 Follow up** (2026-07-09, DJ "need ability to resend") → opens the shared **WSCReeng** editor (`reeng_editor.js`) in a modal, `kind:'reengage'` (partner-keyed, NO so_id needed — works for both tabs; a no-reply reactivation customer gets a warm follow-up nudge). Draft / AI draft / view text chain / send, all via existing endpoints. `onSent` closes + drops the card. ★ followup/launch has a 45-day cooldown that can block a re-send — expected, surfaces as the backend error.
  - **🔎 Open (more info)** (2026-07-09) → deep-links `/owner/field?tab=customers&cust_pid=<pid>&cust_q=<name>&ret=waiting` → the customer's field card (full job history + pricing; DJ checks past pricing before following up, esp. reactivation). `_custDeepLink` in field.html opens it; `ret` makes Back return to /owner/waiting.

## Also on the Outreach "To Send" list (2026-07-09)
DJ wanted the same **🔎 Open (more info)** on the Outreach Campaigns To-Send rows (outreach.html) — added a 🔎 rowmenu button before the ⋯ snooze/remove menu → `openInfo(it)` → `/owner/field?tab=customers&cust_pid=&cust_q=&ret=outreach` (ret=outreach → Back returns to the outreach window). Same field-card deep-link pattern. NOT added: Follow-up/compose (To Send sends the first text via the review sheet) or a separate STOP filter here (DJ picked Open only).

## Backend (routers/owner/)
- **NEW `GET /api/reengagement/sent`** (reactivation.py) — the mirror of `/api/reactivation/sent`. Source = `res.partner` where `x_reengagement_workiz_uuid != False` + company in [1,False] + not DNC + **not snoozed** (`x_snooze_until` empty or ≤ today). Returns `{customers:[{kind:'reeng', partner_id, name, city, primary_service, sent, days_waiting}]}`. ★ Reactivation "sent" = crm.lead stage 5 + graveyard_uuid; Re-engagement "sent" = the parked `x_reengagement_workiz_uuid` on the customer (set at followup/launch, cleared on book/decline). Two totally different data models, unified only at the card layer.
- **`/api/outreach/defer` extended** (reactivation.py) with **`kind:'partner'`** → sets `res.partner.x_snooze_until = next_reach`. ★ Re-engagement has NO project.task for most customers (Trish 23589 had none) and NO x_next_reach — so reeng "not ready" snoozes the PARTNER (the outreach classifier + the sent list both already respect x_snooze_until), mirroring how a reactivation lead's x_next_reach parks it. Do NOT rely on the "Re-engagement:" project.task for defer.
- **`pipeline_counts()` adds `reeng_sent`** (outreach.py) — same domain as the list (parked uuid, contactable, not snoozed). `react_sent` already existed.
- Page route `GET /waiting` serves waiting.html (reactivation.py).

## Cockpit wiring (static/owner/index.html)
- "Awaiting reply" card → `/owner/waiting`, count = `react_sent + reeng_sent` (was react_sent only).
- Also this session: "Maintenance to schedule" count = `stranded + overdue` combined (was stranded-only). See the three maintenance buckets in [[project_daily_sync_date_window_excludes_old]]: Upcoming/Overdue = Odoo Submitted SOs via `/api/scheduled_sos`; In-Workiz stranded = never-synced next-jobs via `/api/maintenance/stranded`.

## ★ STOP compliance in both lists (2026-07-09)
Opted-out (STOP) customers must NEVER appear in the waiting lists. The Workiz STOP webhook sets **`res.partner.x_studio_activelead = 'Do Not Contact'`** — that is the reliable STOP marker to filter on. `/api/reengagement/sent` already excluded it; `/api/reactivation/sent` did NOT (it showed Dawn Hay, a STOP) so 211 vs the 209 count → added `['partner_id.x_studio_activelead', '!=', 'Do Not Contact']` to its domain. ★ **`phone_blacklisted` is NOT domain-searchable** (non-stored computed field → `_search` raises "invalid field"), so you cannot filter STOPs on it in a domain — use `x_studio_activelead`; only test phone_blacklisted in Python after a read. Any new outreach list MUST carry the activelead STOP filter.

Verified E2E 2026-07-09: page 200, reeng_sent=6 / react_sent=209, partner-defer sets snooze + drops the card, cleanup reverted; Dawn Hay (STOP) removed from reactivation Sent (211→205). See [[project_reengagement_vs_reactivation]] [[project_reengagement_logic]] [[project_ai_draft_from_conversation]].
