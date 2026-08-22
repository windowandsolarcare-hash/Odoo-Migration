---
name: project_hof_watcher_non_po_guard
description: HOF inbound watcher must validate a PDF is actually a purchase order before auto-creating a job+invoice — postcard art was misread as a PO (incident + fix)
metadata: 
  node_type: memory
  type: project
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

# HOF watcher: non-PO PDFs must NOT auto-create a job/invoice (incident 2026-06-18)

**Incident:** The Saunders Printing job tracker showed a bogus job **PO 038674 / INV 200240, "Plaque Postcards — 1 design", $22.50**. It was NOT a real PO — someone at the Hall emailed a **postcard art proof (the front image)**, not a purchase order. The HOF watcher force-fit it into the PO schema and auto-created a job + draft invoice.

**Root cause** (`routers/printing/watcher.py`, `check_hof_emails` + `_parse_po_with_claude`):
- `check_hof_emails()` searches Gmail `(UNSEEN FROM "@baseballhall.org")`, grabs the **first PDF attachment**, and sends it to Claude with a prompt that **presumed it was a PO** ("Extract from this … purchase order").
- The model, forced into the schema, grabbed the **card code `C38674`** printed on the artwork → returned `po_number="038674"`, one card `name="Unknown" qty=1`. The watcher then created the invoice (`_create_odoo_invoice`) and job with **zero validation**.
- Tell-tales: real POs are `043xxx–044xxx`; this was `038674` (a card code), card name "Unknown", qty 1, tiny $22.50, single card.

**Cleanup done (the "correct" delete — the app's Delete button only removes the tracker row and orphans the rest):**
1. Deleted draft invoice **11539 (INV 200240)** — was `draft`/`not_paid`/company 3 Saunders Printing → safe `account.move unlink`.
2. Deleted attachment **1656** (`PO_038674.pdf`, the postcard image stored on the invoice).
3. Removed job **`po-038674`** from `ir.config_parameter` key `saunders.printing.jobs` (JSON `{"jobs":[...]}`). 5 legit jobs remained.
4. Bogus Google Drive folder **`NBHOF PO 038674`** (id `1nTm7TytUZKnOnufHAV5H5hzAdTe3DLz0`, under NBHOF root `1wLCboY1FcXIYLF7_HBSc9VVI4WlO9qZh`) — Drive MCP has **no delete/trash tool**, so DJ trashes it manually.

**Fix shipped (commit 7c759a6, watcher.py):** ADDITIVE guard, did not touch the create path.
- `_parse_po_with_claude` prompt now asks the model to FIRST decide if the PDF is really a PO; if not, return `{"is_po": false}`. Also told not to treat a card code (C38674) as a PO number. Returns `is_po:true` on real POs.
- `check_hof_emails` after parse: skip + `_notify_dj('Not a Purchase Order (skipped)')` + mark seen + result `not_a_po` when ANY of: `parsed.get('is_po') is False`, po_number not a 6-digit number, or no card has a real name (name not ''/“unknown”). Only then does it create the invoice/job.

**Lesson:** any "parse an inbound doc → auto-create a financial record" automation MUST first validate the doc IS what it's assumed to be, and sanity-check extracted fields, before creating an invoice. A presumptive prompt + forced schema will hallucinate a record from the wrong attachment. Related: [[project_zoo_printing_automation]], [[session_jun14_saunders_printing]].
