---
name: project_meeting_distill_maxtokens_and_recovery
description: "Meeting pipeline (meeting.py): distill FAILED on a dense hour-long meeting because _distill used max_tokens=4000 -> rich JSON truncated -> json.loads throws -> silent `except: return None` -> generic 'distillation failed'. Transcript+audio are always safe (checkpointed). How to diagnose + recover a stuck meeting, and the screensaver->'you you you' cause."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-10T23:05:06.731Z
---

**Incident 2026-09-10 (DJ's real ~62-min DJ+Cheryl meeting got stuck; he was frightened it was lost). It was NOT lost.**

## Pipeline (routers/owner/meeting.py)
- Status flow: `processing -> transcribing -> distilling -> filed` (or `error`). Stored in `wsc.memory.meetings` (ir.config_parameter JSON; endpoint GET `/owner/api/memory/meetings`, status poll GET `/owner/api/meeting/status?meeting_id=`).
- **Audio chunks** = ir.attachment named `wscmtg:<meeting_id>:<idx6>` (mimetype audio/webm). Gathered by `_gather_audio` (search name like `wscmtg:<mid>:`). ~1 chunk/60s.
- **Transcript checkpoint** = ir.config_parameter `wsc.memory.mtg_transcript.<meeting_id>` — saved AFTER whisper, BEFORE distill, so a restart resumes at distill (skip re-transcribe). Cleared only on successful file.
- Resilience: audio saved before transcription; transcript checkpointed before distill; **cron `_scheduled_meeting_retry` (*/10 min) re-kicks any meeting stuck >10 min** in processing/transcribing/distilling (NOT 'error').
- Tab-exit/resume keeps the SAME meeting_id, so chunks accumulate under one id (recording survives leaving the tab). Two very short (30-40s) 'filed' meetings the same day were accidental start/stops — the real one was the long id.

## Root cause of "distillation failed"
`_distill` called `client.messages.create(..., max_tokens=4000, ...)` asking for a RICH JSON (minutes+decisions+action_items+ideas+campaigns+content+sops+roadmap+reference+open_questions). A dense hour blew past 4000 output tokens -> truncated -> `re.search(r'{.*}', out, re.S)` grabbed incomplete JSON -> `json.loads` threw -> broad `except Exception: return None` swallowed it -> generic 'distillation failed', NO traceback in Render logs. (A shorter meeting the day before fit under 4000 and filed fine.)

## Fix (Specialists, live 2026-09-10, tip 81109449)
`_distill`: max_tokens 4000 -> escalating 8000 then 16000; 3-attempt loop w/ backoff retrying on truncation (stop_reason=='max_tokens' / JSON parse fail) AND transient API errors; STOPPED swallowing (logs repr(e)+stop_reason+out_len); now returns `(dict|None, err)` so `_process_meeting` stores a SPECIFIC error. Transcription/resume untouched. Pending prompt tweak: add a line telling it to capture concrete REFERENCE facts (named accounts/cards, rates, benchmarks) into reference[] — the one category a Gemini cross-check caught that our pass under-weighted (our distill otherwise beat Gemini on completeness — keep Claude, don't switch models).

## How to DIAGNOSE + RECOVER a stuck meeting (read-only Odoo RPC; key = C:/Users/dj/_odoo_key_val.txt)
1. Read `wsc.memory.meetings` -> find the record by id; check status/last_progress_at/error.
2. Confirm content is safe: transcript checkpoint `wsc.memory.mtg_transcript.<id>` length, and count `wscmtg:<id>:` ir.attachments (sum file_size). Both present = nothing lost.
3. Re-kick (cookie-free, no code): reset the meeting record via Odoo RPC -> status='distilling' + STALE last_progress_at + clear error + no filed_at, so the */10 `_scheduled_meeting_retry` cron re-kicks `_process_meeting`, which resumes from the saved transcript. (An 'error'-status meeting is NOT auto-retried by the cron — that's why the reset is needed.) Deploy any code fix FIRST or it'll fail the same way.
4. Watch: poll status until 'filed' (has minutes_link + transcript_link on Drive, decisions[]+action_items[]).

## Screensaver -> "you you you" (separate, DJ-reported same day)
Mid-meeting the phone screen slept -> mic capture dropped to silence -> whisper HALLUCINATES repeated tokens ("you you you"). Fix = **Screen Wake Lock** in the recorder `static/owner/v2_meeting.html`: `navigator.wakeLock.request('screen')` on Start+Resume (user gesture), release on stop(), and RE-ACQUIRE on `visibilitychange` when recording&&visible (wake locks auto-release on background — the re-acquire is the key). iOS needs Safari 16.4+ (else muted-video fallback). Optional belt-and-suspenders: collapse 4+ repeated-word runs in `_transcribe`. Spec in AGENT_MAIL 2026-09-10.

Records live on Drive: interim minutes + transcript backup also saved locally to `.../Migration to Odoo/MEETING_2026-09-10_*.{txt,md}`. Related: [[project_agent_mail_channel]].
