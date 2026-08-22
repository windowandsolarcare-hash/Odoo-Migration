---
name: feedback_assistant_use_app_workflow_not_raw_api
description: "When DJ asks me AS HIS ASSISTANT to DO an operation in the system (create customer/job, schedule, send, take payment), go through the APP'S OWN WORKFLOW/endpoints — never raw Odoo XML-RPC direct writes, which bypass the safeguards + logic they built."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T07:02:05.604Z
---

**★ GOVERNING RULE (DJ 2026-08-21, after Lead created a customer/job via raw RPC).** There are two hats: **assistant/operator** (DJ: "do X for me in the system") vs **coder/diagnostician**. When DJ asks me as his **assistant** to perform an operation that HAS an app workflow, I MUST use that workflow — call the **same app endpoints the phone uses** (`wsc-field-assistant.onrender.com/owner/api/...`: New-Job intake, the scheduler, Send Confirmation, record-payment, etc.). Those endpoints carry the **safeguards + business logic** they built: scheduling logic that issues the date/time, the job-number sequence/naming, field defaults, the SYSTEM's confirmation message, validation.

**Do NOT enter operational data via raw Odoo XML-RPC / direct DB writes.** Raw writes BYPASS all of that → data entered wrong (arbitrary slot instead of scheduler's, hand-picked SO name instead of `_next_job_name`, missing defaults, no system confirmation). That defeats the point of the app.

**Raw Odoo RPC is still fine for:** read-only queries/diagnosis, data CLEANUP/corrections DJ explicitly asks for (stray shift delete, reconcile, backfill), and things with genuinely no app pathway. NOT for "do this for me" ops that have a workflow.

**I do NOT need computer-use for this** — I can CALL the app's HTTP endpoints server-side (runs their live logic). Computer-use is only for things with no API at all. Need: the owner-endpoint AUTH (session / Render access-code PIN / token) — DJ supplies via a file ([[feedback_api_keys_via_file]]). TODO: map New-Job→schedule→confirm endpoints + their auth so job creation always runs the real workflow.

**Incident + RESOLUTION:** 2026-08-21 Lead created Bob Lis via direct RPC, hand-picked the slot, hand-wrote a confirmation. DJ flagged both. **Fixed 2026-08-22 the RIGHT way** — deleted the raw SO and rebuilt via the app's own HTTP endpoints (see [[project_new_job_via_app_endpoints]] for the exact 8-call sequence + that owner endpoints are currently OPEN/monitor-mode so no credential needed yet). Job 264956 got a system-issued number, a scheduler-picked slot (Aug 27 8AM), and was left un-confirmed for DJ to send. This is now the standard path for any "do it in the system" op. Related: [[feedback_never_send_dj_to_odoo]], [[feedback_reuse_canonical_endpoint]], [[project_new_job_via_app_endpoints]].
