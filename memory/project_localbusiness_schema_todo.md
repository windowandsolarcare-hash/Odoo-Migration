---
name: project_localbusiness_schema_todo
description: "TODO (DJ 2026-09-03): add LocalBusiness JSON-LD structured-data markup to the new Odoo website — NAP/hours/service-area/services block that feeds Google; must match GBP (phone 760-334-5355)."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-04T00:38:04.262Z
---

**DJ 2026-09-03 (note to discuss):** the marketing site currently has **no LocalBusiness structured data** — the hidden schema.org JSON-LD `<head>` block that tells Google the business name, phone, hours, service area, and services in machine-readable form. It's a cheap one-time add and it reinforces the Google Business Profile.

**What it is:** a `<script type="application/ld+json">` LocalBusiness (or HomeAndConstructionBusiness) object in the page head — `name`, `telephone`, `address`/`areaServed` (Hemet + Desert), `openingHours`, `url`, `sameAs` (GBP/Yelp), and a `hasOfferCatalog`/service list. Google reads it to corroborate the profile; it does NOT replace the GBP itself.

**Consistency rule (critical):** every field MUST match the corrected GBP — **phone = 760-334-5355** (NOT the old 5350 or the 855-245-2273 that was on the site/Yelp). NAP mismatch is what got the profile flagged; schema markup that disagrees would make it worse, not better.

**Open questions to settle with DJ before dispatching:**
1. Confirm this goes on the **new Odoo site** (Web owns the marketing site) — added via Odoo website custom `<head>` code / a snippet, post-cutover.
2. Is the actual gap the **website** (no schema), the **GBP** (missing fields), or **both**? DJ suspects both — verify GBP has service area/services/hours filled AND the site carries the schema.
3. Owner = **Web** (marketing site). Hand off via a brief once scope is confirmed.

**Status:** captured only — DJ wants to discuss further before we build. Do NOT dispatch to Web yet. Related: the [[project_calendly_retired]] cutover work + GBP suspension/NAP thread (3 phone numbers reconciled to 5355).
