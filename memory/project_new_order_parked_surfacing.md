---
name: project_new_order_parked_surfacing
description: "New Order = 2 buttons (Existing/New). Existing surfaces a customer's PARKED campaign job (reactivation OR re-engagement) and books it. Built 2026-07-03."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# New Order redesign — surface a parked campaign job (2026-07-03)

**Goal:** DJ shouldn't pre-classify orders. New Order front door (`static/owner/new_order.html`) is now **2 buttons: Existing / New** (Existing shown first). New = unchanged (`/owner/new-job?new=1`). Existing = search by name → on tap, check for a PARKED campaign job → surface it → "use it" runs the parked booking; else drop into New Job's 10-job reuse list. Real already-scheduled jobs are NOT surfaced (Customer Brain handles reschedules). The old "Reactivation reply" backlog-browse button is gone.

## How detection works — `GET /owner/api/order/check-parked?partner_id=` (routers/owner/order.py)
Returns `{parked, reactivation, reengagement}`:
- **reactivation** = open `crm.lead` (stage 5 "Attempt 1 - Sent") with `x_workiz_graveyard_uuid` → `{lead_id, graveyard_uuid, price_list, texted}`.
- **reengagement** = `res.partner.x_reengagement_workiz_uuid` (falls back to parent if a property was picked) → `{partner_id, uuid, texted}`.
A customer can have BOTH (verified: Jose Bugarin 23206). new_order.html shows one "Use it" button per parked job + "No — start a new job".

## ★ The parked UUIDs (DJ: can't touch a Workiz job without its UUID)
- Reactivation: `crm.lead.x_workiz_graveyard_uuid` (existing).
- Re-engagement: **`res.partner.x_reengagement_workiz_uuid`** — ALREADY written at LAUNCH by `api_followup_launch` (reactivation.py), alongside `x_studio_last_followup_sent` (the date). I initially thought it wasn't stored; it is. So NO new field, NO launch change, NO backfill were needed (5 customers were already parked: Jose Bugarin/Kenneth Theriault/Nanette Smalley/Pam&Rick Ortega/Sharon Soper). Cleared on book/decline. See [[project_reengagement_vs_reactivation]].

## Booking
- Reactivation: existing `/owner/reactivation?book_lead=<lead_id>` (unchanged).
- Re-engagement: `/owner/reactivation?book_reengage=<partner_id>` → the SAME reactivation Book sheet, generalized with a `BOOK_MODE` flag (reactivation.html). The `?book_reengage` init branch loads `/api/reengagement/parked`, opens the sheet, and `doBook` posts to `/api/reengagement/book`. Reuses the whole sheet incl. `/api/reactivation/suggest?partner_id=` (already partner-keyed) for slots.
- New endpoints in `routers/owner/reactivation.py` (cloned from `api_reactivation_book`): `/api/reengagement/parked` (read), `/api/reengagement/book` (convert the Workiz job in place via workiz_get/workiz_post, then CLEAR `x_reengagement_workiz_uuid` instead of closing a crm.lead; Phase-5 "Add tech + line items" activity uses `res_model_id=90` = res.partner ir.model id), `/api/reengagement/decline` (clear field).

## Verified 2026-07-03 (API-only, render logs, all 200 no 500s)
check-parked (both/one/none), reengagement/parked read, book validation + read-UUID + Workiz-verify + field-clear (via a disposable ZZ TEST partner, cleaned up), pages render 2 buttons. The successful Workiz *convert* itself was NOT live-run (would spawn a Phase-3 stray SO) but is byte-identical to the proven `api_reactivation_book`.

## Multi-company customer scoping (DJ, 2026-07-03)
`/api/intake/search` (new_job.py — the customer picker for New Order AND New Job) now filters `['company_id','in',[1,False]]`. ★ GOTCHA: W&SC customers are NOT tagged company 1 — they're mostly `company_id=False` (shared): distribution = 103 tagged company 1, **1566 shared (False)**, 314 Cheryl Johnson (2), 1 Saunders (3). The 5 parked re-engagement customers are all False. So filter `[1, False]` (company 1 OR shared), NOT `=1` (which would hide ~all real W&SC customers). Excludes Cheryl(2)/Saunders(3). Commit 59ec38e. Ties to CLAUDE.md rule #8.
DJ (2026-07-03): "so we do not run into this problem again." So I AUDITED all customer-facing res.partner name/phone searches and added the same `['company_id','in',[1,False]]` leaf to: new_job.py intake/search (59ec38e), dashboard.py `search_customers` / Customer Brain (97419ee), notes.py Vault `search_customer` (97718b3), payments.py customer name lookup (e9d482a). Skipped: supplier searches (supplier_rank>0 = vendors, not customers) and calendar.py (returns SOs, and Cheryl has no W&SC SOs). res.partner is NOT auto-isolated (DJ's user spans all 3 companies) so each search needs the leaf — codified as a permanent rule in CLAUDE.md rule #8.

## Commits / caveats
reactivation.py dce8e9b · order.py 76f0fa5 · reactivation.html c0ccaed · new_order.html f1a2c54.
★ Update 2026-07-04 (commit efd45f4): New Order is now **3 buttons** — DJ added a 3rd, **"Booking request"** (📥), which routes to `/owner/booking_requests` (`pickType('booking')`). So the front door = Existing / New / Booking request. Workiz cutover: both book flows convert a Workiz job today → re-point to the Odoo record post-Workiz. Button order Existing-first (my call; flip if DJ wants New first). ★ LANDMINE: a stray `C:\Users\dj\calendar.py` (fastapi content) shadows stdlib `calendar` and breaks any python script importing `requests` when run from C:\Users\dj — run such scripts from the scratchpad dir, and it should probably be deleted.
