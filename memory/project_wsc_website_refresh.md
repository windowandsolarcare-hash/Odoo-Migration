---
name: project_wsc_website_refresh
description: "Main marketing site (windowandsolarcare.com, Odoo website_id 1) structure + the 2026-10-08 homepage/CTA refresh DJ ordered. Which view is the live home, where the 'pricing page' is, the shared Request-a-Quote form snippet, hero image attachment, and the Odoo-qweb entity gotcha."
metadata:
  node_type: memory
  type: project
  originSessionId: f76e5ab2-b974-4483-8681-cf3a298418b6
  modified: 2026-10-09T07:10:02.804Z
---

**Site view map (Odoo ir.ui.view, website_id 1; edit arch via `ex('ir.ui.view','write',[[id],{'arch':...}])`, verify by CONTENT):**
- **LIVE homepage = view 1559** (`website.homepage`, site-specific, archlen ~4.9k). View 1551 (`website.homepage`, site=False, ~180 bytes) is a STUB — do NOT edit it.
- **"Pricing page" = `/quote` = view 3839 (`wsc.quote`)** — the "What will it cost?" pane-counting price CALCULATOR the hero's "See your price" links to. DJ calls it "the counting pane prices" page. There is NO separate /pricing page.
- Shared snippets (site=False, t-call'd): `wsc.page`(3832 wrapper), `wsc.topbar`(3827), `wsc.trust`(3853 Thumbtack-stats strip), `wsc.service_grid`(3830), `wsc.guarantees`(3829), `wsc.areas`(3831), `wsc.cta`(3828), `wsc.styles`(3826 CSS), `wsc.schema`(3854 JSON-LD areaServed).
- Service pages: `/services`(3833) + subs incl. `/services/window-cleaning`=**3835** ("Window & Screen Cleaning").

**2026-10-08 refresh SHIPPED (DJ's 8-note batch; #2 chatbot deferred):**
1. **Hero photo** — Del Webb image uploaded to Odoo as **ir.attachment 3713** (`/web/image/3713`, public), set as `.wsc .hero` background in `wsc.styles` 3826 (navy gradient overlay over the photo for white-text contrast).
3. **Hemet** — DJ STILL serves Hemet; only reworded the brand line. `wsc.topbar` 3827 tagline → **"Serving the Coachella Valley & select Riverside County locations"** (the /dw wording). Hemet KEPT in `wsc.areas` city list + `wsc.schema` areaServed (still discoverable/served).
4. **Book Now** (→ `https://wscare.pro/book/`) — added in homepage hero (1559) before "See your price", AND on /quote (3839) phead above the calculator.
5. **Pills removed** — the homepage `<ul class="chips">` (30-Day Rain Guarantee · Licensed & insured · No contracts · Pay after service · Free quotes over the phone) deleted from 1559. (The `wsc.trust` Thumbtack-stats strip is a DIFFERENT element — kept.)
6. **Request-a-Quote form** — built ONCE as shared snippet **`wsc.quote_form` = view 3858** (site=False), t-call'd on BOTH home (1559, before wsc.areas) and /quote (3839, bottom). Posts to `/website/form/mail.mail` → emails **windowandsolarcare@gmail.com**, subject "QUOTE REQUEST (website) - windowandsolarcare.com", fields "QUOTE REQUEST - name/phone/details" + email_from. Self-wired inline CDATA submit (same pattern as careers). **★ Unlike the careers page, `website_form_signature` IS injected for a t-call'd snippet form** — verified live (signature present, test submit mail id 1183, HTTP 200). Inline success message, no redirect.
7. **Screen demo video** — inline `<video controls>` on the window-cleaning page (3835), src `https://wscare.pro/static/dw/screen-machine-demo.mp4` (cross-origin media plays fine, no CORS needed), placed by the "we wet wash the screens" bullet.
8. **Cheryl review** — removed in TWO places: /reviews (view 3841, done 2026-09-18) AND the homepage 1559 testimonials grid (a second "Cheryl J." quote was still there — caught + removed 2026-10-08; grid now shows Bill W. + Kay M.). Both verified 0 live.

**Thousand Palms / home address REMOVED from public site (2026-10-09, DJ "remove all references"):** The home address was leaking publicly in THREE views — footer `website.footer_custom` (2337, a "Thousand Palms, CA" line), `wsc.areas` (3831, a `<li>Thousand Palms</li>` served-city), and **`wsc.schema` (3854) JSON-LD** which exposed the FULL home PostalAddress (`32569 San Miguelito Dr, Thousand Palms, CA 92276`) as the business `address` AND an areaServed city. Removed the whole PostalAddress block (service-area biz → address optional, areaServed covers geo) + both city refs. Verified 0 of "Thousand Palms"/"San Miguelito"/"92276" across all views + live pages. Enforces [[project_wsc_address_do_not_publish]] (home/registered address NEVER on a public listing). /dw was already clean. ⚠ App repo (wscare.pro) + external directories (MapQuest #430179537 etc.) may still carry it — swept separately.

**★ GOTCHA — Odoo qweb XML rejects named HTML entities** (`&mdash;`, `&nbsp;`, etc. → "Entity 'mdash' not defined" on write). Use the literal unicode char (— ) or a numeric entity (`&#8212;`). Only `&amp; &lt; &gt; &quot; &apos;` are safe.

**DEFERRED — #2 avatar + chatbox** (on-site AI assistant greeting/interacting): a real mini-project, needs Lead (architecture) + Specialists (backend, wire to the app's existing assistant). Scope with DJ before building: what it does (answer Qs / book / quote), avatar style, build path.

Related: [[project_careers_page]], [[project_del_webb_landing_page]], [[project_gbp_suspension_appeal]] (Hemet/NAP), [[feedback_odoo_verify_content_not_status]].
