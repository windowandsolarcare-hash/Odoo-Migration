---
name: project_candidate_comparison_page
description: "Candidate Comparison page (Page 2 of the Lead-Technician hire) — live at /owner/hiring/compare, DJ+Cheryl, dials + records candidates. NOTE: per-question transcript auto-fill is NOT wired (static placeholder); interviewers take manual notes — see body."
metadata:
  node_type: memory
  type: project
  originSessionId: e3071731-f37a-4440-a358-34be556223c2
  modified: 2026-10-11T16:30:02.425Z
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
3. Phone-interview answer auto-fill: ⚠️ **NOT WIRED — confirmed by live-code read 2026-10-11.** The "— answer from the recording" slot is HARDCODED PLACEHOLDER text in hiring_compare.html (`ivItem()` returns the literal string); nothing ever replaces it. hiring_compare.py has NO transcript/parse/autofill endpoint (only compare_page/me/notes_all/notes_save/extras), and its own module docstring says auto-fill is a deferred follow-up that "ships as-is." The Call button posts only `{to,name,caller_id}` to `/owner/voice/dial` — **no candidate id / interview context**, so the backend can't tie a call to a candidate.

**Actual call chain (verified live 2026-10-11):** `/owner/voice/dial` rings the logged-in user's phone → on human-answer, `/owner/voice/outbound-bridge` builds `<Dial record="record-from-answer-dual" recordingStatusCallback=/owner/voice/recording-saved?...&dir=out>` with a `<Number url=/voice/consent-whisper>` (plays "This call may be recorded for quality" to the candidate — CA 2-party ✓). So the call IS recorded. Transcript only if VI service `wsc.voice.vi_service` is configured (else silently skipped; recording still saves). `/voice/recording-saved` + `/voice/transcript-ready` write the transcript to the **phone-keyed owner INBOX conversation** + Odoo chatter (only if phone matches a res.partner) — candidates aren't customers, so it lands in an "Unknown (<phone>)" inbox thread. It is NEVER written anywhere the compare page reads, and never parsed per-question.

**Monday/Tuesday workflow (Oct 12–13):** interviewers tap Call → talk → **take notes BY HAND in the per-question note textareas** (these DO persist to Render Postgres via the notes API + sync DJ↔Cheryl, both devices) — that is the primary record. Recording/transcript = backstop; HR can pull each candidate's transcript afterward by matching the booked phone number (same manual record→read→parse the old Workiz [[project_hiring_interview_transcription]] flow did). Do NOT rush a candidate-aware auto-fill build pre-interviews. Open check: confirm VI (`wsc.voice.vi_service`) is actually on — determines transcript-vs-audio-only. See [[project_call_recording_transcript]].

**Access:** DJ via his v2 launcher tile; Cheryl via "WSC Hire" tile → two-button chooser "Old ATS" (legacy /owner/hiring) and "New — ZipRecruiter" (this page).

**Dial test (2026-10-10):** Operator seeded a "TEST - Dial Check" candidate with Cheryl's # (909-821-2822); DJ confirmed the dial rang through + bridged; Operator cleared it. Page is clean.

**Row 6 (RESOLVED 2026-10-11):** The exact per-person ZipRecruiter first messages for the 6 booked were pulled (DJ had ZR logged in; read each thread via Claude-in-Chrome) and wired in — NOT one template: Fernando/Alfonso/Brian got the standard template, Norberto/James/Austin got personalized openers (résumé reference / "thanks for reaching out"). Verbatim text saved at `4_Reference_Data/zr_first_messages_6_booked.md`. Live code: `FIRST_MSG[c.id] || OUTREACH_MSG` — each candidate shows their real message; the generic `OUTREACH_MSG` (which was NEVER actually sent) is only a fallback for not-yet-pulled candidates (Joshua/awaiting/backup).

**Interview questions (as of 2026-10-11 deploy):** 10 general INTERVIEW_Q (count labels derive from `INTERVIEW_Q.length` — dynamic, won't drift) + per-candidate `Q[id]` arrays + a "Don't ask (CA law)" reminder box. CA-compliance edits made: dropped the desert-heat Q (redundant w/ app screening), #7 asks on-time-to-meet-up (not "reliable transportation" — car-ownership proxy risk), the no-insurance line is a factual statement not a probe, added a 32–40 hrs-range expectations Q.

**★ CONSTRAINT — per-question notes are keyed by position (q0..qN).** Reordering/adding/removing an interview question AFTER notes are saved misaligns the saved answers. Once the Oct 12–13 interviews save notes, do NOT renumber questions without flagging Portal to migrate the notes first. Free to change before any notes exist.
