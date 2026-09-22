---
name: project_inbox_slowness_is_odoo_429_not_store
description: "Inbox/list slowness + \"Couldn't load\" was Odoo 429 rate-limiting (inbox-list reads summaries from Odoo), NOT the conv store — a whole PG cutover+revert was spent misattributing it. Diagnose slow-but-200 + 499 + low-CPU as blocked-on-upstream."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-22T22:23:17.017Z
---

# Inbox "slow / Couldn't load" = Odoo 429 rate-limit (upstream), NOT the conversation store

**2026-09-22 incident, root-caused via Render metrics + logs.** DJ's inbox was slow and thread-taps ended in "Couldn't load this conversation. Try again." The fleet first assumed the conversation STORE and did a JSON→PG cutover (SMS_DB_URL flip), then when it still failed, reverted it — BOTH no-ops, because the real cause was upstream:

**ROOT CAUSE:** `window-solar-care.odoo.com/jsonrpc` was returning **HTTP 429 Too Many Requests** (seen live in logs: `httpx.HTTPStatusError: 429` via `odoo_rpc` @ dashboard.py:288). The **inbox-list endpoint reads its thread SUMMARIES from Odoo** (`_bulk_summaries` in sms.py has no PG branch — the "straddle": conv blobs on PG/JSON, list summaries still on Odoo). So when Odoo throttled, `/owner/api/inbox/list` took **~13–14 seconds** to return 200 → exceeded the client's ~10s fetch timeout → DJ's phone aborted the request (**HTTP 499** client-closed spikes) → "Couldn't load." Store-independent, so the cutover AND the revert both changed nothing.

**THE DIAGNOSTIC PATTERN (the reusable lesson) — before blaming the local DB/store for slowness, check for a throttled/slow UPSTREAM:**
- **Slow-but-200** responses (endpoint completes in 13-14s, not a 5xx) + **HTTP 499** (client closed = gave up waiting) + **LOW CPU / normal memory** = the request is **BLOCKED ON I/O waiting for an upstream**, NOT instance saturation, NOT a runaway loop (a loop shows sustained high CPU), NOT a slow local query (that'd be CPU or would've changed with the store swap).
- On this stack the upstream is almost always **Odoo jsonrpc**, and the documented trigger is **"aggressive testing + background dashboard polling overloads Odoo jsonrpc → 429s that make unrelated flows fail intermittently"** (CLAUDE.md infra gotcha). Heavy fleet/diagnostic Odoo usage in a session compounds it.
- Confirm with: Render `get_metrics` (CPU/memory/http_request_count by statusCode — look for 499s) + `list_logs` filtered for `429`/`Odoo`/`Traceback` around the failure window. That combination pinpoints upstream-block vs saturation in one pass.

**FIXES (assigned to Specialists, owns the inbox):**
1. **Immediate relief:** cut Odoo call pressure — a few-minute Odoo cool-down lets the 429 rate-limit recover and the inbox speeds back up.
2. **Durable fix:** DECOUPLE the inbox hot path from Odoo — move list summaries off Odoo to **PG or a cache with a freshness rule** (per [[feedback_data_location_odoo_vs_postgres]], derived/operational summaries belong on PG, not Odoo). Then the inbox is fast AND immune to Odoo throttling.
3. **Graceful 429 handling** in `odoo_rpc` / the summary read: serve stale-cached summaries + short backoff on 429; never hang 14s. A throttle must degrade, not block the field.

**What does NOT fix it:** numInstances=2 / zero-downtime (a 2nd instance hits the same throttled Odoo), the memory-hook runaway-loop work (CPU was healthy — no loop), and the PG conv-pool (revert proved the store isn't the cause). Ties to [[project_store_cutover_smoke_needs_latency_gate.md]] — the sibling lesson from the same incident.
