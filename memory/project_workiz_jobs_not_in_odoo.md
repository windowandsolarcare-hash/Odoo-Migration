---
name: project_workiz_jobs_not_in_odoo
description: "Listing a customer's jobs from Odoo alone is INCOMPLETE — Workiz 'Re-engagement/Reactivation Lead' jobs can exist only in Workiz (no sale.order, no crm.lead). Query Workiz too. Plus job-delete invoice blocker."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**RULE (DJ flagged 2026-06-15): when asked to list/audit a customer's jobs, search BOTH Odoo AND Workiz.** Odoo `sale.order` (+ `crm.lead`) is NOT the complete picture — Workiz can hold jobs that never synced into Odoo at all.

**The gap, concretely:** **"Re-engagement Lead" / "Reactivation Lead"** Workiz jobs (the lead jobs the follow-up/reactivation SMS flow mints — clone → SubStatus 'Re-engagement Trigger' → SMS) can end up **Workiz-only: no `sale.order` AND no `crm.lead` in Odoo.** They **accumulate** when follow-up texts are sent repeatedly (one new Workiz lead job per send). So an Odoo-only search shows zero of them. To find them, hit the Workiz API (job list / search by client) — they show as Unscheduled, Submitted/Pending, type "Re-engagement Lead".

**Bev Hartin case (2026-06-15, CLEANUP PENDING — not done):** Odoo Contact 23629 (29 Toscana Way E, Rancho Mirage) → Property 25799; stray empty dup contact 26935. DJ: "delete all jobs except 2134 AND 2135."
- Workiz showed 6 jobs: **#4526, #4527, #4528, #4529** (Re-engagement Leads — Workiz-ONLY, no Odoo record) + **#4581 (SO 004581, Done) / #4583 (SO 004583, Scheduled)** + **#2134/#2135 (KEEP)**.
- Two delete-paths: (a) #4526-4529 = simple Workiz delete (no Odoo/invoice to clean); (b) #4581/#4583 = Odoo SOs WITH **posted, in_payment** invoices (INV/2026/02388 $1, INV/2026/02391 $2, both 2026-05-10) → BLOCKED.
- DECISIONS STILL NEEDED before doing it: unwind the two posted invoices+payments (or not), and confirm Workiz delete of the 4 leads.

**JOB-DELETE INVOICE BLOCKER:** the safe delete ([[project_delete_job_paired]]) REFUSES any SO with a linked invoice. A **posted** invoice (esp. `payment_state=in_payment/paid`) can't just be cancelled — must reset to draft + unwind/unreconcile the payment + cancel, THEN cancel→unlink the SO, THEN delete the Workiz job last. That's an accounting change → get DJ's explicit OK; never touch posted invoices/payments silently. Multi-company: filter company_id=1 for W&SC.

**OPEN IMPROVEMENT DJ raised:** the follow-up flow keeps creating un-synced Workiz re-engagement leads that pile up — worth fixing so they don't accumulate (and/or so they sync to a single graveyard record instead of N orphans).
