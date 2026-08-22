---
name: project_do_not_contact_forward_looking
description: "Do-Not-Contact / STOP is a HARD exclusion for EVERY forward-looking feature (reactivation, reminders, blasts, scheduling suggestions). How to detect it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5c7951e2-f25a-42b0-ac13-dd386cb454cf
---

# Do Not Contact = exclude from EVERYTHING forward-looking (DJ rule, 2026-06-11)

DJ marks a customer **Do Not Contact** when they say STOP or have moved/passed away. His expectation: that makes them **inactive** — they must be excluded from anything that reaches out or plans future contact. **Any new forward-looking feature MUST check this** (reactivation, re-engagement, reminder texts, marketing blasts, "due/overdue" prompts, scheduling suggestions). Treat it as a standing requirement, not a per-feature nicety.

## How to detect DNC (check BOTH — they come from two paths)
On the **contact** (res.partner, the parent — NOT the property):
- **`x_studio_activelead == 'Do Not Contact'`** — DJ sets this manually (moved / passed away / asked to stop). Exact string, case-sensitive.
- **`phone_blacklisted == True`** — Odoo's mail blacklist, set when a STOP text comes in (Phase 2B STOP webhook adds the number to the blacklist). This field IS readable via read() on res.partner in this Odoo 19 SaaS.

`dnc = (x_studio_activelead == 'Do Not Contact') or bool(phone_blacklisted)`

## Where it's already enforced
- **Reactivation SA 562/563** already skip DNC/blacklisted contacts server-side ("No SMS sent. Contact will remain in Do Not Contact status"). Defense in depth — but the UI must also surface/respect it so DJ doesn't waste time.
- **Customer Analytics** (2026-06-11): compute reads `x_studio_activelead`+`phone_blacklisted` per contact → `dnc` flag on every customer/lead. Lapsed list shows a collapsed **"🚫 Do Not Contact"** group (pulled out of "To review"); the Reactivate button is hidden + a blocked banner shown in the history sheet for DNC customers. 27 contacts flagged total, 13 lapsed (2026-06-11). See [[project_customer_analytics_datamodel]].

## 🛑 Do Not Contact from the job 3-dot menu (2026-07-01)
Field job ⋯ menu now has **🛑 Do Not Contact** → `POST /owner/api/customer/do_not_contact {partner_id}` (reactivation.py) which MIRRORS the Workiz STOP webhook (odoo_webhook_stop_handler.py): resolves property→parent (`_followup_customer_id`), sets `x_studio_activelead='Do Not Contact'`, creates a `phone.blacklist` record for the E.164 phone (10 digits→+1{d}, 11 w/ leading 1→+{d}; best-effort — DNC still holds if the blacklist create is blocked), posts a `[STOP]` chatter note. Confirm dialog first. Lets DJ mark STOP directly from the field without routing through Workiz (which is leaving). ✅ DONE 2026-07-01: `scheduled_sos` + `calendar_jobs` (dashboard.py) now return a **`dnc`** flag (parent's `x_studio_activelead=='Do Not Contact'` OR `phone_blacklisted`), and the FORWARD-LOOKING worklists drop it — loadNeed Overdue/Upcoming (`!j.dnc`) + Investigate. ★ REVISED 2026-07-01: the **Skipped bucket does NOT drop DNC or recently-contacted** — Skipped = the true record of every missed job, so those show WITH a tag instead (`🚫 Do Not Contact` muted / `✓ texted Nd ago` ok), not hidden. DJ's Skipped list had shrunk ~11→5 and he wanted the full history back. Diagnostic (2026-07-01): of 12 real 90-day skipped jobs, 6 were hidden by recent-contact(<45d), 0 by DNC — the "15 DNC" my first pass saw were all Personal Time blocks (already excluded by job_type/name). So on Skipped: tag, don't drop. See [[project_reengagement_logic]].

## ★ scheduled_sos leaked DNC onto the Maintenance page (fixed 2026-07-13)
`/api/scheduled_sos` (dashboard.py, the ACTIVE one — a SECOND dead copy exists in submitted_jobs.py; dashboard's wins because it has the `overdue` param + `days_overdue`) only **TAGGED** each job with `dnc` (`_dnc(so)` = parent `x_studio_activelead=='Do Not Contact'` OR `phone_blacklisted`) and only **excluded snoozed** jobs — it did NOT drop DNC. The **Command Center** (schedule_hub loadNeed) filtered `!j.dnc` **client-side** for Overdue/Upcoming, so DNC was hidden there — but the **Maintenance page** (maintenance.html) does NOT filter, so DNC customers leaked onto its Overdue list (LD Fowler — STOP'd + blacklisted in March, still had a 106-day-overdue Submitted next-job 003833). FIX: dashboard.py `api_scheduled_sos` now `if _dnc(s): continue` — HARD server-side exclusion, so BOTH frontends are clean regardless of client filtering (commit c1b5830). ✅ SAFE: the **Skipped** bucket uses a DIFFERENT endpoint (`/api/calendar_jobs`), so it still keeps DNC jobs tagged (Skipped = full miss history) — unaffected. Lesson: enforce DNC at the SOURCE endpoint, not per-frontend.

## Setting / clearing DNC from the apps (2026-06-11)
- **Reactivation app "🚫 Inactive" button** = `POST /owner/api/reactivation/mark_inactive {partner_id}` (in dashboard.py:12013) → writes `x_studio_activelead='Do Not Contact'`. Now has an **UNDO** banner (7s) → `POST /owner/api/reactivation/mark_active {partner_id}` (in reactivation.py) → writes back `'Active'`. (Also fixed: the Inactive button no longer also opens the candidate card — card onclick guards `if(!event.target.closest('.cand-inactive-btn'))`.)
- **Analytics set-aside reasons "Moved" / "Passed away" auto-mark DNC.** `POST /owner/api/analytics/setaside {pid,on,reason}` — when reason is exactly `'Moved'` or `'Passed away'`, it ALSO writes `x_studio_activelead='Do Not Contact'` and returns `dnc:true` (frontend sets `CUST_BY_PID[pid].dnc=true`). Other set-aside reasons stay soft (set-aside only). Rationale: moved/deceased = permanent, not "maybe later."
- **Valid `x_studio_activelead` values:** `'Active'` (contactable) and `'Do Not Contact'`. Login + candidate queries use `=='Active'`, so un-marking must set `'Active'` (not empty).

## To re-enable a customer
Set `x_studio_activelead='Active'` (the reactivation UNDO / mark_active endpoint does this), and/or remove the phone from the blacklist. Then they re-appear in working lists on the next analytics recompute.

Related: STOP compliance = Phase 2B webhook ([[CLAUDE.md]] Phase table).
