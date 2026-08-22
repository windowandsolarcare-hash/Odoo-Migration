---
name: project_new_order_frontdoor
description: "New Order — single front door (/owner/new-order) that asks order type and routes to reactivation Book sheet or New Job, with open-reactivation auto-detect. Read before touching order routing / booking entry."
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

**Shipped 2026-06-15.** DJ wanted ONE place to go for any booking so he never has to remember "reactivation text → Sent tab" vs "new/repeat → New Job." Thin router that reuses the already-unified flows ([[project_shared_scheduler]]).

## Where
- `routers/owner/order.py` (prefix /owner): serves `/new-order` + `GET /api/order/check-reactivation?partner_id=` (auto-detect).
- `static/owner/new_order.html`: the page.
- Registered in main.py (`owner_order`). Tools tile added to `static/owner/index.html` GROUPS.tools (first card, 🧭 "New Order") + a `neworder` HELP entry.

## Flow
Asks "What kind of order?" → 3 choices:
- **Reactivation reply** → loads `/api/reactivation/sent`, client-side filter, tap → `location.href='/owner/reactivation?book_lead=<lead_id>'`.
- **Existing customer** → `/api/intake/search` → tap → `/api/order/check-reactivation` → if open lead, warn sheet ("Book as reactivation?" → reactivation deep-link) else → `/owner/new-job?contact=<id>`.
- **Brand-new** → `/owner/new-job?new=1`.

**Auto-detect** = the key feature: even if DJ picks the "wrong" door, `check-reactivation` (crm.lead stage 5 + graveyard uuid, partner_id OR x_odoo_contact_id) catches an open reactivation and offers to route correctly. So nothing gets mishandled.

## Deep-link receivers (added this session)
- `new_job.html` init: `?new=1` → `toggleNewCust()`; `?contact=<id>` → `selectContact(id)`.
- `reactivation.html` init IIFE: `?book_lead=<id>` → switch to Sent view → `await loadSent()` → `openLead(id)` → `showBookSheet()`. (openLead sets selectedLead + shows view-sent-detail; showBookSheet from [[project_shared_scheduler]] b2.)

## NOTE
Repeat + New both funnel to New Job (which already does search-or-create) — the only real fork is reactivation-vs-newjob. DJ approved "thin router + auto-detect" (not a full single-app merge — that's a possible later step).
