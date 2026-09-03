---
name: project_wsc_domain_cutover
description: windowandsolarcare.com cutover from the broken WordPress site to the Odoo marketing site — real old slugs, the website.domain canonical trap, and the 760-334-5355 phone fix.
metadata:
  type: project
---

DJ decided 2026-09-03 to retire the broken WordPress `windowandsolarcare.com` and point that domain
(kept as PRIMARY, because Google Business Profile's website field uses it) at the Odoo marketing site.
Driver: the GBP is SUSPENDED over phone-number inconsistency. GBP is now **760-334-5355**; the linked
website must match.

**Phone.** The Odoo site was still carrying the old 855 toll-free everywhere. Fixed 2026-09-03 to
760-334-5355 (`PHONE_DISPLAY` / `PHONE_TEL` in `wsc_shared.py`, plus 3 hardcoded spots in
`run_build.py` and `wsc_pages_b.py`). Verified live: zero `855`/`2273` site-wide.

**★ The trap: Odoo `website.domain` was unset (False).** With it unset every page emits
`<link rel="canonical">` and `og:url` pointing at `window-solar-care.odoo.com`, and robots.txt
advertises the odoo.com sitemap. Cutting the domain over without setting it means Google keeps
indexing the odoo.com URLs and the 301s' link equity is thrown away by the canonical.
Set `website.domain` to the real domain **AT cutover, never before** — set early and canonicals point
at a host that doesn't resolve yet.

**★ Real old WP slugs (two of the guessed ones are 404).** `/our-pricing` and `/on-line-booking` do
NOT exist. The real ones are `/pricing_main/` and `/on-line-scheduling/`. Services live under
`/cleaning_services/<name>/`, not `/services/`. Other non-obvious ones: `/contacts/` (plural),
`/contact/` 301s to `/contact-us-copy/`, `/testimonials/` (→ new `/reviews`), `/faqs/`,
`/privacy-policy/` and `/terms/` (both A2P-relevant — must not 404). Full map is in the
2026-09-03 Web → Lead AGENT_MAIL entry.

**Why:** this cutover is GBP-reinstatement-critical and the canonical trap is invisible — the site
looks perfect while quietly telling Google it lives somewhere else.

**How to apply:** before any Odoo-website domain cutover, check `website.domain` on the `website`
record and plan to set it in the same change window as DNS/SSL. Never trust guessed WP slugs — crawl
the live old site. See [[feedback_odoo_verify_content_not_status]] and
[[feedback_verify_limits_before_declaring]].
