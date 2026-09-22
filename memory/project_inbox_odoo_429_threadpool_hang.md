---
name: project_inbox_odoo_429_threadpool_hang
description: "THE root cause of the 2026-09-22 inbox outage (list slow + tapping any thread hangs → 'Couldn't load'): Odoo 429 rate-limiting + shared.odoo_rpc's patient 3× backoff (~9s/call) on SYNC endpoints exhausting FastAPI's ~40-thread threadpool. NOT the PG cutover (revert didn't fix it). Fix: graceful-429 (fail-fast + timeout 20→5), resilient inbox summary cache, staggered crons. Commit 6a717cf4."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T22:42:51.781Z
---

**Inbox outage root cause + fix (2026-09-22, commit 6a717cf4).** DJ's inbox: list slow, tapping ANY thread (Darcella, Nick — universal) hung then "Couldn't load this conversation." The PG cutover was blamed first but the REVERT to the JSON store did NOT fix it → PG ruled out (see [[project_inbox_pg_cutover_latency_regression]]). Real cause:

## Chain (diagnosed from Render metrics + logs)
- **Odoo rate-limits `/jsonrpc` with HTTP 429** under load (logs: 429 at 22:00/22:14/22:22, recurring). CPU idle (~0.2 peak), mem ~205/512MB → NOT a loop/OOM. 502s NOT recurring (the earlier memory-hook debounce held). The symptom was **499s** (client-cancelled) = requests HANGING then the phone's 10s fetch aborting.
- **`shared.owner.shared.odoo_rpc`** (what the inbox uses — sms.py:17 `from .shared import odoo_rpc`; feed_live too) had a PATIENT retry added for the 5am cron: on 429/5xx it retried **3× with `sleep(1.5×attempt)` = up to ~9s of sleeping per call**, plus `timeout=20`. Great for a cron, FATAL for the field.
- **The inbox endpoints are sync `def`** (inbox_list, /inbox/thread, feed producers) → FastAPI runs them in its **bounded ~40-thread threadpool**. Each slow/throttled Odoo call HOLDS a thread up to ~9-20s. Under a throttle (compounded by feed_live = ~18 Odoo calls/feed-load + DJ's tabs + the cron burst), the pool EXHAUSTS → EVERY new request (list AND thread) queues for a free thread → hang → 499 → "Couldn't load." That's why it was UNIVERSAL and store-independent (summaries live on Odoo either way).
- **Amplifier:** main.py's APScheduler had ~11 Odoo-hitting cron jobs (myday `*/5`, several `*/10` & `*/15`, etc.) all firing on the SAME `:00`/`:15` tick → an ~8-job Odoo burst that self-triggered the 429 regardless of manual cool-downs.

## Fix (3 files, atomic commit 6a717cf4 — forced-429 test ALL PASS)
1. **shared.py `odoo_rpc` graceful-429:** `timeout` 20→**5**; a **429 FAILS FAST** (raises typed **`OdooBusy(RuntimeError)`**, NO retry — retrying INTO a rate-limit extends the throttle); only a transient network-timeout/5xx gets **ONE 0.5s** retry. So a throttled call frees its thread in ms, not seconds → no threadpool exhaustion → the field never hangs on a throttle. Success path + Odoo error-body UNCHANGED.
2. **sms.py resilient inbox-list summary cache:** module `_SUMS_LASTGOOD` (norm→summary); `_bulk_summaries` refreshes it on success and, on any Odoo failure, **serves the last-good stale summaries** instead of {} → the list degrades to STALE-POPULATED, never empty/hung. (Per-instance, lost on restart — the DURABLE version = PG-persisted summaries, a TRACKED follow-on per [[feedback_data_location_odoo_vs_postgres]] + [[feedback_durable_foundation_over_shortcut]].)
3. **main.py staggered cron minutes** off the :00 pile-up (WHEN only, never WHAT) — spreads the ~11 jobs across the hour so no ~8-job Odoo burst.

## Standing lessons
- **`odoo_rpc` has THREE copies** — `routers/owner/shared.py` (inbox/feed — FIXED), `routers/owner/dashboard.py:288` (timeout=20, serves PAYMENTS — a careful money-QC fast-follow: a read can fail-open to stale but a payment WRITE must never silently fail-open nor prematurely abort → needs bounded-retry + surfaced-error + idempotency, NOT a blanket 5s cap), and `shared/odoo.py` (requests, timeout=30, ~39s worst-case — Saunders-scoped). They share the threadpool; align deliberately, distinguishing read vs write.
- **Sync `def` + blocking Odoo httpx on a bounded threadpool = the structural hazard.** The deep fix is async Odoo calls (httpx.AsyncClient / async def) — a separate refactor, noted not done.
- **HTTP 499 (client-cancel) + CPU idle + no 500s = a HANG (blocked/queued), not a crash.** Look at thread/threadpool + slow-dependency, not CPU.
- Verify which `odoo_rpc` a path uses before patching (shadowing/duplication trap). Inbox = shared.py.
