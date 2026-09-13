---
name: project_voice_notes_app
description: "Voice Notes app (v2_voicenote.html + routers/owner/voicenote.py): personal record→transcribe→keep, a TRUNCATED reuse of the meeting engine (meeting._transcribe, NO _distill). Separate store wsc.memory.voicenotes + wscvn: attachments. Same shared transcribe engine now also powers the Idea Board mic."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-13T00:30:17.279Z
---

**Built 2026-09-12 (DJ-requested via Lead; brief `3_Documentation/VOICE_NOTES_APP_BRIEF.md`).** A personal "talk it out so I won't forget it" screen: tap Record → transcribe → DJ gets the **transcript (one-tap copy)** + the **audio (inline play + Save/download)** to move into Gemini/Claude/a text himself. **NO auto-distribution** (no memories/ideas/decisions/tasks) — that's the Meeting app's job, deliberately excluded here.

## Files
- **`static/owner/v2_voicenote.html`** — the screen. Recorder is a VERBATIM reuse of v2_meeting.html's (MediaRecorder + the TWO screen-wake nets [navigator.wakeLock + hidden canvas-fed video] that fix the phone-sleep→whisper "you you you" silence hallucination + resume + flushFailed + chunk-stream). New below it: transcript panel (selectable + Copy button w/ clipboard + execCommand fallback), `<audio>` play + a Save link (`?dl=1` → Content-Disposition attachment), and a **past-notes list** (newest first, tap a row → opens that note's transcript+audio+Delete). Launcher tile in `v2_apps.js` (🗒️ Voice Notes).
- **`routers/owner/voicenote.py`** — a TRUNCATED clone of the meeting pipeline. Endpoints (all `/owner/api/voicenote/*`, feature-namespaced so no route-shadow): `chunk` (durable ir.attachment `wscvn:<id>:<idx>`), `finalize` (kick bg thread), `status`, `list`, `audio` (streams the assembled `wscvn:<id>` attachment; `dl=1` forces download), `delete`. Background `_process_voicenote`: gather chunks → assemble ONE durable `wscvn:<id>` audio attachment (kept for playback, chunks then dropped) → **`meeting._transcribe(audio)`** (REUSED — ffmpeg-segments >24MB + silence-dedupe) → store transcript, status=done. **STOPS THERE — never calls `_distill`.** Retry cron `retry_stuck_voicenotes` (main.py `_scheduled_voicenote_retry`, */10) re-kicks a note whose transcribe died on a worker restart; resume is idempotent (returns fast if transcript exists; re-transcribes from saved audio) — so **no run_token guard needed** (meeting's token guard exists only to dedupe distribution, which we don't do).
- **main.py:** `import voicenote` is TOP-LEVEL → voicenote.py must exist before main.py deploys or boot crashes; push order = voicenote.py first, main.py last. Registered `app.include_router(owner_voicenote.router, prefix="/owner")`.

## Isolation from meetings (QC gate)
Separate store `wsc.memory.voicenotes` (generic `memory_store` keyed by store name — `mem_get/mem_put('voicenotes')`), separate attachment prefix `wscvn:` (never `wscmtg:`), and `_process_voicenote` provably never calls `_distill`. So it never touches the meetings list or the decisions/ideas stores.

## ★ Shared transcribe engine (same day)
`meeting._transcribe(data)` is now the ONE long-audio transcribe path, reused by BOTH Voice Notes AND the **Idea Board mic** (`ideas.py /api/ideas/record` — swapped its single `_vm_whisper(data)` [~25MB / few-min cap] for `_transcribe(data)`; raised ideas.html's upload abort 180s→600s). DJ hit the cap on the Idea Board mic 2026-09-12. **MINIMUM fix applied** (segmented transcribe + longer client timeout); the Ideas recorder is still single-blob synchronous — the ROBUST follow-up (adopt the chunk-stream/background pipeline like Voice Notes/meeting) is deferred for truly-unbounded recordings.

Related: [[project_meeting_pipeline_restart_resilience]], [[project_render_coalesces_rapid_pushes]].
