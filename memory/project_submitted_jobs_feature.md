---
name: Submitted Jobs Feature — UUID Source + Nightly Cron Design
description: Where submitted future job UUIDs live, and the nightly cron pre-cache approach
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**UUID source:** Phase 5 creates the next Workiz job and writes the full URL to `account.move.x_studio_workiz_job_link` (the invoice from the completed job). URL format: `https://app.workiz.com/root/job/{UUID}/1`. Extract UUID from that URL.

**There is NO Odoo SO for these jobs yet.** They sit in Workiz as "Submitted" / unscheduled, waiting for DJ to manually add line items and schedule them. Phase 3 creates the SO later, after DJ schedules them.

**Correct nightly scanner logic:**
1. Query `account.move` where `x_studio_workiz_job_link` is not empty (recent invoices, last ~6 months)
2. Extract UUID from the URL
3. Skip if a `sale.order` with that UUID already exists in Odoo (means Phase 3 already processed it)
4. Call Workiz `job/get/{uuid}/` to verify Status=Submitted and job is still future
5. Cache results to `ir.config_parameter` key `submitted_jobs_cache`

**No extra field needed:** The link on the invoice is sufficient — no new res.partner field required.

**Nightly cron:** Run at ~5:00am (after the 4:17am daily sync finishes). Front end reads cache instantly. Manual Refresh button still available for same-day adds.

**Workiz rate limit:** Speed-based only (no daily cap). Built-in batch sleeps are sufficient. Expected list is small (5–20 jobs), so rate limits are nearly a non-issue.

**Do NOT scan crm.lead graveyard UUIDs** — that was the old wrong approach.

**Why:** Phase 5 always writes the new job link to the invoice (see `update_invoice_with_workiz_link` in zapier_phase5_FLATTENED_FINAL.py line ~518).
**How to apply:** When building/debugging submitted_jobs scanner, start from account.move with x_studio_workiz_job_link set.
