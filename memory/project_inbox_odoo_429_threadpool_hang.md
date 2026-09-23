---
name: project_inbox_odoo_429_threadpool_hang
description: "THE root cause of the 2026-09-22 inbox outage (list slow + tapping any thread hangs → 'Couldn't load'): Odoo 429 rate-limiting + shared.odoo_rpc's patient 3× backoff (~9s/call) on SYNC endpoints exhausting FastAPI's ~40-thread threadpool. NOT the PG cutover (revert didn't fix it). Fix: graceful-429 (fail-fast + timeout 20→5), resilient inbox summary cache, staggered crons. Commit 6a717cf4."
metadata:
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T01:08:22.941Z
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

## Completion — HUD throttle-resilience (2026-09-23, commit e2b67ab)
The graceful-429 raise (#1) was HALF-done: shared.odoo_rpc now raises `OdooBusy` on 429/unreachable, but uncaught callers (dj_alerts, owntracks, HUD endpoints) then hard-**500**. Auditing all ~70 routers to add try/except = the repetition trap (CLAUDE #9). Completed it centrally instead:
- **Global handler:** `@app.exception_handler(OdooBusy)` in main.py (`from routers.owner.shared import OdooBusy`) → any uncaught OdooBusy returns a graceful **503 + Retry-After:5** instead of 500, in ONE place. NARROW (only OdooBusy — real bugs still 500). Money-safe: the payment path uses **dashboard.py's OWN odoo_rpc** which raises `HTTPStatusError` (not OdooBusy) → it does NOT hit this handler → payment behavior unchanged. A throttled WRITE fails LOUD as 503 (never silently succeeds). The `OdooBusy` import sits after the routers are loaded (no circular).
- **feed_live SWR** (feed.py `_assemble_live`): the HUD's `/api/feed/live_list` ran ~18 producer Odoo calls per load → 12s client timeout under a throttle ("Couldn't load the feed"). Split into `_assemble_live` (dispatcher) + `_assemble_live_build` (heavy). Now: fresh hit → cache; **STALE → serve last-good 200 INSTANTLY + refresh in a SINGLE-FLIGHT background thread** (`_LIVE_REFRESHING` set + `_LIVE_REFRESH_LOCK` → one refresh per key, extra stale hits skip spawning = never thread-per-request = REDUCES Odoo pressure under load, never amplifies); cold-start builds once + degrades to `[]` on failure (never 500). The bg thread catches its own OdooBusy.
- **HUD renders per-widget** (why the global 503 + SWR is complete): `feed_live.live_cards()` is already per-producer `try/except` ("never raises") → one throttled producer skipped, feed still returns the rest; v2_hud `loadFeed` writes its errbox into `$('feed')` ONLY (tabs/launcher intact); daily_status fetch is try/ok-guarded; dj_alerts is NOT a v2_hud fetch (0 refs). So no single widget's 503 blanks the HUD.
- **Reusable pattern:** an app-wide "backend temporarily unavailable" signal (OdooBusy) is best mapped to 503 via ONE global exception handler (not N per-caller catches), with last-good SWR on the few hottest read paths. Tests: `force_odoobusy_test.py` (9/9 — handler 503-narrow, happy-path 200, SWR instant-stale + single-flight + cold→[]).
- Tracked P2: dashboard.py's odoo_rpc raises HTTPStatusError-429 (not OdooBusy) so it bypasses the global handler — fold in later by making dashboard.py's odoo_rpc ALSO raise OdooBusy (money-careful; it serves the payment path).

## Inbox SWR — durable fast-inbox (2026-09-23, commit 6a76411b)
`inbox_list` (sms.py) also blocked on its per-load Odoo read (index + summaries) under a SLOW-but-succeeding Odoo (429 fails fast via #1, but high-latency Odoo waited up to timeout×calls → ~12s client timeout). Applied the SAME SWR pattern as feed_live, **mutation-aware** so it can't hide a new customer text:
- The inbox cache version is `_INBOX_MUT:30s-bucket`. New `_INBOX_LASTGOOD[filter]` keeps the last build stamped with the `_INBOX_MUT` it was built at (survives a bucket rollover).
- On a MISS: if `_INBOX_LASTGOOD[filter].mut == _INBOX_MUT` (miss is ONLY a time-rollover, zero conv writes since) → serve last-good INSTANTLY + single-flight bg refresh (`_INBOX_SWR_REFRESHING` + lock; refresh calls `inbox_list(filter, _force_build=True)`). If `_INBOX_MUT` CHANGED (any conv write) → synchronous rebuild.
- ★ GATE BY CONSTRUCTION: **`_conv_set` is the SOLE conv-write chokepoint** (sms.py ~267) and bumps `_INBOX_MUT`; `sms_incoming` writes via it. So ANY inbound/status/reply → `_INBOX_MUT++` → `_lg.mut != _mut_now` → SWR bypassed → fresh build → a new text NEVER hides behind stale. SWR serves stale ONLY on a pure time-rollover. (Added a "SOLE CONV-WRITE CHOKEPOINT" comment at `_conv_set` so a future side-write doesn't escape the bump.)
- ★ BUG the forced-test caught: `_force_build` must bypass the cache-HIT check too (`if (not _force_build) and _c.get('ver')==_ver...`), else the bg refresh no-ops on the version the SWR branch just set. Fixed.
- Test: `inbox_swr_test.py` (8/8 — stale instant + inbound-busts→new-text-appears + single-flight + never-lose). PG-persisted list projection stays the deeper multi-instance follow-on (in-proc last-good is per-instance).
