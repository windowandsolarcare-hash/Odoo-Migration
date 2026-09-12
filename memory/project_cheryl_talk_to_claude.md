---
name: project_cheryl_talk_to_claude
description: "Cheryl's \"Talk to Claude\" in-app chat (/cheryl/assistant). The APP answers her in-app via an APScheduler sweep (NOT the cloud relay — that was dropped 2026-09-12 after it failed DJ's live test). routers/cheryl/assistant.py; thread blob wsc.cheryl.assistant.thread; send/thread cookie-gated, inbox/reply NOTIFY_SECRET-guarded fallback."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-12T15:11:06.930Z
---

**Built 2026-09-12** (DJ: "in cheryl app, make a tile or someway Cheryl can talk to Cheryl's cloud"). Brief: `3_Documentation/CHERYL_ASSISTANT_BRIEF.md`.

## ★ FINAL STATE (DJ 2026-09-12): the tile links OUT to her cloud Claude session
After trying cloud-relay then in-app, DJ chose the simplest: the 💬 "Talk to Claude" tile **links straight out of the app to her claude.ai/code session** (`https://claude.ai/code/session_018w4ShGpSjQ6swSGeyE7big`), opening in a new tab (`target="_blank" rel="noopener"`; launcher.js uses an `ext:true` tile flag → the render adds target/rel). Subtitle: "Dump an idea, ask for a change, or start something new". Lives in BOTH `static/cheryl/launcher.js` (FAB) and `static/cheryl/index.html` (home grid). She "drops into" her real cloud session (full tools + continuity) instead of an in-app chat.
- **The in-app assistant was REMOVED 2026-09-12 (DJ-approved "kill it").** Deleted: `routers/cheryl/assistant.py` (send/thread/inbox/reply + respond_new_messages), `static/cheryl/assistant.html`, and main.py's import/include + the `_scheduled_cheryl_assistant` 45s sweep job. The `wsc.cheryl.assistant.thread` config param was left (harmless). Everything from "Pieces" down is HISTORICAL (describes the removed system) — kept for context if DJ ever wants the in-app path rebuilt. Guard done before removal: both tiles confirmed linking OUT (zero `/cheryl/assistant` refs) so nothing 404s.
- **Note:** the authz `PUBLIC_EXACT` entries for `/cheryl/api/assistant/inbox` + `/reply` were left in place (harmless now the routes are gone; they'd just 404). Remove them if ever tidying authz.

## Architecture — IN-APP responder (the app answers her itself)
Cheryl types in-app → message stored in a durable thread (status 'new') → **an in-app APScheduler sweep** (`main.py` `_scheduled_cheryl_assistant`, interval 45s, max_instances=1) calls `assistant.respond_new_messages()` → for each 'new' message it calls Claude (shared client, CLAUDE_MODEL, pinned anthropic 0.122) with a Cheryl system prompt + the thread history (collapsed to valid alternating turns) → appends `{role:'claude'}` + marks the message 'answered'. Her app polls the thread (12s) and shows it. Texting-with-a-delay.
- **History (2026-09-12):** originally built as an async RELAY to Cheryl's-cloud (it would read `/inbox` and POST `/reply`). That FAILED DJ's live test (his message sat unanswered 10+ min — cloud watcher wasn't reliably answering), so DJ had it stood down and switched to this in-app responder. The `/inbox` + `/reply` endpoints remain as a manual/fallback path but nothing drives them now.
- **v1 limits:** the in-app responder has NO tools — it answers/advises from the system prompt + a light task snapshot; it cannot execute side-effectful actions (the prompt tells it to say it'll flag Dan). After 3 failed Claude attempts on a message it posts a graceful "try again" so she's never stuck on a silent thread.

## Pieces
- **UI:** `static/cheryl/assistant.html` (chat bubbles, 12s poll, "Claude is thinking…" pending state, localStorage draft `cheryl_assistant_draft`, rule-13 edge cases, dark-default + `cheryl_theme` light). Tile in BOTH `static/cheryl/launcher.js` (FAB GROUPS) and `static/cheryl/index.html` (home grid) — icon 💬 "Talk to Claude" → `/cheryl/assistant`.
- **Backend:** `routers/cheryl/assistant.py` (included in main.py, prefix `/cheryl`):
  - `GET /cheryl/assistant` — page (cookie-gated, served via with_cheryl_chrome).
  - `POST /cheryl/api/assistant/send` — Cheryl posts; identity is SESSION pid (23243), never a param; idempotent on optional `client_id`. Cookie-gated.
  - `GET /cheryl/api/assistant/thread` — her poll; returns `{messages, pending}` (pending = her last msg still status 'new'). Cookie-gated.
  - `GET /cheryl/api/assistant/inbox` — RESPONDER reads `{new, thread, owner}`. **NOTIFY_SECRET-guarded.**
  - `POST /cheryl/api/assistant/reply` — RESPONDER writes `{text, reply_to?}` → appends claude msg, marks answered. **NOTIFY_SECRET-guarded.**
- **Store:** `ir.config_parameter` key **`wsc.cheryl.assistant.thread`** = JSON list of `{id, role:'cheryl'|'claude', text, ts, status?, claude_attempts?}` (one Cheryl → one thread; capped 300).
- **Responder (current):** in-app — `respond_new_messages()` in assistant.py, driven by the main.py sweep. `_cheryl_context()` pulls her open project.task (x_owner=23243) for grounding; `_anthropic_messages()` collapses consecutive same-role turns (avoids the 0.122 alternating 400).

## Auth (the key gotcha)
`/cheryl/*` is HARD cookie-gated (main.py `_authz_gate`, role-desync fix). The responder has NO cheryl cookie, so `inbox` + `reply` are added to **authz.py `PUBLIC_EXACT`** (bypasses the cookie gate) and guarded INSIDE by `NOTIFY_SECRET` (header `x-notify-secret` or `?secret=`). `send`/`thread` stay cookie-gated (Cheryl's browser). Verified live: inbox without the secret → 403 "bad or missing NOTIFY_SECRET" (reachable + guarded, not the cookie 401). **`_secret_ok` is FAIL-CLOSED** (denies when `NOTIFY_SECRET` is unset) — unlike `notify_dj`'s bootstrap-allow — because `reply` WRITES into Cheryl's thread as "Claude" and sits in PUBLIC_EXACT, so a cleared secret must never become an open injection surface (Lead hardening note 2026-09-12). Prod has NOTIFY_SECRET set.

Related: [[feedback_dj_owns_cheryl_erp_access]], [[project_agent_mail_channel]], [[feedback_notify_dj_channels]].
