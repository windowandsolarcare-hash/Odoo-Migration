---
name: project_dw_prices_owner_tile
description: "Owner launcher tile 'Del Webb Prices' (v2_dw_prices.html) — a phone-call price lookup that reads the canonical single-source endpoint /api/dw/prices (routers/dw_prices.py). Shipped 2026-10-30."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-31T06:08:42.637Z
---

**What:** owner-facing launcher tile **"Del Webb Prices"** — a phone-call price lookup (type/tap a floor plan → Good/Better/Best, base price big + "1st-time $X" muted under each). Visual by Design (artifact X1C57dYySiqRMEcKPLyMLj); Specialists built the page + endpoint + tile. Shipped 2026-10-30 (Lead byte-QC GREEN; auto-deploy policy = code ships on Lead QC, no DJ trigger).

**★ SINGLE SOURCE OF TRUTH = `routers/dw_prices.py`** (Lead ruling 2026-10-30, rule 9: DW prices drift ~3x/month and our own memory had already diverged, so NO 2nd hardcoded copy). Canonical `GROUPS` + `FIRST_TIME_ADD=50` live there; `GET /api/dw/prices` returns `{groups:[{plans,good,better,best}], first_time_add}`. Public read-only (whitelisted in authz `PUBLIC_ROOT_EXACT` — prices are already public on /dw). Static business data, no Odoo/DB — **to change a DW price, edit GROUPS in dw_prices.py and every reader updates.** Prices verified byte-for-byte vs static/dw/index.html GROUPS on 2026-10-30: 175/210/285 · 225/260/335 · 255/290/365 · 315/350/425 (good/better/best = Essential/Premium/Signature; Premium = postcard price).

**Files (commits 2026-10-30):** routers/dw_prices.py (new, 5061a59b) · static/owner/v2_dw_prices.html (new, 76fe01f4) · routers/authz.py (+1 whitelist line, d9acc81c) · static/owner/v2_apps.js (+tile 🏷️ "Del Webb Prices" fav:true, 2ba2a676) · main.py (import + include_router, 89cfe293). Pushed boot-safe: dw_prices.py FIRST, main.py (imports it) LAST.

**Owner page behavior:** fetches /api/dw/prices (10s timeout). **Fetch-fail → "Reload" prompt, NO hardcoded fallback** — deliberate: a stale price read aloud on a call is the harm, so better nothing than wrong. Chrome mirrors v2_prices.html (wsc_telemetry.js + wsc_back.js + ‹Back → v2_hud.html). No whoami gate (page shows only public prices; /static is public shells anyway). NOTE: the page's `var FIRST_TIME_ADD=50` is a benign DEFAULT, always overridden by the fetched value.

**★ DELIBERATE ASYMMETRY (flagged "do not fix"):** the OWNER tile has NO fallback (fetch-fail→Reload). The PUBLIC /dw page, when it migrates (see below), will KEEP its hardcoded GROUPS as a last-known-good fallback and only OVERRIDE from the fetch — because a public conversion surface must never show empty price cards (phone rule 13). Same endpoint, opposite fetch-fail behavior, each correct for its surface.

**PARKED fast-follow (Lead condition, non-urgent):** migrate the PUBLIC /dw page (static/dw/index.html GROUPS) to also read /api/dw/prices so it stops being a parallel hardcode. **Frontdoor owns** the /dw client-JS swap (fallback-and-override, prices unchanged, staged + Lead-QC'd); Specialists own the endpoint. Recorded durably in [[project_del_webb_landing_page]] + 3_Documentation/review/dw_prices/BUILD_NOTE.md. /dw keeps working on its current hardcode until migrated.

**OPEN — DJ confirm (flagged via Dispatcher 2026-10-30):** the tile shows first-time = **base + $50** on every plan. This is the ONLY displayed figure not printed on the postcard bands (though canonical in the endpoint as `first_time_add`). Awaiting DJ's confirm that's the intended displayed rule; if different, it's a one-number change in dw_prices.py.

Related: [[project_del_webb_landing_page]], [[feedback_question_when_big_picture_wrong]] (the rule-9 single-source call), [[feedback_durable_watcher_not_session_cron]] (sibling /dw visit counter shipped same night).
