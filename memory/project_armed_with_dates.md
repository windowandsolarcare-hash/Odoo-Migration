---
name: project_armed_with_dates
description: "Armed with dates" — /api/openings returns a customer's next open days + booking link; shown on the dialer + text-to-DJ so he has availability mid-call. Phase 1 of the self-scheduling-link vision.
metadata:
  type: project
---

**Why:** the most common end-of-conversation ask is "what's your next available date?" DJ wants those dates in front of him whenever he's communicating with a customer (call or text). Problem: once he taps Dial, the phone is on the call screen, not the app — so on-screen dates are lost mid-call.

**Built (2026-08-05, new_job.py + v2_dialer.html):**
- **`GET /api/openings?partner_id=|phone=`** → `{ok, name, city, options:[{date,time,label}], link}`. Wraps `open_days_for_partner` (route-tight open days for the customer's area, via scheduler.rank_days) + a customer booking link `https://wscare.pro/c/<make_token(pid)>` (booking.py). Options sorted CHRONOLOGICALLY (engine returns route-tight order; re-sorted here so it reads as "next available"). Shared builder `_openings_payload(pid)`; `_openings_pid_from_phone(phone)` resolves phone→partner (company_id in [1,False]).
- **`POST /api/openings/text_me` {partner_id|phone}** → texts DJ's OWN cell (`_send_sms(DJ_PHONE_NUMBER, …)`, raw Twilio, NOT a customer text) the openings + booking link, so he can glance at the notification shade mid-call (his solution to the "app not on screen during the call" problem — a text is a reliable, persistent native notification; web push isn't set up — no service worker).
- **v2_dialer.html:** when prefilled with a customer (`?to=`/`?partner_id=`), auto-loads `/api/openings` and shows a "📅 Next openings · <city> — <dates>" strip + a "🔔 Text these to my phone" button (`textOpenings()` → text_me). The booking link in the self-text is for DJ's REFERENCE (tap to browse further-out dates); he does NOT forward it (that'd be his personal number).

**Verified:** Rod Hahn (3233695008) → city Rancho Mirage, 3 dated openings, link `wscare.pro/c/23379-…`.

**ENGINE UNIFIED (2026-08-05, DJ):** DJ saw the /c customer booking page (leads with the route-tight "📍 We're in your area" day, others "Available") and wanted the dialer to MATCH + both on one engine. There were TWO date engines: the /c page (`api_availability` → **`booking._open_dates_for_city(city,lat,lon)`** — route-tight/fit-first) vs the dialer/inbox/sched (`open_days_for_partner` → `scheduler.rank_days`). Rewrote **`_openings_payload`** to use `_open_dates_for_city` (resolve partner→property→city+partner_latitude/longitude), so the dialer's days + order + `fit` are IDENTICAL to the /c page. Attaches a specific time per day via `scheduler.build_day_plan(lat,lon,date)['suggested_minute']` (DJ's reference; the /c page shows AM/PM for the customer). Options are in `_open_dates_for_city` order (route-first) — removed the chronological re-sort. Dialer shows "📍 We're in your area" on `fit` days; self-text marks them with 📍. STILL on the OLD engine (rank_days, not migrated — separate follow-up, touches lead's inbox assistant): `open_days_for_partner` itself, used by `/api/sched/days` (reschedule day-picker) + the inbox-assistant "when can you come".

**Next (DJ's stated direction, not built):** the same openings strip in the INBOX thread, AND inbox "action buttons" — one-tap canned/AI texts to the customer from the business line (first = "Send booking link" via the existing self-schedule link / `/api/sched/launch`; then Confirm, Running late, …; overflow → an "Actions" sheet). Coordinate with lead (they own the inbox AI-suggestion side). Related: [[project_customer_self_scheduling]], [[project_appt_confirm_ai_and_box]], [[feedback_call_opens_dialer_never_dials]].
