---
name: project_store_cutover_smoke_needs_latency_gate
description: A data-store cutover smoke that only checks data-present + clean-boot MISSES latency regressions — any store cutover needs a real-use latency + load gate before KEEP.
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-22T22:10:52.399Z
---

# Store-cutover smoke MUST include a real-use latency + load gate (not just data-present + clean-boot)

**2026-09-22 incident.** The inbox-thread PG cutover (SMS_DB_URL flip → sms.py reads convs from the wsc-memory-pillar Postgres instead of the JSON store) passed my smoke and I signaled KEEP — then DJ's REAL phone use FAILED minutes later: inbox list slow, tapping a thread (Darcella) hung, ended in "Couldn't load this conversation. Try again." Reverted (Dispatcher unset SMS_DB_URL="" → `_PG=bool("")=False` → back to known-good JSON store, dep-dapfotlbedkc738nfg5g live 22:10). Restore-first, root-cause after.

**Why the smoke passed but real use failed — the gap:** my smoke verified (a) clean boot logs (no sms_store/psycopg errors) and (b) data integrity via a direct PG query (`SELECT count(*) FROM sms_conversations` = 257 convs present/readable). BOTH passed. But neither measured **per-request read LATENCY through the app under real use.** A row-count query over an MCP admin connection is nothing like the app's per-thread point-read on a single 512MB web instance with `connectionPool:"none"` (cold connect per request) — that's the slow-then-timeout profile. Data-present + boot-clean ≠ fast-enough-under-load.

**Why:** a store cutover changes the READ PATH's performance characteristics, not just where bytes live. Correctness smokes (data there? boots?) are necessary but NOT sufficient — they can't catch a latency/timeout regression. On the small single instance, an unindexed point-read or an unpooled cold connect turns a working feature into timeouts under real tap-through.

**How to apply — the re-flip gate for ANY data-store cutover (JSON→PG, instance move, etc.):**
1. **Real-use latency gate, measured through the APP** (not an admin SQL query): inbox LIST < ~1s, cold single-thread open < ~1.5s, no timeout.
2. **Load-test at REAL volume** (here: 257 convs / 205 with partner) — measure latency, not row count.
3. **Verify the read path is index-covered** (the by-key point-read AND the list query — guard against seq-scan / N+1) and the **connection pool is warm** (`connectionPool:"none"` on the DB = a red flag; add/warm a psycopg pool).
4. Only KEEP after 1–3 pass. Data-present + clean-boot alone = NOT enough to KEEP.

Ties to [[feedback_odoo_verify_content_not_status]] (HTTP 200 ≠ success — verify by real behavior) and [[feedback_data_location_odoo_vs_postgres]] (the PG-vs-Odoo seam). Owning session for the PG inbox path fix = Specialists.
