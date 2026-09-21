---
name: project_inbox_pg_reroute
description: "The sms.py conversation funnels (_conv_get/_conv_set/_index_get/_index_set/_touch/_bulk_convs) are now FLAG-GATED (sms_store.pg_on() → Render Postgres DAL, else Odoo ir.config_parameter). Phase 1 moves the conv store + index only; the A41 summary blob stays on Odoo. Write path uses the RAISING conv_get/conv_set (clobber-guard)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-21T23:58:29.084Z
---

**Inbox-PG reroute (2026-09-21, commit caeb38b5, shipped FLAG-OFF, Lead-serialized).** The conversation store moved off Odoo `ir.config_parameter` blobs (a WAN JSON-RPC hop per thread-open = the phone-felt slowness) onto **Render Postgres**. Builder-2 built the net-new DAL `routers/owner/sms_store.py` + table `sms_conversations` + backfill `scripts/migrate_sms_to_pg.py`; Specialists rerouted the sms.py funnels.

## How it works
- **`sms_store.py` DAL** (flag = env `SMS_DB_URL`; `sms_store.pg_on()` True when set; psycopg lazy-imported inside `_connect` → boot-safe when unset). API: `conv_get(norm)` [RAISES SmsStoreError on DB error], `conv_get_safe(norm)` [fail-open None], `conv_set(norm,conv)` [RAISES] / `conv_set_safe`, `touch(norm)`, `delete`, `index_get()` [fail-open [], ORDER BY last_ts DESC, updated_at DESC — the index is DERIVED, no stored list], `bulk_convs(norms=None)` [fail-open {}], `count()`.
- **sms.py funnels are flag-gated** — each is `if sms_store.pg_on(): <DAL> else: <original Odoo body verbatim>`, so **flag-OFF = the exact prior Odoo behavior** (this is what shipped; cutover is separate/DJ-gated). Rerouted: `_conv_get`(→raising conv_get), NEW `_conv_get_safe`(display), `_conv_set`(→raising conv_set, THEN _INBOX_MUT + the A41 summary write), `_index_get`, `_index_set`(**no-op on PG** — index derived), `_touch`(→touch/updated_at), `_bulk_convs`(→bulk_convs). `followups.py::_conv_state` raw `get_param` bypass → `conv_get_safe` on PG.
- **★ CLOBBER-GUARD (hard, A37 class):** the WRITE path uses the RAISING `_conv_get`/`_conv_set` — a PG DB error propagates SmsStoreError and ABORTS before _INBOX_MUT/summary, so a fresh conv is NEVER written over an existing one. `conv_get_safe` is DISPLAY-only; `index_get`/`bulk_convs` fail-open. NEVER make the write-path read fail-open to None.
- **A41 summary blob (`wsc.inbox.sum.*`) STAYS on Odoo — phase 1 out of scope** (`_bulk_summaries` untouched; `_conv_set` still writes the summary to Odoo). Phase 2 (optional, later) folds the ~13 summary fields into PG columns + retires the blob.
- **Non-indexed-conv "invisible customer" risk = RESOLVED** by PG's derived index (index_get selects ALL convs by last_ts → every conv appears; the old ad-hoc wsc.sms.index drift, e.g. Glenn's un-indexed cell conv, can't happen). See [[project_split_number_thread_merge]].
- **Cutover (DJ-gated, Lead-run):** bind `SMS_DB_URL_MIGRATE` (fromDatabase) → run the backfill → VERIFY count both ways → bind `SMS_DB_URL` (flip, redeploy) → smoke (thread-open latency drop; an inbound writes to PG). Rollback = unset `SMS_DB_URL` (Odoo blobs never deleted). ★ Benign order-divergence on flip: recent/active convs keep identical order; only deeper/older list entries re-sort slightly by last_ts (the intended retirement of the ad-hoc _touch index — no rank column). Give DJ that UX heads-up before the flip.
- **Cutover follow-up flagged:** _conv_get was rerouted TRANSPARENTLY (funnel-level = raising on all callers → write-safe). Pure-display callers (except followups) inherit raising → a PERSISTENT DB outage 500s a display read (DAL retries absorb transient blips). If display-fail-open is wanted at cutover, route specific display-only readers to `_conv_get_safe`.

Related: [[project_inbox_summary_readmodel_a5]] (A41 summary read-model, stays Odoo phase 1), [[project_memory_pillar_postgres_a35]] (the DAL playbook this clones), [[feedback_regression_guard_pushes]], [[project_day_off_two_representations]].
