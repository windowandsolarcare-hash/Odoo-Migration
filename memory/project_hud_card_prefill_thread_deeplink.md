---
name: project_hud_card_prefill_thread_deeplink
description: "HUD/approval card that should open an inbox thread with a reply PRE-FILLED must deep-link open=<partner_id>&draft=<urlencoded>, NOT c=<norm>"
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-06T16:21:29.823Z
---

To make a HUD card (or any deep link) open an inbox thread with the reply box already filled in — the standard "Approve → opens thread PRE-FILLED, DJ reads + sends" flow — the card's `action.href` MUST be:

`/static/owner/v2_inbox.html?open=<partner_id>&draft=<URL-encoded message text>`

Do NOT use `?c=<norm>` (the phone/conversation key) when you want a pre-filled draft. It will open the right thread but leave the reply box EMPTY — the draft is silently ignored.

**Why:** The inbox init block in `static/owner/v2_inbox.html` branches on which param is present:
`if(_open){ openByPartner(_open, _draft); } else if(_c){ openThread(_c, true); }`
Only the `open=` branch passes the draft through. `openByPartner(pid, draft)` resolves the partner to a phone via `/owner/api/inbox/thread_by_partner?partner_id=`, seeds+opens the thread, then does `reply.value=draft; focus()`. The `c=` branch calls `openThread(norm, true)` and never touches `_draft`. So `c=` + `draft=` = thread opens blank. This is the same deep link the voice "text <customer>" card uses.

**How to apply:** When building a card whose job is to tee up a customer reply for DJ to send, look up the customer's `res.partner` id and build the href as `?open=<partner_id>&draft=` + `urllib.parse.quote(text, safe='')`. Put the full message (including any booking link) in the draft. The reply box fills and focuses; nothing sends until DJ taps Send (§9). Verify by opening the card link yourself and confirming the text landed in the reply box. Real miss 2026-11-06: Carol Callaghan's offer card used `?c=7606991133`, so it opened her thread empty — DJ caught it. Fix was re-issuing the same card id with `?open=23188&draft=...`.

Ties to [[feedback_no_inventing_customer_lines_hud_confirm]] (Approve opens thread pre-filled, DJ sends), [[feedback_dan_requested_cards_top_pinned_lane]], [[feedback_no_ai_offered_dates_use_link]], and [[project_inbox_name_frozen_at_ingest]].
