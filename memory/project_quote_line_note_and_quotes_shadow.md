---
name: project_quote_line_note_and_quotes_shadow
description: "Quote SO line = clean product-name service line + a display_type='line_note' line carrying the [Render Quote Tool] blob; quotes.py is dead (shadowed by dashboard.py)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-01T15:19:32.289Z
---

Two facts about the Render Quote Tool → sale.order flow (dashboard.py QUOTE_* section, ~L5769–6390), established 2026-08-01 when the job's SERVICE was showing the ugly `[Render Quote Tool] … __QUOTE_JSON__:{…}` blob.

**1. Quote line structure changed (blob moved OFF the priced line):**
A saved quote now writes TWO order lines:
- a **priced service line**: `product_id` (141 in_out / 103 outside), `price_unit`=total, `name` = the product's own display_name ("Windows In & Out - Full Service" / "Outside Windows And Screens") via `_quote_service_label(product_id)`. This is the ONLY thing shown as the service.
- a **note line** (`display_type='line_note'`, no product/price) whose `name` holds `[Render Quote Tool]` + human breakdown + `__QUOTE_JSON__:{counts,mode,difficulty}`. Carries DETECTION + ROUND-TRIP.

Helpers: `_quote_line_creates()` builds both (fresh-create paths); `_replace_quote_line(so_id, product_id, total, counts, mode, difficulty)` is confirmed-SO safe — soft-deletes prior priced lines by ZEROING qty/price (never unlink, Odoo blocks unlink on state=sale) and refreshes the existing note line IN PLACE so blobs don't accumulate on re-edit. `_parse_quote_json_from_line(line_name)` is UNCHANGED — readers scan ALL lines for the marker (now find it on the note line) and parse the same JSON; legacy name-fallback still there so old quotes parse. `_build_quote_acceptance_notes` derives mode from **product_id** (141→in_out / 103→outside), NOT the marker line (that line is filtered out of the priced set). Every priced-line display filters the note line out (New Job recent-jobs = qty>0 & price>0; invoicing = display_type=False; approve-notes = qty/subtotal>0; field job-detail keys off product_id). **Why:** DJ wanted a clean human service name with the breakdown in notes, fixed at the SOURCE (line name) not per-display. **How to apply:** any new reader that needs counts/difficulty must scan ALL lines (incl. note lines) for the marker; mode is recoverable from product_id alone. Legacy quotes migrated 2026-08-01 (5 SOs), migration idempotent.

**2. `routers/owner/quotes.py` is DEAD (shadowed).** It defines the SAME routes as dashboard.py (`/api/quote/save|list|get|update|push_to_workiz`) but main.py includes `owner_dashboard.router` FIRST (L237) before `owner_quotes.router` (L244), so dashboard.py WINS every quote route — same shadowing pattern as hemet.py. quotes.py also references the quote helpers via `from .shared import *`, but shared.py does NOT export them (they live in dashboard.py), so quotes.py would NameError if it ever ran. **How to apply:** edit quote logic in dashboard.py ONLY; patching quotes.py does nothing. Not deleted (needs DJ/lead ok — it's main.py wiring, lead's lane). Related: [[project_two_quote_pages_two_launchers]].
