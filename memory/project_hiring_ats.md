---
name: project_hiring_ats
description: "Hiring ATS built in Render — Odoo hr.applicant backend, hiring.html frontend, Indeed JSON bulk import, AI scoring via Claude Haiku"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Hiring ATS

**Status:** Live as of 2026-05-30

**URL:** `https://wsc-field-assistant.onrender.com/owner/hiring`  
**Dashboard card:** 👥 Hiring (green, between group grid and Quick Links)

---

## Architecture

- **Backend:** `routers/owner/hiring.py` — FastAPI router, Odoo `hr.applicant` model
- **Frontend:** `static/owner/hiring.html` — mobile-first ATS, filter tabs, detail drawer
- **Job ID:** `JOB_ID = 1` (Window Cleaner, Coachella Valley)
- **Stages:** 1=Reviewing, 2=Phone Screen, 3=Interview, 5=Offer, 6=Hired
- **Sources:** 14=Indeed, 4=Facebook, 9=Craigslist, 10=Referral
- **AI scoring:** Claude Haiku via `ANTHROPIC_API_KEY` on Render, `POST /owner/api/hiring/score`
- **PDF extraction:** `POST /owner/api/hiring/extract_resume` — uses `pypdf` (NOT pdfplumber — OOM'd 512MB Render)

## Notes Format (stored in `applicant_notes` on hr.applicant)

```
{"score":2,"summary":"...","strengths":[...],"concerns":[...]}
===RESUME===
resume text
===NOTES===
Imported from Indeed (Google Drive)
===SCREENING===
screening answers (optional)
===RAW_PASTE===
raw paste (optional)
```

`parseNotes()` in hiring.html handles all sections. `serializeNotes(ai, resume, notes, screening)` writes them back.

---

## Bulk Import — 2026-05-30/31

- **46 total applicants** imported (IDs 52–97)
- **Import script:** `C:\Users\dj\indeed_import_gdrive.py`
- **38 full structured resumes** (parsed from Indeed JSON)
- **4 pasted resumes** (no structure, but have content): IDs 92 Jesus Alvarado, 93 Edgar Lopez, 94 Benjamin Whitney, 95 David Osuna
- **4 no resume** (location only — PDF files never uploaded): IDs 52 Josseph Aldana, 96 Eduardo Mosqueda, 97 Aaron Peña, 91 MARTIN Franco CHÁVEZ

### The 7 original PDF-only candidates (from Indeed JSON — no parsed resume):
Benjamin Whitney, Jesus Alvarado, Edgar Lopez, Aaron Peña, David Osuna, Eduardo Mosqueda, MARTIN Franco CHÁVEZ
- Whitney, Alvarado, Lopez, Osuna had resumes pasted in manually → now have text but no AI structure
- Aldana, Mosqueda, Peña, CHÁVEZ still have no resume body

---

## UI Features (as of 2026-05-31)

- Filter tabs: All / Reviewing / Phone Screen / Interview / Passed
- Search bar (fixed top, X to clear)
- Sort: by AI score desc, secondary by distance from home (33.8110, -116.3822)
- Detail drawer: resume, notes, screening answers fields
- ✎ Edit Resume button — textarea + Save & Re-score + Save only + Cancel
- 📎 Upload Resume button — file picker → POST /api/hiring/extract_resume → prefills edit area
- Score with AI button (blocked for PDF-only/empty resumes)
- Pass Applicant / Restore buttons

## Known Bugs Fixed (2026-05-31)

- `pdfplumber` → `pypdf` in requirements.txt (pdfplumber's Pillow dep OOM'd 512MB Render)
- Score model reverted to `claude-haiku-4-5-20251001` (Sonnet + OwnTracks GPS flood = OOM)
- `apiFetchJSON` helper added — throws clean error on non-2xx instead of crashing on `.json()`
- "Save only" button stays enabled while "Save & Re-score" is scoring (was: both disabled = stuck)
- 20s AbortController timeout on score fetch (was: could hang forever)

---

## DJ Fleet Lead Scoring Prompt (100-point system)

**Used for:** Batch scoring all 64 candidates (June 1 session). Scores were reviewed and adjusted upward by DJ + Claude Code after finding the original batch agent missed things. Adjusted top scores: Joe Quevedo 72, Mark Valdez 68, Edgar Lopez 65, Breanna Shaw 63.

```
You are an expert Applicant Tracking System (ATS) screening a batch of 60 resumes for "Window & Solar Care," a premium window and solar panel cleaning business operating in the extreme heat of Thousand Palms, CA.

We are strictly hiring for a FLEET LEAD TECHNICIAN. This individual must be capable of driving the service truck, managing a helper, interacting directly with homeowners, utilizing the Workiz dispatch app, and executing professional-grade cleans autonomously.

Process the resumes using a two-step system: a Pass/Fail Knockout, followed by a 100-point scoring system.

STEP 1: THE KNOCKOUT PHASE (PASS/FAIL)
If a resume fails either of these, score it a 0 and label it "REJECTED - FAILED KNOCKOUT."
1. Must indicate possessing a Valid Driver's License or experience driving company vehicles.
2. Must have at least some history of physical or outdoor labor.

STEP 2: THE 100-POINT SCORING SYSTEM
For resumes that pass the Knockout Phase, score them strictly using these six criteria:

1. LEADERSHIP & CLIENT COMMUNICATION (Max 25 pts):
- 25 pts: Strong history of leading crews AND interacting with clients. Keywords: "Crew Lead," "Foreman," "Customer satisfaction," "Point of contact," "Resolved complaints," "Trained new hires."
- 12 pts: Has either leadership experience OR heavy client-facing experience, but not both.
- 0 pts: Strictly a back-end individual contributor.

2. EXTERIOR CLEANING TRADE EXPERIENCE (Max 20 pts):
- 20 pts: Direct professional experience in window or solar cleaning. Keywords: squeegee, water-fed pole, pure water system, DI tank, RO system.
- 12 pts: Experience in highly adjacent trades: pressure washing, commercial roof cleaning, pool service.
- 0 pts: No related exterior cleaning experience.

3. SAFETY & FLEET DRIVING (Max 15 pts):
- 15 pts: Explicitly states experience operating company service vehicles (vans, box trucks). Extra points for safety certs (OSHA 10/30, Fall Protection).
- 5 pts: Has a license but no mention of driving fleet vehicles.
- ACTION REQUIRED FOR ALL PASSING SCORES: Output a reminder to "Verify clean DMV record during phone screen."

4. DEPENDABILITY & TRUST (Max 15 pts):
- 15 pts: High-integrity indicators with stable longevity (18+ months average per job). Keywords: "Keyholder," "Opened/closed facility," "Managed high-value equipment," "Handled invoicing," "Zero incident record."
- 0 pts: Job hopper (3+ jobs in the last 12 months) or zero historical indicators of independent trust.

5. OUTDOOR PHYSICAL STAMINA (Max 15 pts):
- 15 pts: Recent, sustained outdoor manual labor in high-exertion fields (Roofing, landscaping, solar install, construction) demonstrating the ability to survive desert heat.
- 5 pts: Heavy indoor labor (warehousing) or light outdoor work.

6. DIGITAL LITERACY & ROUTING (Max 10 pts):
- 10 pts: Proven capability utilizing field management apps and admin closeouts. Keywords: Workiz, Jobber, ServiceTitan, CRM, mobile invoicing, photo documentation.

OUTPUT FORMAT:
Do not provide 60 long essays. Group the candidates into the following three tiers:

TIER 1: FAST-TRACK TO INTERVIEW (Scores 80-100)
Provide Name, Total Score, and a 2-sentence summary of why they are a top Lead candidate.

TIER 2: CONSIDER FOR HELPER ROLE (Scores 60-79)
Provide Name, Total Score, and the primary gap preventing them from being a Lead (e.g., "Missing leadership," "No window experience").

TIER 3: REJECTS (Scores below 60 or Failed Knockout)
Provide a simple comma-separated list of names.
```

---

## Decision Values (stored in ===DECISION=== section)

`yes` | `maybe` | `no` | `follow-up`

- **follow-up** added 2026-06-04 — purple badge (↗), for candidates who need another contact attempt (e.g. no response to screening)
- Badge CSS: `.dec-badge.follow-up { background: rgba(168,85,247,.15); color: #a855f7; }`

## Grouped View (as of 2026-06-04)

Groups in order: Excellent+Yes (blue), Strong+Yes (green), Good+Yes (amber), Maybe (amber), Follow Up (purple), No (gray), Not Reviewed (slate). Collapse state persisted in `localStorage('wsc_hiring_collapsed')`. `toggleGroup(key)` function. Empty groups hidden.

## Screening Answers (===SCREENING=== section)

Uploaded from Google Doc "Responses" (Drive ID: `13KFcwVjsO0x-8rLIfiYWGfTurn-X2G6CzZRQ4zJxsNU`). Multiple messages from same candidate separated with `--- Message 1 (time) ---` / `--- Message 2 ---` headers. "No response" written literally for non-responders.

## Candidates Reviewed (2026-06-04)

- **Aaron Peña (ID 161)** — decision: no. Enrolled at UCR through 2028 (teaching degree) + self-employed window cleaner (potential spy concern). AI scored Excellent but both flags are disqualifying.
- **Eduardo Mosqueda (ID 143)** — decision: no. Location-only record, zero resume, no information provided.
- **Joseph Montoya (ID 149), Jesus Giron (ID 117), Josseph Aldana (ID 112)** — decision: follow-up. No response to screening questions.

## Dual Score Feature (PLANNED — not built)

DJ wants to compare default AI score vs. his custom-criteria score side by side.

**Why:** DJ hasn't had time to define his criteria yet. When he does:
1. Update system prompt in `hiring.py` with his criteria
2. Re-score all applicants via script
3. Store BOTH scores in notes JSON — e.g. `{"score": 2, "dj_score": 3, ...}`
4. Show both in detail drawer with labels "Default" and "DJ Criteria"

**DJ's criteria questions (not yet answered):**
1. How strict on local? Coachella Valley only, or IE/Hemet ok if they'll drive?
2. Experience weight — window/solar vs. any outdoor labor (landscaping, construction)?
3. Reliability signals — long tenure? currently employed? anything specific?
4. Red flags from past bad hires?
5. Heights/heat — ask in screening or infer from background?
6. Part-time vs full-time preference?

---

## Current Scoring Prompt (default — DJ hasn't reviewed)

Key factors in order:
1. LOCAL to Coachella Valley / Inland Empire (CRITICAL — remote = hard no)
2. Valid driver's license (required)
3. Physically able for outdoor desert work
4. Comfortable with heights and ladders
5. Prior cleaning, trade, or labor experience
6. Currently/recently employed (stability)

Scale: 0=Weak, 1=Good (worth a call), 2=Strong (prioritize), 3=Excellent (move fast)
