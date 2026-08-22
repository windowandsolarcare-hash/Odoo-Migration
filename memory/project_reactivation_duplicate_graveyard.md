---
name: project_reactivation_duplicate_graveyard
description: Sending a 2nd reactivation text to the same customer creates a DUPLICATE graveyard lead+Workiz job (no dedupe) → orphan on booking
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Bug (found 2026-07-11 via Michelle Proffett, contact 23646):** each reactivation SEND creates a NEW crm.lead (stage 5 "Attempt 1 - Sent") + a NEW Workiz "graveyard" job (JobType "Reactivation Lead", SubStatus "API SMS Test Trigger" = the live send status). The launch does NOT check for an existing open reactivation before creating another, so a follow-up send spawns a parallel lead+job.

Flow: field/CC → `api_reactivation_launch` (reactivation.py:567) → writes SMS to SO `x_studio_manual_sms_override` → runs Odoo **SA 563** which creates the lead + graveyard Workiz job + stores `x_workiz_graveyard_uuid` on the lead. The SubStatus flip fires the Workiz automation that actually texts. NO dedupe anywhere; the 365-day cooldown only gates the candidate LIST + warns on the analytics button — it does NOT block the launch endpoint, so re-sending 3 months later goes through.

**Orphan confirmed:** `api_reactivation_book` (reactivation.py:1831) converts the ONE graveyard job you booked from → real job, sets THAT lead → Won (stage 4). It does NOT touch sibling open leads/jobs. So the other lead stays stage 5 forever and its Workiz job stays live = orphan. Customer also shows twice in the Sent/Waiting tab.

**Scope (2026-07-11):** 233 open Sent leads total; **12 contacts have 2+ open reactivation leads** (one has 3 — contact 23414, leads 82/83/84 all same day). Michelle = leads 407 (O2W14P, today) + 230 (4O70G5, Apr 5), both live Pending jobs.

**★ Why reuse is IMPOSSIBLE (DJ 2026-07-11):** Workiz fires an automation only ONCE per job. A follow-up reactivation text MUST have a new job to re-trigger the SMS automation — so the duplicate graveyard job is inherent to sending again; you cannot re-text on the existing job. Option A (prevent/reuse) is therefore off the table.

**✅ FIX BUILT — cleanup on booking (option B, 2026-07-11 commit 397709b):** `api_reactivation_book` (reactivation.py ~1892), after setting the booked lead → Won, now finds all OTHER open stage-5 reactivation leads for the same `x_odoo_contact_id`, **deletes each sibling's graveyard Workiz job** (`workiz_post('job/delete/{uuid}/', {})`, skips the booked uuid) and **closes the sibling lead → Lost** (stage 6) with a 🧹 breadcrumb. All wrapped in try/except so booking never fails on cleanup. So orphans are cleared at the moment of booking.

**DEFERRED TO WORKIZ RETIREMENT (DJ 2026-07-11): "we'll clean all that up when workiz is gone."** Do NOT re-propose these — (C) backfilling the existing 12 duplicate customers, and adding sibling-cleanup to the decline path (`api_reactivation_decline`), are intentionally left for the Workiz sunset. The booking-time cleanup (built) is enough to stop NEW orphans meanwhile; existing dupes just age at stage 5. See [[project_open_items_2026-07]] (Walter Keller reuse-graveyard fix), [[reference_odoo19_unlink_tracking_bypass]] (Workiz delete = POST /job/delete/{UUID}).
