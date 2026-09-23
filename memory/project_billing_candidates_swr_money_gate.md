---
name: project_billing_candidates_swr_money_gate
description: Billing review SWR cache + synchronous _CAND_MUT money gate so an acted job is never re-shown (double-collect prevention) — specialist_billing.py
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T14:18:05.068Z
---

**GET /owner/api/billing/review** (specialist_billing.py) renders the past-due collect list via `detect_candidates()` = 1 `sale.order` search_read (≤500 SOs) + ~10 helper RPC batches (method/snoozed/hours/awaiting/held/skipped/seen/addr/lines/freq), all synchronous. It was served `no-store`, so EVERY open re-ran the full sweep → each open tied a threadpool thread (uncancelable on client-disconnect), and rapid re-opens saturated the single 512MB worker → **502** (2026-09-23). The v2_hud goAction nav-guard stopped the rapid-tap pile-up; this made the sweep itself instant.

**Fix (commit 13fd590e, 2026-09-23):** SWR cache `_CAND_LG{rows,ts,key,mut}` + `_candidates_cached()`:
- serve last-good instantly if `key match AND mut==_CAND_MUT AND age<TTL(20s)`; stale-by-TTL-only → last-good + single-flight bg refresh (`_kick_cand_refresh`, `_CAND_REFRESHING`/`_CAND_LOCK`); cold/mut-mismatch/keychange → SYNCHRONOUS build.
- `run_sweep()` RE-WARMS the cache with its fresh rows but does **NOT** bump (it's the refresh, not a mutation — bumping there = self-loop).
- `detect_candidates` stays RAW (run_sweep + mutations need truth). Both read paths (review + candidates GET) use `_candidates_cached`.

**★ THE MONEY GATE (double-collect prevention) — the non-obvious part:** `_CAND_MUT` is a counter bumped by `_billing_mutated()` **SYNCHRONOUSLY at the real state-write in every billing write (all 10):** mark_seen, mark_seen_one, sweep, send_zelle (after `_mark_asked`), send_cc (send=true only, after `_mark_asked`; preview writes no state → no bump), reschedule_later, hold, dismiss, **settle (the shared helper — also called best-effort from dashboard.py payment paths, so a payment landing by ANY path busts the cache)**, sync_job.
- **Why synchronous, not via run_sweep:** the 4 money-moves (send_zelle/send_cc/reschedule/hold) DEFER run_sweep via `background_tasks.add_task` — the HTTP response returns BEFORE the refresh runs. A review reload in that window would serve the pre-mutation cache = **double-collect**. The synchronous bump makes the mut mismatch in that window → forced sync rebuild → the acted job is GONE. State writes (`_mark_asked` etc.) are synchronous; only run_sweep is deferred, so the rebuild reads the changed state.
- **Precise bump, NOT a blanket `@decorator`:** a decorator would bump on send_cc PREVIEW (send=false, the common case) too → cache dies during active collection. Over-bump is safe (extra rebuild, never under-bump) but the CC-preview hot path made precision worth it.
- **Structural completeness:** a forced-test SOURCE-AUDIT parses the real file and fails if any billing POST write doesn't bump (settle covered via helper-delegation; review GET must not bump). Machine-enforced so a future write can't silently reintroduce a double-collect. Test: `C:/Users/dj/billing_swr_test.py` (34/34).

Same SWR shape as inbox (`_INBOX_MUT`) / feed / thread cache — see [[project_inbox_odoo_429_threadpool_hang]]. Nav-guard companion fix: [[project_hud_nav_guard_502]].
