---
name: project_receipt_link_owner_endpoint
description: GET /owner/api/receipt_link?so_id= — owner-only read-only endpoint that recomputes the already-issued branded-receipt URL; it is a receipt-token oracle and MUST stay owner-walled
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T22:29:02.290Z
---

Shipped 2026-10-27 (Specialists, main `a81730ddf4`): **`GET /owner/api/receipt_link?so_id=<id>`** in `routers/owner/carddoor.py` (`api_receipt_link`). Returns `{ok, so_id, url}` where `url` = the branded public receipt link `wscare.pro/receipt/<token>`. It **recomputes the SAME signed so-token** the carddoor send path uses (`.receipt.receipt_link` → `calfeed.make_so_token`, HMAC over `so:<id>` with `BOOKING_TOKEN_SECRET`, **no TTL → deterministic**), so the recomputed link is byte-identical to the one already texted/emailed.

**Why it exists:** the issued receipt link is NOT stored anywhere (the SO chatter logs only "🧾 Branded receipt emailed/texted to …", never the URL), and recomputing the token needs the app-only secret. So there was no way to VIEW a receipt already sent — only re-send. This endpoint closes that: DJ/Dispatcher get the existing link without a re-send, without exposing the secret.

**It is READ-ONLY:** computes a string, no Odoo write/read, no send. Owner-cookie-walled by the `/owner` entry in `routers/authz.py` `PROTECTED_PREFIXES` (NOT in any PUBLIC carve-out, handler takes only `so_id` — no forced token, per [[feedback_owner_triggered_endpoint_uses_owner_cookie_not_token]]). AUTH_ENFORCE=1 is ON now → unauth GET `/owner/*` returns a hard **401** (verified live). Placed in carddoor.py (owner-prefixed, already imports receipt_link) — NOT receipt.py, whose router is registered with NO prefix (public) and would have left it unauthenticated.

**★ STANDING DESIGN CONSTRAINT (Lead, non-negotiable):** this is a **receipt-token oracle** → it must **STAY owner-walled forever**. No public "view receipt" affordance, no wall loosening, ever. The receipt *page* `/receipt/{token}` is public (anyone with the token sees it), but *producing* a token is privileged — never add an endpoint/UI that mints or returns a receipt token without the owner cookie.

**Deferred follow-on (bounded, not yet built):** a "View receipt" link/button on the paid job card that opens this URL (there's currently no in-app view-receipt affordance, only re-send). When building it: it calls this owner-walled endpoint from DJ's owner session — keep it owner-only, honor the constraint above.

**To fetch a URL for a waiting DJ:** a builder session CANNOT call this anonymously (401) and must NOT read `BOOKING_TOKEN_SECRET` to compute the token itself (that undercuts the wall). Route the call to an **owner-authenticated** actor — Operator (drives the app via owner cookie) or DJ's own logged-in browser. Then the public `/receipt/<token>` page can be opened anonymously to render-verify. See [[feedback_cant_headlessly_seed_is_security_feature]], [[feedback_wscare_pro_portal_only_no_bare_domain]].
