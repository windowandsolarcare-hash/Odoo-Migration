---
name: project_stripe_duplicate_payments_dashboard
description: "★ CRITICAL GOTCHA: the Stripe endpoints exist TWICE — routers/owner/payments.py AND routers/owner/dashboard.py both define /api/stripe/payment_link, /tip_page, /success, /send_email, /logo. They SHADOW inconsistently: payments.py's payment_link wins (POST), dashboard.py's tip_page wins (GET). Editing only dashboard.py silently does nothing for the shadowed route. payments.py never imported urllib → its payment_link crashed 'name urllib is not defined', breaking ALL Stripe links until fixed 2026-07-27."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-27T18:07:27.947Z
---

**2026-07-27 — burned badly here.** The whole Stripe suite is DUPLICATED across two routers: `routers/owner/payments.py` and `routers/owner/dashboard.py`. Both `@router.post('/api/stripe/payment_link')`, `@router.get('/api/stripe/tip_page')`, `/success`, `/send_email`, `/logo`. main.py includes both (dashboard ~L211, payments ~L219). FastAPI first-match-wins, BUT empirically the shadowing is INCONSISTENT per-route:
- **`/api/stripe/payment_link` (POST) → payments.py's copy serves** (dashboard's was likely un-decorated after an edit).
- **`/api/stripe/tip_page` (GET) → dashboard.py's copy serves** (my svc-details/name/address/date + card-capture render live).

**The bug that ate an hour:** I made ALL my session's Stripe improvements (extract `_create_stripe_tip_link`, wscare.pro, drop tinyurl, card brand/last4 capture, `email_from` domain fix, tip-page customer details) to **dashboard.py**. But payment_link is served by **payments.py**, which STILL had `_RENDER_URL`+tinyurl AND used `urllib.parse.quote` while never importing urllib (payments.py imports: `datetime, json, re, os, httpx, base64, csv, io` + `from .shared import *` — NO urllib). So every call returned `{"ok":false,"error":"name 'urllib' is not defined"}` and customers got ugly tinyurls when it didn't crash. Editing dashboard.py did nothing because payments.py shadowed it. Also wasted time thinking it was a stale-deploy (even a cache-clear rebuild "didn't fix it" — because the code being served was the OTHER file).

**How to diagnose route shadowing:** if editing an endpoint has no effect on the live response, `grep -rn "def <fn>\|'<path>'" routers/owner/*.py` — there's almost certainly a second copy. See CLAUDE.md paired-changes note (dashboard.py shadows hemet.py the same way).

**FIXES 2026-07-27:** payments.py payment_link now builds `https://wscare.pro/owner/api/stripe/tip_page?...` (branded; wscare.pro is a Render custom domain → this app), so_name used raw (URL-safe SO number, no urllib), tinyurl removed. dashboard.py's copy already fixed the same way (belt+braces — either can win). Customer-facing links are branded wscare.pro now ([[project_calendly_retired]] wscare.pro is the branded short domain).

**RULE for any future Stripe change:** edit BOTH payments.py and dashboard.py (or better, make one call the other) — never assume dashboard.py is the live one. Ideally consolidate to a single copy (not yet done — risky, needs care). Billing specialist's CC path calls dashboard's `_create_stripe_tip_link` DIRECTLY (imported fn, not the HTTP route), so it uses dashboard's code — that's why billing CC worked while the field Charge-at-Door (HTTP endpoint → payments.py) was broken. See [[project_billing_specialist]].
