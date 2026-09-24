---
name: feedback_token_budget_discipline
description: "★ STANDING RULE (DJ 2026-09-24, near weekly token limit): cut fleet token spend. No acks/'copy/holding' messages — only message on a RESULT, a DECISION needed, or a PROBLEM. Peer msgs ≤5 lines (detail → doc/BUILD_LOG + link). No large browser test suites (phone telemetry is the measurement; post-deploy = 2-3 screens max). Idle sessions SILENT (no pings/heartbeats/watcher polling). Read-only = smallest query, don't re-read big summarized files. Default Sonnet-class subagents for routine lookups."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-24T05:13:51.601Z
---

# Token-budget discipline — cut fleet spend (DJ near weekly limit)

**DJ directive, 2026-09-24, via Dispatcher.** DJ is near his weekly token limit; several of these were already rules but weren't being followed. Enforce across all sessions:

1. **No acks.** No "copy / holding / standing by" messages. Only send a message when there's a RESULT, a DECISION needed, or a PROBLEM.
2. **Peer messages ≤5 lines.** Long detail goes in a doc / BUILD_LOG; the message links to it.
3. **No large browser-automation test suites.** Phone telemetry is the measurement. Post-deploy checks = 2-3 touched screens max.
4. **Idle sessions stay silent** — no status pings, no heartbeats, no watcher polling.
5. **Read-only investigations = the smallest query that answers the question.** Don't re-read big files already summarized.
6. **Default to Sonnet-class subagents for routine lookups** (ties to [[feedback_use_sonnet_for_routine]]).

**How to apply:** tighten everything. Before sending a peer message, ask "is this a result/decision/problem?" — if not, don't send. Keep the OVER status line (DJ's [[feedback_over_status_line]]) but make it ONE terse line, not a verbose recap. Prefer one doc + a link over long inline text. Smallest diagnostic query. This is a NET reduction — a one-time relay of this rule is worth it; ongoing, message far less. Mirror to Odoo-Migration/memory/ (docs/memory push is deploy-safe).
