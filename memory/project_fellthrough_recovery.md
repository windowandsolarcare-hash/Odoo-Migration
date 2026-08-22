---
name: project_fellthrough_recovery
description: "Recovery of customers who fell through the cracks (H2-2025 done jobs with no follow-up). Reconciliation of the maintenance vs non-maintenance buckets, what's handled, what's left."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Diagnosis (2026-06-23):** re-engagements/next-jobs only started firing ~Feb 2026 when DJ moved billing to Render (Phase 6 payment → Phase 5). Everything billed the OLD way (pre-Feb-2026) never got a follow-up. Earliest re-engagement activity = Aug 2 2026 (= a Feb-2026 job + 6mo default).

**The exercise:** Done jobs June 2025–Feb 2026 = 279 jobs / 192 customers. Coverage: 64 have a future job, 62 have an open re-engagement, **70 fell through (no future job + no re-engagement).** Split by type of service:
- **Maintenance: 25** → handled via the stranded-next-job tool (see below).
- **On Request: 34** → need a re-engagement CONTACT (text/call), NOT scheduling. NO TOOL YET.
- **Unknown: 11** → eyeball/decide per customer. NO TOOL YET.

**Maintenance 25 breakdown:**
- ~13 recent (Apr–May 2026 completions): Phase 5 made a next job in Workiz (Submitted, no tech/items) that never synced to Odoo (old rule). **DJ took care of these (2026-06-23).**
- ~12 older (last clean 8/25–12/25, genuinely overdue): **DJ has been in contact.** Of these, 4 had a stranded Workiz next-job (Mette Haydt, Art Martel, Joan Flickinger, Andy Willinger → in the 📋 In Workiz tab); 6 had NOTHING (no next job ever made — Kay Mitchell, Mark Mitchell, Suzie Sites, Diane Rabelo, Brenda Williams, Scott Cunningham) → need a FRESH re-engagement.

**The tool built:** Maintenance to Schedule app (/owner/maintenance) → new "📋 In Workiz" tab (see [[project_stranded_next_jobs]]). Raw stranded scan = 41 next-job links → 30 customers (latest per customer). As DJ finishes each in Workiz + it syncs, it drops off. **As of 2026-06-23 end of session: down to 13 remaining** in the tab. The "others" still showing (weren't in DJ's original 13+12 because their completed job fell outside the Jun2025–Feb2026 window): Wayne Geringer, Roberta Davis, Scott Cunningham(dup), Rob Seedorf, John Ham, Gary Marsalone, Angela Rafferty (+ older-overdue contacted-not-finished + Jerry Smith).

**STATUS (updated 2026-06-24 per DJ):**
- ✅ DONE: 13 recent maintenance (handled); 13 remaining In-Workiz tab (finished in Workiz); the 6 older maintenance w/ NOTHING (handled/contacted); Twilio port email SENT.
- ✅ DONE 2026-06-24: the 45 non-maintenance → **44 re-engagement project.tasks created** (Option A) via C:/tmp/build45.py, due today, standalone (project_id False), tagged "recovery batch 2026-06-24 (H2-2025 fell-through)". They show in Activities/My-Day digest with the fixed "Launch Re-engagement Text" button (all 44 have a prior Workiz UUID so followup/launch can clone). DJ works them: tap → Launch Re-engagement Text → Workiz sends. (44 not 45: one got a job/task in the interim.)
- ⚠️ TIMING: the re-engagement send goes through WORKIZ (clone job → SubStatus 'Re-engagement Trigger'). Workiz leaves ~2026-06-29 → DJ has ~5 days to blast these 44 before the send breaks; after that it needs the Twilio path (port not yet done — Twilio hadn't replied to the reopen as of 2026-06-24; A2P re-registration confirmed required).
- To bulk-undo the batch if needed: project.task where description ilike 'recovery batch 2026-06-24'.

Relates to [[project_reengagement_vs_reactivation]], [[project_type_of_service_fields_map]], [[project_stranded_next_jobs]].
