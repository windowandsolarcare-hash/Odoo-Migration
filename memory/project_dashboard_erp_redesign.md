---
name: project_dashboard_erp_redesign
description: Owner dashboard (/owner/) redesigned ERP-style into ~10 top-level module cards (2026-06-16). Classic version preserved at /owner/classic.
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ wants the Render owner hub to look like a small-company ERP** (modules like an Odoo/SAP: Sales, CRM, Accounting, HR…) tailored to Window & Solar Care. Top-level = module cards; each drills into its apps (and may get sub-cards later).

## SHIPPED 2026-06-16 — `static/owner/index.html`
The hub ALREADY had a drill-in pattern (GROUPS data → group-card grid → `openGroup()` slide-in `group-screen` → app tiles). Redesign = restructured the `GROUPS` object + `_GROUP_ORDER`/`_GROUP_COLORS` into **10 module cards** (kept all the infra: voice modal, help overlay `HELP{}`/`showHelp` (no-ops on missing key), inline calculator `openInlineCalc`, pre-deposit live widget, primary Field Assistant card up top). Removed the 3 standalone cards (Hiring/Analytics/Quick Links) — folded into modules.

**Modules (key → name):** schedule "Schedule & Dispatch" (field/calendar/booking_requests/submitted_jobs/shift_review), customers "Customers" (field?tab=customers brain / analytics), sales "Sales & Quotes" (new-order/quote — New Job tile REMOVED 2026-06-16 per DJ: replaced by New Order front door; /owner/new-job route still exists as the engine New Order routes into), marketing "Marketing & Retention" (reactivation/hemet), money "Money" (pre-deposit/stale_sos), team "Team" (timeclock/hiring), myday "My Day" (myday/activities/notes/planner/chores), reports "Reports & Insights" (weekly_reports/analytics/deleted_jobs), assistant "Assistant" (Voice Command fn:openVoiceModal / quick), tools "Tools & Links" (workiz/odoo/calendly/maps/calc ext).

**Every classic tile/link carried over** (verified vs inventory). Only confirmed-working routes used (no dead links).

## PRESERVED — classic dashboard
- File `static/owner/index_classic.html` (verbatim copy of the pre-redesign hub).
- Live at **`/owner/classic`** (route `hub_classic()` in dashboard.py, ~L7225). Use to compare / restore.

## DEFERRED (DJ's 12 → shipped 10)
2 of the approved 12 cards left out for now (no owner-accessible pages yet — avoid empty cards): **📦 Supplies & Equipment** (PO/inventory) and **🏢 Businesses** (Saunders Printing /printing, Cheryl /cheryl multi-company switch). Add when wired.

## NEXT (DJ's plan)
Per-card deep-dive: each top-level card may get **sub-cards** that congregate apps (not just a flat app list). DJ will add/subtract/rename/reorder the top level first, then we design inside each card one at a time. Unsurfaced apps to consider adding: Payments view, SMS, PO (no standalone pages confirmed yet).
