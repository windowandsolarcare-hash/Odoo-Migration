---
name: project_sms_inbox_live_db_is_sms_db_url
description: "The LIVE SMS/voicemail inbox store (sms_conversations) is on SMS_DB_URL — a Postgres that BLOCKS external conns, so it is NOT queryable from a Claude session. wsc-memory-pillar (MEMORY_DB_URL, open allowlist) has a STALE COPY of sms_conversations — querying it for inbox analysis gives WRONG counts. Burned 2026-10-24."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-24T07:16:54.026Z
---

**The live inbox conversation store is on `SMS_DB_URL`, NOT `MEMORY_DB_URL`.** (`sms_store.py:45` → `_SMS_DB_URL = os.environ.get('SMS_DB_URL')`; `_conn = psycopg.connect(_SMS_DB_URL)`.) Every `_conv_get/_conv_set/_bulk_convs/index_get` on the PG path reads/writes THAT database's `sms_conversations(norm, partner_id, status, last_ts, data jsonb, updated_at)`.

**Two Postgres instances in the Render workspace `tea-d78l9fqdbo4c7388n9og`:**
- `wsc-memory-pillar` (`dpg-danl5vqjnfac7390g8g0-a`, db `wsc_memory_pillar`) — **`MEMORY_DB_URL`**: the scheduler advisory-lock DB (`_sched_singleton`) + memory pillar. `ipAllowList = 0.0.0.0/0` → **queryable** via the Render MCP `query_render_postgres`. It ALSO contains an `sms_conversations` table, but that is a **STALE COPY/snapshot** (same data lineage — same customers, fewer VM rows). **Querying it for inbox analysis returns WRONG (undercounted) numbers.**
- `momscare-db` (`dpg-daocj0btqb8s73eq8kt0-a`) — `ipAllowList` EMPTY → blocks all external conns → **not reachable** from a session.

**`SMS_DB_URL` points to a DB that BLOCKS external connections** (empty allowlist — momscare-db-instance or external), so **you CANNOT query the live inbox directly from a Claude session.** The in-process app (sms_store, scheduled jobs) reaches it fine; a session cannot. To analyze the live inbox from a session you must use the app's own read path (an endpoint / an in-process one-shot that LOGS the result) or ask DJ. **Never trust `wsc-memory-pillar.sms_conversations` as the live inbox.**

**How this burned us (2026-10-24):** the spam-VM "option C" backfill census was built by querying `wsc-memory-pillar` → showed 34 unknown-number voicemails, DJ protected 5. But the LIVE inbox (`SMS_DB_URL`) had **58** unknown VMs. The one-shot sweep ran in-process (correct DB) and did "all unknowns except the 5" → **moved 53, not the ~29 DJ reviewed** — over-reaching DJ's "everything in the 34" by ~24 (incl. 12 local 442/760 numbers he never saw). Reversible (Not-spam). **Why:** a wrong-DB census silently undercounts, and the discrepancy only showed up when the in-process run's `moved=53 scanned_vm=77` contradicted the session's query (`spam=0`). **How to apply:** before any inbox count/census/analysis, confirm you're on the live store — and since `SMS_DB_URL` is unreachable from a session, drive inbox reads through the app (or an in-process logging job), never a session-side SQL query of wsc-memory-pillar. See [[feedback_verify_limits_before_declaring]], [[project_inbox_twilio_voicemail_storage]], [[project_spam_voicemail_segregation]].
