---
name: project_inbox_list_vs_thread_partner_merge_mismatch
description: "Inbox threading/attribution bug class (found 2026-10-29): a text can PREVIEW under customer A's row in the inbox LIST but be ABSENT when A's thread is opened (and absent from the real recipient B too). Root = the LIST merges conversation rows by the conv's STORED partner_id (sms.py:2591-2604) while OPENING a row re-derives members from that partner's ODOO phone numbers (_merge_partner_thread→_partner_norms, sms.py:2680/2763). When a conv carries a partner_id that does NOT match its own phone (norm), the two disagree. Conv store is keyed by norm (phone); partner_id is a flip-able secondary attribute."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-29T22:33:09.259Z
---

**Symptom (DJ 2026-10-29, via Dispatcher):** an outbound text "I left my pole at your house…" to customer **Jeff** showed as the latest-message PREVIEW under **Bill Zwick**'s row in v2_inbox LIST ("Bill Zwick · You: I left my pole…"), but was NOT in Bill's opened thread, and NOT under Jeff either. Bill Zwick = brand-new partner **27310** (property 27311, SO 17784), created from a call that day.

**Root cause (code-proven; mine + an Explore sweep, independently):** the inbox conversation store (`sms_conversations`, DAL `sms_store.py`) is **keyed solely by `norm` = last-10-digit phone** (`_norm`, sms.py:89). `partner_id` is a PROMOTED, non-authoritative, flip-able attribute on the row. The bug is a **two-path inconsistency**:
- **LIST** (`inbox_list`, sms.py:2511) collapses rows sharing `partner_id>0` into one representative row **by the conv's STORED `partner_id`** (sms.py:2591-2604). A conv whose stored partner_id = 27310 folds under "Bill Zwick" and, if it owns the newest message, supplies the preview.
- **OPEN** (`/api/inbox/thread_by_partner` → `_merge_partner_thread`, sms.py:2763 → `_partner_norms`, sms.py:2680) re-derives the member convs from that partner's **ODOO phone numbers** (`phone` + `x_studio_x_studio_second_phone`, partner + parent).

So when a conversation carries a `partner_id` that does **not** correspond to any of that partner's real Odoo numbers, the LIST shows it under that partner but OPEN excludes it (it loads only the Odoo-number threads) → the message "appears then vanishes." The real recipient's row disappears because their conv is wearing the other partner's id/name.

**How a conv gets the wrong partner_id (two candidate triggers — not yet disambiguated; needs a live read):**
(a) **Outbound stamped a stale partner_id:** `messaging.send(partner_id=…)` writes partner_id only in `_conv_new` (messaging.py:667-689); `_conv_append` never re-stamps. A caller passing a stale/wrong partner_id (e.g. 27310, just created from the call) while `to` = a different number creates `_conv_new(norm=other#, name=Bill, partner_id=27310)`. The Twilio send still goes to `to`, so **the text reaches the right phone; only the in-app label is wrong.**
(b) **Inbound resolve-flip on a shared number:** `_resolve_partner_by_phone` (sms.py:719) returns `hits[0]` — arbitrary when ≥2 W&SC partners share a number — and the inbound path (sms.py:1976) OVERWRITES `conv['partner_id']` with it. Documented dup-on-number hazard already in code (`clear_needs_reply_for_so`, sms.py:2711: Sally Walsh, partners 24158 vs 23036 on one number).

**Delivery vs label are independent:** the number a text is SENT to (`to`/`conv.phone`) is separate from the displayed partner name. A wrong partner label does NOT by itself mean the SMS went to the wrong phone. Record of truth for the actual destination number = Twilio's sent-log (or the live conv's `phone`).

**★ LIVE SMS STORE IS SESSION-UNREACHABLE (by design):** the live inbox runs on **`momscare-db`** (`SMS_DB_URL`, Postgres id `dpg-daocj0btqb8s73eq8kt0-a`) whose **IP allowlist is EMPTY** → `query_render_postgres` returns "blocks all external connections" (a security boundary — do NOT open it; see [[feedback_cant_headlessly_seed_is_security_feature]]). The **`wsc-memory-pillar`** copy (`dpg-danl5vqjnfac7390g8g0-a`, which `MEMORY_DB_URL`/`_MEM_DB_URL` uses for the idempotency ledger) still HAS a `sms_conversations` table but it is **frozen at 2026-09-21** (the cutover date to momscare) — a stale mirror, not the live inbox. To read the live conv, go through the APP's own endpoints (the Render process holds the creds) via **Operator**, not a direct PG connection.

**Proposed fix (staged for Lead QC; customer-facing → DJ-gated, not self-promoted):** (1) guard the stamp — only set/keep a conv's `partner_id` when that partner's Odoo number matches the conv `norm`; (2) make the LIST merge consistent with the thread OPEN (don't fold a conv under a partner row unless its norm is one of that partner's numbers). Disambiguate (a)/(b) with one live read first (Operator), then fix the exact cause, not a guess ([[feedback_root_cause_not_just_instance]]).

See [[feedback_data_location_odoo_vs_postgres]], [[feedback_gate_bulk_migration_scope_and_db]] (the SMS_DB live vs MEMORY_DB reachable split), [[feedback_builders_dont_sequence_or_defer]].
