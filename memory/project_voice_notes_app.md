---
name: project_voice_notes_app
description: "Voice Notes app (v2_voicenote.html + routers/owner/voicenote.py): personal record→transcribe→keep, a TRUNCATED reuse of the meeting engine (meeting._transcribe, NO _distill). Separate store wsc.memory.voicenotes + wscvn: attachments. Same shared transcribe engine now also powers the Idea Board mic."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-13T00:54:45.880Z
---

**Built 2026-09-12 (DJ-requested via Lead; brief `3_Documentation/VOICE_NOTES_APP_BRIEF.md`).** A personal "talk it out so I won't forget it" screen: tap Record → transcribe → DJ gets the **transcript (one-tap copy)** + the **audio (inline play + Save/download)** to move into Gemini/Claude/a text himself. **NO auto-distribution** (no memories/ideas/decisions/tasks) — that's the Meeting app's job, deliberately excluded here.

## Files
- **`static/owner/v2_voicenote.html`** — the screen. Recorder is a VERBATIM reuse of v2_meeting.html's (MediaRecorder + the TWO screen-wake nets [navigator.wakeLock + hidden canvas-fed video] that fix the phone-sleep→whisper "you you you" silence hallucination + resume + flushFailed + chunk-stream). New below it: transcript panel (selectable + Copy button w/ clipboard + execCommand fallback), `<audio>` play + a Save link (`?dl=1` → Content-Disposition attachment), and a **past-notes list** (newest first, tap a row → opens that note's transcript+audio+Delete). Launcher tile in `v2_apps.js` (🗒️ Voice Notes).
- **`routers/owner/voicenote.py`** — a TRUNCATED clone of the meeting pipeline. Endpoints (all `/owner/api/voicenote/*`, feature-namespaced so no route-shadow): `chunk` (durable ir.attachment `wscvn:<id>:<idx>`), `finalize` (kick bg thread), `status`, `list`, `audio` (streams the assembled `wscvn:<id>` attachment; `dl=1` forces download), `delete`. Background `_process_voicenote`: gather chunks → assemble ONE durable `wscvn:<id>` audio attachment (kept for playback, chunks then dropped) → **`meeting._transcribe(audio)`** (REUSED — ffmpeg-segments >24MB + silence-dedupe) → store transcript, status=done. **STOPS THERE — never calls `_distill`.** Retry cron `retry_stuck_voicenotes` (main.py `_scheduled_voicenote_retry`, */10) re-kicks a note whose transcribe died on a worker restart; resume is idempotent (returns fast if transcript exists; re-transcribes from saved audio) — so **no run_token guard needed** (meeting's token guard exists only to dedupe distribution, which we don't do).
- **main.py:** `import voicenote` is TOP-LEVEL → voicenote.py must exist before main.py deploys or boot crashes; push order = voicenote.py first, main.py last. Registered `app.include_router(owner_voicenote.router, prefix="/owner")`.

## Isolation from meetings (QC gate)
Separate store `wsc.memory.voicenotes` (generic `memory_store` keyed by store name — `mem_get/mem_put('voicenotes')`), separate attachment prefix `wscvn:` (never `wscmtg:`), and `_process_voicenote` provably never calls `_distill`. So it never touches the meetings list or the decisions/ideas stores.

## ★ Shared transcribe engine + shared RECORDER (same day)
`meeting._transcribe(data)` is the ONE long-audio transcribe path (ffmpeg-segments >24MB), reused by Voice Notes, the Idea Board mic, and meeting.

**★ DJ STANDING RULE (2026-09-12): EVERY recording feature MUST chunk-stream to the server WHILE recording** so a dead/slept phone never loses what was already spoken (single-blob-at-stop is banned). To honor it without forking three recorders:
- **`static/owner/wsc_recorder.js`** — ONE shared, phone-death-safe chunk-stream recorder, ported from meeting's field-proven recorder (both screen-wake nets + 60s durable chunk-stream + resume + flushFailed). DOM-decoupled: the page passes `{chunkUrl, finalizeUrl, discardUrl, idField, idPrefix, activeKey, finalizeExtra, on:{state,tick,rec,finalized,resume,canceled}}` and gets callbacks; `WSCRecorder(cfg)` returns `{start,stop,cancel,resume,finishExisting,checkResume,isRecording}`. finalized passes the finalize RESPONSE JSON (so a synchronous-finalize app can toast its result). Each app keeps its OWN backend finalize/process.
- **Voice Notes** + **Idea Board mic** both now use wsc_recorder.js. **Meeting** still has its own inline copy — migration to the shared recorder is a deliberate CAREFUL fast-follow (don't destabilize the flagship recorder in the same pass); 2 recorder sources now → 1 after.
- **Ideas conversion (2026-09-12):** `/api/ideas/chunk` + `/api/ideas/finalize` + `/api/ideas/discard`; finalize is SYNCHRONOUS (assemble chunks → `ideaboard_session_<sid>` attachment → segmented `_transcribe` → `_format_speakers` → scan `_extract_ideas`/`_append_proposals` → append the 'recording' chat msg → return {added,chars} for the toast) so the chat flow/render is UNCHANGED (lowest risk to the live feature). Chunk prefix `ideaboard_chunk_<sid>:<idx>`. Orphan-retry cron `retry_orphan_ideas_recordings` (main.py `_scheduled_ideas_rec_retry`, */10) finalizes any chunk-set whose **NEWEST** chunk is >15min old with no chat msg (covers a finalize request dying after the audio was saved). ★ Keys on the NEWEST chunk, NOT the oldest (Lead QC caught this): keying on oldest would finalize+truncate a still-STREAMING >15-min recording mid-stream (its first chunk passes the cutoff while it's still live), losing the tail — an active recording always has a fresh newest chunk (60s cadence), so newest>15min = genuinely stopped/dead. Old single-blob `/api/ideas/record` KEPT server-side (back-compat), retired from the UI. author from `session_actor` (2026-09-06 rule), never the body.

Related: [[project_meeting_pipeline_restart_resilience]], [[project_render_coalesces_rapid_pushes]].
