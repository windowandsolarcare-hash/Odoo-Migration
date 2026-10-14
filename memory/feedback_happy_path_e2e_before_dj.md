---
name: feedback_happy_path_e2e_before_dj
description: "DJ rule (2026-10-14, found by live-testing App Building): before any multi-step flow is called DONE, the fleet runs ONE start-to-finish HAPPY-PATH pass through the obvious path and reports it plainly — DJ must never be the first to hit the obvious path; his live testing should only ever surface EDGE cases."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T14:03:40.283Z
---

DJ was live-testing App Building by voice, confirmed a card, and nothing happened — the flow just died there. His words: *"all we built was a transcription... it just dies there... when I test I should only hit EDGE cases, not the obvious case."* The confirm→handoff link had never been exercised end-to-end, so DJ discovered the dead-end himself.

**The rule:** before any multi-step flow is called DONE, the fleet runs ONE start-to-finish HAPPY-PATH pass through the OBVIOUS path — capture → … → its natural conclusion (who's notified, what gets built) — and reports it plainly. **DJ must NEVER be the first to hit the obvious path.** His live testing should only ever surface EDGE cases, not the obvious dead-end.

**Why:** a green deploy + an endpoint that returns 200 is NOT "done" if the user's happy path dies partway. Claude optimizes for the literal ask (build the endpoint) and stops at the seam (what happens AFTER confirm?). The e2e happy-path pass is what catches a missing LINK between steps — exactly the gap DJ hit.

**How to apply:**
- Part of Audit's post-build walk: walk the full happy path to its CONCLUSION, not just "the endpoint responds." Follow the user's actual journey to where it ends.
- Part of the builder's "done" bar: no multi-step flow is handed off without one clean start-to-finish pass, reported plainly.
- Lead QC confirms the happy-path pass was run + reported for any multi-step flow.
- Lives operatively in `3_Documentation/roles/FLEET_GOVERNANCE.md` §16 (commit 4969fda1, 2026-10-14). Ties [[feedback_auditor_user_perspective_gapfinder]] (Audit hunts what the PLAN missed), [[feedback_verify_collection_and_live_pipe]] (green deploy ≠ works), and §15 Audit-architect / the ship-system review trail. Sibling in-flight: project_gemini_followup_end_to_end_test_gate (Dispatcher holds; test-gate/sandbox finalization, token-bounded, not built without DJ's go).
