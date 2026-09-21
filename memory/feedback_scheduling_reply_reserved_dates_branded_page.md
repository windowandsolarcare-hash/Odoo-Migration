---
name: feedback_scheduling_reply_reserved_dates_branded_page
description: "Scheduling/booking replies to customers = RESERVE specific dates on the branded booking page (offers/reserve -> wscare.pro/c/<tok>) so the customer just taps to pick. NEVER send an open 'what day works for you?' question that makes them type."
metadata:
  node_type: memory
  type: feedback
---

**★ DJ correction (2026-09-21).** When replying to a customer who wants to book/re-book, DO NOT ask an open-ended "what day works for you?" question that forces them to type a date. **That is not how we reply.**

**Instead:** give them RESERVED dates that work for US, delivered through the BRANDED booking page, and they tap to pick one.
- Mechanism: `POST /owner/api/offers/reserve {partner_id, name, slots_pt:[{date,time},...]}` -> returns `{offer_id, link: wscare.pro/c/<tok>}`. `so_id` is OPTIONAL (record_offer accepts so_id=None) — no job needs to exist first.
- Choose slots on the customer's CITY ANCHOR DAY (batch-by-geography) — e.g. Indio=Wed, Hemet=Tue (see CITY_WEEKDAYS / [[project_operator_playbook]]).
- Then the reply text is warm + one-push and CONTAINS the link: "I've reserved a few dates for you - just tap to pick whichever works best and you're all set: <link>". Customer taps a reserved slot on the branded page -> booked. No typing.
- Offers auto-expire after 48h (slot_offers _TTL_HOURS) so unbooked reservations free themselves.

Ties to [[feedback_dj_operating_instincts]] (DATES = reserved/tap-to-book, batch-by-geography) and [[project_operator_playbook]] (offers/reserve recipe). Applies to HUD reply cards too: the card action should deep-link the inbox thread with the branded-link draft prefilled for DJ to review+send.
