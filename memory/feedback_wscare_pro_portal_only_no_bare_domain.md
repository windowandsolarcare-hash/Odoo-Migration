---
name: feedback_wscare_pro_portal_only_no_bare_domain
description: wscare.pro is PORTAL-ONLY — tokenized links only; NEVER print it as a bare/typeable domain on any customer-facing surface
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T19:44:32.439Z
---

DJ rule (2026-10-27, via Dispatcher): **`wscare.pro` is the portal / Render-app domain and is PORTAL-ONLY.** Customers reach it ONLY through tokenized LINKS (e.g. `wscare.pro/p/<token>`, `/c/<token>`, `/pay/<token>`, `/receipt/<token>`, `/book/sched/<token>`). It must **NEVER appear publicly as a plain, typeable domain** on anything customer-facing — receipts, texts, emails, marketing, footers, signatures.

**Why:** DJ saw "wscare.pro" printed as a bare footer domain on a customer receipt and wants it off — a bare domain invites a customer to type the root (which is the app, not a public site) instead of using their signed link.

**How to apply:**
- Customer-facing bare `wscare.pro` text → **strip it** (or, if a website line is wanted, that's the MARKETING domain **windowandsolarcare.com** — Frontdoor's lane — and the exact wording is a Dispatcher/DJ review).
- **Keep** legitimate tokenized / path links (`/p/`, `/c/`, `/pay/`, `/receipt/`, `/book`…) — those are functional links, not a bare domain.
- **Not affected:** internal Odoo logs (`x_studio_creation_log`), code comments, owner-only launcher tiles, and `<img src="https://wscare.pro/static/...">` asset URLs (not visible text). These are not customer-facing bare domains.
- Marketing/website surfaces live in Odoo-website (Frontdoor) — route those via Dispatcher.

First fix under this rule: removed the `<a href='https://wscare.pro'>wscare.pro</a>` footer line from the branded receipt (`routers/owner/receipt.py`, BIZ_WEB). See [[feedback_never_send_dj_to_odoo]], [[project_calendly_retired]] (same "kill a bare/stale customer-facing URL" pattern).
