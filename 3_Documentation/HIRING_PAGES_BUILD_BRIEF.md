# HIRING PAGES — BUILD BRIEF (Lead Tech hire)

**Owner:** Portal (builds) · **Design** (styles) · **Started:** 2026-10-08 · DJ-directed via HR, routed by Dispatcher.
**Deadline:** P1 staged + Lead-QC'd **Thu Oct 9**; DJ sends candidate links **Fri Oct 10**; interviews **Mon/Tue PM**.
*(This file was missing from the repo when the task landed; Portal authored the build-side structure so Design and the build share one source. Content items marked **[HR/DJ]** are open — see §4.)*

## Rules (from Dispatcher)
- **Postgres for state** (NOT Odoo) — use the app's existing `psycopg` pattern (`memory_store.py` / `_MEM_DB_URL`). Interview bookings are operational/high-write + need a hard no-double-book lock → Postgres unique constraint.
- **Feature-namespaced routes** (`/interview/...`, `/hiring/...`) — portal.py-class late-registration shadow risk; namespacing avoids it.
- **DJ sends candidate links** (review-first) — pages never auto-send.
- **main.py registration** — coordinate with Specialists (additive include).
- **Deploy:** stage on branch; DJ types "deploy" in the Specialists tab.
- Candidate confirmation phone: **(760) 334-5355**.

---

## P1 — `/interview/<token>` candidate slot-booking (PRIORITY)

**Candidate-facing, mobile-first, no login, brand #1e5aa8, large-text/sunlight-readable (Design styles).**
Per-candidate token (HMAC, like booking.make_token but candidate-scoped). Token → candidate record.

**Page sections (what the candidate sees / does):**
1. Brand bar — logo + "Window & Solar Care".
2. Hero — "You're invited to interview — **Lead Technician**" + 1–2 line warm intro **[HR/DJ copy]**.
3. **Pick your interview time** — list of admin-defined open slots (Mon/Tue PM). Tap one. Slot is **locked server-side on submit** (unique constraint; if it was just taken → it drops out with "just filled, pick another").
4. **Confirm your info** — name (prefilled from candidate record), phone (required), email (optional).
5. **3 quick questions** **[HR/DJ: exact wording]** — short-answer/radio. Placeholder set until provided (e.g. years of experience · reliable transportation + valid license? · earliest start date).
6. Submit → locks slot + saves answers to Postgres.
7. **Confirmation screen** — "You're booked for <day/time>. We look forward to meeting you. Questions? Call or text **(760) 334-5355**." + add-to-calendar. **[HR/DJ: final confirm copy]**

**Admin view (DJ/HR, authed `/owner/...`):**
- Create/edit **reusable** slots (date + time, capacity 1 each), open/close them.
- See candidates, each one's booked slot + their 3 answers.
- Generate a per-candidate `/interview/<token>` link to hand DJ (DJ sends).

**Postgres tables (proposed):** `hiring_candidate` (id, name, phone, email, role, token, created) · `hiring_slot` (id, starts_at, label, is_open) · `hiring_booking` (id, candidate_id, slot_id UNIQUE, answers jsonb, booked_at) — UNIQUE(slot_id) = the no-double-book guarantee.

---

## P2 — compare grid (right after P1)

**DJ + Cheryl auth only.** Accordion by **dimension** (rows), candidates as columns; per-candidate comments.
**Proposed dimensions [HR/DJ confirm]:** Experience (window/solar) · Reliability & transport (license/vehicle) · Availability / start date · Physical / ladder comfort · Customer-facing demeanor · Pay expectation · Interview impression · References.

---

## §4 OPEN — content needed from HR/DJ (gates final copy, NOT the backbone)
1. The **3 screening questions** (exact wording + answer type).
2. The **actual interview slots** (which Mon/Tue PM date-times, how many).
3. Role **intro line** for the hero + **confirmation-screen copy**.
4. **P2 dimensions** — confirm/adjust the proposed list above.

*Backbone (routes, Postgres tables, slot-lock, admin slot editor) is content-agnostic and proceeds now; the above swap in as copy.*
