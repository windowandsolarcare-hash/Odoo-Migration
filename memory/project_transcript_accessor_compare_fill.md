---
name: project_transcript_accessor_compare_fill
description: "sms.py get_latest_transcript(phone)->{ready,text,when,id} surfaces the latest 📄 call transcript from the phone-keyed inbox conv for Candidate-Compare 'Fill answers from recording' (Portal imports it). id = VI tsid (voice.py stashes it in the transcript msg meta) with ts fallback."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-11T17:58:06.116Z
---

**DEPLOYED 2026-10-11 to main (DJ "deploy" via §12 picker; Lead QC-GREEN). Pairs with Portal's hiring_compare.py /fill (both landed same wave; feature live).**

**Where call transcripts live:** `routers/owner/voice.py` /transcript-ready builds a readable "Dan:/Customer:" transcript and appends it to the PHONE-KEYED owner inbox conversation (`_conv_*` store in sms.py) with body `📄 {Outgoing|Incoming} call transcript:\n<text>` via `_conv_append(conv,'in',body)`, keyed by `_norm(phone)`. (Recording log body = `📞 {who} call recording...`; voicemail = `📝 Voicemail transcript:`.) Candidates aren't customers → lands in an "Unknown (<phone>)" thread.

**Accessor (sms.py):** `get_latest_transcript(phone) -> {'ready':bool,'text':str,'when':str|None,'id':str|None}`. Uses `_conv_get_safe` (fail-open display read — a PG hiccup renders empty, never 500s the caller; `_conv_get` would RAISE). Scans `reversed(conv['msgs'])` for a body `startswith('📄') and 'call transcript' in b.lower()` → latest CALL transcript (correctly EXCLUDES the 📝 voicemail body). `text` = full body incl. the 📄 marker line (Portal strips line 1 before its parse prompt). Import-only (Portal does `from .sms import get_latest_transcript`) — NO route, no ENDPOINT_MAP entry.

**Stable `id` (button grey/light state machine, HR/DJ):** voice.py now stashes the VI transcript SID into the transcript msg meta (`_conv_append(..., meta={'tsid': tsid})`); accessor returns `id = (meta.tsid) or ts`. Why tsid over bare ts: a VI re-post of the SAME call keeps the same SID → button stays greyed; a genuine 2nd call → new SID → new id → re-lights. Portal's `/fill-status` compares `transcript_id != last_filled_id`. See [[feedback_reuse_canonical_endpoint]], [[feedback_data_location_odoo_vs_postgres]].
