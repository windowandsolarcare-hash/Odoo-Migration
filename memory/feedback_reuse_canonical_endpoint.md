---
name: feedback_reuse_canonical_endpoint
description: "Don't duplicate existing logic for a new UI entry point — call the canonical endpoint; extend it if it's missing something"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

When a new feature needs behavior that ALREADY exists elsewhere (snooze, defer, delete, send, book…), **call the existing canonical endpoint — do not write a second copy.** If the old one is missing something the new caller needs, **extend the old one** (surgically) so it serves both.

**Why (DJ, 2026-07-11):** I built a new `/api/schedule/snooze` in dashboard.py for a field-menu snooze instead of reusing `/api/outreach/defer`. DJ pushed back: "why build the snooze logic again... you're missing some of the old logic [the reason paper-trail] and now we have to remember to update two pieces of code rather than one." Two copies drift and one always misses logic (mine lacked the reason/timeline write).

**How to apply:**
- Before writing a new endpoint/handler, grep for an existing one doing the same job. Reuse it.
- If it needs a new param or a small correctness fix to work for your caller, edit that ONE endpoint (e.g. defer now writes partner+parent — [[project_cc_overdue_and_snooze]]).
- Watch for the app's duplicate-route pattern: some routes exist in BOTH dashboard.py and a feature router; find the LIVE one first (see [[reference_customer_brain_deeplink]] gotcha) rather than adding a third.
- Removing code YOU just added to consolidate is fine; removing pre-existing working code still needs DJ ([[feedback_never_remove_working_code]]).
