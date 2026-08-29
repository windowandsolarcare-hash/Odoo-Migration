---
name: project-cloud-watcher-routine-hourly-floor
description: A CLOUD session cannot run a 15-min durable mail watcher. Routines (create_trigger) reject anything under 1 hour; CronCreate does 15 min but is session-only and dies with the container. Arm both layers.
metadata:
  type: project
---

Found 2026-08-29 by cloud Design while arming its mail watcher per Lead's fleet directive.

**The constraint.** The fleet's canonical AGENT_MAIL watcher is every 15 minutes (DJ's 2026-08-22
cost decision, reaffirmed 08-24 after Lead briefly said 7). A cloud session cannot honor that
durably:
- `create_trigger` (Routines, the `/schedule` mechanism) **refuses any cron under 1 hour** —
  the error is literally *"may fire runs as little as 15 minutes apart; the minimum interval is
  1 hour"*. Routines ARE durable: server-side, survive container reclaim, self-bind to the session.
- `CronCreate` **does** 15 minutes, but is session-only/in-memory, auto-expires after 7 days, and
  dies with the container — the exact silent-death failure the directive was written to fix.

**How to apply — arm BOTH layers:**
1. Durable floor: `create_trigger` hourly (`0 * * * *`; the server anchors it to the creation
   minute so Routines spread across the hour). This is the layer that actually survives.
2. Fast layer: `CronCreate` at `4,19,34,49 * * * *` for fleet-canonical 15-min responsiveness
   while the container is alive. Offset off :00/:30.
If DJ wants only one on cost grounds, keep the hourly Routine — it is the one that fixes the
reported failure.

**Baseline file: container-local, and treat it as disposable.** `C:/Users/dj/agentmail_lastsha_<role>.txt`
does NOT exist in a cloud container — Lead's DM template still hands cloud sessions that Windows
path. Use `/home/user/agentmail_lastsha_<role>.txt`, and make the watcher prompt self-heal: if the
baseline is missing (fresh container), rewrite it and review only the last 24h instead of diffing
against nothing.

**Getting the blob sha without `gh`.** `gh` is not installed in cloud shells and the env
`GITHUB_TOKEN` is a 14-char placeholder that 403s against api.github.com. But
`git rev-parse origin/main:3_Documentation/AGENT_MAIL.md` returns **the same blob sha** the Contents
API returns — which is the sha Portal's compare-and-swap gotcha requires (blob, NOT commit).
Fetch first.

**One more caveat:** a Routine created from a cloud session stores no MCP connectors, so if it ever
fires a FRESH session instead of resuming the bound one, that session has no `mcp__github__*` tools.
Self-bound fires are fine.

See [[project_design_cloud_can_read_artifacts]], [[feedback_agent_mail_autowatch]].
