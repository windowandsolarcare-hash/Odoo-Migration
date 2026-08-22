---
name: project_outreach_recent_jobs_done_only
description: "Outreach/reactivation customer modal 'Recent jobs' listed ALL SOs (incl. not-done ones like status 'Solar May') as if done. Fixed: v2_outreach.html filters to Done-only, same set that drives Total sales (done)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-25T05:48:41.627Z
---

**2026-07-24 (DJ, screenshot: Fernando Hernandez reactivation modal showed a Jan 5 2025 job as if he'd done it — he hadn't).**

**Root cause:** In `v2_outreach.html` (the reactivation/outreach review modal, opened from Outreach Campaigns), the "Recent jobs" list rendered the RAW `cj.jobs` array from `/owner/api/customer_jobs` (`jobs.slice(0,5)`), with NO done filter — while "Total sales (done)" right above it correctly summed only jobs whose `status` contains 'done'. So a not-done SO showed as a completed job (green $ amount, no status shown).

Verified in Odoo: Fernando (contact 23423) has 2 SOs — `002972` 2025-01-05 status **'Solar May'** (NOT done) and `002916` 2024-07-17 status **'Done'**. The 'Solar May' one was the phantom.

**Fix (commit f43f37b):** build one `doneJobs = jobs.filter(status contains 'done')` and drive BOTH the sales total AND the Recent-jobs list from it. Now only Workiz-status-Done SOs appear as jobs. Consistent with the project rule: a "job DJ did" = `x_studio_x_studio_workiz_status = 'Done'` ([[feedback_done_jobs_definition]]).

**Related, NOT changed (flagged to DJ):** the **Inbox** "Recent jobs" panel comes from `sms.py _customer_context` — it lists the last 3 SOs and PRINTS each SO's status on the line (so it doesn't falsely present non-done as done), and that same string feeds the AI reply draft as customer history. Left as-is to avoid changing AI-draft context unasked; revisit if DJ wants Inbox filtered to Done too. `/owner/api/customer_jobs` still returns ALL jobs (other callers may need them) — the Done filter is applied per-view in the frontend.
