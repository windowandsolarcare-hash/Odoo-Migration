---
name: project_hud_card_prefill_thread_deeplink
description: "HUD/approval card that should open an inbox thread with a reply PRE-FILLED must deep-link open=<partner_id>&draft=<urlencoded>, NOT c=<norm>"
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-06T19:10:00.514Z
---

To make a HUD card (or any deep link) open an inbox thread with the reply box already filled in — the standard "Approve → opens thread PRE-FILLED, DJ reads + sends" flow — the card's `action.href` MUST be:

`/static/owner/v2_inbox.html?open=<partner_id>&draft=<URL-encoded message text>`

Do NOT use `?c=<norm>` (the phone/conversation key) when you want a pre-filled draft. It will open the right thread but leave the reply box EMPTY — the draft is silently ignored.

**Why:** The inbox init block in `static/owner/v2_inbox.html` branches on which param is present:
`if(_open){ openByPartner(_open, _draft); } else if(_c){ openThread(_c, true); }`
Only the `open=` branch passes the draft through. `openByPartner(pid, draft)` resolves the partner to a phone via `/owner/api/inbox/thread_by_partner?partner_id=`, seeds+opens the thread, then does `reply.value=draft; focus()`. The `c=` branch calls `openThread(norm, true)` and never touches `_draft`. So `c=` + `draft=` = thread opens blank. This is the same deep link the voice "text <customer>" card uses.

**How to apply:** When building a card whose job is to tee up a customer reply for DJ to send, look up the customer's `res.partner` id and build the href as `?open=<partner_id>&draft=` + `urllib.parse.quote(text, safe='')`. Put the full message (including any booking link) in the draft. The reply box fills and focuses; nothing sends until DJ taps Send (§9). Real miss 2026-11-06: Carol Callaghan's offer card used `?c=7606991133`, so it opened her thread empty — DJ caught it. Fix was re-issuing the same card id with `?open=23188&draft=...`.

**Partnerless / "Unknown" threads (no res.partner yet):** `?open=` needs a partner_id, so an inbound referral/VM thread still showing "Unknown (+1…)" (conv.partner_id = null) has nothing to hang the draft on. FIRST create the contact via `POST /owner/api/intake/contact` {first_name, [last_name], phone:"+1…"} → returns {id}; then use `?open=<that id>&draft=`. (Chad 2026-11-06: referral VM, no record → created partner 27327 "Chad", re-issued card `?open=27327&draft=`.) Creating the contact is in-lane Operator work and also gets them out of "Unknown."

**Verifying the prefill:** the owner inbox page (`v2_inbox.html`) and its APIs require the OWNER session cookie. `openByPartner` pops a blocking `alert("No phone number on file…")` and bails to the list whenever its `thread_by_partner` fetch comes back not-ok — which includes `{"ok":false,"error":"auth required"}`. So a browser that is NOT logged into the owner app (e.g. a cross-session Claude-in-Chrome on a Chrome without the owner cookie) CANNOT verify the prefill and will FREEZE on that alert. Verify on an owner-authed device, or trust the server-side facts (partner exists + `thread_by_partner` returns ok+norm when authed) — this is the same shipped `?open=&draft=` pattern used by the review-request and confirm-ack cards.

Ties to [[feedback_no_inventing_customer_lines_hud_confirm]] (Approve opens thread pre-filled, DJ sends), [[feedback_dan_requested_cards_top_pinned_lane]], [[feedback_no_ai_offered_dates_use_link]], and [[project_inbox_name_frozen_at_ingest]].
