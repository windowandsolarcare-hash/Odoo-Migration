---
name: feedback_inbox_single_source_all_exchanges
description: "DJ governing rule: the in-app inbox must be the SINGLE complete record of EVERY customer exchange (texts, voicemail, branded-page submissions, acknowledgements, confirmations), each labeled by type + source. HUD cards derive from it — no parallel stores."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-14T03:05:52.472Z
---

**DJ 2026-09-14 (verbatim):** "Everything should run through the inbox and labeled appropriately." + "Yes, the inbox should capture everything — acknowledgements, confirmations, any exchange that happens."

**Why:** customer responses were fragmenting across channels — inbound/outbound SMS + voicemail thread through the in-app inbox (sms.py conv store, AI classify/draft), but **branded-PAGE submissions bypass it** (appt confirm/reschedule/cancel via wscare.pro/appt/<token>, booking requests, gate-code updates) and only land in SO chatter + side-blobs (`wsc.maint.replies`, `wsc.maint.advance.*`) surfaced as HUD cards. Live example: Gayle Ormond's page reschedule (SO 17612) never entered the inbox. DJ wants ONE complete per-customer record, no parallel stores that drift.

**How to apply — for ANY new customer-touch feature going forward:**
- Every customer-originated response AND every system acknowledgement/confirmation must **write a message into that customer's inbox conversation thread** (reuse the sms.py conv store). Never create a new side-store that only feeds a HUD card.
- **Label every inbox item** — TYPE (Confirmed · Reschedule · Cancel · Gate/Access · Question · Payment · Acknowledgement · Other) + SOURCE (📱 Text · 🔗 Page · ☎ Voicemail · ⚙ System/Auto).
- **HUD cards are VIEWS of labeled inbox items**, not a separate pipe (the "Reschedule/cancel" + "Next service confirmed" cards should be filtered slices; the inbox is the source of truth).

Build in flight (2026-09-14): brief `3_Documentation/UNIFIED_INBOX_CAPTURE_ALL_BRIEF.md`, handed to Specialists APPROACH-FIRST (Lead QCs the label/source data model + page→conv write path + HUD re-derivation + phasing before broad build). Related: [[feedback_hud_cards_live_not_inbox]] (HUD cards live-derived, not a stored inbox — consistent: the inbox is the record, cards are live views of it).
