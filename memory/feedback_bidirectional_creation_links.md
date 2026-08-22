---
name: feedback_bidirectional_creation_links
description: "DJ's standing rule: whenever ANYTHING creates something, build clickable links BOTH directions between the origin and the created thing. Apply by default to every create flow."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ce7b153f-3bb6-4e33-a982-35d4d7a9f4ba
---

**DJ's standing design rule (2026-07-06): anytime one thing CREATES another, there must be links to navigate BACK AND FORTH between them — origin→created and created→origin.** Not just a provenance log; actual tappable navigation on both records.

**Why:** DJ works on a phone in the field and loses the thread when a created record is disconnected from what spawned it (e.g., a schedule block with no way back to its My Day task; a job with no link to the online booking that created it). Two-way links let him verify, complete, and understand any record without hunting. This is the navigational backbone of the comprehensive-CRM north star [[project_north_star_comprehensive_crm]] and complements the one-way `x_studio_creation_log` provenance [[project_job_creation_provenance]].

**How to apply:** When building/observing any create flow, wire BOTH links (store the counterpart id on each side; render a tappable link on each). Reference implementation = My Day task ↔ schedule block [[project_schedule_add_block]]: task carries `x_myday_block_so`; block reverse-looked-up via `/api/myday/blocks_tasks`; CC block shows "↩ task" → `/owner/myday?open=<id>`; task badge → `/owner/field?open_so=<block_so>&from=cc`. Existing deep-link params to reuse: field.html `?open_so=<so>&date_raw=&from=cc` (opens a job), `/owner/myday?open=<task_id>` (opens a task editor), booking task `?focus=<so_id>` (booking_requests).

**"Creates" relationships that should ALL be two-way (audit + fill gaps):**
- My Day task ↔ schedule block — ✅ DONE (both directions).
- Online booking (wscare.pro) ↔ job — ✅ DONE 2026-07-06 (commit b6c6172d). booking→job = Booking Requests "Approved" log "Workiz ↗" link (already existed, booking_requests.html renderApproved). job→booking = `api_booking_request_approve` now stamps the created Workiz job's JobNotes with "Booked online via wscare.pro | requested <date> (<pref>) | Notes: <x>" (both reuse + clone paths, right before the My Day task is marked done). NOTE the booking REQUEST SO is ephemeral (clone path unlinks it; Phase 3 makes the real SO) — so the durable job→booking artifact is the note, not a live record link. This generalizes the manual Bibi fix (job 004825 had no info-to-remember).
- Re-engagement launch → Workiz lead job (contact.x_reengagement_workiz_uuid) — one-way stamp; no UI link either way.
- Reactivation campaign → lead job (crm.lead) — one-way.
- Workiz job → Odoo SO (creation_log has Workiz #) — has WZ/Odoo pills; OK-ish.
- Order/quote → invoice; Duplicate job → source job; Phase 5 → next job — check/fill.
