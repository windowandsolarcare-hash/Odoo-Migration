---
name: Cheryl Project — Interview to Plan Workflow (Best Practice Approach)
description: Three-phase workflow for Cheryl's real estate system: (1) Interview gathers current workflow, (2) Plan shows best-practice benchmarks vs. current state with gap analysis, (3) DJ approves the approach. NOT "sell best practice in interview" but "show best practice in plan for approval."
type: project
originSessionId: 7b5c02c5-8e4d-4515-9792-ed30f27fe6c4
---
## The Workflow

### Phase 1: Interview (Gather Data — Current State Only)
**What happens:** Refined 29-question interview template walks through her real deal workflow, pain points, tools, what she wants.

**What we're collecting:** 
- How she actually works now
- Where it hurts (Q14: "what would you pay to outsource?")
- What she aspires to (Q19: "magic feature?")
- Business metrics (volume, close ratio, revenue mix)
- Adoption readiness (Q23: how she learns, what makes tools stick)

**What we're NOT doing:** Selling best practices in the interview. No "top 1% agents do X" comparisons. Just listen and gather.

**Output:** Interview answers captured in `INTERVIEW_CHERYL_[DATE].md` (fork of template with her answers inline)

---

### Phase 2: Plan (Show Best Practice vs. Current State)
**What happens (AFTER interview):** Claude researches real estate best practices, builds a proposal showing:

**Structure:**
1. **Current State Summary** (from her interview)
   - How she works now (deal flow, tools, team, metrics)
   - Top 3 pain points she mentioned
   - What she aspires to

2. **Best-Practice Benchmarks** (real estate industry standards)
   - Lead follow-up cadence (daily hot, weekly warm)
   - Referral generation system (ask at close, track sphere, nurture)
   - Communication templates (pre-contract, in-contract, post-close sequences)
   - Automation triggers (milestone-based sends)
   - Metrics tracked (close ratio, days-on-market, CAC, LTV, referral %)
   - Past-client revenue (typically 40-60% for top agents)
   - Time allocation (highest-value activities vs. admin)

3. **Gap Analysis** (Current vs. Best Practice)
   - Where she aligns with best practice (keep/strengthen)
   - Where she has significant gaps (opportunities for improvement)
   - What's blocking her from best practice (time, knowledge, tooling, discipline)

4. **Proposed System Architecture**
   - How we'll close the gaps
   - What we'll automate vs. what stays personal
   - What data/tools/workflows we'll build
   - Timeline and phases

**Output:** Proposal document (PDF or Google Doc) ready for DJ + Cheryl review and approval

---

### Phase 3: Approval & Refinement
**What happens:** DJ and Cheryl review the plan together.

**Outcomes:**
- Cheryl sees best practice + where she is vs. that (no surprises)
- Cheryl approves the approach (or asks for adjustments)
- We have explicit buy-in on "we're building a best-practice system, not just automating what you do now"
- Scope and priorities are locked in before we build

---

## Why This Workflow

| Mistake | Why It's Bad | Our Approach |
|---|---|---|
| Sell best practice IN interview | Feels preachy, defensive, wastes interview time | Gather data first, show best practice in plan with context |
| Build system to her current workflow | Locks in her inefficiencies | Build to best practice, she approves before we build |
| No explicit discussion of best practice | She might expect automation of status quo | Plan shows "here's best practice, here's the gap, here's how we close it" |
| Scope creep later | "Why didn't you include X from best practice?" | Approved plan = locked scope |

## When to Apply This

**Timing:**
- Interview: 2026-04-26 or later (when Cheryl is ready, 75–120 min)
- Post-interview: Claude builds best-practice proposal (1–2 days)
- Review: DJ + Cheryl discuss, approve, iterate (scheduled with Cheryl)
- Build: Only after written plan approval

**Key Decision Point:** Before Claude writes ANY code or builds ANY system, there must be an approved plan that shows:
✅ Current state
✅ Best-practice benchmarks
✅ Gap analysis
✅ Proposed architecture
✅ DJ + Cheryl sign-off

---

## What "Best Practice" Means Here

Real estate best practices (sourced from industry studies, top-agent playbooks, automation platforms):

1. **Lead Management** — Systematic follow-up (hot: daily, warm: weekly, cold: monthly)
2. **Referral Generation** — Ask at close, track source, nurture sphere (should be 40–60% of revenue for mature agents)
3. **Communication Cadence** — Pre-contract weekly, in-contract milestone-triggered, post-close nurture schedule
4. **Automation** — Trigger-based messages (inspection day, appraisal complete, 30-day post-close, anniversary, market update)
5. **Metrics** — Close ratio, days-on-market, cost per lead, lifetime value by source, referral attribution
6. **Data** — Centralized contact DB, complete transaction history, preference tracking, searchable communication logs
7. **Checklists** — Stage-based workflows to prevent dropped balls
8. **Time Allocation** — Top agents spend 60%+ on highest-value activities (client calls, negotiations, referral cultivation), 40% or less on admin

---

## Files Involved

- `3_Documentation/INTERVIEW_BEST_PRACTICES.md` — The 29-question template (workflow-focused, not best-practice-focused)
- `INTERVIEW_CHERYL_[DATE].md` — Cheryl's interview answers (will be created during interview)
- `CHERYL_PROPOSAL_BEST_PRACTICE_[DATE].md` — The plan showing current vs. best practice (will be created post-interview)
- `MODELS_SPEC.md` — Will be updated based on best-practice system requirements (not interview answers)

---

## Key Principle

**Interview = Data gathering. Plan = Best practice presentation & approval. Build = Execute approved plan.**

Don't mix them. The interview doesn't need to sell best practice — the plan does, with context and data to back it up.
