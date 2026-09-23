---
name: project_odoo_throttle_resilience_pattern
description: "How to make the Render app ride out an Odoo 429 throttle gracefully — a raised OdooBusy needs a GLOBAL exception handler (not N per-file catches), and heavy Odoo-dependent endpoints need stale-while-revalidate. Also: raising a new exception across a shared helper without matching catches converts hangs into 500s."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-23T00:54:02.306Z
---

# Odoo-throttle resilience: global OdooBusy→503 handler + SWR for heavy endpoints

**2026-09-22, shipped commit e2b67ab.** The shared Odoo instance (0.1-CPU, serves 3 companies + crons + the fleet) intermittently returns HTTP 429 under load. Two lessons from making the app survive it:

## 1. A raised exception across a shared helper is HALF a fix without matching catches
The graceful-429 change made `shared.odoo_rpc` RAISE a typed `OdooBusy` on a 429 (instead of hanging 20s). That fixed the endpoints that CATCH it (inbox_list fails-open) — but every endpoint that calls `shared.odoo_rpc` WITHOUT catching `OdooBusy` then **hard-500'd** on a throttle (confirmed: `dj_alerts`, the owntracks webhook). So we converted "hang 20s" into "500" for the uncaught callers. **Rule:** when you introduce a new raised exception through a widely-imported helper, you MUST also add the catches (or a global handler) in the SAME change, or you've just moved the failure mode.

## 2. The DRY completion = a GLOBAL FastAPI exception handler (not N per-file try/excepts)
There are dozens of `from .shared import odoo_rpc` callers across ~70 routers. Adding a try/except to each = the CLAUDE #9 repetition trap (and you'll miss some). Instead, ONE global handler in `main.py`:
`@app.exception_handler(OdooBusy)` → returns a graceful **503 + Retry-After** for EVERY uncaught OdooBusy, app-wide, in one place. Money-safe because it's NARROW (only OdooBusy — a real bug like ValueError still 500s, not swallowed) and a throttled WRITE fails-LOUD as 503, never silently succeeds. Import note: `from routers.owner.shared import OdooBusy` in main.py has no circular import (shared is a leaf, doesn't import main; routers already loaded by then). Boot-verify: `[route-check] ok` + "Application startup complete."
- ★ The **payment path is unaffected**: `dashboard.py` has its OWN `odoo_rpc` that raises `httpx.HTTPStatusError` (not OdooBusy), so it doesn't hit this handler. The clean way to fold it in later (the tracked P2 "twin" fast-follow) = make dashboard.py's odoo_rpc ALSO raise OdooBusy → then the same global handler covers it. Money-careful (payment writes need bounded-retry + surfaced-error + idempotency, not silent fail-open).

## 3. Heavy Odoo-dependent endpoints need stale-while-revalidate (SWR)
`feed/live_list` makes ~18 Odoo calls/load → under a throttle it went slow-200 (>12s) → client 12s fetch-timeout → "Couldn't load the feed." Fix = **SWR**: serve the last-good result INSTANTLY (200, 0.000s) + refresh from Odoo in a **SINGLE-FLIGHT** background thread (a lock/flag so extra stale hits serve stale + skip spawning — verified 6 stale hits → exactly 1 refresh). ★ Single-flight is critical: a thread-PER-REQUEST refresh would spawn N concurrent Odoo refreshes under load = MORE throttle pressure = worse. Cold-start with no cached value degrades to `[]`, never raises/500. The background refresh catches its own OdooBusy so the thread never crashes. This is the durable version of the inbox_list SWR + belongs on any Odoo-heavy hot path.

## Client complement
The HUD (`v2_hud.html`) already degrades PER-WIDGET (a feed non-200 writes an errbox into `#feed` only; `daily_status` is try/ok-checked; `live_cards()` is per-producer try/except) — so one widget's failure never blanks the page. Verify per-widget degrade on any dashboard so a single 503 can't blank the whole screen. (`dj_alerts` is a standalone endpoint + a feed producer — NOT a v2_hud fetch — so its 503 can't blank the HUD.)

**How to apply:** the app should NEVER hard-500 or hang on an Odoo throttle. New Odoo-calling endpoint → it's covered by the global OdooBusy→503 net automatically; if it's a hot/heavy path, give it SWR (single-flight) too. Ties to [[project_inbox_slowness_is_odoo_429_not_store]] (the root-cause sibling) and [[feedback_odoo_verify_content_not_status]].
