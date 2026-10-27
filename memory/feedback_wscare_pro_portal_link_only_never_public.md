---
name: feedback_wscare_pro_portal_link_only_never_public
description: "DJ 2026-10-27: wscare.pro is the PORTAL/Render-app domain, accessed by tokenized LINKS only — NEVER print it as a bare, typeable domain publicly on anything customer-facing (receipts, texts, emails, marketing, footers)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: e025c990-f5b0-4a94-874c-5016d12b0b5a
  modified: 2026-10-27T19:43:22.076Z
---

DJ (2026-10-27) saw "wscare.pro" printed as a plain/typeable domain on a customer receipt and wanted it removed. His rule:

**THE RULE:** `wscare.pro` is the **portal / Render-app domain**, and it is reached **by tokenized links only** (magic links like `wscare.pro/p/<token>` for the customer portal, `wscare.pro/c/<token>` for personalized booking). It must **NEVER appear publicly as a bare domain** that a customer could just type — not on receipts, not in texts/emails, not on marketing, not in page footers. "That is our portal information only... accessed by links only... don't use that publicly on anything."

**Why:** the portal/app surfaces behind wscare.pro are link-gated (token auth). Advertising the bare domain invites people to try to reach it directly, and it's not meant to be a public front door. The PUBLIC-facing brand/web domain is **windowandsolarcare.com** (the Odoo marketing site); wscare.pro is the internal app/portal domain, link-access only.

**How to apply:** (1) Strip any bare `wscare.pro` from customer-facing output; keep only intentional full tokenized links. (2) Builders: never hardcode a plain `wscare.pro` into a receipt/sms/email/marketing template — if a customer needs the portal, give them their tokenized magic link. (3) Dispatcher/Frontdoor: treat a bare public `wscare.pro` as a bug to remove. Related: [[feedback_calendly_retired]] (all booking links = wscare.pro/c/<token>), [[feedback_repeat_portal_link_every_save]], [[feedback_company_name_no_a]].
