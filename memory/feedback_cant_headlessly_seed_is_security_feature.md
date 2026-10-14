---
name: feedback_cant_headlessly_seed_is_security_feature
description: "When a post-build runtime test can't be staged because the action needs privileged auth the fleet DELIBERATELY lacks (owner-cookie-gated write, read-only DB, no admin path), that inability is a SECURITY PROPERTY CONFIRMED — not a test gap. Close the walk on deterministic code-proof of the un-stageable edge + the LIVE path verified by the next ORGANIC occurrence. NEVER manufacture a bypass to stage a test."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-14T15:25:00.031Z
---

During the App Building confirm→handoff post-build walk (2026-10-14), the crash-reclaim edge needed a `dj_confirmed`, stale-leased test card. There was NO headless path to create one: `/card/confirm` is owner-COOKIE-gated (the M4 gate, by design), the Render Postgres MCP (`query_render_postgres`) is READ-ONLY, and no fleet session holds an owner cookie or DB-write path. Specialists correctly refused to over-claim a seed path; Lead + Audit correctly refused to manufacture one.

**The principle:** when a runtime test can't be staged because the triggering action requires privileged auth the fleet deliberately does NOT have, that is the security boundary **working** — a finding, not a hole. Do NOT weaken the boundary (grab an owner cookie, do a raw DB write, add a NOTIFY_SECRET path to a privileged action) just to stage the test — that defeats the very property the test would check.

**How to close such a walk instead:**
1. **Deterministic code-proof** of the un-stageable edge — SOUND when the edge is pure SQL / boolean logic with no hidden runtime behavior (e.g. a lease re-offer predicate `claimed_at < now() - interval '10 minutes'`: Postgres interval arithmetic adds nothing a byte-read doesn't already prove). Read it firsthand in the shipped bytes.
2. **The LIVE path verified by the next ORGANIC occurrence** — a real user action (here: the next genuine DJ-confirm) exercises the end-to-end happy path (wiring, registration, real side-effects); Audit observes it post-hoc. This catches any mis-wiring a code-read can't.
3. Confirm the **endpoint is live-serving** (200 by content) + the **columns/migration landed** — the deploy-gap checks (ties [[feedback_verify_collection_and_live_pipe]]).

**How to apply:** don't treat "can't headlessly stage it" as a QC blocker OR as license to bypass the gate. Close on code-proof (for the deterministic edge) + organic live-observation (for the path a user hits). An optional forced runtime test that would cost DJ's time or pause live infra for a low-probability deterministic edge is usually NOT worth it — say so. Ties [[feedback_happy_path_e2e_before_dj]] (§16), [[feedback_audit_stamp_confirm_firsthand]] (§15), and the owner-gate boundary in [[feedback_assistant_use_app_workflow_not_raw_api]].
