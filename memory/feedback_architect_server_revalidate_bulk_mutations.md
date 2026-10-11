---
name: feedback_architect_server_revalidate_bulk_mutations
description: "Architect plan-review lens — any bulk/mutating action MUST re-validate submitted ids server-side against the SAME canonical domain, never trust the client's list."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-11T21:46:09.226Z
---

When reviewing (or building) any BULK or record-mutating action (cancel, delete, archive, bulk-write), require that the SERVER endpoint re-applies the canonical selection filter to every submitted id before acting — it must NOT trust the id list the front-end sent. The list filter (what the user sees/approves) and the server re-check (the backstop) must use the SAME domain, ideally a shared helper (e.g. `_residue_domain` reused in both the list query AND `safe_set`/the cancel handler).

**Why:** On the migration-cleanup build (2026-10-11), the residue review list correctly filtered state=draft + age + job_type denylist [Reactivation Lead, Personal Time, Dr. Appointment] + company_id. But the bulk `residue_cancel` server re-check DROPPED the job_type denylist + company leaves — so a wrong/stale id for a Personal Time / Dr. Appointment draft, or a non-W&SC draft, could have bulk-cancelled despite the denylist. Lead caught it at byte-QC; my PLAN review had not required the server-side re-validation. This mirrors the reactivation.py pattern already in the code: "Re-validate contact + cooldown (don't trust the front-end)."

**How to apply:** In any §15 plan-review of a bulk/mutating feature, add to the checklist: "Does the server re-validate each submitted id against the canonical domain (shared helper), or does it trust the client list?" If it trusts the client, that's an INCOMPLETE — the per-row human approval is a gate, but the server re-validation is the backstop and both must hold (defense in depth). Ties to [[feedback_auditor_user_perspective_gapfinder]] and the route-shadow / verify-by-content discipline.
