---
name: feedback_no_conclusion_from_single_test_sporadic
description: "★ For SPORADIC/intermittent failures, NEVER call 'fixed' or 'root cause' from a single test (pass OR fail). Require REPEATED tests with a failure RATE. When the real surface is unobservable (DJ's phone), stage telemetry to record every failure automatically — don't guess from one screenshot."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-23T14:57:06.355Z
---

# Sporadic failure = no conclusion from a single test; demand repeated data + a failure RATE

**DJ directive, 2026-09-23 (frustrated, and right), during the phone HUD/inbox reliability incident.** The fleet kept declaring "fixed" / "root cause" off ONE observation — a single pass looked fixed, a single fail looked like the cause. The failure is INTERMITTENT, so a single data point proves nothing either way.

**The rule:** for any sporadic/intermittent problem, do NOT draw a conclusion or pick a direction — pass or fail — from a single test. A "fixed" or "root cause" call must be backed by REPEATED tests with an actual failure RATE (N failures over M cycles). One green ≠ fixed; one red ≠ the cause.

**Why:** intermittent bugs self-heal and re-break on cache/timing/load conditions a single run can't reproduce; a premature "fixed" ships false confidence and a premature "root cause" sends the fix at the wrong target. DJ has been burned by both in one incident (the "logs healthy but user broken" recurrence + a confident 503 "working-as-designed" call from one hit — see [[project_logs_healthy_but_user_broken_is_client_side]]).

**How to apply:**
1. **Gather a rate first.** Run REPEATED cycles (a background agent doing e.g. HUD-cold-load ×20, inbox+thread ×15, the full HUD→inbox→thread→HUD sequence ×15) and report failures with exact error text + request evidence — a rate, not a verdict.
2. **When the real surface is unobservable, instrument it.** DJ's PHONE is the real surface and we can't watch it. Stage lightweight CLIENT FAILURE TELEMETRY (beacon {page, step, url, status, elapsed, error text, appver, SW version, online} to a PG-only, non-Odoo, non-blocking endpoint) so every failure DJ hits is recorded automatically — no screenshots, no one-off tests. Spec: scratchpad CLIENT_FAILURE_TELEMETRY_SPEC.md.
3. **Baseline → fix → measure the drop.** Ship telemetry FIRST to get a baseline rate, THEN deploy the candidate fix and measure the rate fall against that baseline. Only then may you say "fixed," with the numbers.
4. Applies to my OWN language too: reframe any single-observation diagnosis as a HYPOTHESIS to validate, never a root-cause conclusion.

Ties to [[feedback_odoo_verify_content_not_status]] (verify by real behavior) and [[feedback_verify_limits_before_declaring]] (test before declaring). MIRROR to Odoo-Migration/memory/ pending (held during the deploy/push freeze).
