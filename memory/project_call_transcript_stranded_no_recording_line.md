---
name: project_call_transcript_stranded_no_recording_line
description: "Candidate/customer call transcript can be in the thread but invisible on the compare card — get_all_calls anchors only on 📞 recording lines, and recording-saved can land the 📄 transcript while its 📞 write failed."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-15T14:36:30.433Z
---

A call's `📄 … call transcript` can exist in a phone's inbox thread yet NOT show on the Candidate-Compare card. Discovered 2026-10-15 via HR's Norberto Villa task (candidate_id 'norberto', phone 7608449054, Oct-12 interview): the compare card showed only Cheryl's earlier voicemail recording, but `compare_fill` had parsed q0–q8 correctly — proving the real interview transcript WAS in his thread.

**Why:** two independent accessors read the same thread differently.
- `get_latest_transcript(phone)` (sms.py) returns the NEWEST `📄 … call transcript` for `_norm(phone)` → `compare_fill` uses it → q0–q8 fill works.
- `get_all_calls(phone)` / `get_latest_call(phone)` (sms.py) anchor ONLY on `📞 … call — recording` lines, then pair each with the first following `📄`. A `📄` transcript whose `📞` line is MISSING is stranded — never surfaced on the card.

**Root of the missing 📞 line:** `voice.py /voice/recording-saved` does the `📞` thread-write and the Voice-Intelligence transcription kick in TWO separate `try/except: pass` blocks (~:846 thread-write, ~:864 VI kick). The `📞` write can fail silently (PG hiccup, `_find_customer` raising, etc.) while the VI kick still succeeds → `/voice/transcript-ready` later lands the `📄`. Result: transcript present, recording line absent.

**How to apply:**
- To READ a stranded transcript now: open that number's inbox conversation — the `📄 Outgoing/Incoming call transcript:` msg is in `data->'msgs'` (source defaults to 'text', so it shows in the thread). No backfill/code needed.
- Durable fix (sms.py accessor, Specialists' lane): after building the recording-anchored list, append any UNPAIRED `📄` call-transcript as a transcript-only "call" (`audio_url=''`, id=tsid), deduped by tsid, chronological. Additive; existing paired entries unchanged; fixes the whole class. Behavior change → §15 (Lead). Unit-testable offline with synthetic msgs.
- Audio-on-card for a stranded call needs a separate `📞`-line backfill (Twilio has the recording — VI was kicked, so a rec_sid existed) — low value; the transcript is the deliverable.

**Env/access facts proven same day (why this can't be observed headlessly):** the LIVE SMS store (`sms_conversations.data` JSONB, keyed by `_norm` phone) is in Render PG **momscare-db** (`dpg-daocj0btqb8s73eq8kt0-a`), whose IP allowlist is EMPTY → the read-only Render MCP can't reach it. `wsc-memory-pillar` (`dpg-danl5vqjnfac7390g8g0-a`, allowlist 0.0.0.0/0) holds `ship_cards` + a STALE `sms_conversations` copy (newest ~2026-09-21). The Twilio diagnostics `/owner/voice/recordings` + `/owner/voice/recent` (CRON_SECRET token = the daily-sync cron value) and `/owner/api/hiring/compare/media` are NOT in authz `PUBLIC_EXACT` → owner-cookie-gated; a 401 there is the authz layer, not the token. Deliberate boundary — do not add them to PUBLIC_EXACT or forge the cookie to run a diagnostic ([[feedback_cant_headlessly_seed_is_security_feature]]). See [[feedback_data_location_odoo_vs_postgres]], [[feedback_root_cause_not_just_instance]].
