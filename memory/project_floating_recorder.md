---
name: project_floating_recorder
description: "Floating voice recorder (DJ 2026-09-13, Phase 1): a floating mic button on every app screen that keeps ONE recording going ACROSS in-app page navigation, streams durably, and saves a searchable NOTE {audio, transcript, context=screens-visited} — passive (no distill). New store wsc.memory.floatnotes."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-13T05:55:33.478Z
---

**Built 2026-09-13 (DJ-requested via Lead; brief `3_Documentation/FLOATING_RECORDER_BRIEF.md`). Phase 1.** A floating 🎙️ button on every app screen (Cheryl app first; owner app is a one-line add — already wired). Two uses: DJ's app-walkthrough capture (narrate across screens, hand me the transcript) + Cheryl's quick verbal notes. PASSIVE — nothing auto-distilled/filed (the key difference from the Meeting app).

## Files
- **`static/owner/wsc_floatrec.js`** — the widget (app-agnostic: `BASE=/cheryl|/owner` from path). Reuses the shared hardened `wsc_recorder.js` (10s durable chunk-stream + mic-meter + no-sound + tab-hidden warning). Floating FAB when idle → a pill "● MM:SS + meter + Stop" while recording. **★ The novel bit — persist ONE recording across in-app page navigation:** session id + screens-visited `context[]` live in `localStorage 'wsc_float_active'`; on EVERY page load, if a session is active, the widget re-acquires the mic into the SAME note_id (continuing chunk indices, so finalize assembles ALL chunks across ALL pages into ONE note) and appends this screen to context. Each page is a full reload (MediaRecorder can't survive it) → it RESUMES. Android Chrome resumes silently post-grant; **iOS Safari may need a gesture** → a blocked resume shows an UNMISSABLE "▶ Tap to resume" pill (big/high-contrast amber, flashing, `navigator.vibrate`) — never a silent dead recording (mic-meter flat is the backstop).
- **`routers/owner/floatnote.py`** — backend (a passive clone of voicenote.py + a `context` field). Endpoints `/api/floatnote/chunk|finalize|discard|status|list(searchable q)|audio|delete` + `/floatnotes` (the list PAGE) + `retry_stuck_floatnotes` cron. Chunk prefix `wscfn:<id>:<idx>` → assembled `wscfn:<id>`. `_process_floatnote` = gather→assemble→`meeting._transcribe`→save note, **STOPS (no _distill)**. author + company FROM THE SESSION (`session_actor`: cheryl→company 2, owner→1), so the SAME router serves BOTH apps — included under `/owner` AND `/cheryl` in main.py. Store `wsc.memory.floatnotes` (never meetings/voicenotes). List scoped by **author + company** (Cheryl sees hers, owner his — never crossed; a DJ-sees-Cheryl's toggle is a later progressive-access item).
- **`static/owner/floatnotes.html`** — searchable notes list (BASE-aware) served under both `/cheryl/floatnotes` and `/owner/floatnotes`; each row shows the context ("📍 recorded across: Clients, Tasks"); detail = transcript(copy) + audio(play/download) + delete.
- **Injection:** `with_cheryl_chrome` injects the widget on every Cheryl page; the `/cheryl/` HOME is served RAW (see [[project_cheryl_pwa]]) so the widget tag is ALSO hardcoded in static/cheryl/index.html. Widget self-guards double-init.

## Phase 2 (later)
Per-note **"Hand to Claude"** action (make a task / log a decision / email it) → routes to Cheryl's-cloud. Not built.

Related: [[project_voice_notes_app]] (shared recorder + chunk-stream + hardening), [[project_cheryl_pwa]].
