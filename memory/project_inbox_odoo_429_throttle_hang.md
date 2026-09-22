---
name: project_inbox_odoo_429_throttle_hang
description: "Owner READ hot paths (inbox/feed) that call Odoo per-load HANG on Odoo 429 throttles → 'Couldn't load this conversation.' Root source = the ~8-job in-proc APScheduler cron cluster bursting Odoo on one tick (shared 3-company instance). Fix = graceful-429 fail-fast + stale-populated cache + cron-stagger. NOT a store/PG/instance problem."
metadata:
  node_type: memory
  type: project
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-22T22:54:17.550Z
---

**2026-09-22 incident:** DJ's field inbox went slow, then threads failed with "Couldn't load this conversation. Try again." for ~1 hr. Log-evidenced root cause (Lead): **httpx 429 Too Many Requests from `window-solar-care.odoo.com/jsonrpc`.** The inbox reads thread SUMMARIES from Odoo on EVERY load (`/owner/api/inbox/list`), so under throttle the call took **13–14s > the client's ~10s fetch timeout → 499 abort → the error.** The instance was HEALTHY the whole time (CPU ~0.2, mem ~205/512MB) — **NOT** PG, **NOT** saturation, **NOT** a runaway loop.

**Why it wasted time:** we first blamed a recent inbox-thread PG-store cutover and REVERTED it (`SMS_DB_URL=""`). The revert changed nothing — because the summaries live on Odoo regardless of the store. Chasing the backend store was the wrong box entirely.

**The structural throttle source:** the app's **in-process APScheduler crons (~8 jobs) auto-fire against Odoo on the same `:00`/`:15` tick**, plus `feed_live` (~18 Odoo calls/load), plus DJ's open tabs, plus Saunders/Cheryl crons — all on the shared 3-company Odoo. A human/fleet "stop calling Odoo" cool-down **cannot** fix it: the crons keep re-triggering the 429 on their own ticks.

**How to apply:**
- **Owner/field READ hot paths (inbox, feed, anything the phone loads repeatedly) must NOT call Odoo per-load.** Serve from a cache (in-proc stopgap → PG-persisted durable) so they're fast AND immune to Odoo throttling. This is the durable fix; the graceful-429 handling below is the survival net.
- **`odoo_rpc` must degrade on 429, not hang:** fail-FAST (short timeout ~5s, was ~20) instead of holding a request ~9–14s (which also exhausts the threadpool). On a READ path, **fail-OPEN to stale-populated cache** (show what we have — threads still render) rather than empty/hung.
- **NEVER fail-open on a WRITE / payment path.** A payment write under 429 needs bounded-retry + surfaced-error + idempotency — see the P2 payment-path (`dashboard.py:288`) fast-follow. Two `odoo_rpc` twins exist: **`shared.py`** (inbox/feed — fixed here) vs **`dashboard.py:288`** (payment path — separate, careful). Fix the right one.
- **Stagger the APScheduler cron minutes** so the ~8 jobs don't burst Odoo on one tick.
- **On the shared 3-company Odoo, 429s WILL recur** — design for graceful degradation; don't rely on cool-downs.
- **Diagnosis lesson:** slow/erroring ≠ a store problem. Check LOGS for `429`/`OdooBusy` + instance CPU/mem FIRST, before flipping backends. Ties to [[feedback_odoo_verify_content_not_status]] and the Odoo-429 gotcha in CLAUDE.md.

**Fix shipped:** deploy `6a717cf4` (2026-09-22) — `shared.py` graceful-429 fail-fast + stale cache, `main.py` cron-stagger. Verified real-path: inbox list **~0.2s** (was 13–14s), 3 thread-opens 200/fast, **zero** 429 hangs. DJ confirmed "speed back." Durable follow-on tracked: PG-persist the inbox summaries (retire the in-proc stopgap).
