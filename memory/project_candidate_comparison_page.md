---
name: project_candidate_comparison_page
description: "Candidate Comparison page (Page 2 of the Lead-Technician hire) — live at /owner/hiring/compare, DJ+Cheryl, dials + records candidates. Per-question transcript auto-fill IS now wired+live (Fill-from-recording button + state machine). Has a 📋 Interview Schedule box + by-person time-sort. See body for the current 10-question set."
metadata:
  node_type: memory
  type: project
  originSessionId: e3071731-f37a-4440-a358-34be556223c2
  modified: 2026-10-12T03:29:19.786Z
---

Page 2 of the 2026 Lead Window & Solar Cleaning Technician hire (the HR/ZipRecruiter round). Built + deployed 2026-10-10, ahead of the Oct 12–13 phone interviews. Cheryl + DJ use it to compare candidates and run the phone screens.

**Where it lives (saunders-render-app repo):**
- Route: `/owner/hiring/compare` — 401-gated to DJ + Cheryl only.
- Router: `routers/owner/hiring_compare.py`; template: `static/owner/hiring_compare.html`.
- Built by duplicating the approved HR mockup EXACTLY (RULE #1 — no rebuild-from-description). Canonical mockup: `Odoo-Migration/3_Documentation/candidate_comparison_mockup.html` (50,345 bytes). HR verified the live source 1:1 against it 2026-10-10 (all three views, DIMS order, sticky header, collapsibles, note fields, call button match; the only deltas are the live wiring below).

**Three views:** By topic / By person / Grid. Topics (DIMS) in chronological order: application → resume → skills → exp → loc → exchange (our message + their reply, merged) → interview (phone-interview Q&A) → status → glance (our read) → notes. Sticky candidate header; topics collapsible per person in By-person view.

**Live wiring (the only things added over the mockup's localStorage fakes):**
1. Notes (DJ note / Cheryl note / shared comment / per-question interview note) save server-side (Render Postgres), sync across both users + devices.
2. Call button → live dialer `/owner/voice/dial`. **The dialer rings the LOGGED-IN user's own phone** (Cheryl's when she's on it — NOT hard-coded to DJ), then bridges to the candidate; caller ID = Main line (760) 334-5355. See [[feedback_call_opens_dialer_never_dials]].
3. Phone-interview answer auto-fill: ✅ **NOW WIRED + LIVE (shipped 2026-10-11).** Post-call "⤵ Fill answers from recording" button per booked candidate: greyed by default; a state machine (`/owner/api/hiring/compare/fill-status`, page polls ~25s + on focus) LIGHTS it when a fresh transcript exists for the candidate's booked phone (`ready && transcript_id && transcript_id != last_filled_id`); press → `/owner/api/hiring/compare/fill` pulls the transcript (via Specialists' `get_latest_transcript(phone)` in sms.py), Claude parses it into per-qid answers (persisted to Postgres `hiring_compare_answer`), records `last_filled_id`, button greys. A 2nd call = new transcript id = re-lights. Parsed answers are the record; manual per-question notes are the optional "highlight only" layer. See [[project_call_recording_transcript]].

**Actual call chain (verified live 2026-10-11):** `/owner/voice/dial` rings the logged-in user's phone → on human-answer, `/owner/voice/outbound-bridge` builds `<Dial record="record-from-answer-dual" recordingStatusCallback=/owner/voice/recording-saved?...&dir=out>` with a `<Number url=/voice/consent-whisper>` (plays "This call may be recorded for quality" to the candidate — CA 2-party ✓). So the call IS recorded. Transcript only if VI service `wsc.voice.vi_service` is configured (else silently skipped; recording still saves). `/voice/recording-saved` + `/voice/transcript-ready` write the transcript to the **phone-keyed owner INBOX conversation** + Odoo chatter (only if phone matches a res.partner) — candidates aren't customers, so it lands in an "Unknown (<phone>)" inbox thread. It is NEVER written anywhere the compare page reads, and never parsed per-question.

**Monday/Tuesday workflow (Oct 12–13):** interviewers tap Call → talk → **take notes BY HAND in the per-question note textareas** (these DO persist to Render Postgres via the notes API + sync DJ↔Cheryl, both devices) — that is the primary record. Recording/transcript = backstop; HR can pull each candidate's transcript afterward by matching the booked phone number (same manual record→read→parse the old Workiz [[project_hiring_interview_transcription]] flow did). Do NOT rush a candidate-aware auto-fill build pre-interviews. Open check: confirm VI (`wsc.voice.vi_service`) is actually on — determines transcript-vs-audio-only. See [[project_call_recording_transcript]].

**Access:** DJ via his v2 launcher tile; Cheryl via "WSC Hire" tile → two-button chooser "Old ATS" (legacy /owner/hiring) and "New — ZipRecruiter" (this page).

**Dial test (2026-10-10):** Operator seeded a "TEST - Dial Check" candidate with Cheryl's # (909-821-2822); DJ confirmed the dial rang through + bridged; Operator cleared it. Page is clean.

**Row 6 (RESOLVED 2026-10-11):** The exact per-person ZipRecruiter first messages for the 6 booked were pulled (DJ had ZR logged in; read each thread via Claude-in-Chrome) and wired in — NOT one template: Fernando/Alfonso/Brian got the standard template, Norberto/James/Austin got personalized openers (résumé reference / "thanks for reaching out"). Verbatim text saved at `4_Reference_Data/zr_first_messages_6_booked.md`. Live code: `FIRST_MSG[c.id] || OUTREACH_MSG` — each candidate shows their real message; the generic `OUTREACH_MSG` (which was NEVER actually sent) is only a fallback for not-yet-pulled candidates (Joshua/awaiting/backup).

**Interview questions (REVISED 2026-10-11 eve, commit 48f76e5):** 10 general INTERVIEW_Q (count labels derive from `INTERVIEW_Q.length` — dynamic) + per-candidate `Q[id]` arrays + a "Don't ask (CA law)" reminder box. Earlier CA-compliance edits: dropped desert-heat Q, on-time-to-meet-up (not "reliable transportation"), no-insurance = factual statement, 32–40 hrs-range expectations Q. **This revision (DJ-directed, "steal the best from the old ATS phone screen"):** REMOVED two weak Qs — "Have you ever cleaned windows or solar panels…" (redundant w/ the field-work Q right before it) and "What do you remember about this job, and what made you apply?" (soft recall, overlaps Q1). ADDED two character Qs stolen from old `hiring.html` PHONE_QUESTIONS: the behavioral **"Tell me about a time things didn't go as planned at work — how did you handle it?"** and the **background/DMV/references comfort** Q (worded as a forward-looking NOTICE, NOT a criminal-history probe → Fair-Chance-Act compliant).

**📋 Interview Schedule box + by-person time-sort (added same commit, stolen from old ATS):** a day-grouped, time-sorted agenda pinned at the top (via `parseWhen("Mon Oct 12 · 1:00 PM")` → sortable ts; returns null for the TEST card `when==="TEST"` so it's EXCLUDED from the box). By-person view sorts booked candidates FIRST by (day, time), everyone else keeps rank order (stable sort; `DATA` identity untouched so fill-status/notes keys stay valid). Rows tap-to-jump.

**TEST candidate seed (dial-check / end-to-end dry run):** `POST /owner/api/hiring/compare/extras {name,phone}` seeds a LIVE-DB-only test card (table `hiring_compare_test`, id `test-<N>`) layered on top of the static mockup candidates at runtime; `{clear:true}` removes all. Gets full Call + Fill buttons keyed to the seeded phone. Seeded DJ's cell (951-972-6946, id test-8) 2026-10-11 for a Cheryl↔DJ end-to-end test of the record→transcribe→fill chain. CLEAR it before/after real use.

**★ CONSTRAINT — per-question notes are keyed by position (q0..qN).** Reordering/adding/removing an interview question AFTER notes are saved misaligns the saved answers. Once the Oct 12–13 interviews save notes, do NOT renumber questions without flagging Portal to migrate the notes first. Free to change before any notes exist.
