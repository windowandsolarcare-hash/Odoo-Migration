---
name: feedback_testing_tools_not_build_filtered
description: "2_Testing_Tools/ is NOT in Render's buildFilter — a push there REDEPLOYS the app (unlike 3_Documentation/**)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4a3934c7-cb02-4949-8807-74eee8a68861
  modified: 2026-09-27T16:55:07.943Z
---

**A push to `2_Testing_Tools/` triggers a Render redeploy** (confirmed 2026-09-27: a test-only fast-follow push, `test_billing_mutated_kinds.py`, immediately spun up a second deploy right after a code deploy = a minor restart-stack). Only `3_Documentation/**` is in the service buildFilter ignore list (roster/mail/docs commits are free); `2_Testing_Tools/` is NOT.

**Why:** the no-stacking + no-mid-payment deploy guardrails ([[feedback_no_deploy_during_customer_payment]] + deploy-cadence rules) apply to EVERY push that redeploys, including test files. A "fast-follow" test push is not free — it's another worker restart.

**How to apply:**
- **Bundle test files with the code push** they cover (one commit → one deploy), OR push the test in the same batched deploy window — do NOT push a test as a separate immediate fast-follow right after a code deploy.
- Before treating any push as "free/no-deploy," verify the path is actually build-filtered — only `3_Documentation/**` is today. When unsure, assume it redeploys.
- SUGGESTED infra improvement (flagged to Lead/Dispatcher 2026-09-27, not yet done): add `2_Testing_Tools/` to the service buildFilter ignore list so test pushes become free like docs. Needs the render.yaml/service-config change + care.

Ties [[feedback_regression_guard_pushes]], [[project_render_coalesces_rapid_pushes]].
