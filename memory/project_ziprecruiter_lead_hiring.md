---
name: project_ziprecruiter_lead_hiring
description: "ZipRecruiter hiring pivot (2026-09-27) — hiring the Fleet Lead Technician on ZipRecruiter after Indeed produced a low-caliber hire; the candidate profile, pay, ZR posting mechanics, and the Indeed-miss diagnosis"
metadata:
  node_type: memory
  type: project
  originSessionId: 966146af-3679-41f5-a78f-cd180bf33806
  modified: 2026-09-28T00:22:38.263Z
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
