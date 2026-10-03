---
name: project_booking_stale_autocomplete_coords
description: "A booking whose address was AUTOCOMPLETED to the wrong place then TEXT-corrected keeps the WRONG lat/lon: api_request trusts the page's autocomplete partner_latitude/longitude and there is NO server-side forward-geocode to re-derive from the corrected address (only a reverse-geocoder for GPS). Symptom (Del Webb SO 17732 / property 27266, 2026-10-03): address text = Rancho Mirage but stored coords = Albany NY (42.77,-73.85) → the review screen's map routes from NY AND the scheduler's drive-time (~2365 mi to the service area) rejects EVERY slot → 'No open 1.5h slots' + the manual start falls back to 8:00."
metadata:
  node_type: memory
  type: project
  originSessionId: 8a97aa73-5f27-4f02-a0f6-64f2dd10d242
  modified: 2026-10-03T03:28:23.211Z
---

**Symptom (DJ, 2026-10-03):** the Booking-Requests review screen (`static/owner/v2_booking.html` + `routers/owner/booking_requests.py`) for a Del Webb landing booking showed the route map starting in **New York** and "No open 1.5h slots" for a day that clearly had a 10:00–1:30 gap, with the manual start defaulting to 8:00 AM.

**Root cause (verified via Odoo):** property **27266** (SO 17732's `partner_shipping_id`) had the CORRECT address text (`street='21 Riesling Road'`, `city='Rancho Mirage'`) but stored **`partner_latitude=42.7692634`, `partner_longitude=-73.8471898`** — near Albany, NY (2,365 mi from Rancho Mirage, 143 mi from NYC). DJ's first address autocomplete picked a NY place; he corrected the TEXT, but the page kept the NY lat/lon and `routers/booking.py api_request` stored it. **The booking flow TRUSTS the page's autocomplete lat/lon — there is NO server-side forward-geocoder** (address→coords) to re-derive from the corrected address; the only geocoder in the app is `dashboard._reverse_geocode` (coords→address, for GPS).

**One bad coordinate causes BOTH visible bugs:**
- the review-screen MAP uses the property's coords → routes from NY.
- the SCHEDULER's drive-time from the service area to a NY point is enormous → every candidate slot exceeds reachable drive time → "No open slots" → manual start falls back to 8:00. (So the "no slots" is NOT a slot-finder gap — it's the coords.)

**How to apply:**
1. **Immediate unblock = DATA, not code:** correct the property's `partner_latitude`/`partner_longitude` to the real location (Rancho Mirage ≈ 33.74, -116.41). Map + slots recover at once. (An Operator/DJ action — don't guess-fix silently.)
2. **When "no slots" or a wrong map appears for a NEW web/Del Webb booking, CHECK the property's stored lat/lon FIRST** (is it plausibly near the service area?) before suspecting the slot-finder. A huge drive-time from bad coords masquerades as a scheduling bug.
3. **Prevent-the-class (design options, 2026-10-03):** (A) forward-geocode server-side from the authoritative address at booking/approve instead of trusting the page's autocomplete lat/lon (needs a Google Geocoding helper; `GOOGLE_API_KEY` exists); (B) the /book + /dw pages clear or re-geocode the captured lat/lon when the user EDITS the address after an autocomplete pick (Web); (C) the scheduler sanity-checks property coords against the service-area bbox and treats wildly-out-of-area coords as unknown so one bad point degrades gracefully instead of nuking all slots.
4. Unrelated same-screen cleanup shipped-staged: the review footer "Approve creates the real Workiz job" was a stale Workiz label (Workiz retired 2026-08-03) → "Approve schedules the job". Related: [[project_workiz_retirement]].
