---
name: project_new_job_book_asis
description: "New Job screen (v2_new_job.html) previous-job cards have a 'Book as-is' button — reuses Duplicate's exact-line prefill but jumps straight to date+Create. Added 2026-07-31."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-08-01T04:26:51.136Z
---

`static/owner/v2_new_job.html` — the New Order → New Job screen ("Property" view: customer + previous jobs + service addresses, reached via `v2_new_order.html?contact=<pid>`). Each **previous-job card** now has up to three buttons:

- **Book as-is →** (`bookAsIs`, NEW 2026-07-31, class `.prev-book`, solid green): takes that job/quote's EXACT line items and goes straight to scheduling. Implementation = calls the existing `useThis` (which prefills property + lines + gate/pricing/job_type and `gotoStep(3)`), then `setStatus('…pick a date and tap Create Job')` + scrolls to the Create button. **Skips the service-editing step** — DJ's ask. No new create path: it lands on the same `createJob()` → `POST /owner/api/intake/create-job` (a DATE is still required — a job can't be created without one; "book as-is" means skip editing the services, not skip picking a date).
- **Use this job →** (`openJob`, existing, conditional): opens the EXISTING Workiz job in a tab to schedule/finish it — no new SO. Only shows when `wst!=='Done' && not in the 4 SCHED statuses && has workiz_link`.
- **Duplicate this →** (`useThis`, existing): prefill the New Job form (editable) for a fresh job.

**Why:** DJ (2026-07-31), looking at Tim Albert's $282.50 windows QUOTE (a Render Quote Tool quote, no Workiz job → only Duplicate showed), wanted a one-tap "use this quote to book it." He picked "Book the quote as-is" over "open in Workiz." A quote has no Workiz job to open, so booking = create a new job from its lines. **How to apply:** this is the pattern for "turn a quote/prior job into a booking fast." Reached from the follow-up "🗓️ Get them on the schedule" button ([[project_hud_followups_surface]]) which deep-links here. Don't fork createJob; bookAsIs is a thin wrapper over useThis + createJob. See [[feedback_reuse_canonical_endpoint]].
