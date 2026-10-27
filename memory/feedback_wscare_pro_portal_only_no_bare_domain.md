---
name: feedback_wscare_pro_portal_only_no_bare_domain
description: wscare.pro is PORTAL-ONLY — tokenized links only; NEVER print it as a bare/typeable domain on any customer-facing surface
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T22:41:37.776Z
---

DJ rule (2026-10-27, via Dispatcher): **`wscare.pro` is the portal / Render-app domain and is PORTAL-ONLY.** Customers reach it ONLY through tokenized LINKS (e.g. `wscare.pro/p/<token>`, `/c/<token>`, `/pay/<token>`, `/receipt/<token>`, `/book/sched/<token>`). It must **NEVER appear publicly as a plain, typeable domain** on anything customer-facing — receipts, texts, emails, marketing, footers, signatures.

**Why:** DJ saw "wscare.pro" printed as a bare footer domain on a customer receipt and wants it off — a bare domain invites a customer to type the root (which is the app, not a public site) instead of using their signed link.

**How to apply:**
- Customer-facing bare `wscare.pro` text → **strip it** (or, if a website line is wanted, that's the MARKETING domain **windowandsolarcare.com** — Frontdoor's lane — and the exact wording is a Dispatcher/DJ review).
- **Keep** legitimate tokenized / path links (`/p/`, `/c/`, `/pay/`, `/receipt/`, `/book`…) — those are functional links, not a bare domain.
- **Not affected:** internal Odoo logs (`x_studio_creation_log`), code comments, owner-only launcher tiles, and `<img src="https://wscare.pro/static/...">` asset URLs (not visible text). These are not customer-facing bare domains.
- Marketing/website surfaces live in Odoo-website (Frontdoor) — route those via Dispatcher.

**Shipped example (2026-10-27, live @ main 3b20aa84):** the branded-receipt PAGE footer (`routers/owner/receipt.py`, `BIZ_WEB`, rendered at `/receipt/<token>`) showed a bare `wscare.pro`. DJ's pick was NOT to strip it but to **swap in the public marketing domain**: `BIZ_WEB = "windowandsolarcare.com"` (one-line constant; the footer anchor renders `windowandsolarcare.com` tappable). So when a website line IS wanted on a customer surface, show **windowandsolarcare.com** (public brand site), never the app/portal domain. The receipt EMAIL + SMS surfaces (`carddoor.py`) were already clean — they carry only the tokenized `/receipt/<token>` link, no bare domain. Two gotchas that bit this fix: (1) the receipt *page* footer is a SEPARATE spot from the email/SMS footer — sweep ALL surfaces; (2) a strip-variant branch was staged but never promoted and went stale, so the bare domain stayed LIVE — a staged fix only counts once promoted + deploy reaches Render 'live'. See [[feedback_never_send_dj_to_odoo]], [[project_calendly_retired]] (same "kill a bare/stale customer-facing URL" pattern), [[feedback_staged_mirror_stale_base_refetch]], [[project_receipt_link_owner_endpoint]].
