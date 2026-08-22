---
name: project_marketing_site_odoo
description: "The public marketing site lives in Odoo's website module (website id 1, company 1) and is built by a re-runnable script — shared views, never per-page copies."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1cb095a1-10e5-4519-903e-c06b100b873a
  modified: 2026-08-18T13:49:50.232Z
---

The rebuilt **public marketing site** (replacing the slow WordPress windowandsolarcare.com) lives in
**Odoo's website module**, website **id 1**, company 1. Target domain **wscare.pro** (Lead owns DNS).
Owned by the **Web** session — see [[project_agent_mail_channel]] for the session roster.

**Structure — ONE source per repeated thing, never N copies** (this is the whole architecture; see
[[feedback_question_when_big_picture_wrong]]):
- `wsc.styles` — the entire stylesheet, inlined once per page (no extra request, zero custom JS).
- `wsc.page` — the wrapper every page `t-call`s; it calls `website.layout`, then styles, topbar,
  `<t t-out="0"/>` (the page body), and the CTA band.
- `wsc.topbar` / `wsc.cta` / `wsc.guarantees` / `wsc.service_grid` / `wsc.areas` — the repeated bands.
- Pages are `website.page` records whose arch is ONLY the page body wrapped in `t-call="wsc.page"`.

Build scripts (scratchpad, re-runnable and idempotent): `wsc_shared.py` (components + CSS + footer +
header overrides), `wsc_pages_a.py` (home, services hub, 5 service pages), `wsc_pages_b.py` (quote,
what-to-expect, about, FAQ, reviews, gallery, contact, service-areas, privacy, terms), `deploy.py`
(upsert helpers + an XML validity gate), `run_build.py` (`components|header|logo|pages|menus|all`).

**Why:** the WordPress site was slow from platform bloat; the fix is a lean stack AND a structure
where a change to the CTA or the city list happens in exactly one place.

**How to apply:** to change anything site-wide (phone, cities, CTA copy, colors), edit the constant
or component in `wsc_shared.py` and re-run — do NOT edit 17 page bodies. Content was carried over
verbatim from the old site; the solar flagship copy is word-for-word per the brief.
