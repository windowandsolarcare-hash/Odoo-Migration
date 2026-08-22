---
name: feedback_workiz_no_job_all
description: Never use Workiz job/all endpoint — DJ's explicit rule
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Never use the Workiz `job/all/` endpoint.

**Why:** DJ explicitly prohibited it (2026-05-04). No reason given but likely reliability, rate limits, pagination issues, or missing fields.

**How to apply:** Any code that needs to list/search Workiz jobs must use an alternative approach — either query Odoo (for jobs already synced), use `job/get/{UUID}/` for known UUIDs, or ask DJ what endpoint to use. Do not use `job/all/` even as a fallback.
