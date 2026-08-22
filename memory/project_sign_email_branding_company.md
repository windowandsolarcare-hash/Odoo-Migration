---
name: project_sign_email_branding_company
description: Odoo Sign/offer-letter emails branded with wrong company = sign.request.communication_company_id (defaults to active company at send time)
metadata: 
  node_type: memory
  type: project
  originSessionId: d2946c99-3a0a-4d7d-8300-e27ce0c3eef0
---

Odoo Sign completion/offer emails (and the logo + company name in them) are branded by the field **`sign.request.communication_company_id`** ("Company used for communication") — NOT by the applicant's company, NOT by the creator's default company. It **defaults to the active company in the user's company switcher at the moment the document is sent.**

**Incident 2026-06-23:** David Osuna's W&SC offer letter (hr.applicant 109, correctly company_id=1) went out branded **Saunders Printing** because DJ's Odoo company switcher was on Saunders Printing (company 3) when the Sign doc was created. Both companies share phone 9519726946 + email windowandsolarcare@gmail.com, so only the name/SP-logo exposed it. Fixed by writing `communication_company_id=1` on sign.request id 1. Note: the already-sent email keeps the wrong brand — only a re-send fixes the customer-facing copy.

**Why:** Odoo multi-company picks up the *active* company for outbound branding regardless of the record's real owner. [[CLAUDE.md rule 8 — always filter/​set company_id]] applies to comms too, not just financial queries.

**How to apply:** Before generating ANY branded outbound doc for W&SC (Sign/offer letters, invoices, quotes), set the company switcher (top-right in Odoo) to **Window and Solar Care** first. To audit/fix after the fact: `sign.request` search_read field `communication_company_id`; write the correct company id. GOTCHA: `sign.request`/`sign.template` have NO `company_id` field in this Odoo 19, and plain `read` on sign.request trips an unhashable-list error on a computed field — use `search_read` with explicit fields instead.
