---
name: project_public_quote_rates_feed
description: "ONE price source: the public marketing-site /quote calculator reads live window prices from the app via GET /owner/api/public/quote-rates (cookieless, CORS-scoped, server-side cached) instead of its own hardcoded copy. DJ edits prices once in the app quote-rates screen and the website follows."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-20T23:00:10.060Z
---

**Problem (DJ, 2026-10-20, via Frontdoor):** the public marketing site (windowandsolarcare.com `/quote` pane-counter) had its OWN hardcoded unit prices, while DJ edits the real ones in the app's quote-rates screen (`/owner/quote-rates` → `POST /owner/api/quote/rates/save` → `ir.config_parameter` `quote.rates.override`, merged over `QUOTE_RATES` defaults by `_get_quote_config()`). Two copies drift. DJ wanted to edit ONCE in the app and have the website follow.

**Solution (SHIPPED 2026-10-20):** a PUBLIC read-only mirror of the app's existing rates read path.
- **Endpoint:** `GET /owner/api/public/quote-rates` (+ an `OPTIONS` twin for CORS preflight). Defined in `routers/owner/dashboard.py` right after `api_quote_rates` (dashboard router mounts at `prefix="/owner"`, main.py). Public URL: **`https://wscare.pro/owner/api/public/quote-rates`**.
- **Source of truth is NOT duplicated:** it calls the SAME canonical `_get_quote_config()` (dashboard.py). A small per-instance TTL cache (`_public_rates_cache`, `_PUBLIC_RATES_TTL=300`) just MEMOIZES that output so a public marketing-site view doesn't hit Odoo/`ir.config_parameter` on every load (≤1 config read per 300s per web instance — same load-reduction theme as prewarm). The OWNER editor endpoint stays UNcached (DJ sees edits instantly); `api_quote_rates_save` busts the public cache (`_public_rates_cache['at']=0.0`) after `set_param`.
- **Payload (minimal public surface):** `{ok:true, rates:{...}, difficulty:{...}, labels:{...}}`. Internal `updated_at` AND `updated_by` are DROPPED (not exposed publicly). Frontdoor's site consumes `rates` only (6 keys: reg_panes/over_panes/ss_panes/reg_sliders/over_sliders/triple_sliders) + a website-constant `OUT_F=0.55` (outside-only; not app-editable).
- **CORS:** `Access-Control-Allow-Origin: https://www.windowandsolarcare.com` (apex 301s→www; that's the effective browser origin), no `Allow-Credentials` (simple GET, no cookies). `*` is a tolerable fallback for public pricing if a second marketing origin ever appears.
- **Auth:** the one EXACT path `/owner/api/public/quote-rates` is in `routers/authz.py` `PUBLIC_EXACT` (after the gallery/photo carve-outs) → cookieless GET/OPTIONS pass the `/owner` PROTECTED-prefix gate; EXACT (not prefix) so no sibling leak; also gives it R1 deny-by-default coverage. `/owner/api/quote/rates/save` is NOT listed → stays owner-cookie gated.

**Why safe to be fully public:** the rates are pricing ALREADY shown to every anonymous visitor on the public calculator; no PII/secret. Zero input surface (no query/body params). `_get_quote_config()` is whitelist-on-read — only the 6 known rate keys + 3 known difficulty keys, coerced to float — so a poisoned `quote.rates.override` blob cannot inject arbitrary keys/data into the public response. Read is fail-safe (try/except → defaults, never 500s/leaks an Odoo body).

**Propagation SLA:** after a DJ price edit the site reflects it **within ~5 min**, NOT instantly — cache + bust are PER WEB INSTANCE and the service runs 2 instances (the non-serving instance keeps its cached payload until its own 300s TTL + `Cache-Control: max-age=300` client lag). Fine for rarely-changing pricing; Frontdoor's site keeps a hardcoded fallback so it never breaks if the feed is unreachable. (Instant cross-instance would need shared-cache — not built; same limitation as prewarm.)

**Frontdoor's half (marketing site, Odoo website module):** fetch this feed on `/quote` load, override the calculator's RATES, keep today's numbers as fallback. The BINDING CORS check is Frontdoor's IN-BROWSER fetch from the live www page (curl only proves the header is emitted, never that a browser accepts it). See [[feedback_odoo_verify_content_not_status]], [[feedback_verify_collection_and_live_pipe]].

**Commits (2026-10-20):** dashboard.py b8d0997e (+45 additive), authz.py 9773bc58 (+6, EXACT entry), ENDPOINT_MAP.md 26e558f5. §15: Audit fresh-eyes GREEN → Lead firsthand confirm → build+stage → Lead byte-QC PASS → auto-deploy → Lead post-push live-diff PASS. PLAN: saunders-render-app `3_Documentation/review/public_quote_rates/PLAN.md`.

**Marketing-site wiring (Frontdoor's half, DONE 2026-10-20):** the `/quote` page is the Odoo marketing view **`wsc.quote` (`ir.ui.view` id 3839)** — its single source. Frontdoor edited it to fetch this feed on load and override its RATES, keeping a (now-corrected: over_panes 9→10, ss_panes 10.5→11) hardcoded fallback for feed-unreachable. **E2E VERIFIED LIVE in a real browser on www.windowandsolarcare.com/quote:** on-load GET → 200 ×3, zero CORS/console errors, in-page fetch returns ok:true + live rates, and an Oversized pane rendered $10 (the live app rate, was $9 hardcoded). The one-price-source loop is fully live: DJ edits in the app quote-rates screen → site follows within ~5min.
