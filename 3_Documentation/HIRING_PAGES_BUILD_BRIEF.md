# Hiring Pages — Build Brief (from HR, 2026-10-08)

Two web pages for the Lead Window & Solar Cleaning Technician hire. Both on **wscare.pro / Render** (our own infra — real server-side state). DJ wants both **routed through Dispatcher**, who funnels to Portal (build) + Design (look). **Deadline driver:** interviews are **Mon Oct 12 and Tue Oct 13 afternoons**, so Page 1 must be live and links sent by **Fri Oct 10**. Page 2 is needed for the interview decisions right after.

Brand: dark-blue accent **#1e5aa8** (DJ's default), large-text / high-contrast / sunlight-readable, **mobile-first** (both DJ/Cheryl and candidates are on phones). Company name is **Window & Solar Care** (no "A"). Main line to display: **(760) 334-5355**.

---

## PAGE 1 — Interview Booking Page (self-service, first-come slot lock)

**Who uses it:** the 7 candidates who replied (external applicants, NOT logged into anything).
**Goal:** each gets a personalized link, picks one phone-screen slot, and that slot **locks server-side instantly** so no one else can take it (no double-booking).

**Job refresher at the top of the page** (DJ, 2026-10-08 — candidates applied to hundreds of jobs and don't remember us; remind them before they book). Condensed FROM THE ACTUAL ZR POSTING (full text: `4_Reference_Data/ziprecruiter_lead_job_posting_2de9bdcf.md`). Use this verbiage:
> **About Window & Solar Care** — a premium residential window and solar panel cleaning company serving the Coachella Valley.
> **The role — Lead Technician (Route Driver).** You'd clean windows and solar panels to a premium standard at homes across the valley, drive the company truck, and run a daily route — working directly with homeowners. You start out alongside the owner learning how we do things, then run the route yourself, with a path to leading your own assistant down the road. A real career track, not a dead-end job.
> Each morning the crew meets near the first job — leave your car, ride in the truck, back to your car at day's end (no commute to a shop). Full-time and year-round, outdoors in the desert, comfortable on a one-story ladder. About 32–40 hrs/week, $23–27/hr depending on experience.

**Per-candidate personalized link** (e.g. `wscare.pro/interview/<token>`): the token maps to the candidate so the page **greets them by name and pre-fills the name field** (editable). One token per candidate. The 7 (rank order):
1. Fernando Marentes
2. Norberto Villa
3. James Rose
4. Joshua Bogle
5. Brian Cummings
6. Alfonso Sarabia
7. Austin Moore

**Slot grid** — 30-min slots, candidate taps one, it locks and disappears for everyone else:
- Mon Oct 12: 1:00, 1:45, 2:30, 3:15 PM
- Tue Oct 13: 1:00, 1:45, 2:30, 3:15 PM
(8 slots, 7 candidates. Admin needs a way to edit slots/dates for future hires — make it reusable, not hardcoded to these dates.)

**Fields when booking:**
1. **Best phone number** — the number we'll call. (No reliable pre-fill source; candidate enters/confirms it. This is also how we capture/confirm their number.)
2. **Earliest you could start?** — short text.
3. **"Any question you'd like us to answer on the call?"** — open text, optional.
- NO pay question (DJ 2026-10-08 — it's in the job description; dropped).
- Static prep line on the page: *"Be ready to talk about working outdoors on ladders/roofs in desert heat, and why you're looking for a long-term position."*

**Platform decision (DJ 2026-10-08):** ZipRecruiter has NO native phone-screen scheduling (only ZipIntro, which is video + AI-matched — doesn't fit our curated 7 + phone preference). So scheduling lives on OUR page. The booking LINK is sent to candidates through **ZipRecruiter messaging** (keep the conversation on-platform), and **DJ sends the links himself**. Confirmation page + callbacks use the **main line (760) 334-5355** (DJ chose main line over a spare).

**Confirmation screen after they pick:**
> "You're set — **[Day, Date] at [Time]**. We'll call you at **[their number]**. Caller ID will show our main line, **(760) 334-5355** — save it so you know it's us."

**Admin side (DJ):** a simple view of who booked which slot + their answers (phone, start date, their question). Could notify DJ on each booking.

---

## PAGE 2 — Candidate Comparison Page (editable by DJ + Cheryl)

**Who uses it:** DJ and Cheryl only — **both can edit and leave comments.** Needs auth (magic-link or login) scoped to the two of them. This is Cheryl's request: compare candidates **visually, side by side**, instead of a doc that scrolls off-screen.

**Layout:** side-by-side **compare grid / table** of candidates. Per candidate, these are visible/accessible in one place (the part DJ says isn't linkable today):
- Tier (A/B/C/D), fit note
- **Contacted?** / **Replied?**
- **What we asked / reached out about** (the outreach + the phone-screen ask)
- **Their reply** (full text)
- **Skills**, **Experience** (from resume)
- **Resume link**
- **DJ notes** and **Cheryl notes** — editable, saved per candidate
- A shared **comment field** per candidate

**Interaction DJ/Cheryl want:** **expand/collapse by dimension** — e.g. open "Responses" and see everyone's responses together, collapse it, open "Skills" and see everyone's skills, then "Experience," etc. So it's grouped by attribute across candidates, collapsible to avoid clutter, leave-open if they want. Accordion-style.

**Data source** — all content already assembled by HR; builder can pull from these:
- Doc 1 (Evaluations, all 22 by tier): `https://docs.google.com/document/d/1UJFpnL0miP8s0GRZPkCI6HEaBxzrouQWVel5P12biCQ/edit`
- Doc 2 (Responses ranked 1–7 + quotes): `https://docs.google.com/document/d/1vgZBp2B-QpUt4tZiCZEle-u3TgeyLouwcnCB9G_c6OQ/edit`
- Resume PDFs folder (22 files): Google Drive folder ID `1I_Qe2oIXRUbzk9Eq4jpw6gr5Je2FnxXc`
- Working CSV: `4_Reference_Data/ziprecruiter_lead_applicants_2026-10-02.csv`
- Resume links are `https://drive.google.com/file/d/<FILE_ID>/view` (IDs are in Doc 1/Doc 2 after each person).

Scope v1 can focus on the **9 contacted** (7 replied + 2 awaiting) since those are the live comparison; include all 22 if easy (backups C/D).

---

## Notes for the builders
- Page 1 is the priority (interview deadline). Page 2 right behind it.
- HR owns the candidate CONTENT (evaluations, responses, what-we-asked, tiers) — ping HR for any content questions. Portal/Design own the build + look.
- Reusable for future hires where practical (don't hardcode this one job's dates/candidates any deeper than necessary).
