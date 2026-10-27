---
name: project_marketing_site_wscare_pro_inventory
description: "Where wscare.pro appears on the PUBLIC marketing site (windowandsolarcare.com = Odoo-website) and why it's not a clean find-and-replace: some refs are brand/SEO (safe to rebrand), others are FUNCTIONAL cross-app links to the Render app that windowandsolarcare.com 404s."
metadata:
  node_type: memory
  type: project
  originSessionId: 967bdc43-a1eb-42bc-82ff-a4be56f896dc
  modified: 2026-10-27T19:53:31.082Z
---

**DJ rule (2026-10-27, relayed via Dispatcher):** `wscare.pro` is PORTAL-ONLY / tokenized-link
access only — must NEVER appear as a bare/typeable domain on anything customer-facing. Public
brand domain = **windowandsolarcare.com**. Specialists already stripped it from the app receipt
footer. Frontdoor owns the marketing-site side.

**Hosting (verified by headers 2026-10-27):**
- `windowandsolarcare.com` = **Odoo** (nginx + `session_id`/`frontend_lang` cookies) — Odoo-website
  module, NOT in the app repo (Specialists can't see it; Frontdoor owns it).
- `wscare.pro` = the **Render app** (Cloudflare → uvicorn).
- `windowandsolarcare.com/book` → **404**; `/owner/api/public/quote-rates` → **404** on Odoo but
  **200** on wscare.pro. So the marketing site's booking + quote tool FUNCTIONALLY depend on the app.

**wscare.pro inventory on the marketing site — 6 Odoo `ir.ui.view` records, 16 hits:**
- **CLEAN:** no `wscare.pro` in any `mail.template`, nor in any company `report_footer` (all 3 cos).
- **A) BRAND/SEO (safe to rebrand to windowandsolarcare.com, zero functional risk):**
  - view **3854 `wsc.schema`** ("WSC Structured Data") — JSON-LD publishes `https://wscare.pro/` as
    the LocalBusiness canonical `url` + 5 `https://wscare.pro/services/*` URLs. This is the real
    violation (brand domain broadcast to Google as wscare.pro). All 5 service paths also exist on
    windowandsolarcare.com, so the swap is safe.
- **B) FUNCTIONAL cross-app links — do NOT blind-swap (windowandsolarcare.com 404s them all):**
  - **2337 `website.footer_custom`** (1): "Book online" → `wscare.pro/book/` (site-wide footer)
  - **1559 `website.homepage`** (2): Book buttons → `wscare.pro/book/`
  - **3845 `wsc.contact`** (1): Book online → `wscare.pro/book/`
  - **3839 `wsc.quote`** (5): Book buttons + `var BOOK='wscare.pro/book/'` + live fetch
    `wscare.pro/owner/api/public/quote-rates` (the quote-rate feed)
  - **3835 `wsc.services_window_cleaning`** (1): video `<source src=wscare.pro/static/dw/screen-machine-demo.mp4>`
  These are `href`/`src` behind labeled links — NOT bare/typeable domains — so they may already
  satisfy the "no bare domain" rule. wscare.pro/book is the CLAUDE.md-sanctioned booking fallback.
  To remove wscare.pro from the markup without breaking anything needs Odoo 301 redirects
  (windowandsolarcare.com/book → wscare.pro/book, /quote-rates, + rehost the video), a small build.

**Status (2026-10-27):** DJ (via Dispatcher) ruled: FIX A, LEAVE B as-is, redirect-cleanup = parked
option (don't build unless DJ asks). **A is staged + verified** — one clean replace in view 3854
`https://wscare.pro/` → `https://www.windowandsolarcare.com/` (6/6 hits, AFTER=0 wscare.pro / 6
windowandsolarcare.com, XML well-formed; BEFORE/AFTER in scratchpad). **BLOCKED on apply:** the live
`ir.ui.view` write via Bash XML-RPC is denied by the session auto-mode classifier ("Modify Shared
Resources") — needs DJ to approve the Odoo write in-session (or a mode flip). Do NOT route the write
through a peer (permission laundering). On approval: write `arch_db`, re-read view (expect 0 wscare.pro),
re-crawl a live page to confirm render, report live. Odoo key = `/c/Users/dj/_odoo_key_val.txt`; canonical
brand URL = `https://www.windowandsolarcare.com/` (live site redirects to www).

See [[feedback_never_send_dj_to_odoo]] (app is the UI — but the marketing SITE genuinely is Odoo-website
content), [[feedback_durable_foundation_over_shortcut]], [[feedback_question_when_big_picture_wrong]].
