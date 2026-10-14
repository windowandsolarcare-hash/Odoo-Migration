---
name: project_reparent_setcategory_endpoint
description: "Two owner-gated endpoints in brain.py fix the recurring mis-parented-contact / blank-record_category class: POST /owner/api/contact/reparent (move a PROPERTY to a different top-level CONTACT, res.partner.parent_id) + POST /owner/api/contact/set_category (fill a BLANK record_category). Server-validated structural writes. Shipped + PRODUCTION-PROVEN on the two-Robins (Andreas) case 2026-10-14."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-14T07:16:44.663Z
---

Shipped 2026-10-14 (branch card-reparent, commit d5a4aaaa; §15 Audit 37536a37 + Lead byte-QC 43deca44). In `routers/owner/brain.py`, owner-gated (under /owner, NOT in PUBLIC_EXACT — like `/api/customer/edit`; no authz change). The app pathway for structural res.partner linkage that `/api/customer/edit` (basic fields) and `/api/job/property` (same-customer only) did NOT cover.

**`POST /owner/api/contact/reparent` {child_id, new_parent_id}** — move a PROPERTY under a different CONTACT (`parent_id`). Server RE-READS both ids (never trusts the client — [[feedback_architect_server_revalidate_bulk_mutations]]): child MUST be `active`, W&SC (`company_id in (1,False)`), `x_studio_x_studio_record_category=='Property'`; new_parent MUST be `active`, W&SC, NOT a property, and **top-level (no `parent_id`)**. Rejects self / archived / mis-typed / off-company / nested. No-op → `{ok, changed:false}` (no write/chatter). Writes `parent_id`, chatter-audited (🔗) with `session_actor`.

**`POST /owner/api/contact/set_category` {contact_id, category}** — fill `x_studio_x_studio_record_category`. **★ BLANK→value ONLY** (`_blank_cat` treats False/None/''/whitespace as blank): writes only when currently blank; an already-set DIFFERENT value is REJECTED (re-categorizing an in-use record orphans its SOs + breaks the schedule gate/due-math — value→value is DEFERRED, needs an SO-orphan check; no override path). allowed = `{Contact, Property}` (the app's live set). Chatter-audited (🏷️).

**Why blank-only matters:** `record_category` is LOAD-BEARING (property searches, the schedule gate, due-math) — [[feedback_done_jobs_definition]] / the field table. A careless re-categorize silently drops records off searches/schedule.

**PRODUCTION-PROVEN 2026-10-14 (Operator, the two-Robins / "Andreas" fix):** two Robins in Workiz had a property on the wrong contact + a blank category. `set_category 27301→Contact` then `reparent 24090→27301` → Robyn 27301 now owns property 24090 (job 003993's po/ship followed the property automatically); Robin 22968 keeps 24923. Pricing ($150) stayed correct on the property (not person-specific); gate blank everywhere so F5 gate/pricing re-sync was a no-op. The endpoint's validation held; the fix landed clean. **Operator runs these via the app (owner session); a reparent may still need an Operator gate/pricing re-sync step after (reparent is linkage only).**
