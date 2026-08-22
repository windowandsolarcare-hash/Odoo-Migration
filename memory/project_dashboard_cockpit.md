---
name: project_dashboard_cockpit
description: "The dashboard 'cockpit' — live worklist number cards at the top of the owner home (static/owner/index.html); DJ's daily 'glance, pick, go' command center. Step 1 toward an informational dashboard."
metadata:
  node_type: memory
  type: project
---

**★ DJ's vision (2026-07-08): the dashboard should be NUMBERS, not icons.** The old home was "a bunch of icons that do things — not informational." DJ wants a daily cockpit: a row of live numbers, each = a pile of work waiting, and tapping a number takes him STRAIGHT to the work. So instead of hunting through Booking / Reachout / Maintenance / My Day, he glances at the dashboard, sees where the piles are, and picks what to attack. Root pain: "don't want to look all over and remember." This is the North-Star "one place" ([[project_north_star_comprehensive_crm]]).

**✅ COCKPIT built 2026-07-08** — `static/owner/index.html`, `.cockpit` grid (3-col) of `.ck-card` number cards right under the universal search, above the app-icon groups. `loadCockpit()` Promise.all-fetches each count (all work WITHOUT access_code from the owner page) and each card is an `<a>` straight to the work:
1. 🔧 Maintenance to schedule → `/api/maintenance/stranded` `.count` → `/owner/maintenance` (DJ's "big miss" — jobs needing line items/tech/status)
2. 📣 Outreach to send → `/api/outreach/pipeline` `reeng_due+react_launch` → `/owner/outreach`
3. 🔁 Awaiting reply → `/api/outreach/nudge` `react_sent` → `/owner/reactivation`
4. 🆕 New bookings → `/api/myday` items where title~/booking/ → `/owner/myday`
5. ☀️ My Day → `/api/myday` items !waiting && !scheduled && date<=today → `/owner/myday`
6. 📅 Today's jobs → `/api/dashboard` `.schedule.count` → `/owner/command-center`
Verified live: 10 / 83 / 208 / 1 / 53 / 4. `.ck-n.hot` (red) when count>0 on maintenance+bookings.

**STILL TODO (blessed, not built): 💵 jobs to invoice and ⏰ skipped-to-reschedule cockpit cards** — no clean count source wired yet. To-invoice is PARTLY covered already by the existing **Pre-Deposit Check** panel lower on the dashboard (`/api/payroll/unpaid_jobs`). **NEXT (agreed): put the smart scheduler brain (scheduler.py route-tight best-day/best-slot, like Command Center/booking) into the MAINTENANCE next-job creation** — currently Phase 5 places the next maintenance job crudely by city-by-day (Tuesdays Hemet / Fridays Palm Springs); DJ wants our modern scheduling applied. Build it Render-side so Phase 5 calls it NOW (Workiz still live) AND it becomes the core of the Odoo-native flow when Workiz retires. ★ DJ's framing: maintenance = the FUNCTIONALITY of creating the next job for a recurring customer, NOT storing facts.
