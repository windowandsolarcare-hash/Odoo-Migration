---
name: project_hiring_interview_transcription
description: Phone-interview transcription workflow + data model. Transcribe Workiz call recordings (Whisper medium) → ID candidate → drop parsed answers into per-question Transcribed Answer fields; store full transcript + audio as Odoo attachments. READ before processing an interview recording.
metadata: 
  node_type: memory
  type: project
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

# Phone-interview transcription → hiring ATS (built 2026-06-09, for interviews 6/10)

**Goal:** Cheryl phone-interviews phone-screen candidates; Workiz auto-records. DJ downloads the `.wav` (like the test `z7WyC4-459758878.wav`) and sends it. I transcribe, identify the candidate, parse each question's answer, and populate the hiring ATS.

## ⚠ The recording file carries NO phone number (verified)
The Workiz `.wav` has zero metadata (no INFO/comment tags) and the filename is just Workiz IDs (`z7WyC4` record id + `459758878` call id — NOT a 10-digit phone). **Cannot ID the candidate from the file.** Match by: (a) Cheryl says the name at call start → read from transcript; (b) DJ tells me / renames the file; (c) phone from Workiz call log → match `hr.applicant.partner_phone`.

## Transcription
Use **Whisper `medium`** model (8 kHz phone audio — `small` is rough). `whisper FILE --model medium --language en ...`. Tools at `/c/Users/dj/bin/whisper` + `ffmpeg`. Speaker labels ("Interviewer"/"Candidate"): Whisper alone does NOT diarize — best-effort by turn-taking, or set up whisperx/pyannote for true diarization (NOT done yet).

## Where data goes (hiring ATS — hr.applicant)
The questions live in the candidate detail "Phone Interview" area:
- **General Questions** — shared list (`/api/hiring/general_questions`); per-candidate data in `===PHONE_INTERVIEW===` section of `applicant_notes` = JSON `{ q.id: {c, n, a} }`.
- **Individual Questions** — per-candidate `===INDIVIDUAL_QUESTIONS===` = JSON array `[{id, text, c, n, a}]`.
- **`a` = the Transcribed Answer field** (added 2026-06-09). Per question: Question → Notes (`n`) → collapsible editable Transcribed Answer (`a`). To populate: parse each Q's answer from the transcript, write it into the matching question's `a`.
- **Full transcript** → Odoo `ir.attachment` on hr.applicant, name **`Interview Transcript.txt`** (mimetype text/plain). Frontend "▶ Full Transcript" toggle fetches `/api/hiring/applicant/{id}/transcript`.
- **Audio file** → `ir.attachment` on hr.applicant, name **`Interview Recording - <Name>.wav`** (mimetype audio/wav). List `has_audio` flag = batch attachment query (name ilike 'Interview Recording').
- **Inline player (2026-06-10):** candidate detail has an `<audio id="interviewAudio" controls preload="none">` (in `#audioPlayerWrap`) — `openDetail` sets its src to `/api/hiring/applicant/{id}/audio` when `has_audio`. DJ plays in-app, no download. `preload="none"` so the 20MB only streams on tap. The endpoint streams **inline + supports HTTP Range** (206 partial) so seeking works on the phone; `?dl=1` forces `Content-Disposition: attachment` for the "⬇ Download" button. Multi-part calls (e.g. David Pt1+Pt2) are **concatenated into ONE wav with ffmpeg** (`concat` filter) before upload so one player covers the whole interview.

**Attachment naming is load-bearing** — the list/endpoints match on `name ilike 'Interview Recording'` / `'Interview Transcript'` (ilike = substring). **Name them `Interview Recording - <Candidate Name>.wav` and `Interview Transcript - <Candidate Name>.txt`** (DJ asked 2026-06-10 — the download filename = the attachment name, so the name lets him tell candidates apart). The "Interview Recording" / "Interview Transcript" prefix MUST stay intact for the ilike match; just append " - <Name>".

## My processing steps per recording
1. Transcribe (medium) → text with speaker labels.
2. Identify candidate (name from transcript / DJ).
3. Upload audio as ir.attachment `Interview Recording.wav` (datas=base64) on the applicant.
4. Upload transcript as ir.attachment `Interview Transcript.txt`.
5. Parse each general + individual question's answer; write into the question JSON `a` field; PUT `applicant_notes` (preserve all other sections — see [[project_hiring_ats]] section format). Don't clobber `===RAW_JSON===` etc.

## ⚠ Cheryl checks off questions LIVE during the call → MERGE, never insert (2026-06-10)
While Cheryl interviews, she taps the question checkboxes, which writes a `===PHONE_INTERVIEW===` section ( `{qid:{c:true,n}}` ) to `applicant_notes` — possibly AFTER you've already read the notes. If you then *insert* your own PHONE_INTERVIEW block you get TWO sections → `JSON.parse` sees "Extra data" → answers don't render. **Always: read notes fresh → parse ALL existing PHONE_INTERVIEW blocks → merge (keep her `c`/`n`, overlay your `a`) → rebuild with exactly ONE of each marker.** Same for INDIVIDUAL_QUESTIONS. Use a generic regex split over all `===MARKER===`, dedupe, reserialize in canonical order. The order-independent reader is [[project_hiring_notes_marker_parser]].

## Answer field = `a`, written as a clean faithful summary (not raw rambling)
Phone audio + nervous candidate = very rambly transcript. Parse each Q's answer into a concise, faithful summary in `a` (paraphrase, keep what they actually said). General answers → PHONE_INTERVIEW `{qid:{c,n,a}}`; individual → INDIVIDUAL_QUESTIONS array `[{id,text,c,n,a}]`. Diego (id 145) done 2026-06-10 as the worked example: 14/15 general + 4/4 individual.

## Transcription speed (CPU, no GPU)
`medium` ≈ 75 min for a ~13-min call on this box (~32 frames/s). `small` ≈ 10-15 min, very usable for phone audio (Diego's small pass was clean). Run `small` first for format check, `medium` in background to replace. Whisper is 100% LOCAL — zero Claude/API tokens, zero subscription cost.

Files: static/owner/hiring.html, routers/owner/hiring.py. [[project_hiring_ats]] [[project_hiring_interview_tracker]] [[project_hiring_notes_marker_parser]]
