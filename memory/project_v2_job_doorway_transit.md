---
name: project_v2_job_doorway_transit
description: "Job-detail doorways now point at v2_job.html (fast host), not v2_field.html — plus the two booking_requests.py shadow-twin trap"
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-27T18:49:00.562Z
---

**Field-Day transit fix (2026-09-27):** DJ's #1 pain was slow transit into job detail (v2_field.html is 7k+
lines + eager Leaflet). Fix = a tiny **`v2_job.html`** host (lazy-Leaflet, hosts `_job_detail_panel.js`) that
opens fast. **Every "open a job" DOORWAY now points at `v2_job.html?open_so=...` instead of
`v2_field.html?open_so=...`** — ALL params preserved (open_so, date_raw, rs_date, rs_win, rs, reserve,
inplace=1). The doorway transform is a pure filename swap (`v2_field.html?open_so` → `v2_job.html?open_so`);
params follow the `?` so they carry over untouched.

**Who repointed what (clean file-owner split, no cross-owner edits):**
- Specialists built `v2_job.html` + lazy-Leaflet + the top-5 (v2_command / v2_myday / v2_calendar /
  v2_customers / v2_inbox) + owns `v2_field.html`.
- **Builder-2 repointed 16 files / 19 doorways** (one Git Data API commit 5d64461, deploy live 2026-09-27):
  9 screens (v2_activities, v2_analytics, v2_maint_comms, v2_maint_advance×2, v2_callcard, v2_stats,
  v2_shift_review, v2_outreach, v2_waiting) + 6 routers (routers/booking.py×2, routers/owner/booking_requests.py,
  reminders.py, payments.py, followups.py, current_job.py×2) + static/owner/wsc_thread.js.
- [1d0f11] owns its own-file lines: `feed_live.py` (4) + `specialist_reschedule/billing/paywatch` (4).
- V1 `field.html` and non-doorway `v2_field` COMMENTS were left as-is (surgical; scope = doorway LINKS only).

**★ SHADOW-TWIN TRAP — there are TWO `booking_requests.py`:** `routers/booking_requests.py` (~299 lines) AND
`routers/owner/booking_requests.py` (~437 lines). **main.py (~:971) serves the OWNER one** — the doorway is
in `routers/owner/booking_requests.py:360`. When editing/pushing "booking_requests.py", ALWAYS confirm the
`routers/owner/` path — a Git Data commit or `gh api` PUT to `routers/booking_requests.py` would edit the
dead shadow twin (change lands, nothing happens). Same route-shadowing class as dashboard.py↔hemet.py and
the /owner/ask twin. See the PAIRED-CHANGES / route-shadowing rule in CLAUDE.md.

**How to apply:** any NEW "open this job" link (screen or router card) → emit `v2_job.html?open_so=<so_id>`
(+ whatever params), NOT `v2_field.html`. Verify a doorway change by CONTENT of the live-served file
(curl + grep `v2_job.html?open_so`, 0 leftover `v2_field?open_so`), per [[feedback_odoo_verify_content_not_status]].
Related: [[project_two_quote_pages_two_launchers]], [[project_field_deeplink_return_latch]].
