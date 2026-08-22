---
name: project_voicemail_to_task
description: Voicemail-to-task upload tool — /owner/voicemails page + /api/voicemail/ingest (Whisper transcribe → My Day task)
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

Built 2026-07-13. DJ wanted his voicemails turned into tasks. Carrier voicemail is a locked box (no API), so scope narrowed (DJ's calls) to a **one-time backlog upload tool** — he shares old voicemails out of AT&T visual voicemail to Gmail, saves the audio, and uploads the files.

**What it is:** page `GET /owner/voicemails` (static/owner/voicemails.html, multi-file `<input accept="audio/*">`) → `POST /owner/api/voicemail/ingest` (in routers/owner/myday.py). Per file: Whisper transcribe → Claude makes a short title + pulls any callback number → `_find_customer` matches caller to Odoo → creates a My Day `project.task` (mirrors `api_myday_add`: user_ids [(4,ODOO_USER_ID)], date_deadline today 09:00, x_myday_status todo, x_myday_type task; if matched: partner_id + x_myday_action='call' one-tap callback) → attaches the audio as ir.attachment (res_model project.task, res_id tid) so DJ can play it. Returns per-file results; page links each to `/owner/myday?open=<id>`.

**Key reuse facts:**
- ★ **Whisper is already in the app** — `dashboard.py` `/transcribe` calls OpenAI `https://api.openai.com/v1/audio/transcriptions` model `whisper-1`, key from env `OPENAI_API_KEY`. Reused that exact call. So NO new key was needed. (whisper-1 accepts m4a/mp3/mp4/wav/webm/mpga — NOT .amr; per-file errors are surfaced. If AT&T files turn out .amr we'll need server-side ffmpeg convert — untested until DJ uploads one.)
- Claude via `get_anthropic_client()` + `CLAUDE_MODEL` (shared.py).
- `from .sms import _find_customer` at myday top-level is SAFE: sms.py's only top-level imports are fastapi+shared; its `from .myday import` is a lazy import inside a function (no boot cycle). Confirmed live deploy came up healthy.
- Owner API endpoints are NOT frontend access-code gated (`api_myday_add` has no code check) — so the ingest endpoint has none either, matching posture.

**Commits:** myday.py b6396a8, voicemails.html fd753c6.

**First real test (2026-07-13) surfaced TWO bugs, both fixed:**
1. ★ **AT&T Android visual-voicemail exports `.amr`, which Whisper (whisper-1) REJECTS.** Fix: `_to_wav_if_needed()` transcodes any non-Whisper format → wav via **`imageio-ffmpeg`** (bundled static ffmpeg, added to requirements.txt — NO system apt needed; ffmpeg has native AMR-NB/WB decode). Only imports imageio_ffmpeg when an unsupported ext arrives. Whisper OK exts: mp3/mp4/mpeg/mpga/m4a/wav/webm/ogg/oga/flac. Commit myday 73760eb, requirements f6206d6.
2. ★ **Android file picker hands back a `content://`-backed File that fails to STREAM at upload time → the POST never left the phone (no server request log at all) → page showed "Network error".** Fix: page now reads each File via `f.arrayBuffer()` into a `Blob` BEFORE building FormData, so bytes are materialized in JS memory. Reusable rule for ANY mobile upload page. Commit voicemails.html 3ab01e7.
- Diagnosed via Render logs (mcp__render list_logs; workspace tea-d78l9fqdbo4c7388n9og must be select_workspace'd first): GET /owner/voicemails = 200 but ZERO POST /owner/api/voicemail/ingest request logged = never reached uvicorn = client-side upload failure.

**★ THEN a MULTI-AGENT COLLISION wiped it (2026-07-13):** a concurrent session pushed `myday.py` commit 7f5539dc (/api/capture) **17 seconds after** my 73760eb, based on a STALE pre-voicemail copy → reverted ALL my myday.py voicemail routes → page + endpoint went 404 ("detail: Not Found"). requirements.txt + voicemails.html survived (different files). RESTORED by re-fetching current myday.py (kept their api_capture), re-applying my 2 edits, pushing with an explicit `sha` guard (commit 1ad5fd4). Verified live: page 200, POST returns my JSON not 404. ★ Lesson (again, see [[feedback_multiagent_collision_field_html]]): on shared repos, push large files WITH the just-fetched `sha` for optimistic-concurrency (GitHub 409s a stale push) instead of the shaless PUT — the line-count guard alone can't catch a same-file concurrent revert.
**NOT done (dropped from scope by DJ):** going-forward capture (AT&T conditional-forward `**004*<twilio#>#` → the EXISTING Twilio voicemail system in voice.py, which already records+transcribes+inbox+push for business lines but does NOT yet create tasks). If DJ later wants live personal-cell voicemails as tasks, add a task-create step to voice.py's `/voice/transcription` + a personal (no ring-DJ) entry point. See [[project_email_to_myday_task]] [[project_myday_action_catalog]].
