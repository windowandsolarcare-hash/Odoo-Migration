---
name: project_inbox_conv_store_pg
description: Inbox conversation store → Render Postgres migration (fix thread-open WAN latency). Builder-2 M1 = new sms_store.py DAL + backfill; Specialists reroutes sms.py. Env vars, design decisions, cutover.
metadata:
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-21T23:43:26.484Z
---

**Move the inbox CONVERSATION store off Odoo `ir.config_parameter` blobs (`wsc.sms.conv.<norm>` + `wsc.sms.index`, ~196 convs) → Render Postgres**, killing the per-thread-open WAN JSON-RPC hop DJ feels on his phone. Store relocation ONLY (conversation content + threading UNCHANGED). Follows [[feedback_data_location_odoo_vs_postgres]] + the A35/A36 memory-pillar migrate-verify-rollback playbook. Brief: `saunders-render-app/3_Documentation/INBOX_THREAD_POSTGRES_BRIEF.md`.

## Ownership (Lead-serialized)
- **Builder-2 (net-new, DONE-M1-code):** `routers/owner/sms_store.py` (DAL + admin endpoint) + `scripts/migrate_sms_to_pg.py`. Pushed via gh api (main protected — NEVER git push). NO sms.py touch.
- **Specialists (AFTER B2's DAL lands+parity):** reroute sms.py funnels (`_conv_get/_conv_set/_index_get/_touch/_bulk_convs`) + fix the raw bypass `followups.py:61` → call the DAL. Lead file-locks sms.py (one holder).

## Table (control the schema)
`sms_conversations(norm TEXT PK, partner_id INT, status TEXT, last_ts TEXT, data JSONB, updated_at TIMESTAMPTZ)`. `data` = FULL conv dict (source of truth). partner_id/status/last_ts PROMOTED for indexing. Conv dict shape (from sms.py `_conv_new`): norm/phone/name/partner_id/status/snooze_until/tags/priority/unread/draft/msgs[]/last_ts/last_dir; msgs capped last 300 (full history in Odoo chatter).

## Env vars (two-var cutover, like memory)
- `SMS_DB_URL` = the FLIP/DAL flag (DAL active only when set; rollback = UNSET it, Odoo blobs untouched).
- `SMS_DB_URL_MIGRATE` = the CONNECT var for the backfill (run BEFORE flip, no pre-schema window). DAL ignores this name.
- `SMS_EXPECT_MIN` (default 150) integrity floor. `NOTIFY_SECRET` gates the admin endpoint.
- ★ Recommend REUSING the Memory Pillar Postgres INSTANCE (new table, independent flag) — zero new DB cost. Dispatcher binds the URL fromDatabase (secret, never via a session).

## ★ Design decisions (Builder-2, for QC / Specialists' reroute)
- **A37 CLOBBER-GUARD:** `conv_get`/`conv_set` RAISE `SmsStoreError` on a hard DB error (None = genuinely absent), NOT fail-open. WHY: the inbound path does `existing = _conv_get(norm); conv = existing or _conv_new()` — a fail-open-to-None on a transient blip would treat an EXISTING convo as NEW and the next conv_set CLOBBERS history. So the reroute's WRITE-path read must use raising `conv_get` (or catch), never fail-open. `conv_get_safe`/`conv_set_safe` (fail-open) are for DISPLAY only. `index_get`/`bulk_convs` DO fail-open ([]/{}) — list reads can't clobber.
- **Index order** derives from `last_ts DESC` + `updated_at` tiebreak (retires `wsc.sms.index`); `touch()` bumps updated_at so a status-only change still resurfaces. `run_backfill` REPORTS index-order divergence vs the legacy _touch order → tells us pre-cutover if a `rank` column is needed.
- **Parity = TWO ways** (A35/A36): count (pg_rows==migrated) + spot-content (deep-equal Odoo blob vs PG data on sampled norms). Guarded Odoo reads (retry→ABORT, never copy an empty read); EXPECT_MIN floor; never writes Odoo.

## Status (2026-09-21)
- ✅ M1 CODE: table+DAL+backfill+CLI+admin endpoint (`POST /api/sms/admin/migrate`, NOTIFY_SECRET-gated) pushed, compile-clean, inert. → Lead QC.
- ✅ LIVE BACKFILL DONE + VERIFIED PASS (2026-09-21): DJ bound SMS_DB_URL_MIGRATE (Datastore-URL link to wsc-memory-pillar PG, renamed off Render's DATABASE_URL default) + ran the CLI one-off in the wsc-field-assistant Render shell (I have NO Render shell/one-off tool via MCP → DJ runs it). Result: source_index 260, source_convs 257, missing_conv_blobs 3 (orphaned index entries — norms w/ no conv blob, incl. 2 test 555s; SAFE to skip, "missing"=genuinely absent not a read error since a hard read ABORTS), pg_rows 257, count_parity PASS, spot_content 8/8 PASS. order_divergence 130/257 positions differ BUT first_10 identical = BENIGN (intended last_ts ordering vs the retiring _touch order; actionable top stable; position-count overstates it; NO rank column needed — that'd defeat retiring the index).
- ⏭ Then Specialists reroute (M2) → cutover flip SMS_DB_URL (M3) → smoke → rollback ready.

Related: [[feedback_data_location_odoo_vs_postgres]], [[feedback_durable_foundation_over_shortcut]], [[feedback_github_deployment_bash]], [[feedback_never_relay_credential_via_session]].
