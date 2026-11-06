---
name: project_inbox_name_frozen_at_ingest
description: "Inbox shows \"Unknown (number)\" for real customers because the thread name is frozen at first-message ingest and never re-resolved"
metadata:
  node_type: memory
  type: project
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-06T13:47:41.706Z
---

The app message inbox (routers/owner/sms.py) stamps a conversation's display NAME at the moment the FIRST message arrives (sms.py:1977 — `customer_name = resolved['name'] if resolved else f'Unknown ({from_number})'`) and stores it as the `wsc.sms.conv.<norm>` ir.config_parameter. It does NOT re-resolve a stored thread name afterward. So any customer who calls/texts BEFORE their res.partner exists (contact-first, booked after — the booking page creates the contact minutes later) stays frozen as "Unknown (number)" forever, even though the live resolver `_resolve_partner_by_phone` would find them now.

**Why:** Confirmed 2026-11-06 (Operator) on Mark Bradshaw: his texts/call landed Nov 4 18:01; the booking page created his contact (partner 27320) at 18:05 — 4 min later. Thread stayed "Unknown (6192087799)" despite his number being present + correctly 10-digit-formatted on BOTH his contact (27320) and property (27321). Louise & Rainer Lang is the same story. It is NOT a missing/mismatched-phone problem — do not "fix" by editing the number.

**How to apply:** This is a resolver/caching bug for Specialists, not an Operator data write (nothing to raw-write; number is already correct). Three code seams: (1) sms.py:1977 name frozen at ingest; (2) sms.py:607-609 `append_inbox_event` backfills `partner_id` onto an existing conv but NEVER refreshes `name`; (3) `/api/inbox/backfill_links` (sms.py:3672) re-resolves name+partner for threads but SKIPS any conv that already has a `partner_id` — so a thread linked to a Property id with an Unknown name (Mark's exact case) is never repaired. Fix = refresh/re-resolve display name when a partner gets linked, and don't skip Unknown-named threads just because a Property id is attached. `backfill_links` is CRON_SECRET-gated (not owner cookie) → Specialists runs/patches it, not Operator. Related: [[feedback_hud_cards_live_not_inbox]] (HUD cards are live-derived; the inbox conv NAME is the opposite — stored/stale) and [[project_inbox_thread_partner_stamp_fragility]] (same resolver family: list vs open disagreement, arbitrary hits[0], inbound overwrites pid).
