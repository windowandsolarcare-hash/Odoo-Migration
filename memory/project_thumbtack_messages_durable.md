---
name: project_thumbtack_messages_durable
description: "Thumbtack MessageCreatedV4 (both directions) now persists durably to Render Postgres (idempotent on messageID), chatter breadcrumb, inbound-customer HUD card — fixes the lead-loss where replies fell into the 30-entry ring buffer and rolled off."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T08:24:45.396Z
---

**Lead-loss fixed (STAGED 2026-10-10, branch specialists/thumbtack-messages, thumbtack.py e64b0c91; Lead QC-GREEN; held for DJ deploy).** Before: `routers/thumbtack.py` acted only on `NegotiationCreated` and early-returned on everything else at ~line 262, so inbound **MessageCreatedV4** replies (BOTH directions: `from='Customer'|'Business'`) existed only in the 30-entry ring buffer `ir.config_parameter wsc.thumbtack.raw_log` (`_LOG_MAX=30`) and rolled off — Ben Jarnagin's 2026-10-09 "postpone til after Nov 9" reply was silently lost.

**MessageCreatedV4 payload shape** (confirmed): `data = {messageID, negotiationID, customer:{customerID,displayName}, business:{businessID,displayName}, from:'Customer'|'Business', text, sentAt}`.

**Fix (additive branch, NegotiationCreated path untouched):**
- Durable store = **Render Postgres** (`MEMORY_DB_URL`, psycopg3, same instance as feedback/memory — [[feedback_data_location_odoo_vs_postgres]]), table `thumbtack_message`, `message_id TEXT UNIQUE`. INSERT … `ON CONFLICT (message_id) DO NOTHING RETURNING id` → **idempotent** (redelivered webhooks don't dupe). NOT the ring buffer.
- One-line **chatter breadcrumb** on first insert → the linked partner (record-of-truth), time in **Pacific 12-h** (`_pt_label`, DST — [[feedback_times_in_pacific]]).
- **Lead linkage by negotiationID, never a phone** (Thumbtack proxy numbers): `_lead_for_neg` prefers the existing 72h flow blob (neg_id→lead_id) then a crm.lead description fallback. No new Odoo field.
- **§9/§10 RECEIVE-ONLY:** nothing auto-responds/auto-offers a date. Inbound `from='Customer'` → HUD card `thumbtack_msg:<neg_id>` (kind attention, action "Respond in Thumbtack") + one away push; `from='Business'` → persist + chatter only.
- **Card dismiss/snooze:** `created`=message `sentAt` → a NEW reply re-raises after a dismiss/snooze (feed `submit_item` resets a terminal occurrence when `created` changes, feed.py:175); a redelivered same-messageID keeps its sentAt → same occurrence → no resurrection (dedupe, "not stuck-terminal"). Coordinated with banner dismiss/snooze spec 3eda55c6.
- **+2 owner-gated routes** (authz by `/owner` prefix; namespaced, no shadow vs sms.py's `/reply`+`/capture_contact`): `GET /owner/api/thumbtack/thread/{neg_id}` (durable thread read) + `POST /owner/api/thumbtack/backfill_messages` (one-time, idempotent; no body=ring buffer, `{entries:[...]}`=Operator's backup JSON `C:/Users/dj/_thumbtack_raw_log_backup_2026-10-09.json`; re-raises one card per negotiation whose latest msg is an unanswered customer reply → recovers Ben's).

**POST-DEPLOY:** run `POST /owner/api/thumbtack/backfill_messages` once (Specialists owns); Lead verifies Ben's card + the table populate.

**Facts:** `res.partner` on this Odoo has **no `mobile` field** (phone only). hr.employee phone fields: phone, work_phone, mobile_phone(=Work Mobile), private_phone, emergency_phone. See [[project_thumbtack_proxy_numbers]], [[feedback_hud_cards_live_not_inbox]], [[feedback_reuse_canonical_endpoint]].
