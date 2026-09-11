---
name: project_fleet_stale_watchdog
description: "Zero-token server-side fleet stale-watchdog (main.py APScheduler) that alerts DJ when a session's SESSION_ROSTER heartbeat goes stale — the durable replacement for per-session heartbeat crons."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-11T07:47:52.298Z
---

**Why:** per-session mail/heartbeat crons die on session exit + expire after 7 days, so a silently-dead session went unnoticed. DJ wanted something ABOVE the fleet, always alive, that catches a stale/dead session and alerts him — WITHOUT Claude tokens (a Lead relay or pinging sessions both cost tokens).

**Built (2026-09-11, main.py tip ae64c4c):** `_scheduled_fleet_watchdog` on the existing AsyncIOScheduler, `add_job(..., 'cron', hour='*/3', minute=19, misfire_grace_time=600)` — runs every 3h, pure server-side, ZERO tokens. It:
- Fetches the **LIVE** `3_Documentation/SESSION_ROSTER.md` via the **GitHub Contents API** (`https://api.github.com/repos/windowandsolarcare-hash/saunders-render-app/contents/...`, header `Authorization: token <GITHUB_TOKEN>`, base64-decode `.content`) — the SAME env token dashboard.py uses for SHARED_MEMORY.
- ★ **Why GitHub API, not the on-disk file:** the deployed container's `3_Documentation/SESSION_ROSTER.md` is FROZEN at the last CODE deploy — doc commits (heartbeats re-stamp the roster constantly) are in Render's **Build-Filter Ignored Paths = `3_Documentation/**`**, so they DON'T redeploy → on-disk is always stale. Reusable rule: to read a LIVE `3_Documentation/*` file at app runtime, fetch it from GitHub, never from disk.
- Parses each `| **<Role>** | <ref> | <kind> | <Last-checked> | … |` row (split on `|`, role from `**…**` in cell[0], timestamp `YYYY-MM-DD[ HH:MM]` from cell[3] — time optional, defaults 00:00, so a date-only/malformed old row is still caught). Flags role if `now - Last-checked > _FLEET_STALE_HOURS` (=8; was 4 — raised to cut false positives, a live session may not re-stamp for hours).
- **EXCLUDES Cheryl's-cloud** (`'cheryl' in role.lower()`) — it can't self-stamp (no main write) + its ref churns, so its timestamp is never a valid staleness signal.
- **De-dupe:** ir.config_parameter **`wsc.fleet.watchdog`** = `{role: iso_when_alerted}`. Alert only on a FRESH→STALE transition (role not already in state); clear a role from state once it's fresh again so a later staleness re-alerts. One `notify.push_dj(from_role='watchdog', sms='never')` banner — **NOT SMS** — with the SPECIFICS in the SUMMARY so they show on the banner header without tapping ("⚠️ Fleet: N session(s) quiet — Design ~28h, Portal ~1wk…", worst-first, human ~h/~d/~wk; worded "may just need a re-stamp," NOT "may be down") (a session down at night isn't a can't-miss 3am text).

Verified: app boots clean (scheduler accepted the job); offline-ran the parser on the live roster (fresh roles pass, Operator/Design/Portal flagged stale, Cheryl excluded). Tune via `_FLEET_STALE_HOURS` + the add_job cron. See [[feedback_agent_mail_autowatch]], [[feedback_lead_roster_restamp]].
