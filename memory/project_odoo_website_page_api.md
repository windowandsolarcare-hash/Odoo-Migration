---
name: project_odoo_website_page_api
description: "How to create/override Odoo website pages, header and footer over JSON-RPC — plus the reserved /terms route that silently 500s."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1cb095a1-10e5-4519-903e-c06b100b873a
  modified: 2026-08-18T15:23:29.869Z
---

Verified 2026-08-18 while building [[project_marketing_site_odoo]] on window-solar-care.odoo.com
(Odoo 19, `website` module installed; `website_sale`/`website_crm`/`website_blog` are NOT).

**Creating a page in one call.** `website.page` `_inherits` `ir.ui.view`, so a single
`website.page.create` accepts the view fields inline: `url`, `name`, `key`, `type='qweb'`,
`mode='primary'`, `arch`, `is_published`, `website_indexed`, `website_meta_title`,
`website_meta_description`, `website_id`. No separate `ir.ui.view` create needed.

**Callable components.** A plain `ir.ui.view` with `type='qweb'` + a `key` is reachable as
`<t t-call="that.key"/>`. Render the caller's body inside a wrapper with `<t t-out="0"/>`
(`t-raw` is gone in Odoo 17+).

**★ `/terms` is a RESERVED route — a website.page at `/terms` returns "HTTP Error", not your page.**
Nothing warns you: the record saves fine, `is_published` is True, and the URL just serves Odoo's
error template (with HTTP **200**, so status-code checks miss it). Use `/terms-and-conditions`.
Root cause: `/terms` belongs to the **account** module — it renders the company's terms &
conditions and blows up when `res.company.terms_type = 'plain'` with no `invoice_terms_html`.
A `website.rewrite` 301 does NOT rescue it: a matching controller route wins over a rewrite.
Fixing it properly means flipping `terms_type` to `html` on the company, which changes what
prints on that company's invoices — so it is a business decision, not a website one.
Suspect the same for other short base routes if a page renders as an HTTP error while its
siblings work.

**Overriding header/footer without touching module views.** The website-specific footer is the
`website.footer_custom` view carrying `website_id = <site>` — write its `arch` (a
`<data inherit_id="website.layout">` block xpath-replacing `//div[@id='footer']`). For header pieces
(the CTA button, the phone text element), do what the web editor's COW does: create a NEW
`ir.ui.view` with the SAME key as the module view (`website.header_call_to_action`,
`website.header_text_element`), `website_id = <site>`, `mode='extension'`, `inherit_id` = the
matching `website.placeholder_header_*` view. Odoo prefers the website-specific one and the module
view stays clean through updates.

**Defaults that must be replaced on a fresh site:** the footer ships lorem ipsum ("a team of
passionate people"), the header CTA is a plum "Contact Us" → `/contactus`, the header phone is a
hardcoded `+1 555-555-5556` (NOT `res.company.phone`), and `website.logo` is an auto-generated SVG
text logo. Two `/` homepages exist (one global, one per-website) — write the one whose `website_id`
matches, that's the one served.

**Why:** each of these cost a debugging round trip; the `/terms` one fails silently.

**How to apply:** validate arch as XML locally before every write (a malformed arch is accepted at
the RPC layer and only explodes at render), and after any page write, curl the URL and grep for
`QWebException` / `HTTP Error` — a 200 alone does not mean your template rendered.
