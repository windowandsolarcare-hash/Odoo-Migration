---
name: project_fleet_ship_system
description: "The Fleet Ship System (routers/owner/ship.py) — DJ's capture→board→ship tracker. S1 capture spine + S2 derived board + S3 aging/latch/self-heal are LIVE; S4 (bridge+gates) pending. Covers the routes, PG tables, the PR-less git-derive model, the shipped-latch, git_ok outage-handling, the recorder reuse, and the auth split."
metadata:
  node_type: memory
  type: project
  originSessionId: 7f93eb62-ab56-4528-a75a-3a6b108e7612
  modified: 2026-09-28T00:58:31.743Z
---

Built 2026-09-27 (Specialists, DJ-approved v3.4, Lead-QC'd each stage). Plan: `3_Documentation/review/FLEET_SHIP_SYSTEM_BUILD_PLAN.md` (+ PROPOSAL). Turns DJ's spoken/typed thoughts into tracked ship cards on a board that shows what ACTUALLY shipped. **All app-side work is DETERMINISTIC (store/echo/serve/derive) + the existing whisper utility — NO Anthropic API here; decomposition/root-cause/QC run on the Max SUBSCRIPTION via fleet sessions (S4 bridge).**

**Code:** `routers/owner/ship.py` (registered in main.py under `/owner`), UI `static/owner/v2_ship_capture.html` (capture) + Builder-2's `v2_ship_board.html` (board) + a "📥 Capture" launcher tile. Aging job `_scheduled_ship_aging` in main.py (build_scheduler, `minute='7-59/15'`, `_sched_singleton`-guarded). HUD aging producer in feed_live.py (`_ship_aging_alerts`).

**PG tables** (Render PG `wsc-memory-pillar` dpg-danl5vqjnfac7390g8g0-a, via short-lived autocommit conns — regen-store pattern, numInstances-safe): `ship_captures` (id, raw_audio_ref, transcript, raw_fragments jsonb, status[new|claimed|decomposed], created_at) + `ship_cards` (id, title, state[Captured|Building|QC|Ready|Shipped], owner_role, branch, root_cause_ref, dj_confirmed, dep_on jsonb, created_at, state_changed_at, **shipped_at** [S3 latch]) + `ship_heartbeat` (last_tick — dead-man's-switch).

**Routes** (owner-gated unless noted): `POST /owner/api/ship/capture` (raw sink + deterministic `_echo_fragments` sentence/pause split) · `POST .../capture/finalize` (recorder Stop terminal — reuses `meeting._gather_audio`+`_transcribe`) · `GET .../captures` · `GET .../board` (the derive) · `GET .../cards` · `POST .../card` + `POST .../card/state` (**NOTIFY_SECRET**, headless fleet/bridge writes — in PUBLIC_EXACT, `_hook_auth_ok`) · `GET .../health` (**NOTIFY_SECRET**, dead-man's-switch stale_minutes for an external uptime-ping).

**★ Recorder reuse (S1):** the capture front door REUSES the ONE shared `wsc_recorder.js` — configured with `chunkUrl:'/owner/api/meeting/chunk'` (the durable meeting chunk store), `finalizeUrl:'/owner/api/ship/capture/finalize'`, `idField:'meeting_id'`, `idPrefix:'cap_'` (own id namespace → `wscmtg:cap_…` chunks, invisible to the meeting retry cron which is RECORD-driven not chunk-scanning). NO 2nd recorder. Transcription = `_vm_whisper` (OpenAI whisper — the allowed existing utility, NOT the Anthropic API). ★ LESSON (fixed live): a recording finalize that transcribes synchronously can lose its RESPONSE on a phone (slow whisper + backgrounding) → the CLIENT falsely reported "transcription snag" though the capture SAVED. Fix: the page VERIFIES the durable capture (polls GET /captures for the recorder id) instead of trusting the finalize response — mirror the meeting status-poll. See [[feedback_recordings_chunk_stream_durable]].

**★ PR-less derive model (S2, Lead-blessed — this fleet has NO PRs, never merges branches, deploys via Contents-PUT-to-main):** CAPTURED + SHIPPED are DERIVED from git reality; middle states (Building/QC/Ready) are STORED in ship_cards.state (no git artifact for "Lead QC'd it"). SHIPPED = a `card-<id>` / `ships #<id>` reference in a LIVE-main commit message (the PR-less equivalent of "PR closed") — **git WINS** over stored state. Derive via the **GitHub REST API** (branches + recent-commits scan), NOT `git log` (Render has no local git); reuses the app's GITHUB_TOKEN+httpx; SWR-cached ~60s. Bidirectional self-check flags: `building_no_branch`, `claimed_shipped_no_commit`. **Convention going forward: a card's shipping Contents-PUT commit message includes `card-<id>` so Shipped auto-derives + latches.**

**★ S3 two hard requirements (Lead, without which the board regresses):**
1. **LATCH Shipped on first sighting** — `_git_signals` only scans the last 100 main commits, so a card shipped >100 commits ago falls out of the window and would un-ship. `aging_tick`'s `_latch_shipped` PERSISTS state=Shipped + `shipped_at` on first `card-<id>` sighting (git_ok-gated, idempotent COALESCE); `_derive_board` treats a stored `shipped_at` as Shipped → never un-ships.
2. **git-unavailable ≠ git-says-no** — `_git_signals` returns a `git_ok` flag (True only if BOTH GitHub reads succeeded; else keeps last-known cache). `_derive_board` SUPPRESSES all self-check flags when not git_ok → a GitHub outage never spams false alerts. `claimed_shipped_no_commit` also excludes latched cards.

**Aging (S3):** thresholds Captured 48h / Building 120h / QC 24h / Ready 24h (QC/Ready most aggressive per M5); a card with an unmet `dep_on` (blocker not Shipped) is "parked" → aging paused to a 168h backstop + dependency-trigger. Alerts are LIVE-DERIVED HUD cards (never a stored inbox), higher urgency at 2× threshold. **SMS escalation deliberately NOT wired** (an aged internal ship card isn't a can't-miss for DJ — [[feedback_notify_dj_channels]]); revisit once thresholds prove out. Orphan sweep: deletes `wscmtg:cap_*` attachments >12h old with no ship_captures row (triple-guarded, can't touch a meeting chunk). Dead-man's-switch: heartbeat + `/health` for an external uptime-ping.

**Dogfood:** cards `ships1/ships2/ships3` (Shipped) + `ships4` (Captured) + `shipsys` (umbrella) track the system's own build on the board.

**Pending: S4** = the subscription-session BRIDGE (pulls captures, decomposes transcript→cards IN its own session, marks decomposed) + M4 root-cause gate (HARD Building precondition) + M5 ship-by-default — Lead owns the bridge-decompose + M4 spec. Related: [[project_endpoint_map]], [[feedback_data_location_odoo_vs_postgres]], [[feedback_recordings_chunk_stream_durable]], [[feedback_hud_cards_live_not_inbox]].
