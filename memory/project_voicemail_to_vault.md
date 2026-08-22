---
name: project_voicemail_to_vault
description: "Voicemail (.amr) → Vault pipeline: Android Visual Voicemail Share → 'Saunders Vault' Drive-folder shortcut drops the raw .amr into the Vault; convert amr→mp3 (local ffmpeg) + transcribe (local Whisper) + upload mp3 & transcript Doc into the Vault 'Voicemails' folder. DJ approved building this auto (2026-08-06). Manual pipeline proven end-to-end."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-06T18:46:30.886Z
---

**DJ's goal (2026-08-06):** get a phone voicemail into his app to READ (he's a reader, not a listener) — the .amr wouldn't play/save to Evernote. "Yes to all": build share-target/auto-convert + auto-transcribe. Manual pipeline proven twice this session.

## The Android workflow (WORKS, confirmed)
Visual Voicemail → tap voicemail → **Share** → **"Saunders Vault"** (a Google Drive **folder shortcut** in the Samsung share sheet). That folder = the app's Vault root **VAULT_ROOT_ID `1uVXJjg4YYfqcijh4Vbvf-snWGfUIyb9Q`** (title literally "Saunders Vault"). Sharing drops the raw `.amr` into the Vault root. **Sync lag ~1 min** (first check often empty, then it lands; DJ tapped 3× → 3 identical dups — same byte size = same voicemail).

## Manual convert + transcribe (what I do now, until server-side auto is built)
1. **Pull raw bytes cleanly (don't hand-copy base64):** `GET https://wsc-field-assistant.onrender.com/owner/api/vault/file?id=<driveFileId>` streams the file bytes (uses the app's own Drive `get_media`). Works while `AUTH_ENFORCE=0`. (download_file_content MCP returns base64 inline for small files, or saves to a tool-results file when > token limit.)
2. **Convert amr→mp3:** local ffmpeg `/c/Users/dj/bin/ffmpeg -i in.amr -codec:a libmp3lame -qscale:a 4 -ac 1 out.mp3`. AMR header = `#!AMR`. (23KB amr ≈ 14s; 42KB ≈ 26s.)
3. **Transcribe:** LOCAL **Whisper** — openai-whisper installed, CLI at `/c/Users/dj/bin/whisper`, models `medium.pt`+`small.pt` cached (`~/.cache/whisper`). Run **`whisper "<mp3>" --model small --language en --output_format txt --output_dir <dir> --fp16 False`** with ffmpeg on PATH (`export PATH=/c/Users/dj/bin:$PATH`). ★ Call `whisper` directly — `python /c/Users/dj/bin/whisper` fails ("can't open file"). `small` is plenty for a clean voicemail.
4. **Upload mp3 to Vault:** `POST /owner/api/notes/upload_file` multipart `file=@...;type=audio/mpeg` `category=Voicemails` `tags=voicemail` → lands in Vault **Voicemails** folder `1cjl1rTntwnZrVhBQL06RCy3ssuEpk5jP`.
5. **Transcript note:** Drive MCP `create_file` — **content must be BASE64**, `mimeType=application/vnd.google-apps.document`, `parentId`=Voicemails folder. (Plain-text content errors "not a valid base64 string".) Verify with `read_file_content`.
6. **Cleanup:** trash the raw `.amr` dups via `POST /owner/api/notes/<driveId>/delete` (trashes, recoverable).

## ★ BUILT 2026-08-06 — the combined Voicemails screen (server-side, no more manual)
DJ: "I already have code that converts a voice into a task. Combine them into one screen." Turned out the app ALREADY had the voice→task half — so I combined, didn't duplicate.

**Pre-existing (DON'T rebuild):**
- Screen **`static/owner/v2_voicemails.html`** (launcher `v2_apps.js` → this file; the `/owner/voicemails` route + `static/owner/voicemails.html` stub are DEAD — V2 twin trap). Pick audio → POST `/owner/api/voicemail/ingest` (multipart field `audio`, multiple).
- Backend `myday.py`: `_vm_whisper` transcribes via **OpenAI Whisper API** (`whisper-1`, needs `OPENAI_API_KEY` — CONFIRMED SET, works ~5s). `_to_wav_if_needed` already transcodes `.amr`→wav via **server imageio-ffmpeg** (so server ffmpeg DOES decode amr). `_vm_meta` = Claude title+callback#. Then creates a **My Day task** (+ audio as ir.attachment).
- Separately, `voice.py` = Twilio BUSINESS-line inbound → in-app **inbox** voicemails, transcribed by **Twilio** (`<Record transcribe=true>` → `/voice/transcription`). Different pipeline (business line, not DJ's personal cell).

**What I ADDED (myday.py + v2_voicemails.html, pushed 2026-08-06):**
- `/api/voicemail/ingest` now takes a **`dest`** form field: `task` (default, unchanged) | `vault` | `both`. Transcribes ONCE, then routes.
- `_to_playable(data,fname)` — passthrough for playable formats; else imageio-ffmpeg → **m4a/aac** (aac built-in, no external encoder). `_vm_to_vault(...)` — reuses **notes.py** helpers (`_drive_service/_find_or_create_folder/_upload_image/_make_doc/_verbatim_html/VAULT_ROOT_ID`) to drop a playable audio + a Google-Doc transcript note into the Vault **"Voicemails"** folder. ONE Vault code path (no dup).
- Screen: retitled "Voicemails"; **destination picker** (📁 Vault default / 📋 Task / 📁+📋 Both); result rows link ▶ Play audio · 📄 Open note · 📋 Open task.

## ★★ AUTO-SWEEP BUILT 2026-08-06 — the true "share and forget" (DJ: "just share… then you take it from there")
- **Endpoint `GET /owner/api/cron/voicemail_sweep?token=<CRON_SECRET>`** (myday.py; CRON_SECRET=`wsc-daily-sync-2026`). Lists `mimeType contains 'audio/'` files DIRECTLY under **VAULT_ROOT** (where the Android Share→Saunders Vault drops them), for each: `get_media` bytes → `_vm_whisper` → `_vm_meta` → `_vm_to_vault` (Vault Voicemails note+playable) → **trashes the raw** → **push DJ** via `_notify`. Transcription failures → moved to Quick Notes/Voicemails/_needs_attention (no infinite reprocess). Helper `_vm_move_to(svc,fid,*segs)`.
- **Render cron `WSC Voicemail Sweep`** (crn-d9qcptqjobas73ftljp0, `*/10 * * * *`, starter, autoDeploy no) hits it every 10 min. Same pattern as the other 5 crons (python `requests.get`). Cost ≈ $0.25–$1/mo (Render bills cron by run-seconds, not flat).
- **"⚡ Check now" button (DJ, cost concern 2026-08-06):** sweep logic refactored into `_run_voicemail_sweep()`; token cron calls it; NEW owner-facing **`POST /owner/api/voicemail/sweep_now`** (no CRON_SECRET) calls it too. `v2_voicemails.html` has a **⚡ Check now** button (`scanNow()`, 120s timeout) → instant processing, shows "✅ N new" / "✓ Up to date", refreshes the list. So the frequent cron can be dialed to daily as a mere backup.
- **★ Render MCP can CREATE crons but NOT update/delete them** — to re-time the sweep to daily, change it in the DASHBOARD: dashboard.render.com/cron/crn-d9qcptqjobas73ftljp0 → Settings → Schedule → `0 12 * * *`. (Left at */10 unless DJ opts to change it.)
- **Proven live 2026-08-06:** processed 4 root audio files (a test mp3 + 3 REAL shared voicemails: Leonard Gleeson solar lead 714-318-4591 / Brad Pearson Kit Carson printing bid 530-417-4999 / Arroyo PT for Anita 442-334-7176), 0 errors; .amr transcoded server-side (imageio-ffmpeg) + whisper OK.

**DJ's workflow now = Visual Voicemail → Share → Saunders Vault → done** (readable+playable note in Vault Voicemails within ~10 min + push). The Voicemails screen (Vault/Task/Both picker) remains for manual/task use.

**★ WHERE DJ READS THEM (he asked twice — this was the real gap):** `v2_voicemails.html` now shows a **"🎙️ Your voicemails" list** on the screen itself (`loadVoicemails()` → `GET /api/notes/list` filtered to `category==='Voicemails' && kind==='doc'`, newest first; each row = 📞 title + `description` snippet + date, taps to the note's `webViewLink`). Refreshes after an upload. So the answer to "where do I see the transcript" = **open the Voicemails screen** (🚀 launcher → Voicemails). DON'T leave transcripts only in the Vault category — DJ looks on the Voicemails screen. (Confirmed live: cron auto-processed a "Call Carol back" voicemail that appeared on the screen unaided.)

## ★ PLAYBACK FIX (DJ: "I see the transcript, but playing it doesn't work")
Cause: the notes' "Audio:" link opened the file in **Google Drive's player, which chokes on tiny 8 kHz mono voicemail files** (the m4a/mp3 are VALID — ffprobe plays them fine; `/api/vault/file` serves correct `audio/mp4`). Fix = play IN-APP, never Drive:
- New endpoint **`GET /owner/api/voicemail/audio?note_id=<docId>`** (myday.py): resolves the note's audio (note `properties.vm_audio`, else parses the "Audio: …/d/<id>/" link out of the exported doc text — so it works for pre-existing notes too) → **307 redirect to `/owner/api/vault/file?id=<audio_id>`** (streams bytes as audio/mp4). Verified: returns 200 audio/mp4, valid aac.
- `_vm_to_vault` now (a) names the audio file after the note title (not generic `voicemail.m4a`) and (b) stamps the note with a `vm_audio` property = audio file id (fast path for the resolver).
- `v2_voicemails.html` list: each row now has an inline `<audio class="vma" controls preload="none" src="/owner/api/voicemail/audio?note_id=<id>">` → native play bar, streams via the app. THIS is how DJ plays a voicemail.
- **Vault viewer also plays audio now** (`v2_vault.html`, DJ asked "can it play there too?"): `previewable()` now includes `audio/`, and `openPreview` has an `isAudio` branch that shows a `#pv-audio` `<audio controls>` (src=`/api/vault/file?id=`), `closePreview` pauses/clears it. So tapping the `🎵 voicemail.m4a` file item in the Vault plays it inline. (The transcript NOTE and the audio FILE are two separate Vault items — note→editor/read, file→play.) Any audio file in the Vault is now playable, not just voicemails.

## Known polish TODO (minor, not yet done)
- Note stamp uses `today_pt()` (processing date) not the voicemail's real date — parse `VoiceMail_YYYY-MM-DD_HH-MM-SS` from the filename when present. (Audio-naming TODO = DONE above.)

**★ Folder-placement fix (same day):** first version put the note/audio in a "Voicemails" folder under **VAULT_ROOT_ID** → it did NOT show in the Vault app, because `notes.py list_notes` only surfaces notes under **Quick Notes** and its subfolders (each Quick-Notes subfolder = a category via `_get_categories`). Fix: `_vm_to_vault` now does `qn_id=_find_or_create_folder('Quick Notes',VAULT_ROOT_ID); folder=_find_or_create_folder('Voicemails',qn_id)` → shows as the **"Voicemails" category** in the Vault. Rule: anything meant to appear in the Vault app must live under **Quick Notes/<category>**, never at VAULT_ROOT. To relocate an existing note+file: `PATCH /owner/api/notes/<id>/move {category}` (works on any Drive file, not just docs; it's PATCH not POST).

See [[project_saunders_vault_notes]] [[project_vault_evernote_drive]] [[project_inputs_notedoc_drops_text]].

## Gmail caveat
Gmail MCP can READ a message but CANNOT download attachment bytes (no GetMessageAttachment tool) → route attachments through Drive ("Save to Drive" then `download_file_content` / `/api/vault/file`).
