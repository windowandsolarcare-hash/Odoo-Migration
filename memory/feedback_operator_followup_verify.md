---
name: feedback_operator_followup_verify
description: "When Operator addresses a situation that has an expected OUTCOME, set a CONCRETE scheduled follow-up to verify it actually happened — never a vague \"I'll keep an eye out\" (those silently fail over time). DJ has been burned by this repeatedly."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2c61606-e81d-478f-b7ff-3a0b8fb045a8
  modified: 2026-09-05T05:19:37.631Z
---

**Rule (DJ 2026-09-05):** Whenever I take an action that has an EXPECTED RESULT, I must set a CONCRETE follow-up that VERIFIES the result — not promise to "watch for it." A vague "I'll keep an eye out" reliably fails with time; DJ has had too many assistants say that and then drop it.

**Examples of outcome-bearing actions:** sent a customer an offer → did they book? sent a confirmation → did they reply/confirm? replied to a customer (e.g. Jim/Robert) → did they respond? moved/rescheduled a job → did it land on the right day? handed a build to Lead → did it ship?

**Why:** the follow-through is the job. Telling DJ "done, I'll watch for it" without a real trigger is a silent-failure trap.

**How to apply:**
- At the moment I complete the action, schedule a CONCRETE check — a `CronCreate` one-shot at an interval matched to the expected response window (minutes for a deploy, a few hours/next-day for a customer reply). On fire: verify the outcome (read the thread / SO state / board) and REPORT + act. (Model: the auth-rollback one-shot verify that worked cleanly.)
- If it genuinely can't be automated, hand it to DJ EXPLICITLY with a date/trigger ("if Jim hasn't replied by Sat, I'll re-ping") — not a vague promise.
- Prefer the app's own auto-mechanisms where they exist (auto-clear cards, confirm-state) — but if none covers it, the scheduled check is mandatory.
- State the follow-up plan in my reply so DJ sees the trigger exists, not just an intention.

Related: [[project_operator_playbook]], [[feedback_over_status_line]].
