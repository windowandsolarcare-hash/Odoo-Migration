---
name: project_candidate_comparison_page
description: "Candidate Comparison page (Page 2 of the Lead-Technician hire) — live at /owner/hiring/compare, DJ+Cheryl, dials candidates, auto-fills interview answers from call transcripts."
metadata:
  node_type: memory
  type: project
  originSessionId: e3071731-f37a-4440-a358-34be556223c2
  modified: 2026-10-10T15:21:31.761Z
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
3. Phone-interview answer auto-fill: the "— answer from the recording" slot under each question gets filled by parsing each candidate's Twilio Voice Intelligence transcript (same record→transcribe→parse pattern as [[project_hiring_interview_transcription]]), mapped candidate↔transcript by phone. Unproven until the first real call (Oct 12–13) produces a transcript.

**Access:** DJ via his v2 launcher tile; Cheryl via "WSC Hire" tile → two-button chooser "Old ATS" (legacy /owner/hiring) and "New — ZipRecruiter" (this page).

**Dial test (2026-10-10):** Operator seeded a "TEST - Dial Check" candidate with Cheryl's # (909-821-2822); DJ confirmed the dial rang through + bridged; Operator cleared it. Page is clean.

**Open item (DJ's side):** Row 6 "Our message & their reply" shows standard outreach copy as a placeholder — DJ pulls the exact per-person ZipRecruiter first-message copy WITH HR when he can access ZR (ZR UI glitches under browser automation). Page works fully without it.
