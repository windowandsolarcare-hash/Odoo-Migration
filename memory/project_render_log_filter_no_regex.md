---
name: project_render_log_filter_no_regex
description: "Render list_logs money-check — request lines are type=app (not request) and the text filter ignores regex; use one plain word per query or you get a false \"clear\""
metadata:
  node_type: memory
  type: project
  originSessionId: 66a9262c-f30f-42dd-96ba-6b96f344343d
  modified: 2026-09-23T14:29:54.696Z
---

Two silent traps in `mcp__render__list_logs` on the app service `srv-d78le0fkijhs738dsli0` (found 2026-09-23 by Dispatcher):

1. **HTTP request lines are logged as `type=app`, not `type=request`.** Filtering `type: ["request"]` returns EMPTY for everything, even healthz.
2. **The `text` filter does NOT honor regex.** `(?i).*(pay|checkout|stripe).*` matched NOTHING, while a plain `billing` query found real `/owner/api/billing/review` hits in the same window. The `path` filter with regex also came back empty.

**Why:** the pre-deploy money-check in DISPATCHER_HANDOFF_BRIEF.md used a type=request + regex filter, so every check "passed" whether or not a customer was paying. That is a false green on a money gate. See [[feedback_no_deploy_during_customer_payment]].

**How to apply:** for a deploy money-check, run one list_logs per plain word (`pay`, `checkout`, `stripe`, `charge`, `invoice`, `collect`), with no type filter, over the last ~15 min. Ignore pip build lines ("Collecting …"). Sanity-check the query by searching a word you KNOW appears (e.g. `healthz`). To see DJ's live activity, search his device IP `76.90.35.160`. Note that a desktop/computer-use session on DJ's home network shares that IP.
