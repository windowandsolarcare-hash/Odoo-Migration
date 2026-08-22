---
name: project-open-tasks
description: Running task list — open items to pick up next session. Check this at session start.
metadata: 
  node_type: memory
  type: project
  originSessionId: 8e984a7e-5f77-4f3b-b6bf-41405514c5d2
---

## Open Tasks

> **Strategic roadmap** (the bigger "complete the system" build list) lives in [[project_system_roadmap]] — read it when DJ asks "what's next". The table below is the granular running list.

| Created | Task | Context |
|---------|------|---------|
| 2026-06-17 | **AI answers inbound texts + phone calls (AI receptionist)** — DJ-requested | Auto-answer inbound SMS (book/reschedule via `rank_days`, answer Qs, handle reactivation replies, escalate) + AI voice for missed/after-hours calls. Needs Twilio A2P (#5) + Voice number. Approve-first → autonomous. Roadmap #13 in [[project_system_roadmap]]. |
| 2026-06-17 | **Revisit Render Claude — make him better** — DJ-requested | Audit + upgrade the field assistant: SYSTEM_PROMPT, tool set/capability gaps (give him the customer brain + `rank_days`), numbered-list UX, model/cost, reliability. Roadmap #14. |
| 2026-06-16 | **Customer-tab "brain" — next ideas (DJ wants to revisit)** | Two follow-ups to the property-header + full-SO build ([[project_customer_search_multifield]]): (1) **Editable property-header fields in place** — edit gate code / pricing / frequency / type-of-service right from the customer card (writes to the Property master `res.partner`; mind the SO-snapshot vs Property-master split + the SA-955 roll-up). (2) **Quick action button on the customer header** — one-tap "Book / Reactivate" (Book → New Job/booking flow prefilled for this customer; Reactivate → `/owner/reactivation?contact_id=`). Backend already returns property fields via `/api/customer_jobs` and full SO via `/api/so_full`. |
| 2026-06-16 | **Bev Hartin cleanup DONE + set up as reactivation test** | Deleted test SOs 004581/004583 + their posted invoices + 3 test payments ($4 from Chase) + Workiz jobs HW3N5B/K68L24. Kept real 002134/002135. Archived fake property 26326 "123456 Main St". Corrected contact 23629 gating fields (last_visit_all_properties→2023-06-14, last_reactivation_sent→False, next_job_date→False) → **she now shows on reactivation candidates** (Rancho Mirage/Window). Email+phone already = DJ's (dansyourrealtor / 951-972-6946) so the test text comes to DJ. Workiz-only leads #4526-4529 not found via API (gone or unscheduled). DJ to LAUNCH the reactivation. |
| 2026-06-15 | **Fix: follow-up flow mints un-synced Workiz re-engagement leads that pile up** | Each follow-up send creates a new Workiz "Re-engagement Lead" with no Odoo record; they accumulate (Bev had 4). Decide single-graveyard-record vs cleanup. See [[project_workiz_jobs_not_in_odoo]]. |
| 2026-06-14 | **TABLED: move Calendly off Zapier → Odoo webhook (capture-first)** | DJ's reliability concern. Calendly retries 25×/24h on non-2xx but Zapier 2xx's instantly before processing = effectively fires-once today. Target: Calendly→Odoo webhook, store-payload-first→2xx→process idempotently. Full plan + Calendly retry facts in [[project_calendly_offzapier_odoo_webhook]]. Part of dropping Zapier. |
| 2026-06-14 | **Saunders Printing — local-view card pricing (DEFERRED by DJ)** | HOF local-view cards (H1000/H1028/H1134/H1138/J7164/P3819) list at $0.15 but billed $0.25; product-driven invoicing would bill low. DJ said "deal with later." Confirm price + update those products. See [[project_zoo_printing_automation]]. |
| 2026-06-11 | **LATER (after Workiz is gone):** merge duplicate Property records into one per address with one agreed-upon name | Workiz kept creating a NEW res.partner Property record (different name) for the same physical address instead of reusing it → 896 property records for ~680 contacts; 132 contacts have up to 4 dup records (e.g. Linnea Rowden = 4× "560 Tewell Dr", contact 23001). DJ wants them combined into a single record per property with an agreed name. Not urgent — analytics already roll up to the Contact (parent_id) so counts/lapsed are correct meanwhile. Tie to [[project_workiz_exit_field_editability]]. Merge = reassign all child SOs' partner_id to the survivor, copy any missing fields, then unlink the dupes. |
| 2026-06-03 | Opening balances — pull QB balances for 9 accounts | Chase, 4 CC cards, 3 loans, Notes Payable. Cutover date TBD (Jan 1 2025 recommended). See [[project-opening-balances-needed]]. |

## Completed (keep last 10 for reference)

| Completed | Task |
|-----------|------|
| 2026-06-14 | Reactivation broken out as its OWN app (like the others): removed 9 duplicated /api/reactivation+/followup routes + page route from dashboard.py (−896 lines), reactivation.py now owns all 14 routes + page. No more dashboard shadowing — edit reactivation.py now. See [[project_reactivation_route_shadowed_in_dashboard]]. |
| 2026-06-14 | type_of_service/frequency read-order fix + contact→property re-point (customer lists read PROPERTY current, not stale contact). See [[project_type_of_service_read_order]]. |
| 2026-06-14 | Customer booking page Phase 1 live (/book) — self-hosted, replaces Calendly long-term. See [[project_customer_portal_booking]]. |
| 2026-06-14 | Removed dormant Render cloner copy (dashboard build_clone_payload + /api/workiz/clone_job + phase5 RENDER_CLONE_* consts). Canonical = Odoo SA 1338 only. Deploy live. See [[project_shared_workiz_clone]]. |
| 2026-06-14 | Shared Workiz cloner — ALL 3 STAGES done: build_clone_payload + /api/workiz/clone_job; Duplicate, Phase 5, reactivation SA 563 all use it. Validated end-to-end. See [[project_shared_workiz_clone]]. |
| 2026-06-05 | Clock-in bar visibility — bar now appearing at top of pages |
| 2026-06-05 | Customer tab improvements — discussed and built |
| 2026-06-04 | Hiring ATS: collapsible grouped view (Excellent/Strong/Good+Yes, Maybe, Follow Up, No, Not Reviewed) |
| 2026-06-04 | Hiring ATS: screening answers uploaded for 17 candidates from Google Doc "Responses" |
| 2026-06-04 | Odoo: 73 missing invoices created+paid (2020–2024 Done SOs); 1 flagged (Stephen Hatch SO 001803, -$5 balance) |
| 2026-06-04 | Odoo: tip SO lines with product_id=False assigned to Tip product (id=2) across 34 SOs |
| 2026-06-03 | Add Note save button fixed — removed activeJob setTimeout that nulled it before user tapped Save |
| 2026-06-03 | Historical modal: address, frequency, editable property note, always-show customer notes, payment method |
| 2026-06-03 | clockin-bar.js injected into all 18 HTML pages |
| 2026-06-03 | crew modal: closeHistModal missing — X + 3 buttons broken in hist modal |
| 2026-06-03 | crew modal double-tap guard + fetch timeout + localStorage retry queue |
| 2026-06-03 | crew modal re-asking who's in truck on page refresh — localStorage fix |
| 2026-06-03 | Blair Becker 11 duplicate in_process payments deleted from Odoo |
| 2026-06-03 | payment filter tightened to paid/in_payment only (so_history + payment_history) |
