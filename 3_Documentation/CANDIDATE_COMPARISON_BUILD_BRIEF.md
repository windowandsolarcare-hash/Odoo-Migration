# Candidate Comparison Page — Build Brief (from HR, 2026-10-10)

## ‼ RULE #1 — DUPLICATE THE MOCKUP EXACTLY. DO NOT REBUILD FROM THIS DESCRIPTION.

DJ approved a specific, fine-tuned mockup after many rounds. **Build the live page by duplicating that file's markup, CSS, and behavior exactly.** This brief exists to tell you *where the file is* and *what the live-only wiring is* — it is NOT a spec to rebuild from your own interpretation. If the live page comes back looking different from the mockup, it's wrong. When anything is unclear, **ask HR** — do not improvise.

(This rule is here because the booking page drifted when a builder worked from a text description instead of the approved artifact. Not again.)

## The approved mockup — two ways to open and read it
1. **Exact source file in this repo:** `3_Documentation/candidate_comparison_mockup.html` (fetch it with `gh api .../contents/3_Documentation/candidate_comparison_mockup.html`, base64-decode, open in a browser). This is the canonical source — copy its HTML/CSS/JS verbatim as the starting point.
2. **Live artifact (same content):** https://claude.ai/artifact/NAp3obHgxR2RCL7KRgsqE1 — if you can open claude.ai artifacts on this account, use the Artifact `read` action on that URL to get the raw HTML. If you can't open it, use the repo file (#1). Either way, **read the real thing before building.**

## What it is
An internal hiring comparison page for **DJ and Cheryl only** — compare the Lead Technician candidates and run the phone interviews from it. Three views (By topic / By person / Grid), chronological topics (Application → Résumé → Skills → Experience → Location → Our message & their reply → Phone interview Q&A → Status → Our read → Notes), sticky candidate header, per-question note fields, a Call button, editable DJ/Cheryl/shared notes.

## What's MOCKUP-only and must become real in the live build (the only things you add)
The mockup fakes these with localStorage / notes / placeholders. Make them real — **without changing the look**:
1. **Auth** — private to DJ + Cheryl only (magic-link or the app's existing owner/Cheryl login). No public access.
2. **Notes that save + sync** — the DJ note, Cheryl note, shared comment, AND the per-question interview note boxes must persist server-side (Render Postgres, per the data-location rule) and sync between both of them + both devices. In the mockup these are localStorage (per-device) — replace with real storage; keep the same fields/keys/placement.
3. **Call button** — wire it to the app dialer: tap → place the outbound call via `/owner/voice/dial` with the **Main line (760) 334-5355** as caller ID. ⚠ See the related dialer change already routed: the dial must ring the **logged-in user's own phone** (Cheryl's, when she's using it), not a hard-coded number. Coordinate with whoever takes that voice.py change.
4. **Phone-interview answer auto-fill** — the "— answer from the recording" slots under each question get filled by parsing each candidate's **call transcript** (Twilio Voice Intelligence transcript from the app-dialer recording) into the matching question's answer. This is the same record→transcribe→parse pattern used last round (`project_hiring_interview_transcription`). Map candidate↔transcript by phone number.

## Data in the mockup
All candidate content (tiers, quick reads, reply quotes, skills, experience, résumé links, booked slots/phones, the 10 interview questions + per-person questions, the 4 application screening questions) is already in the file's `DATA` / `Q` / `INTERVIEW_Q` / `APP_Q` structures. Reuse it; the live page can later read candidates from the real source, but match the exact fields/layout shown.

## One known placeholder — leave it, DJ finalizes
**Row 6 "Our message & their reply"** shows a *standard* first-message text with a note "confirming each person's exact sent copy from ZipRecruiter." The exact per-person ZR copy isn't pulled yet (ZR's UI glitches under automation) — **DJ will pull it with HR and we'll drop the real copy in.** Build row 6 as-is; it'll update.

## Sign-off gate
**HR verifies the built live page side-by-side against this mockup before it's called done.** It does not ship as "matching" until HR has confirmed it matches. Ping HR for that check.

— HR
