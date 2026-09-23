---
name: feedback_sporadic_bugs_repeat_test
description: "For sporadic/intermittent bugs, never conclude \"fixed\" or pick a root cause from ONE test (pass or fail); test repeatedly and report failure rates, and instrument the real device"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 66a9262c-f30f-42dd-96ba-6b96f344343d
  modified: 2026-09-23T14:54:57.319Z
---

For an intermittent failure, a single test run is not evidence either way. Do not declare "it works," "fixed," or "root cause is X" from one pass or one fail. Test many cycles, report failure RATES with per-failure evidence, and add client-side failure telemetry, so failures on DJ's real phone get recorded while he works.

**Why:** DJ, 2026-09-23, after ~24h of mobile HUD/inbox failures: "stop making decisions on one test alone… There's a problem that's sporadic… if it fails we run in this direction, if it succeeds we run in this direction, stop running. Let's test." The fleet had shipped fix after fix, each "confirmed" by one clean run, while his phone kept failing. It later turned out his phone had been on a stale client the whole time, and the "DJ's device" in the logs was his desktop.

**How to apply:** Before calling anything fixed: (1) run repeated automated cycles (desktop computer-use at phone size) and report pass/fail counts; (2) confirm on DJ's PHONE, which may share the home IP 76.90.35.160 with the desktop, so tell them apart by client behavior (e.g. thread `&n=30`), not IP; (3) prefer telemetry (client beacons on every error) over asking DJ for screenshots. See [[feedback_test_like_real_app_before_delivering]] and [[project_render_log_filter_no_regex]].
