---
name: project_transcribe_drive_endpoint
description: "POST/GET /owner/api/transcribe_drive — transcribe any Drive audio file (walkthroughs) using the app's own Drive creds; bypasses the claude.ai 10MB connector cap + local-token expiry"
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-15T12:35:02.638Z
---

**`/owner/api/transcribe_drive`** (routers/owner/notes.py, shipped 2026-09-15) — the durable way to transcribe a large audio file (e.g. DJ's field-walkthrough m4a) that lives in the Vault/Drive.

**Why it exists:** the claude.ai Google Drive connector caps downloads at ~10MB, and a local `drive_token.pickle` expires (invalid_grant → needs re-auth). A ~60MB walkthrough can't come down either way. But the APP holds valid Drive creds and a long-audio transcriber, so it reads the PRIVATE file itself — no DJ "share with anyone," no local-token maintenance.

**How (all reused 1:1, no re-impl):**
- `notes._drive_service()` (env `GOOGLE_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN`) downloads the file by id.
- non-webm audio is normalized to **webm/opus** (mono 16k) via the bundled `imageio_ffmpeg` — because `meeting._transcribe`'s segmenter does `-c copy` into `.webm` and labels whisper `audio/webm`, so a raw m4a would mishandle. Format-prep only; transcription stays 100% in `_transcribe`.
- `meeting._transcribe(data)` = OpenAI whisper-1, ffmpeg-segmented for >24MB (`_WHISPER_LIMIT`), run-deduped. Returns `(text, error)`.
- writes the transcript as a **text file next to the source** in Drive (`<name> — transcript.txt`, same parent folder).

**★ TRANSCRIBE-ONLY** — it does NOT call `_distill`/`log_meeting`/`mem_put`, so it never populates DJ's memory/decisions/tasks/ideas (his explicit concern about the meeting pipeline). Just transcript.

**Shape:** `POST /owner/api/transcribe_drive {file_id}` → starts a BACKGROUND thread (async because an hour-long file segments into minutes of whisper calls — a sync request would blow the gateway timeout), returns `{ok, started, poll}`. `GET /owner/api/transcribe_drive?file_id=` → status stashed in ir.config_parameter `wsc.transcribe.<file_id>`: `{status: downloading|transcoding|transcribing|saving|done|error, transcript_file_id, link, chars}`.

**Watch-point:** the transcode uses `-c:a libopus`. If a future imageio-ffmpeg build lacks libopus, the status shows the ffmpeg stderr — fall back to `libvorbis` (also webm-valid). Owner-gated. Related: [[project_odoo_get_param_returns_false_unset]] (same ir.config_parameter store pattern).
