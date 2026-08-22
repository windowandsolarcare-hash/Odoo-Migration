---
name: session_jun14_saunders_printing
description: "2026-06-14 Saunders Printing build — full scope of everything shipped (Zoo automation, invoice send, Drive filing, NBHOF email, pricing). Detail in project_zoo_printing_automation."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

2026-06-14 — big Saunders Printing (HOF postcard) session. App lives in **saunders-render-app** repo: `routers/printing/{jobs.py, watcher.py, zoo_watcher.py, drive_filer.py}` + `static/printing/index.html`. Server actions in Odoo. Deep detail + quirks in [[project_zoo_printing_automation]]. Card-type/pricing also there.

**WHAT SHIPPED (all live):**

1. **Zoo Printing email automation** — `zoo_watcher.py` (NEW). Reads UNSEEN `contact@zooprinting.com`, classifies estimate/confirmation/shipped, matches to tracker job by `Job Name: PO nnnnnn`, records each `-A/-B/-C` sub-order under `job['zoo']['suborders']`, advances steps (zoo_estimate/upload_zoo/order_shipped), stores UPS tracking. 1 PO splits into A/B/C sub-orders (one card each). Folded into the existing daily cron (`/printing/api/check-po` now runs HOF + Zoo). Manual: `/printing/api/check-zoo`.

2. **Invoice send to NBHOF — ONE-TAP APPROVE** — Odoo server action **1335** "Saunders: Email Invoice to HOF" (posts draft→posted, renders PDF, emails). Recipients **bhatton@baseballhall.org + retailinvoices@baseballhall.org**, from Dan Saunders<dan@scenicartprint.com>, + silent [COPY] to windowandsolarcare@gmail.com (separate mail.mail, no BCC in Odoo 19). Triggered by Send Invoice button → `/api/jobs/{id}/send-invoice`. Open-tracking pixel in NBHOF copy only → "✅ NBHOF opened" badge.

3. **Invoice render** — server action **1336** "Render Invoice PDF to Attachment" (renders draft-or-posted to ir.attachment, no post/email). Used by View Invoice + Drive filing.

4. **Per-card invoice format + PRODUCT-DRIVEN pricing** — one line item per card (`{code} — {Player} — {Type} Postcard`), price pulled from the product's `list_price` (no rate tables/date logic in code). Banding baked into product price (no banding line). Freight = table+interp (separate line, computed). July = DJ batch-updates plaque product prices (no code change). Dawson = last $0.18 card.

5. **Products created (company 3, $0.228):** C38659 ANDRE DAWSON (REVISED), C38668 TY COBB PHOTO, + C38660–C38680 (20 more photo cards). 3 card types: plaque/photo/local_view.

6. **Invoices:** scrapped bogus Ty Cobb 200237 (not a real PO; "1936"=induction year misread). Created+rebuilt Dawson **200238** ($227.27, per-card) for PO 043859.

7. **View PO / View Invoice buttons** — `/api/jobs/{id}/po.pdf` + `/invoice.pdf` stream PDFs in-app. PO PDF stored in Odoo (ir.attachment on the invoice) by watcher; `/api/jobs/{id}/import-po` backfills from IMAP.

8. **Google Drive filing** — `drive_filer.py` (NEW). Files PO + invoice + NBHOF email into the synced NBHOF folder `…/A Printing/Customers - Printing/NBHOF/NBHOF PO {num}/` (Drive folder ID **1wLCboY1FcXIYLF7_HBSc9VVI4WlO9qZh**). Uses OAuth USER token (GOOGLE_OAUTH_*); service account CAN'T write My Drive. Final (posted) invoice re-files to Drive on Send. UI 📁 Drive button. Backfilled all 4 tracked POs (043221/736/762/859).

9. **NBHOF email → Google Doc + in-app view** — Ben's PO cover email saved as a Google Doc in the PO Drive folder PROACTIVELY at PO processing (not gated on button). "📧 View NBHOF Email" opens fast in-app view (`/api/jobs/{id}/nbhof-email`, cached html) — no Google account picker. `/api/jobs/{id}/import-nbhof` backfills.

10. **check-zoo 502/worker-hang fix** — made check-po/check-zoo + heavy printing endpoints sync `def` (FastAPI threadpool, no event-loop block) + IMAP `timeout=30`.

**KEY IDs:** HOF partner 26947 (no email on partner — recipients hardcoded in SA 1335). Saunders company_id=3, journal 21, revenue acct 266. SA 1335 (email invoice), 1336 (render invoice). Daily cron crn-d84cabd8nd3s73cus3hg (0 6 * * *). NBHOF Drive folder 1wLCb….

**DEFERRED:** local-view card pricing ($0.15 vs $0.25) — DJ "deal with later" (see [[project_open_tasks]]). Twilio text-to-approve idea parked (needs A2P reg).
