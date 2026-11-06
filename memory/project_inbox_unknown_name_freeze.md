---
name: project_inbox_unknown_name_freeze
description: "SMS inbox froze a thread's display name at first-message ingest; a customer who texted before being booked stayed \"Unknown\" forever. Fixed in sms.py (refresh-on-link + backfill repair), 2026-11-06."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-11-06T14:13:12.195Z
---

# Inbox "Unknown (phone)" name-freeze — root cause + fix (2026-11-06)

**Symptom:** a confirmed customer showed as `Unknown (6192087799)` in the message inbox (`v2_inbox`) even though his number was on his contact + property. Live case: **Mark Bradshaw, SO 265060** (person partner 27320; Property 27321 "2020 S Navajo", parent=27320). Same pattern: **Louise & Rainer Lang** (person 27325).

**Root cause:** the inbox display name is resolved ONLY at inbound ingest (`routers/owner/sms.py` ~1976, `resolved = _resolve_partner_by_phone(...)` → else `Unknown (<num>)`). Mark texted Nov 4 6:01 PM; the booking page created his contact 6:05 PM — 4 min LATER — so the thread was born `Unknown`/partner_id=None and never re-resolved. It stuck because:
- `append_inbox_event` (~607) backfilled `partner_id` onto the existing thread (via a later event, e.g. a booking ack) but did **NOT** refresh the frozen `name`.
- `/api/inbox/backfill_links` (~3672) SKIPPED any thread that already had a `partner_id` — so a linked-but-Unknown thread (Mark, linked to his Property 27321) was never repaired. (It caught the Langs, who had no partner yet.)

Hits ANY customer who contacts BEFORE being booked.

**Fix (sms.py, two commits):**
1. `3e1ef535` — HUNK 1 `append_inbox_event`: when linking a partner to an existing thread, refresh `name` only if current is empty/`Unknown` (keeps the never-clobber-a-human-set-name guard). HUNK 2 `backfill_links`: stop skipping threads that already have `partner_id`; the existing name-guard still leaves human-set/correct names alone. `_resolve_partner_by_phone` walks Property→parent, so a thread linked to a Property re-resolves to the PERSON (27321→27320).
2. `ed0635d1` — `backfill_links` now accepts a valid OWNER session (mirrors DJ-blessed sibling `backfill_sent` 2026-10-27) IN ADDITION to `CRON_SECRET`, so Operator runs the repair cookie-only — no secret in any URL. (The endpoint is behind the `/owner` authz wall; a bogus-token/no-cookie probe 401s BEFORE the handler — confirmed. I did NOT self-mint a cookie or put CRON_SECRET in a URL = security boundary respected. See [[feedback_cant_headlessly_seed_is_security_feature]].)

**Repair run:** Operator GET `/owner/api/inbox/backfill_links` (owner session) → `{ok, scanned:430, linked:3}`. Verified firsthand via Odoo read: Mark's `wsc.sms.conv.6192087799` blob flipped `Unknown (6192087799)`→`Mark Bradshaw`, partner_id 27321→27320. Langs cleared too.

**★ STORE-ROUTING GOTCHA (nearly a false-done):** `backfill_links` reads/writes **Odoo `ir.config_parameter`** (via `_pset`/direct `search_read`), but the inbox CAN read **Postgres** when `sms_store.pg_on()` == `bool(SMS_DB_URL)`. Before trusting the repair I checked which store is LIVE: the PG `sms_conversations` table (in `wsc-memory-pillar` dpg-danl5vqjnfac7390g8g0-a) EXISTS but its newest `updated_at` is **2026-09-21** and Mark (born Nov 4) is ABSENT → it's a **stale Sept migration snapshot, NOT live**; `SMS_DB_URL` is effectively off, live inbox = Odoo. So `backfill_links` (Odoo) hits the right store. **If PG were live, the Odoo-only repair would have looked done and changed nothing.** Always verify the live data store before declaring a data-repair done. See [[feedback_data_location_odoo_vs_postgres]] + [[feedback_gate_bulk_migration_scope_and_db]].

**OPEN FOLLOW-UP (Lead-noted, out of scope here, NOT yet fixed):** `sms.py` ~1986 sets `conv['name'] = customer_name` UNCONDITIONALLY on every RESOLVED inbound — that clobbers a human-set name, the opposite of the guard used elsewhere. Latent/pre-existing. Fix in a later surgical pass (only overwrite when current is empty/Unknown, same guard as HUNK 1).
