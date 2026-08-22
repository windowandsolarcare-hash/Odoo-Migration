---
name: project_reactivation_sent_book
description: "Reactivation \"Sent\" tab — manually book a customer who replied to a reactivation text directly (not via Calendly) + close the CRM lead"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Shipped 2026-06-09.** Manual booking path for when a reactivation customer calls/texts back instead of using the Calendly link. DJ wanted this because he doesn't yet trust Render Claude to do it conversationally — this is a deterministic button flow, no LLM.

## Where it lives
`reactivation.html` (repo saunders-render-app, `static/owner/reactivation.html`). Header toggle `[ To Send ] [ Sent ]`. "To Send" = existing candidate list. "Sent" = open reactivation leads awaiting booking (searchable by name, count badge).

## The flow
Tap Sent → tap a lead → see the exact quote that was texted (`x_price_list_text`) → **Book Job** sheet:
- **Suggested slots** (top 3) from `_find_scheduling_openings` called DIRECTLY (no Claude layer) — see [[project_scheduling_app.md]].
- **Job type** picker (9 service types), default from `last_job_type` (returned by suggest) or parsed from quote; multi-line quote → "Combination of Services".
- **Date + time** pickers (tap a slot to fill, or override).
- **Book It** → converts the graveyard Workiz job IN PLACE (`JobType` + `JobDateTime`, Pacific 'YYYY-MM-DD HH:MM:SS'), NO SubStatus (DJ sets line items + Scheduled himself in Workiz), then closes CRM lead → Won. Opens the Workiz job link.
- **Not Interested** → lead → Lost.

## CRM stage IDs (crm.lead) — VERIFIED 2026-06-09
- `5` = "Attempt 1 - Sent" (where reactivation leads land — the OPEN backlog)
- `4` = "Won" (is_won) — booked
- `6` = "Lost" — declined
As of 2026-06-09: 195 leads stuck open in stage 5 (never closed), 30 in Won. This tab is how they get closed going forward.

## Endpoints (reactivation.py, prefix /owner)
- `GET /api/reactivation/sent` — open leads (stage 5 + graveyard uuid set). Fields off crm.lead: name, partner_id, city, expected_revenue, x_primary_service, x_price_list_text, x_workiz_graveyard_uuid/link, create_date (=date sent).
- `GET /api/reactivation/suggest?partner_id=` — lazy-imports `_find_scheduling_openings({'partner_id':id,'structured':True})`. Returns dict {options, last_job_type, matched_city, day_labels} OR (if string) {options:[], note} → form falls back to manual pickers.
- `POST /api/reactivation/book` — {lead_id, graveyard_uuid, job_type, date, time}. workiz_post update JobType+JobDateTime, crm.lead → stage 4, chatter breadcrumb.
- `POST /api/reactivation/decline` — {lead_id} → crm.lead stage 6.

## field.py change (surgical, Render Claude path untouched)
`_find_scheduling_openings(args)` gained: (1) `args['partner_id']` → exact resolution instead of fuzzy name; (2) `args['structured']` → returns dict (options with date ISO, time, job_count, min_dist + last_job_type) instead of the human string. When neither set, behaves exactly as before for find_next_opening tool.

## Clipboard preload on Book (fixed 2026-06-18)
The Book sheet copies the item+price to the clipboard so DJ pastes them into the Workiz job (same 2-clip flow as Duplicate/Phase-5: price then name → keyboard clipboard history). `reactCopyItems(text)` parses `Name: $Price` lines. Source = the editable **bk-pricing** box, prefilled from the lead's `x_price_list_text` (e.g. `• Windows In & Out - Full Service: $160`).
- **BUG (DJ reported, Dwight lead 182):** clipboard wasn't preloading. Root cause: `doBook` copied AFTER the slow `/api/reactivation/book` fetch (Workiz GET+update+Odoo writes), and then immediately did `location.href='/owner/'`. On mobile the clipboard write after the long await + the teardown navigation silently failed (writes caught by try/catch). The data was fine (graveyard `next_job_line_items` had the item).
- **FIX:** copy ON THE TAP, before the fetch — `reactCopyItems(bk-pricing.value || l.price_list)` runs first (within user activation), server `d.line_items` kept only as a fallback if the box was empty. **LESSON (applies to all "open Workiz with items" flows): do the clipboard write within the user gesture, before any slow network call — copying after a slow `await` and/or before a `location.href` navigation fails on mobile.** Duplicate flow works because its copy isn't followed by a navigation; reactivation had the extra `location.href`.

## Booking Requests also preloads items now (2026-06-18)
DJ's Dwight case: he'd sent Dwight TWO reactivation touches → two parallel jobs. The reactivation graveyard (UI1RBG, lead 182) had the $160 item; but DJ actually booked via **Booking Requests → Approve & Create**, which clones the customer's most recent same-type job into a fresh Workiz job (SO 004771 / 18XXY4) — that came across blank (Workiz create can't set structured line items). Fixed: `api_booking_request_approve` (booking_requests.py) now returns `line_items` = the SOURCE (cloned-from) SO's `sale.order.line` (name+price); `booking_requests.html` makes the success-screen **"Open in Workiz"** button copy them on tap (price then name) then open — same robust on-gesture clipboard pattern. New customers with no prior same-type job still create blank (and approve already errors if no source job exists). Also closed the duplicate lead 182 → Won.

## Not tested (mutating) — DJ runs first real one
`/book` and `/decline` were NOT smoke-tested (would mutate real Workiz job + CRM lead). Read paths (/sent, /suggest) verified live against real leads. See [[feedback_no_mutating_smoketest_payroll]].
