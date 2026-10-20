---
name: project_marketing_quote_rates_live_source
description: "The marketing /quote pane-calculator (Odoo view wsc.quote id 3839) pulls live prices from the app's public quote-rates feed — one price source; and marketing-site build scripts are GONE so edits are direct Odoo view writes."
metadata:
  node_type: memory
  type: project
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-20T23:01:17.224Z
---

**One price source for window quotes (DJ-directed, built 2026-10-20).** DJ edits the per-pane/slider
prices ONCE in the app's quote-rates screen (`wscare.pro/owner/quote-rates` → `quote_rates_page`,
dashboard.py; saves to `ir.config_parameter` via `POST /owner/api/quote/rates/save`). That is the
SINGLE source of truth; the app's own quote tool already reads it via `GET /owner/api/quote/rates`.

The public **marketing-site** `/quote` pane-calculator used to have its OWN hardcoded `var RATES`
(drifted: it showed over_panes $9 / ss_panes $10.5 while DJ's live were $10 / $11). Now wired to the
same source:
- **Specialists** added a PUBLIC CORS read mirror: `GET /owner/api/public/quote-rates`
  (dashboard.py ~:7171, `api_public_quote_rates`; added to authz PUBLIC_EXACT; + an OPTIONS preflight).
  Returns `{ok, rates, difficulty, labels}` (whitelisted — NO internal fields). Headers
  `Access-Control-Allow-Origin: https://www.windowandsolarcare.com`, `Cache-Control: public, max-age=300`.
  Same `_get_quote_config` source as the owner endpoint — NOT a second store. `/save` stays owner-gated.
- **Frontdoor** edited the Odoo marketing view `wsc.quote` (`ir.ui.view` id **3839**, the ONLY view
  holding the estimator; used by `website.page` id 12 `/quote`): on load it fetches the public feed and
  overrides RATES (`for k in RATES: if typeof feed.rates[k]==='number' → RATES[k]=...; draw()`),
  hardcoded RATES kept as the **current-value fallback** (prefer-live; fall back only on hard failure).
- **Propagation SLA ~5 min** after a DJ price edit (per-instance in-process cache × 2 instances, 300s TTL).
- **Binding CORS proof** = in-browser fetch from the live `www.windowandsolarcare.com/quote` (curl can't
  prove CORS). Verified 2026-10-20: page's own on-load GET → 200, no CORS/console errors, UI shows the
  live rate ($10 oversized). `OUT_F` (0.55 outside-only) stays a website constant (not app-editable).

**★ The marketing-site build scripts are GONE.** [[project_marketing_site_odoo]] described re-runnable
scripts (`wsc_shared.py`, `wsc_pages_a/b.py`, `run_build.py`, `deploy.py`) in a session scratchpad —
they are NOT on disk and NOT in any repo (searched 2026-10-20). So marketing-site edits are now **direct
Odoo `ir.ui.view` JSON-RPC writes**: read `arch_db`, surgical string edit (assert count==1), XML-validate
(`ET.fromstring`), concurrency-guard (live arch == the version you edited from, else ABORT), write back,
read-back confirm, then browser-verify. Odoo key at `C:/Users/dj/_odoo_key_val.txt`; XML-RPC
`window-solar-care.odoo.com`, DB `window-solar-care`, auth as windowandsolarcare@gmail.com. The site has
NO branch/preview — direct-to-live by design, so keep a backup of the original arch to revert.
See [[feedback_odoo_verify_content_not_status]], [[feedback_push_compare_and_swap]].
