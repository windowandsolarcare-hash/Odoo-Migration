---
name: Workiz job/all/ endpoint skips unscheduled jobs — use job/get/{UUID}/ directly
description: 2026-04-27 — discovered when trying to find a follow-up trigger job created with no JobDateTime. job/all/ paginated through 100+ jobs, never returned the new one. job/get/{UUID}/ found it instantly.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
The Workiz REST API endpoint `job/all/?start_date=...&records=...` returns only **scheduled** jobs (jobs with a real JobDateTime). Jobs created with no JobDateTime — like reactivation graveyard jobs and follow-up trigger jobs — will NOT appear in `job/all/` results regardless of how far back you push `start_date`.

**Practical implication:**
- If you're hunting for a recently-created Workiz job and you don't have the UUID handy, `job/all/` will not save you for unscheduled jobs.
- `job/get/{UUID}/` works for any UUID, scheduled or not.
- The Render `tool_search_customers` lookup pulls jobs from Odoo SOs — that's the right path when you only know a customer name.

**How I found it:** 2026-04-27, I sent a follow-up text to Bev Hartin via the new follow-up flow. The launch wrote x_studio_last_followup_sent=today (proving the Workiz job was created), but `job/all/` paginated 100+ rows from start_date=2026-04-01 with zero matches for ClientId 1533. Initially looked like the Workiz create silently failed; turned out the job exists, it's just unscheduled, and the listing endpoint won't show it.

**Why:** Saves wasted scan time when debugging a "did this Workiz job get created" question for a known unscheduled JobType (Reactivation Lead, Follow Up Lead).

**How to apply:**
- Don't use `job/all/` to verify creation of an unscheduled job — verify by JobAmountDue / chatter / direct UUID lookup.
- For the follow-up flow specifically: the launch endpoint now posts the UUID + Workiz link to the contact's chatter (commit 728252f), so future sends are findable through the contact record.
- If a customer says "I never got that text," go to their res.partner chatter, find the most recent "Text sent" line, click the Workiz link to verify.
