---
name: feedback_durable_watcher_not_session_cron
description: "★ DJ standing rule (2026-09-12): DURABLE/must-always-run background work goes in a SERVER-SIDE Render watcher (APScheduler in main.py), NEVER a session CronCreate cron (those expire in 7 days + die on session exit = an accident waiting to happen). Session crons are ONLY for a live session's OWN presence (heartbeat/mail-watcher — they SHOULD die with the session + self-re-arm on restart). If a session cron is ever unavoidable for durable work, it MUST have a re-arm safeguard (re-armed on restart AND a scheduled re-arm before the 7-day expiry) — never set one up to just silently expire."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-12T18:39:15.428Z
---

**DJ (2026-09-12), on discovering the ENDPOINT_MAP hourly regen backstop was a session cron:** *"a watcher that expires in 7 days with no ability to restart it… it's an accident waiting to happen. The first go-to has gotta be a good, steady watcher, and that sounds like it needs to come from Render. Worst case, if we set one up within a session, at least set up the ability to reset it every 5-6 days. Just to set one up to expire in 7 days doesn't make sense. We've run into this far too many times."*

**The rule — durable-watcher-first:**
- **Any recurring background job that must keep running regardless of who's logged in → a Render server-side scheduler job** (APScheduler `scheduler.add_job` in `main.py`, like `_scheduled_fleet_watchdog`, `_scheduled_thumbtack_72h`, etc.). These are zero-Claude-token, survive every session death, and NEVER expire. This is the DEFAULT, the first choice — not an afterthought.
- **Session `CronCreate` crons are last-resort, and ONLY appropriate for things that represent a LIVE SESSION'S OWN presence** — the Lead roster-heartbeat, per-role AGENT_MAIL watchers. Those SHOULD die when the session dies (a dead session must stop heartbeating) and they self-re-arm on the next session start ([[feedback_agent_mail_autowatch]], [[feedback_lead_roster_restamp]]). That's correct use.
- **NEVER put durable, must-not-lapse work in a session cron.** CronCreate crons auto-expire 7 days from creation, firing does NOT reset that clock, and they die on session exit — so durable work in one silently STOPS with no alert. That's the repeated failure DJ is calling out.
- **If a session cron is ever the only option for durable work:** it MUST have a re-arm safeguard — re-armed on session restart AND a scheduled re-arm well before the 7-day expiry (e.g. a 5-6 day one-shot that re-creates it). Never rely on the raw 7-day lifetime.

**How to apply:** before creating ANY recurring timer/watcher, ask "must this survive session death + never lapse?" → yes = Render APScheduler. Only "this is this session's own presence signal" justifies a session cron. When you catch durable work sitting in a session cron, migrate it to Render (the endpoint-map regen did exactly this 2026-09-12). See [[feedback_check_endpoint_map_first]] (the map this rule was triggered by) and [[project_endpoint_map]].
