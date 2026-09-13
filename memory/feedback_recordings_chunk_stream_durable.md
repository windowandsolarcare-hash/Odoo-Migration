---
name: feedback_recordings_chunk_stream_durable
description: "★ DJ standing rule (2026-09-12): EVERY audio-recording feature must CHUNK-STREAM to the server continuously WHILE recording, so a dead/slept phone loses nothing already spoken — NEVER hold the whole clip on the device and upload only on Stop. Reuse the meeting app's chunk pipeline (/api/meeting/chunk → durable ir.attachment per chunk → finalize assembles) + its segmented long-audio _transcribe (ffmpeg-split >24MB). One shared recorder for meeting + ideas mic + voice notes; unlimited length + durable + consistent."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-13T00:31:59.583Z
---

**DJ (2026-09-12):** *"I thought it continued to move it up to the server so if the phone died we wouldn't lose anything. I like that for all recordings."*

**The rule — durable recording, phone-death-safe:**
- **Every recording feature streams audio to the server in chunks AS it records** — each chunk persisted server-side (ir.attachment) the moment it's captured. If the phone dies, sleeps, backgrounds, or loses signal mid-recording, everything spoken up to that point is already saved. This is a hard requirement, not a nice-to-have.
- **NEVER** the naive pattern of holding the entire clip in browser memory (`_recChunks`) and uploading one big blob only on Stop — that loses the whole recording to a dead phone AND hits Whisper's 25MB single-call cap / upload timeouts on anything long. (That was the ERP Idea-Board mic's bug, 2026-09-12.)
- **Reuse the MEETING app's pipeline** (`meeting.py`), don't fork: `/api/meeting/chunk` stores each chunk as a durable ir.attachment during recording; `/api/meeting/finalize` assembles; `_transcribe` ffmpeg-segments audio >24MB into ~20-min slices, transcribes each, concatenates (`_WHISPER_LIMIT=24MB`) → unlimited length. Also carries the wakeLock (screensaver-kills-mic → "you you you" hallucination guard) + run-dedupe.
- **Build ONE shared chunk-stream recorder** used by the meeting app, the Idea-Board mic, and the Voice Notes app — not three divergent copies (avoids the fix-it-in-N-places drift).

**How to apply:** any new/edited recording UI → chunk-stream + segmented transcribe from the meeting pipeline, verify chunks persist server-side MID-record (kill the tab mid-recording → the partial is still recoverable). See [[feedback_durable_watcher_not_session_cron]] (same "durable, survives death" instinct), the Voice Notes build (VOICE_NOTES_APP_BRIEF.md), and meeting.py.
