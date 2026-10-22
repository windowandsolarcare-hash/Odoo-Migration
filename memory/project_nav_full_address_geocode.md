---
name: project_nav_full_address_geocode
description: "Field Navigate/maps links must build the Google Maps destination from nav_addr (FULL 'street, city, state zip' via _nav_by_partner) -> coords -> display address, NEVER a partner display-NAME parse, SO number, or customer name. A suffix-less street like '21 Chardonnay' geocodes to the wrong place (e.g. 'Chardonnay Lane' 20 min away) without the zip. Fixed 2026-10-22 across owner + tech surfaces."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-22T16:39:48.134Z
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
---

**Problem (DJ live-ops 2026-10-22, via Operator):** DJ tapped Navigate to a scheduled job and Google Maps sent him ~20 min away to "Chardonnay Lane" instead of 21 Chardonnay, Rancho Mirage. The Odoo data was COMPLETE (contact 22971 + property 24093 both had street `21 Chardonnay`, city `Rancho Mirage`, state California, zip `92270`, coords 33.807/-116.414). The bug was that nav builders passed a zip-less / name-derived destination.

**Canonical source: `_nav_by_partner(pids)` (dashboard.py:4983).** Batch-reads street/city/state_id/zip + lat/lon, returns `{pid: {lat, lon, addr}}` where `addr = 'street, city, STATE zip'` (state is the FULL name from `state_id[1]` minus ' (US)', e.g. "California" not "CA" — geocodes fine, the zip is the disambiguator). This is the ONE source every nav destination should use. `tool_navigate_to` (voice, dashboard.py:1198) already builds the full address directly and was never affected.

**Client rule:** `navUrlForJob(j)` (field.html:3685, _job_detail_panel.js:324, field.html-twin) = `dest = j.nav_addr || j.address` then coords fallback. So the job payload MUST carry a full `nav_addr`; a zip-less `address` with no `nav_addr` is the failure mode.

**Root cause + fix (all shipped 2026-10-22, §15):**
- **Owner deep-link path:** `api_so_history` (dashboard.py:5395) read only `street,city` (no zip) and returned NO `nav_addr`/coords; `openJobById` (_job_detail_panel.js:287) built the job with `address` only. A deep-link open (`v2_job.html?open_so=`) misses the host schedule and uses so_history → zip-less nav. FIX: so_history adds `nav_addr`(from `_nav_by_partner([partner_id])`, falls back to street+city) + `nav_lat`/`nav_lon`; openJobById passes them through. Commits dash `45bb7819`, panel `83fdb060`.
- **Tech surfaces:** `/tech/field` serves `static/owner/field.html` (tech/jobs.py:16) whose `openJobById` (field.html:4676 → so_history) also dropped nav_addr; `static/tech/app.html` `:808` geocoded `activeJob.address||activeJob.name` (the SO NUMBER!) and `:1120` fell to `nxt.customer` (a NAME). FIX (client-only — so_history now supplies nav_addr, and `/owner/api/upcoming` [dashboard.py:6722→6853, feeds the tech app's jobs[]] already set nav_addr): field.html openJobById passthrough; tech app :808/:1120 prefer nav_addr→coords→address and DROP name/SO#. Commits field.html `5fcb8966`, tech/app.html `e5515cb5`. Tech reaches so_history (proven: techs use /tech/field in prod).

**NOT nav offenders (firsthand-confirmed, left per rule 10/11):** `_find_invoiceable_sos_for_partner` ×2 (field.py:3283 / dashboard.py:5012) name-parse `pid[1]` to a street-only `address`, but that feeds ONLY the `record_check_payment` CLARIFY display text — never a Navigate link. Also the panel post-sync merge (_job_detail_panel.js:875, field.html:3384) preserves nav fields, and `openHistModal` (field.html:4933) is display-only. The host-schedule nav path (dashboard.py 5291/6853/9518/11818 = today/upcoming/list/past) already set nav_addr and was correct.

**Verification pattern (useful):** the app's `static/*` files are served PUBLICLY (no auth) — so you can `curl https://wscare.pro/static/owner/field.html` and grep for an edit to confirm a deployed CLIENT change from the live bytes. But `/owner/api/so_history` (and all `/owner/api/*`) are auth-gated (401 without the owner cookie) — do NOT forge the cookie to test; prove server output by running `_nav_by_partner` against live Odoo (same function so_history calls) + let the authenticated in-browser click close organically / via Operator. See [[feedback_cant_headlessly_seed_is_security_feature]].

**Parked follow-ups (trigger = next touch of each file):** tech/app.html :808 no-address case is a safe no-op (no showToast in that file) — wire a real "No address" message next tech/app.html touch; add `||activeJob.nav_addr` to field.html openNav guard (:3698) next field.html touch (latent: nav_addr-without-address doesn't happen today).
