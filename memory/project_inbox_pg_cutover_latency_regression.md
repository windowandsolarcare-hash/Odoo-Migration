---
name: project_inbox_pg_cutover_latency_regression
description: "The inbox-thread PG cutover (SMS_DB_URL → wsc-memory-pillar) REGRESSED in DJ's real use (list slow, thread open hung → 'Couldn't load this conversation') though smoke passed. Root cause = sms_store.py's SINGLE unpooled psycopg connection under one global lock (serializes all callers) + cold-reconnect-under-lock, NOT a missing index. Reverted. Re-flip needs a warm pool + real-volume latency gate."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T22:13:22.877Z
---

**Inbox PG cutover latency regression (2026-09-22).** Flipping `SMS_DB_URL` → the `wsc-memory-pillar` Postgres moved the inbox conversation store from Odoo `ir.config_parameter` blobs to PG. Smoke passed (257 convs intact, 205 with partner) but DJ's LIVE phone use failed: inbox list slow, tapping a thread (Darcella) hung then "Couldn't load this conversation. Try again." Dispatcher reverted SMS_DB_URL to the JSON store (data was intact — a LATENCY/timeout regression, not data loss).

## Root cause (Specialists diagnosis — read sms_store.py + sms.py)
- **NOT a missing index.** `norm` is the PRIMARY KEY of `sms_conversations`, so the thread-read `SELECT data WHERE norm=%s` is a PK point-read — instant even at millions of rows. At 257 rows every query (even a seq scan) is sub-ms. Rules out the "index/volume" hypothesis.
- **★ It's the connection design.** `sms_store.py` uses a SINGLE, unpooled psycopg connection (`_conn_obj`) guarded by ONE global `threading.Lock` (`_run` → `_lock`). `connectionPool:"none"` on the PG confirms no Render PgBouncer either. EVERY sms_store op — inbox list, thread open, the HUD live_list poll's needs_reply count, dashboard, inbound-SMS webhooks — SERIALIZES through that one lock+connection. Smoke = a single sequential request = fast; real use = concurrent requests queue behind the lock. The killer: `_run` reconnects-on-drop (close+reconnect+retry) UNDER the lock, and managed PG drops idle connections → a cold/slow reconnect (TLS+auth, seconds) blocks every queued caller → "slow, then hang, then 'Couldn't load'". That's the smoke-vs-real gap.
- **Secondary (amplifier + smell): the inbox path STRADDLES two stores.** Conv blobs are on PG, but the list SUMMARIES are still on Odoo — `_bulk_summaries` (sms.py) has NO PG branch, and `_conv_set` DUAL-writes blob→PG + summary→Odoo (`_pset(INBOX_SUM_PREFIX...)`). Doubles per-write latency + couples the hot path to both backends. (Not the direct hang — Odoo summaries survived the migration, so the list still reads them in one search_read — but it's extra latency + a Phase-2 cleanup.)

## The PG itself
`wsc-memory-pillar` = `dpg-danl5vqjnfac7390g8g0-a`, plan **0.1 CPU / 256 MB**, 1 GB disk, oregon, PG18, `connectionPool:"none"`. SHARED — the inbox conv store AND the Memory Pillar both use it. A tiny 0.1-CPU DB serving both is a latency risk under concurrent JSONB reads independent of the app conn layer.

## Fix for re-flip readiness (Specialists owns; BLOCKED until it passes a real-volume gate)
1. Replace the single-locked-conn with a WARM psycopg pool (min 2 / max ~4 — deliberately tiny for a 0.1-CPU shared PG). `psycopg[binary]==3.2.3` is installed but the pool lives in the separate `psycopg_pool` package → a requirements add (COORDINATE with Builder-2, who owns a held requirements.txt commit; or a no-dep manual pool of N connections). The app-level read-modify-write on a conv (conv_get→mutate→conv_set in sms.py) is a PRE-EXISTING last-write-wins pattern — the single lock never protected it either (lock released between the two calls) — so a pool introduces NO new race.
2. Optionally enable Render's built-in PgBouncer (`connectionPool`) on the PG (infra toggle, DJ — changes the connection string) as defense-in-depth for BOTH tenants.
3. LOAD-TEST at real volume (257 convs): concurrent inbox-list + a COLD single-thread open — gate = list <1s, thread <1.5s cold, ZERO timeouts. That's the gate the row-count smoke missed.
4. If the load-test shows the PG itself CPU/RAM-bound (not just the app conn layer), surface a plan-bump cost tradeoff to DJ (feedback_durable_foundation_over_shortcut) — don't assume.

See [[feedback_data_location_odoo_vs_postgres]] (inbox convs correctly belong in PG), [[feedback_hud_cards_live_not_inbox]], [[feedback_durable_foundation_over_shortcut]]. The triage 3-file push is also HELD until the app is stable.
