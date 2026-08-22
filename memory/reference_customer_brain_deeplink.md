---
name: reference_customer_brain_deeplink
description: "URL format to deep-link straight into a specific customer's Customer Brain (research a customer from any page)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Deep-link to a customer's Customer Brain:**
`/owner/field?tab=customers&cust_q=<name>&cust_pid=<partner_id>`

The Customer Brain IS the "customers" tab of `field.html`. Handler `_custDeepLink()` (field.html) reads the params and calls `preloadCustomer(cust_q, cust_pid, true)` to auto-open that customer with a banner. Requires BOTH `cust_q` (name, for the search box) and `cust_pid` (res.partner id). `encodeURIComponent` the name.

**How to apply:** to add a "🧠 Research / Customer Brain" link on any card/list that has a partner_id, emit:
`'<a class="..." href="/owner/field?tab=customers&cust_q='+encodeURIComponent(name)+'&cust_pid='+pid+'" onclick="event.stopPropagation()">🧠 Customer Brain →</a>'`
Use `event.stopPropagation()` when the parent card already has its own onclick (else you fire both).

**Used by:** reactivation "View customer card"; Maintenance to Schedule cards (2026-07-10, `_brainLink(j)` in maintenance.html — added to upcoming/overdue/stranded; also patched submitted_jobs.py `/api/maintenance/stranded` to return `partner_id`).

★ **GOTCHA — two `/api/scheduled_sos` endpoints exist:** dashboard.py:7947 (`api_scheduled_sos(overdue=0)`) AND submitted_jobs.py:248. The **dashboard.py one is LIVE** (it's the only one accepting the `?overdue=1` param the Maintenance Upcoming/Overdue tabs use; dup-route, dashboard.py wins). The submitted_jobs one already had partner_id but is NOT the served route — that's why the button showed on the "In Workiz" tab (its own stranded endpoint) but NOT Upcoming/Overdue until dashboard.py:7947's job dict got `'partner_id'` added (2026-07-11, commit 0c98f70). When a maintenance list is missing a field, curl `/owner/api/scheduled_sos` and check the LIVE keys — don't trust the first matching function. See [[project_addschedule_gcal_picker]] for how deep-links survive the SW cache ([[project_sw_cache_stale_page]]).
