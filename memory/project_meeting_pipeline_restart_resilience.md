---
name: project_meeting_pipeline_restart_resilience
description: "In-worker background jobs (meeting transcription) die on EVERY Render worker restart, and EVERY commit to main (incl. AGENT_MAIL.md / SESSION_ROSTER.md doc commits) triggers an autodeploy → restart. Fixed w/ resumable pipeline + heartbeat; root-cause kill = Render Ignored Paths. 2026-09-09."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-09T21:47:51.689Z
---

**Incident (2026-09-09, DJ's FIRST real meeting):** the Memory-pillar meeting stuck at `status=transcribing` for ~40 min, never filing. Root cause = a chain, worst-first:

1. **The meeting pipeline runs in a daemon THREAD inside the FastAPI web worker** (`_process_meeting` spawned from finalize/cron). A Render **worker restart kills that thread mid-transcription** — leaving status frozen at 'transcribing' with `err=None` (no error, the thread just vanished). whisper (httpx `timeout=180`) + ffmpeg (`timeout=600`) mean it can't HANG — a freeze = a killed thread, not a stall.
2. **EVERY commit to `main` triggers a Render autodeploy → worker restart.** That includes doc/mail commits: **`AGENT_MAIL.md` writes and every session's `SESSION_ROSTER.md` watcher-heartbeat.** With 6 sessions heartbeating on offsets, that's a restart every ~2 min — the ~3-min transcription never survived. ★ The URGENT "recover the meeting" AGENT_MAIL entry itself deployed and killed the cron's recovery re-kick.
3. The `retry_stuck_meetings` cron (`*/10`) DID work — it re-kicked at the 10-min-stale mark — but each re-kick was killed by the next deploy before finishing.

**EMERGENCY RECOVERY PLAY (worked):** a **FULL commit freeze** by the whole fleet — NO code pushes, NO AGENT_MAIL writes, NO roster heartbeats (coordinate by DIRECT SendMessage, not mail — a mail write is the exact killer). With the worker stable, the `*/10` cron re-kick completed in ~3 min and filed. Verify state by reading Odoo directly: `ir.config_parameter 'wsc.memory.meetings'` (status/run_token/last_progress_at) + chunk sizes via `ir.attachment name like 'wscmtg:<mid>:'`. Local Odoo key = `C:/Users/dj/_odoo_key_val.txt` (JSON-RPC to window-solar-care, uid 2).

**DURABLE FIXES:**
- **★ #4 Render BUILD FILTER (root-cause kill):** set the service's **Ignored Paths = `3_Documentation/**`** (covers AGENT_MAIL.md, SESSION_ROSTER.md, docs). Render skips a deploy when a commit touches ONLY ignored paths → mail/roster/doc commits stop bouncing the worker. Code (routers/**, static/**, main.py, requirements.txt) still deploys. **Not settable via the render MCP (env-vars only) — needs the Render dashboard (Settings→Build Filters) or a Render API key to PATCH `buildFilter`.** DJ-owned. This alone would've prevented the incident.
- **#1 heartbeat during `_transcribe`** (built): `_transcribe(data, mid, token)` `_beat()`s before whisper, after ffmpeg, per segment → a long transcribe isn't seen as stale → cron won't re-kick a running run.
- **#2 restart-RESUMABLE** (built): after whisper, checkpoint the transcript to `wsc.memory.mtg_transcript.<mid>`; `_process_meeting` resumes at DISTILL if that exists (skips re-transcribe). ★ Fixed a latent bug — chunks were deleted right after transcription, so a mid-distill restart re-gathered→found none→"no audio" (lost meeting); chunk-delete + checkpoint-clear MOVED to `_file_distribution` success. Restart at any stage now resumes cleanly.
- **#3 off-worker transcription** (dedicated Render worker / job queue) — scoped, DEFERRED: #4+#1+#2 make the in-worker approach reliable.

**★ FLEET LESSON:** any in-worker background job (transcription, long syncs) is fragile to the fleet's own doc/mail commit churn. Until Ignored Paths is set, a doc commit = a worker restart. Design long jobs to be restart-resumable, and know the freeze play for emergencies.

See [[project_memory_pillar_phase1]], [[project_render_coalesces_rapid_pushes]], [[feedback_agent_mail_autowatch]].
