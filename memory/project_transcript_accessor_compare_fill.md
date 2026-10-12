---
name: project_transcript_accessor_compare_fill
description: "sms.py get_latest_transcript(phone)->{ready,text,when,id} surfaces the latest 📄 call transcript from the phone-keyed inbox conv for Candidate-Compare 'Fill answers from recording' (Portal imports it). id = VI tsid (voice.py stashes it in the transcript msg meta) with ts fallback. SIBLING get_latest_call(phone)->{ready,id,when,transcript,audio_url} adds the 📞 recording's audio_url (rec_sid from msg meta, body-parse fallback) for the call PLAYER — staged 2026-10-11."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-12T06:26:52.611Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy" via §12 picker; Lead QC-GREEN). Pairs with Portal's hiring_compare.py /fill (both landed same wave; feature live).**

**Where call transcripts live:** `routers/owner/voice.py` /transcript-ready builds a readable "Dan:/Customer:" transcript and appends it to the PHONE-KEYED owner inbox conversation (`_conv_*` store in sms.py) with body `📄 {Outgoing|Incoming} call transcript:\n<text>` via `_conv_append(conv,'in',body)`, keyed by `_norm(phone)`. (Recording log body = `📞 {who} call recording...`; voicemail = `📝 Voicemail transcript:`.) Candidates aren't customers → lands in an "Unknown (<phone>)" thread.

**Accessor (sms.py):** `get_latest_transcript(phone) -> {'ready':bool,'text':str,'when':str|None,'id':str|None}`. Uses `_conv_get_safe` (fail-open display read — a PG hiccup renders empty, never 500s the caller; `_conv_get` would RAISE). Scans `reversed(conv['msgs'])` for a body `startswith('📄') and 'call transcript' in b.lower()` → latest CALL transcript (correctly EXCLUDES the 📝 voicemail body). `text` = full body incl. the 📄 marker line (Portal strips line 1 before its parse prompt). Import-only (Portal does `from .sms import get_latest_transcript`) — NO route, no ENDPOINT_MAP entry.

**Stable `id` (button grey/light state machine, HR/DJ):** voice.py now stashes the VI transcript SID into the transcript msg meta (`_conv_append(..., meta={'tsid': tsid})`); accessor returns `id = (meta.tsid) or ts`. Why tsid over bare ts: a VI re-post of the SAME call keeps the same SID → button stays greyed; a genuine 2nd call → new SID → new id → re-lights. Portal's `/fill-status` compares `transcript_id != last_filled_id`. See [[feedback_reuse_canonical_endpoint]], [[feedback_data_location_odoo_vs_postgres]].

---

**SIBLING `get_latest_call(phone)` — STAGED 2026-10-11 (branch `specialists/compare-call-player-accessor`; NOT yet deployed — Frontdoor fires its own deploy picker per COMPARE_AUDIO_TRANSCRIPT_BRIEF Part A).** For Candidate-Compare's call **player + collapsible full transcript** (HR, DJ-approved). 2 Specialists-owned files, both LF: sms.py (+48/-0, new func) + voice.py (+1/-1, meta stash). No route, no ENDPOINT_MAP entry (import-only, like its sibling).

`get_latest_call(phone) -> {'ready':bool,'id':str|None,'when':str|None,'transcript':str,'audio_url':str}`:
- **audio_url:** scans `reversed(conv['msgs'])` for the newest body `startswith('📞') and '/owner/voice/rec?sid=' in b` (the `📞 {who} call — recording. Listen: /owner/voice/rec?sid=<sid> (transcript to follow)` written by voice.py `/recording-saved` :816). Returns `'/owner/voice/rec?sid=<sid>'`; `''` if none. **Prefers `rec_sid` from the msg meta, falls back to regex-parsing the sid out of the body** (`/owner/voice/rec\?sid=([A-Za-z0-9]+)`) — covers recordings logged before the meta stash. `startswith('📞')` deliberately EXCLUDES the 🎙️ voicemail-recording line.
- **voice.py hardening (the brief's blessed nice-to-have):** `/recording-saved` now appends `meta=({'rec_sid': rec_sid} if rec_sid else None)` so the sid is structured, not only in body text. `_conv_append` already supports `meta` (it stored `tsid` the same way).
- **transcript:** `get_latest_transcript(phone)['text']` verbatim — exact parity, reused not re-implemented.
- **ready = bool(audio_url)** → player shows even while transcript still `''` (audio lands before VI posts text; the two are independent, per spec). **id** = rec_sid (meta/parsed) → ts → transcript id. **when** = recording msg ts → transcript when. Fail-open via `_conv_get_safe` + the sibling (never 500s).

Frontdoor builds Part B (`POST /owner/api/hiring/compare/media {cand,phone}`, defensive import → degrade ready:false if accessor not deployed) + Part C (lazy ▶ player + ▸ collapsed transcript per booked candidate). Test case = seeded `test-8` (DJ's cell, has a real dry-run recording+transcript). See [[feedback_reuse_function_follow_full_logic]], [[feedback_lazy_on_demand_not_prefetch]], [[feedback_dj_deploy_control_stage_and_trigger]].
