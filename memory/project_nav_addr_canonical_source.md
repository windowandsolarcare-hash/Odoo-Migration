---
name: nav-addr-canonical-source
description: "App Navigate destinations come from _nav_by_partner → nav_addr (full \"street, city, state zip\" + coords); api_so_history carries it as of 2026-10-22. Trace the CONSUMER (navUrlForJob), not the producer."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-22T16:42:38.805Z
---

Every in-app **Navigate** destination must come from the canonical `_nav_by_partner(pids: list)` (`routers/owner/dashboard.py` ~4983) → returns `{partner_id(int): {lat, lon, addr}}` where `addr` is the FULL `"street, city, state zip"` assembled from STRUCTURED `res.partner` fields (`street, city, state_id, zip`) + `partner_latitude/longitude`. The dict key is `p['id']` (int), so callers must pass the int partner id (e.g. `so['partner_id'][0]`), not the `[id, name]` pair — a type mismatch makes `.get(pid)` miss and silently fall back (feature ships inert but looks done).

Client `navUrlForJob` (`_job_detail_panel.js:324`, `field.html:3687`) prefers `nav_addr` → `address` → coords.

**Root-cause class (fixed 2026-10-22):** a suffix-less street ("21 Chardonnay") misrouted ~20 min because the job payload carried only a street+city `address` with NO `nav_addr`/coords → Google mis-geocoded to a "Chardonnay Lane" elsewhere. `api_so_history` (`dashboard.py:5508`) was the owner gap (built `address = "street, city"`, no state/zip, no nav_addr); fixed by adding `nav_addr`+coords from `_nav_by_partner([partner_id])` and passing them through `openJobById` (`_job_detail_panel.js` ~287). Deploy 83fdb060; verified live body `nav_addr="21 Chardonnay, Rancho Mirage, California 92270"`.

**Method lesson:** a street-ish string is only a NAV bug if its CONSUMER is a Navigate destination (`navUrlForJob`). Two `pid[1]` display-name-parse helpers (`_find_invoiceable_sos_for_partner` in field.py + dashboard.py) LOOKED like nav offenders but only feed a record_check_payment **display** label — left them (rule 10/11). Trace the data flow to `navUrlForJob`, don't just fix where the string is built.

**How to apply:** any job/customer payload that can feed a Navigate button MUST carry `nav_addr` (full, WITH zip) + coords from `_nav_by_partner`; never geocode a display name / SO number. The `address` field may stay street+city for DISPLAY. Remember the field screen is dual-surfaced — see [[field-html-served-live-at-tech-field]].

**Tech surfaces (2026-10-22, same class):** `static/owner/field.html`@/tech/field `openJobById` needed the nav_addr passthrough (commit 5fcb8966), AND `static/tech/app.html` Navigate (`:808`) geocoded `activeJob.address||activeJob.name` (the SO NUMBER) and next-job (`:1120`) fell to `nxt.customer` (a NAME) — both fixed to prefer `nav_addr`→coords→address, dropping name/SO# (commit e5515cb5). The tech app's `jobs[]` come from `/owner/api/upcoming` (dashboard.py:6722→6853) which already sets `nav_addr`, passed through unreshaped → those were client-only.

**Verify method:** `static/*` is served PUBLICLY (no auth) → `curl https://wscare.pro/static/owner/field.html | grep <edit>` confirms a deployed CLIENT change from the live bytes. But `/owner/api/*` (incl. so_history) is auth-gated (401 w/o owner cookie) — do NOT forge it; prove server output by running `_nav_by_partner` against live Odoo + let the authenticated in-browser click close organically/via Operator. See [[feedback_cant_headlessly_seed_is_security_feature]].
