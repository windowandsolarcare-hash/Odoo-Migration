---
name: project_logs_healthy_but_user_broken_is_client_side
description: "When server logs/metrics show healthy (200s, fast) but the user reports the app broken — especially repeatedly — the fault is CLIENT-side (service worker / cached bundle / client fetch timeout). Verify via the user's ACTUAL device IP in the access logs, not aggregate metrics."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-23T00:10:30.720Z
---

# "Server logs healthy but the user says it's broken" = a CLIENT-side fault — verify by the user's device IP

**2026-09-22 incident (the three-headed inbox P1).** DJ's inbox was "broken" on his phone while Render logs showed his requests returning 200 fast — this DIVERGENCE recurred TWICE before it was correctly pinned as client-side. The lesson is the diagnostic method, so it doesn't take a third miss next time.

**The tell:** server-side signals (Render access logs, `get_metrics` CPU/mem/status-code, deploy boot) all look HEALTHY — the user's requests return 200, no 429/500, CPU/mem fine — yet the user reports the app broken. When that divergence repeats, STOP re-verifying the server. The fault is in the layer the server logs can't see: the CLIENT.

**How to verify it's client-side (fast, decisive):**
1. **Pull the USER'S ACTUAL DEVICE IP from the access logs, not aggregate metrics.** `mcp__render__list_logs` with `text:["<their external IP>"]` (DJ's was 76.90.35.160 — an external residential IP; internal `10.228.x` = Render health checks, NOT the user). If their real requests are 200 + fast, the server is serving them fine and the break is downstream on their device.
2. **Check whether the failing endpoint is FAIL-OPEN server-side.** If the endpoint cannot 500 (returns 200 empty/stale on any backend failure — like `inbox_list` here), then a client error banner ("Can't reach the server") is *definitionally* client-origin: a fetch-level failure (client timeout, dropped signal, non-JSON body, or a stale cached bundle), NOT the server.
3. **Distinguish a TRANSIENT from a persistent bug:** if you see a burst of the user's requests succeed (200) shortly after the reported failure — especially with a client auto-retry — it self-healed; it was a transient (cold cache, a deploy/SW-swap window, a weak-signal blip), not a standing fault.

**The concrete client causes found this incident:**
- **Stale service worker on the v2 SPA** — the v2 pages never registered/updated the SW, so the phone was stranded on an old cache-first SW serving a stale JS bundle → dead tap-handler. The SW did NOT intercept `/owner/api/*`, so API calls still hit the server (200) while the cached UI was broken = the exact "logs≠reality" signature. Fixed by registering+auto-updating the SW on v2 pages + a cache-version bump (see [[project_inbox_stale_sw_v2_no_update]]).
- **Cold-first-load with no localStorage cache** — after the cache bump, a single failed/slow fetch on a filter with no cached fallback showed a hard "Can't reach the server" (no skeleton, no retry-backoff) instead of a graceful loading state → a transient LOOKED like a hard break.

**How to apply:** when a user says "still broken" but the logs say fine, don't declare either "fixed" (from logs alone) or "server bug" — pull THEIR device IP, confirm 200s, check fail-open, and look for self-heal. Then hand the client layer (SW/cache/fetch-timeout/render) to the FE owner. Ties to [[feedback_odoo_verify_content_not_status]] (verify by real behavior) and [[project_inbox_slowness_is_odoo_429_not_store.md]] (the sibling server-side lesson — the FIRST head of this same incident, which WAS a real server/Odoo cause; so: check server first, but once the server is provably healthy for the user, move to the client).
