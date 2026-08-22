---
name: Cheryl Interview Template Refinements (2026-04-26)
description: 8 template improvements based on transcript analysis; 60→90 min interview; identifies gaps between MODELS_SPEC and Cheryl's actual workflow
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## What Was Done

**Analyzed two Cheryl interview transcripts** and refined the 20-question template with 8 improvements:

### New Questions Added
1. **Q5.5 — Pre-Contract Communication Strategy** (~6 min)
   - What info does she WANT to send clients between qualification and contract?
   - Cheryl emphasized this is a major pain point (clients confused, she repeats herself, no system)

2. **Q18.5 — Automation & Triggers** (~4 min)
   - What communications should auto-send at the right moment?
   - Cheryl talked extensively about automation: "here's what you should know per stage"

3. **Q18.7 — Broker & System Portability** (~2 min)
   - What survives a broker change, what gets left behind?
   - She said "I still have stuff with old pictures, old broker information" — major pain

### Questions Revised
- **Q2** — Changed from time allocation → client segmentation (pre-qualified, active, past clients) + priority gaps
- **Q17** — Added follow-up about proof/audit trail of communications (critical for escrow compliance)
- **Q18** — Added depth: "What pain point does it solve? Which would you delete first?"
- **Q19** — Added specificity: if "dashboard" is the magic feature, get her to sketch it directly

### Metadata Updated
- **Duration:** 60 min → **75–90 min** (added 12 min of new material; can trim Q7 by 2–3 min if time-constrained)
- **Section headers:** Updated to reflect new timing allocations
- **Emphasis:** Added note that template probes deeper on 5 unmet needs (segmentation, communication, personalization, automation, portability)

**File:** `windowandsolarcare-hash/cheryl-real-estate` | `3_Documentation/INTERVIEW.md`
**Pushed:** 2026-04-26 | commit `60015bcb5a06f9185b81bcc51d69ef69c5ac7ead`

## Key Findings from Transcript Analysis

### Cheryl's Top Pain Points (in order of emphasis)
1. **Pre-contract communication cadence** — clients don't know what to expect, she sends same info multiple times
2. **Tool fragmentation** — 7–8 tools doing overlapping things (CRM, MLS, forms, texting, etc.)
3. **Personalized follow-up** — wants to send smart reminders (solar maintenance, home value updates, property-feature-based outreach)
4. **System churn on broker switch** — data and workflows don't port when she changes brokers
5. **Communication proof/audit trail** — needs documented evidence of what was sent when (escrow compliance)

### Workflow Themes Cheryl Emphasized
- **Deal stages matter:** pre-contract, under-contract, close, post-close have very different communication needs
- **Automation via triggers:** wants system to send right message at right time based on stage
- **Client segmentation:** "serve current clients first, then expand" — active deals ≠ past clients ≠ prospects
- **Data persistence:** wants to carry client history, preferences, notes across broker changes

## Gap: MODELS_SPEC vs. Cheryl's Reality

**MODELS_SPEC.md status:** DRAFT, built 2026-04-20 from contract samples + domain knowledge, NOT from Cheryl's workflow

### What MODELS_SPEC Has (✓ aligned)
- Transaction/Opportunity/Property structure (correct)
- Deal stages + state transitions (correct)
- Contact tracking (lenders, escrow, title, etc.) (correct)
- Checklist attachment at stage level (correct)

### What MODELS_SPEC Lacks (gaps to fill after full interview)
- **Cadence/communication templates** — no fields for pre-contract message sequence
- **Personalization data** — no structured fields for client preference data that drives smart sends
- **Automation rules/triggers** — no model for "send message X when deal reaches stage Y"
- **Tool integrations** — no mention of MLS sync, texting platform, calendar integrations
- **Broker/portability metadata** — no fields to mark "this stays, this goes" during broker transitions

### Next Step
After Cheryl completes the full refined interview, add fields to MODELS_SPEC:
- `x_cheryl_communication_template` model (pre-contract, in-contract, post-close sequences)
- `x_cheryl_personalization_field_id` (solar, lot size, school district, etc.) on Transaction + Property
- `x_cheryl_automation_rule` (trigger-based message sends)
- Metadata on key integrations (MLS, texting, calendar)

## How to Apply

**When to run refined interview:**
- Use the updated `INTERVIEW.md` as-is for Cheryl's next session (75–90 min allocation)
- New questions will surface the communication/automation/personalization workflows we couldn't see before
- Capture her answers inline in a fork: `INTERVIEW_CHERYL_[DATE].md`

**After interview:**
1. Extract data shape from her answers (template fields, cadence rules, personalization triggers)
2. Propose additions to MODELS_SPEC
3. Build new models for communication + automation
4. Test with her live workflow

## Files
- `3_Documentation/INTERVIEW.md` — the refined template (live on main)
- `MODELS_SPEC.md` — existing spec (needs field additions post-interview)
