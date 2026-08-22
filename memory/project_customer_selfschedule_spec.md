---
name: project_customer_selfschedule_spec
description: "★ DJ's payoff feature (2026-08-04): customer self-scheduling 3-choice message + job-detail launch button + Accepted banner/reset + 4-day confirm + night-before gated-conditional. Full spec = 3_Documentation/CUSTOMER_SCHEDULING_SPEC.md."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T14:10:51.258Z
---

**DJ's payoff feature — the 'cool but elderly-friendly' self-scheduling flow he kept asking about.** Full spec: **`3_Documentation/CUSTOMER_SCHEDULING_SPEC.md`** (repo). Captured 2026-08-04 so it stops getting lost.

## ✅ FULLY BUILT 2026-08-04 (pending DJ eyeball + first live approval)
All 3 parts done. Specialist: booking.py `/book/sched/<token>` (branded portal page, name/address/job-type/history) + 3-choice flow (1 book / 2 next-available via open_days_for_partner / 3 free-pick) + v2_field launch button + states + reset; reminders.py Part2 (CONFIRM_LEAD_DAYS 3→4, "reply YES / reply to reschedule / text us") + Part3 `_eve_body` gated-conditional (gate sentence + code ONLY when property x_studio_gated). Free-pick → HUD **approval** card (`sched_req:<so_id>`, on_approve → `/owner/api/sched/approve_request` books). State store = `wsc.sched.<so_id>` {state:none|sent|accepted|requested}. Lead: x_studio_gated field, `/api/schedule/request_date`, `/api/sched/states` batch, and **Command-Center Accepted/Sent/Requested badge** in v2_command.html `jobCard` (reads /api/sched/states; RESET clears it). Free-pick is HUD-only (no duplicate booking-requests surface). Parts 2/3 stay HUD-approve-first (DJ: auto later).

## The 3 parts (build order)
1. **★ PRIORITY: "Send scheduling options" 3-choice message.** Launch button on the JOB DETAIL screen (v2_field). Customer gets a proposed date + link → page (refined DJ 2026-08-04): **Btn1 "That works"** → book proposed date; **Btn2 "That day doesn't work — give me the next available date"** → show next available date(s) (route-tight, rank_days engine); pick → book; at the BOTTOM a **"None work, I'll select my own"** button; **Btn3 "I have a particular day I want to select."** **Btn3 AND the Btn2-bottom button → SAME place** = free date/time picker → "we'll confirm if available" → DJ review queue (not auto-booked). On book via Btn1/Btn2: **"Accepted" banner on the schedule front card + launch button GRAYED**. **RESET: changing date_order after grayed re-arms the button + clears the banner** (customer calls back later needing a new day).
2. **4-day confirm** ("confirm / reschedule / text us"). reminders.py already does a **3-day** confirm → change 3→4.
3. **Night-before + GATED conditional.** reminders.py night-before EXISTS with DJ's real Workiz-recovered wording. Delta = make the gate-code sentence **conditional on a real gated field** (omit entirely for non-gated); pull `x_studio_x_gate_code` when gated.

## What already exists (don't rebuild — [[project_reminder_texts_build]])
messaging.py (canonical send, STOP/DNC/quiet-hold) + reminders.py (3-day confirm + night-before, HUD-approved, live 2026-07-30) + booking portal (wscare.pro/c/<token>, [[project_customer_portal_booking]]) + specialist's v2_field appt-confirm + standalone Send-confirmation button.

## Lane split (mailed 2026-08-04) — DJ uses v2_field NOT field.html
Specialist: customer page (booking.py) + job-detail launch button/states (v2_field) + inbound reply (sms.py) + reminders.py tweaks + Accepted banner + reset hook. Lead HOOKS — **ALL 3 BUILT + LIVE 2026-08-04:**
1. **`x_studio_gated`** (boolean, field id 21376) on res.partner (Property) — night-before builder includes the gate sentence only when True, pulls `x_studio_x_gate_code`.
2. **`POST /api/schedule/request_date {so_id, date, time, note?}`** (scheduler.py) = choice-3/"select my own" landing — does NOT book; records to `wsc.schedule.requests` + SO chatter + a My Day task deep-linking `/static/owner/v2_field.html?open_so=<id>`. Returns `{ok, requested}`.
3. **book-on-confirm** = `schedule_odoo_so(so_id, dt_pt, set_status=True)` (live). #2 next-available = specialist reuses `open_days_for_partner(partner_id, 3)`. See [[project_appt_confirmation_odoo]], [[project_workiz_retirement]].
