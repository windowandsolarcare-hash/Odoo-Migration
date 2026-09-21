---
name: project_momscare_phase2_data_source
description: "Mom's Care Phase 2 (Care Assistant) licensed-data-source decision: openFDA + RxNorm for v1 (free, zero-PHI, zero license question); DDInter deferred; NIH RxNav DDI API is DEAD (Jan 2024). Plus the five hard safety gates."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-21T13:45:43.411Z
---

**Mom's Care Phase 2 = the Care Assistant** (decision-SUPPORT, NOT a doctor). Kicked off 2026-09-21 (DJ via Dispatcher). Full build spec: `windowandsolarcare-hash/saunders-render-app` → `review/momscare/PHASE2_ASSISTANT_SPEC.md` + local `C:\Users\dj\MomsCare\MOMS_CARE_PHASE2_SPEC.md`. Builder-2 = primary builder (momscare-app repo); Cheryl's-cloud = security review (her highest-risk area, a HARD gate); Audit = UX/edge pass; Lead = spec + QC.

**★ DATA POSTURE (DJ 2026-09-21):** built + polished ENTIRELY on the FICTIONAL dataset (demo persona Anita — NOT the real care recipient's name, which is scrubbed from the repo; keep it out of GitHub/chat/memory). NO real-PHI flip, NO real logins — the demo→real cutover is DEFERRED to the very end, once everything's done + looks good. Highest-risk feature built with zero real PHI at risk.

## Licensed data-source decision (the linchpin — gate: clinical facts NEVER from model free-recall)
- **NIH/NLM RxNav Drug-Drug INTERACTION API is DEAD** (discontinued ~Jan 2024, no replacement). RxNorm *name normalization* (`findRxcuiByString`, RxClass) is STILL live — use it as the drug-NAME normalizer only, not a fact source.
- **v1 = openFDA drug-label API + RxNorm ONLY.** openFDA is free, FDA-authoritative (the approved label), no key, no account, **zero PHI** (queried by drug NAME only). Sections: `drug_interactions`, `adverse_reactions`, `contraindications`, `warnings`, `boxed_warning`. Chosen because it has ZERO license ambiguity + zero PHI + no procurement. Weakness: per-drug label PROSE, not a pairwise A×B engine, no severity score — the cross-match against her med list is code we build. That weakness is exactly why the "decision-support only, confirm with pharmacist/Dr." framing is non-negotiable.
- **DDInter 2.0** (open academic, true pairwise ~302k-record matrix, self-hostable/offline = zero PHI) is a **Phase-2.1 fast-follow GATED on confirming its non-commercial license** — deliberately NOT in v1.
- **DrugBank / FDB / Medi-Span / Micromedex** = gold-standard but $50k–200k+/yr enterprise — cost-prohibitive overkill; far upgrade path. **RxLabelGuard (~$20–99/mo)** = cheap SaaS repackage of the SAME openFDA data with severity/citations — only if we later want severity without building it.

## The five hard gates (build as CODE, not prompt text)
1. Clinical facts ONLY from the fetched licensed data; no free-recall; if empty, say so.
2. **Zero PHI to the model** — payload = drug NAMES + symptom CATEGORY + fetched facts only (no name/DOB/ids/notes/docs). Source queried by drug name only.
3. **Red-flag guardrail = DETERMINISTIC CODE, PRE-model, non-overridable** (runs before record fetch + before LLM): fever/blood/chest pain/difficulty breathing/dizziness/confusion/severe pain/symptom >2 days → 911 / Kaiser nurse-line card, STOP.
4. Always cite record + source; a code POST-CHECK suppresses any answer lacking a citation or naming a drug not in her list.
5. Safety framing verbatim every clinical answer; walled off (own repo/DB/secret/AI-key; reuse `anthropic==0.122.0`).

New DATA_CLASS `assistant` (read-only; caregivers+owner, NOT Mom). Feature flag `MC_ASSISTANT_ENABLED` default OFF until all 5 gates pass + Cheryl sign-off + DJ. See [[feedback_data_location_odoo_vs_postgres]], [[project_cheryl_cloud_profile]].
