---
name: project_ziprecruiter_lead_hiring
description: "ZipRecruiter hiring pivot (2026-09-27) — hiring the Fleet Lead Technician on ZipRecruiter after Indeed produced a low-caliber hire; the candidate profile, pay, ZR posting mechanics, and the Indeed-miss diagnosis"
metadata:
  node_type: memory
  type: project
  originSessionId: 966146af-3679-41f5-a78f-cd180bf33806
  modified: 2026-09-30T21:30:05.104Z
---

## ZipRecruiter Lead Hire (started 2026-09-27)

**Channel pivot:** ALL prior hiring ran through **Indeed** (see [[project_hiring_ats]]) and produced a **low-caliber hire.** This round = **ZipRecruiter**, for higher-quality candidates. First time on this channel — fresh ground.

### The Indeed-miss diagnosis (DJ 2026-09-27)
Root cause was NOT the platform — **the post was written for an ASSISTANT/helper role**, so it signaled "low bar / entry-level" and attracted assistant-caliber applicants. **Fix = write the post for the LEAD.** (HR principle: you attract the caliber you write for. Low pay + helper wording say "low bar" twice.) This matches the existing 100-point Fleet Lead scoring rubric in [[project_hiring_ats]].

### The role & pay (confirmed by DJ)
- **Role:** Fleet Lead Technician — drives the service truck, runs a helper, homeowner-facing solo, executes premium residential window + solar cleaning autonomously, uses the field app for closeouts. Coachella Valley (Thousand Palms yard), desert heat.
- **Pay:** **$23–27/hr DOE** (confirmed). Rationale: local CV window cleaner ~$21–22/hr, CA technician avg ~$25/hr, leads/supervisors above that. Posting a stated range at the TOP of local market both signals "real lead role" and filters tire-kickers. Underpaying $2/hr to save money is how you get another cheap hire who quits — a bad hire costs far more than the wage gap.
- **Hours:** default full-time, M–F daytime (reversible — confirm with DJ if he wants part-time-to-grow like the last assistant post).

### Candidate profile (DJ-defined + HR additions)
**Must-haves (→ ZipRecruiter deal-breaker screening qs, auto-filter):** valid CA license + **clean DMV** (driving the truck = safety/insurance, non-negotiable); comfortable on a ladder ~1 story; can work full days in **CV summer heat 100°F+** (the single most CV-specific filter — many quit by July); reliable transport to the yard + shows up on time.
**Pluses (name in the post; score, don't knockout):**
- Window/solar cleaning experience (definite plus).
- **Route-service background** = the temperament signal DJ values most: pool, pest control, landscaping, irrigation, gutters, pressure washing, solar install, holiday lights, alarm/security field tech, appliance/HVAC service, mobile detailing, delivery driver — anyone who runs a residential route solo is trained to be reliable, self-managing, customer-facing.
- Selling / **upselling** experience (screens, solar, frequency upgrades).
- Reliability/tenure (18+ mo per job, not a job-hopper) — #1 predictor of a hire that STAYS.
- Trust signals (keyholder, handled cash/high-value gear) — he's alone at homes with gate codes, sometimes taking payment.
- Crew-lead/trainer/foreman history (he'll run a helper).
- Bilingual English/Spanish (job-related plus for the CV customer base).
- Phone/field-app comfort — **kept a PLUS, NOT a must-have** (DJ 2026-09-27: the app is basic; anyone with a phone should manage it).

**Red flag to SCREEN OUT: a currently self-employed window cleaner** — competitor/spy risk + won't stay under someone. Burned last round (Aaron Peña, [[project_hiring_ats]]). Handle as a review-flag screening question, not a blunt auto-reject.

### ZipRecruiter posting mechanics (learned 2026-09-27)
- **Screening questions:** attach **3–5**; can mark as **"deal-breaker"** = auto-filters candidates who fail. Mix yes/no deal-breakers (license, heat, ladder, availability) + free-form (route/route-selling experience, self-employed flag).
- **Post:** recognizable title + industry terms (not internal jargon); structured sections (responsibilities / qualifications / **stated comp** / location / arrangement) so ZR's matching tech reads it.
- **Speed:** respond to strong applicants within ~3 days (I'd move faster — good people are hired within days). Same as [[project_hiring_screening_messages]]: no promises/timelines in the screening message.
- Runs through the existing ATS ([[project_hiring_ats]]): `hiring.py`/`hiring.html`, `hr.applicant`, JOB_ID=1. There's already an `import_zip_preview` endpoint (built for Indeed ZIP export — verify whether ZipRecruiter's export drops into the same parser or needs a tweak before bulk import).

### Referral in parallel
The $250 employee referral ([[project_employee_referral_program]]) is a strong parallel channel (referred hires stay longer). NOTE: its send mechanism in memory is **Workiz-based = RETIRED** — a referral blast now goes via **Twilio**, not Workiz. Concept + message text still good.

**Why:** first ZipRecruiter run — capture what works here so the next hire is faster. **How to apply:** reuse this profile + the deal-breaker screening set; log ZR results (response quality vs Indeed) back here.

---

## ★ ATS DECISION (DJ 2026-09-27): run hiring NATIVELY in ZipRecruiter — RETIRE the custom Odoo ATS
DJ chose **Option A**: manage the pipeline inside ZipRecruiter's own tools; **stop using / retire** the Odoo custom ATS ([[project_hiring_ats]] — `hiring.py`/`hiring.html`). Flag Lead to deprecate/park it (don't rebuild).
- **Why the custom ATS existed = the Indeed clunk:** Indeed MASKS contact info (`@indeedemail.com` relay), delivers unstructured PDF resumes + screening answers in a separate doc → we built bulk-JSON import + a fragile marker-parser + AI scoring just to wrangle it. That complexity IS the friction DJ wants gone.
- **ZipRecruiter fixes it natively:** gives the applicant's REAL phone + email (no relay); dashboard IS a light ATS — Candidates list, AI rating/match, drag-through **hiring stages**, in-app messaging, **ZipIntro** (one-way video screening), **Schedule** tab; screening questions auto-filter. Matches DJ's ask: "less customized, just take applicants and move them through stages."
- **No clean pull-out:** ZipRecruiter's automated candidate feed is a **Partner API (ATS-vendor only, formal agreement — atsintegrations@ziprecruiter.com)**, NOT available to a normal employer account. So a custom ATS would STILL need manual data entry → not worth it for occasional hiring. Revisit only if hiring becomes frequent/multi-role AND partner access is realistic.

## ★ RECORD-KEEPING (DJ 2026-09-27) — the employer holds the duty, NOT the job board
- **Correct DJ's assumption:** ZipRecruiter retains data per ITS OWN terms/policies (and can purge/close/delete) — it is NOT your legal record-keeper and does not discharge YOUR retention duty. If you ever need records for a claim, have your OWN copies; don't rely on ZR still having them.
- **The law (not legal advice — confirm w/ an employment attorney/HR service, esp. once ≥5 employees):**
  - **Federal (Title VII/ADA/ADEA):** keep applications/resumes/hiring records ≥ **1 year** from record date or hiring decision. (Applies at 15+ employees; ADEA 20+.)
  - **California FEHA:** retain applications/personnel records **4 years** (from creation or the employment action). FEHA generally applies at **5+ employees** — DJ is currently below that, so the 4-yr rule may not strictly bind yet, but follow it as best practice as he grows.
  - **For the HIRED person (regardless of size):** I-9 (retain 3 yrs after hire OR 1 yr after termination, whichever later), W-4, CA new-hire paperwork, offer letter — separate from application retention.
- **Practical plan (keep it simple for a business this size):**
  - **At hire:** download the FINAL candidate's resume + application + screening answers (+ later signed offer/I-9/W-4) → save to Google Drive / Saunders Vault. (HR/Operator can do this via the ZR dashboard when the hire lands.)
  - **Anyone actually INTERVIEWED:** keep their resume/app ~1 yr (smaller set, highest claim risk).
  - **Mass of unqualified applicants:** leaving on ZipRecruiter is an acceptable practical choice at this size — understanding it's convenience storage, not a guaranteed legal archive.

## Candidate message templates (approved 2026-09-27) — NO promises of a call/timeline (the Indeed burn, [[project_hiring_screening_messages]])
**★ LOCKED first reach-out (DJ 2026-09-30) — send in ZipRecruiter to applicants who cleared the 4 deal-breakers; carries the experience ask (old Q5) + tests interest; "possible fit" not "strong fit" (no over-promise):**
> Hi [Name], thanks for applying for the Lead Window & Solar Cleaning Technician role at Window & Solar Care — looks like a possible fit. Before we go further, tell me a bit about your experience with window or solar cleaning, or running a residential route (pool, pest control, landscaping, etc.), and what you're looking for in your next job. — Dan

**Second touch — call invite (only after they reply well; a real reply = still interested):**
> Thanks [Name], that's helpful. I'd like to set up a quick call to talk it through. What days and times work for you in the next few days? — Dan

*(Ghosts self-select out — that's the interest filter by design. Deliberate steps, but reply to THEIR replies within a day or two so slowness = steps, not going dark.)*

**Polite "not this round":**
> Hi [Name], thank you for taking the time to apply — I appreciate it. We had a strong response and have moved forward with a small group for this round. I'll keep your information on file and reach out if something opens up. Thanks again for your interest in Window & Solar Care. — Dan

## Interview scorecard (1–5 each, notes separate from score)
Reliability (real tenure, owns mistakes, on time to interview) · Route/customer-facing (ran a route solo, homeowner stories) · Cleaning/trade skill · Heat & physical (sustained outdoor in a hot season) · Presentation (neat, professional, easy conversation — would you put them in a client's home?) · Leadership potential (can train/check a helper) · Trust ("I'd hand this person a truck").
STAR Qs: unhappy customer + what you did · a job you stayed at long + why · hottest day of outdoor work · a time you noticed a customer needed something extra. Red flags: vague answers, blames every past boss, late/no-show, currently self-employed cleaner, job-hopper.

## Screening-question set (to enter in ZR before posting — deal-breakers auto-filter)
Deal-breakers: (1) valid CA license + clean driving record? (2) work outdoors 100°+ heat a full day? (3) comfortable on a ladder up to one story? (4) reliably commute to job / daily meet-up spot? · Info (not knockout): (5) short-answer route/homeowner experience; (6) currently running your own window cleaning business? (flag, not auto-no). Optional (DJ's call): Work Authorization; Background Check.

## Draft state (2026-09-27)
ZR job DRAFT id `2de9bdcf` (Window & Solar Care account, "Welcome back, Dan"): title "Lead Window & Solar Cleaning Technician (Route Driver)", Palm Desert CA on-site, within 50 mi + relocate OFF, Full-Time, $23–27/hr. Company "About" blurb fixed to established/steady. **Cheryl's feedback folded in (2026-09-27):** description closing line changed to "about 32 to 40 hours a week to start, year-round, at $23-27/hr DOE. Please note this position does not include health insurance." (Cheryl: honest hours since ~32 to start, and state no-insurance up front so needers bow out early; DJ agreed. Employment-type field kept "Full-Time".) **★ LEAD-ONLY DECISION (DJ 2026-09-30):** considered posting a combined $20–27 range to cover an assistant fallback (assistant tier $20–24, lead $23–27), but DJ chose to KEEP $23–27 and hire for the LEAD ONLY. Description rewritten to drop the "come in as the Lead OR the Assistant" fork — now opens "We're hiring one Lead Technician to run our route" and keeps the honest growth arc (start alongside owner → trained → run route → eventually lead an assistant of your own). If a strong applicant turns out assistant-caliber, DJ handles that as a SEPARATE offer/conversation, not in the post. Pay field + hours line stay $23–27. **★ FUNNEL DESIGN (DJ 2026-09-30):** DJ deliberately DELETED the experience question (old #5) from the ZR application and MOVED it into the FIRST REACH-OUT message. Rationale (his): a checkbox on an app is low-effort and everyone can "fast-walk" it; requiring a REPLY to a direct message tests genuine INTEREST + responsiveness (job-relevant for a homeowner-facing lead) and weeds out app-spammers. He's optimizing for the reliable 7/10 who really wants the job and will STAY over the 10/10 who bolts (retention-first — the last hire's problem was fit/staying). He knows he may lose the fastest top candidate; accepts it (he's a deliberate mover anyway). App now = **4 deal-breaker screening Qs only** (license/DMV, heat, ladder, commute — all auto-filter). ⚠ The self-employed-cleaner flag (old #6) did NOT persist from the 2026-09-27 session (only 5 Qs were live on re-open; now 4 after deleting experience) — DJ DECIDED (2026-09-30) NOT to re-add it: a competitor won't answer a "do you run your own window business?" question honestly, so it gives false comfort and wastes a screening slot — it surfaces on its own in the reach-out experience answer + the interview ("comes out in the wash"). App stays at the 4 deal-breakers, final. Message wording changed "strong fit" → "possible fit" (no over-promise). **Screening questions ENTERED + SAVED (2026-09-27):** 6 total — Q1 license+clean DMV, Q2 100°F+ heat full day, Q3 ladder 1 story, Q4 reliable to daily meet-up on time (all 4 **Deal-breaker**, Yes=correct/auto-hide) + Q5 route/homeowner experience (Required long answer) + Q6 currently self-employed window cleaner? (Required Yes/No **flag**, not a knockout — captures the answer). PENDING before DJ hits Post Job: DJ's final review + **Post Job** (he handles any plan/payment prompt — Standard plan, 0 job slots); OPTIONAL fix of the 140-char "Why work at this company?" one-liner (still says "growing local company" — only editable via company profile, not the job screen). Email draft of the full posting sent to Cheryl (cjcherylcj@gmail.com) for input (DJ decided NOT to wait on her — she catches up after). ⚠ ZR pages glitch under automation (renderer timeouts + auto-zoom); the RELIABLE method = `find` + `read_page` + `form_input`/ref clicks + `browser_batch` (screenshots time out). Custom Yes/No question flow: click "Add a custom question" → click "Yes/No" type → fill question text, tick Answer-1 "Correct" (=Yes), pick Deal-breaker/Required radio → Add; then "Save Questions" to persist. Refs churn after every add — re-find each time.


## ★ POSTED LIVE 2026-09-30
Job `2de9bdcf` is **Active** on ZipRecruiter (Window & Solar Care account). Post went through the plan step cleanly. ⚠ Employment-type shows **Part-time** on the live post (was Full-Time when built — changed during the post/plan step; flagged to DJ to confirm intended vs revert to Full-Time). Next: applicants arrive pre-filtered by the 4 deal-breakers → new-candidate email alerts to windowandsolarcare@gmail.com → work them in the Candidates tab (rate/stage/message). HR to help triage: first reach-out to keepers, 'not this round' to passes; download the final hire's resume+application+I-9/W-4/offer to Drive at hire.
