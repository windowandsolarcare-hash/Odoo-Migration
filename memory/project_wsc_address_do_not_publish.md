---
name: project_wsc_address_do_not_publish
description: "W&SC has no public street address — the Odoo company address is stale and the real one is DJ's home. Never publish it; never put it in schema."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1cb095a1-10e5-4519-903e-c06b100b873a
  modified: 2026-08-18T15:40:31.962Z
---

**Window & Solar Care is a service-area business with NO public street address.** Two addresses
exist and both are wrong to publish:

- `res.company` id 1 carries **41995 Boardwalk Ste. J, Palm Desert** — **STALE / WRONG** (confirmed
  by Lead 2026-08-18). Do not assert it anywhere. It still prints on that company's invoices; that
  cleanup is a separate business task, not a website one.
- DJ's real, current address (the one on the Twilio A2P profile) is **32569 San Miguelito Dr.,
  Thousand Palms, CA 92276** — but that is **DJ's HOME**. He is a mobile home-services operator
  with no premises customers visit.

**Why:** publishing a home address is a privacy and safety downside with no upside. Google fully
supports service-area businesses that hide their address, so there is no SEO cost either. Asserting
the *stale* one is worse still — Google cross-checks name/address/phone consistency for local
ranking, so a wrong address actively hurts.

**How to apply:** on the public site ([[project_marketing_site_odoo]]) keep it address-less — the
Contact page says "mobile service business, we come to you" and links the service-area page, and the
LocalBusiness JSON-LD carries `addressRegion: CA` + `areaServed` cities but **no `streetAddress`**.
The old WordPress Privacy Policy printed the home address; that line was deliberately dropped when
the text was carried over (phone + email satisfy the contact requirement). If DJ ever asks for an
address back, get him to confirm which one first.
