---
name: project_cheryl_talk_to_claude
description: "Cheryl's \"Talk to Claude\" in-app chat (/cheryl/assistant) = ASYNC RELAY to Cheryl's-cloud. routers/cheryl/assistant.py; thread blob wsc.cheryl.assistant.thread; send/thread cookie-gated, inbox/reply NOTIFY_SECRET-guarded + whitelisted in authz PUBLIC_EXACT."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T07:33:49.016Z
---

**Built 2026-09-12** (DJ: "in cheryl app, make a tile or someway Cheryl can talk to Cheryl's cloud"). Brief: `3_Documentation/CHERYL_ASSISTANT_BRIEF.md`.

## Architecture — async relay (NOT an in-app Claude-API call)
Cheryl types in-app → message stored in a durable thread → **Cheryl's-cloud** (the always-up cloud session) watcher reads it, acts with her full tools + memory, writes the reply back → her app polls and shows it. Texting-with-a-delay. Chosen over a stateless in-app /ask so she gets true continuity with the session that knows her ongoing projects. (DJ can switch to instant/stateless if he prefers — flagged; default is relay.)

## Pieces
- **UI:** `static/cheryl/assistant.html` (chat bubbles, 12s poll, "Claude is thinking…" pending state, localStorage draft `cheryl_assistant_draft`, rule-13 edge cases, dark-default + `cheryl_theme` light). Tile in BOTH `static/cheryl/launcher.js` (FAB GROUPS) and `static/cheryl/index.html` (home grid) — icon 💬 "Talk to Claude" → `/cheryl/assistant`.
- **Backend:** `routers/cheryl/assistant.py` (included in main.py, prefix `/cheryl`):
  - `GET /cheryl/assistant` — page (cookie-gated, served via with_cheryl_chrome).
  - `POST /cheryl/api/assistant/send` — Cheryl posts; identity is SESSION pid (23243), never a param; idempotent on optional `client_id`. Cookie-gated.
  - `GET /cheryl/api/assistant/thread` — her poll; returns `{messages, pending}` (pending = her last msg still status 'new'). Cookie-gated.
  - `GET /cheryl/api/assistant/inbox` — RESPONDER reads `{new, thread, owner}`. **NOTIFY_SECRET-guarded.**
  - `POST /cheryl/api/assistant/reply` — RESPONDER writes `{text, reply_to?}` → appends claude msg, marks answered. **NOTIFY_SECRET-guarded.**
- **Store:** `ir.config_parameter` key **`wsc.cheryl.assistant.thread`** = JSON list of `{id, role:'cheryl'|'claude', text, ts, status?}` (one Cheryl → one thread; capped 300).
- **Responder:** Cheryl's-cloud arms its own watcher (GET inbox → act → POST reply, with `X-Notify-Secret: <NOTIFY_SECRET>`). No app files. Cadence ~5 min while up.

## Auth (the key gotcha)
`/cheryl/*` is HARD cookie-gated (main.py `_authz_gate`, role-desync fix). The responder has NO cheryl cookie, so `inbox` + `reply` are added to **authz.py `PUBLIC_EXACT`** (bypasses the cookie gate) and guarded INSIDE by `NOTIFY_SECRET` (header `x-notify-secret` or `?secret=`) — same server-to-server secret pattern as `notify_dj`. `send`/`thread` stay cookie-gated (Cheryl's browser). Verified live: inbox without the secret → 403 "bad or missing NOTIFY_SECRET" (reachable + guarded, not the cookie 401).

Related: [[feedback_dj_owns_cheryl_erp_access]], [[project_agent_mail_channel]], [[feedback_notify_dj_channels]].
