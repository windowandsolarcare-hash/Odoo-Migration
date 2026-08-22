---
name: project_nbhof_watcher_reorder_po
description: "How the Saunders NBHOF PO watcher works, why it missed reorder POs, and the 2026-07-01 fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: d90ccd3d-e7c6-409d-a9dd-f3d770122077
---

**The NBHOF PO watcher = `routers/printing/watcher.py` in repo `windowandsolarcare-hash/saunders-render-app`** (deploys to wsc-field-assistant on Render). Push to main = deploy. Key facts:

- **Trigger:** `GET /printing/api/check-po` (jobs.py), hit by ONE daily cron. Runs `check_hof_emails()` + `zoo_watcher.check_zoo_emails()`. Safe to curl manually to force a run.
- **Mailbox:** logs into IMAP `dan@scenicartprint.com` (env `GMAIL_SCENIC_APP_PASSWORD`), searches `(UNSEEN FROM "@baseballhall.org")` in INBOX. All Saunders mail also forwards to windowandsolarcare@gmail.com (I CAN read that via Gmail MCP; I canNOT read dan@scenicartprint.com or download attachments via MCP).
- **UNSEEN gate — FIXED 2026-07-01 (commit b0185f9).** Was: only searched `UNSEEN` mail, so a PO opened before the daily run got marked read and skipped FOREVER. Now searches `(FROM "@baseballhall.org" SINCE <30d ago>)` (read+unread) and dedups by email **Message-ID** tracked in `blob['processed_msgids']` — a read PO is still caught, and anything already handled is skipped silently (no re-parse/re-notify). Helper `_seen_and_record()` marks \Seen AND records the msgid at every terminal branch; unexpected per-msg errors still don't record (so they retry). One-time: first run after deploy re-examines up to 30d of mail once (already-invoiced POs hit the po_number dedup; old proof emails may re-notify once) then settles.
- **Pipeline:** find PDF → `_parse_po_with_claude(pdf, email_body)` (Sonnet, PDF as document block) → guard → `_calc_total` → `_create_odoo_invoice` (draft, NO invoice_date so it dates on SEND) → `_save_po_attachment` → Drive filing → append job to blob `ir.config_parameter` key `saunders.printing.jobs` → notify DJ.
- **Invoice constants:** company_id=3, journal_id=21, partner_id(HOF)=26947, revenue account=266, Net30 term=4, invoice number = `_next_invoice_num()` (max numeric name +1). Cards priced from product `list_price` by `default_code` (C-code); ALL plaque = $0.228, local view = $0.25. **Freight is COMPUTED from total qty** via `FREIGHT_TABLE` + `_calc_freight` (interpolated; ≥32k pieces caps at $592.85) — NOT read off the PO.

**Why reorders were missed (root cause, discovered 2026-07-01 on PO 044322):** the parser prompt only described the ITEMIZED PO format (code + name + qty per line). NBHOF **reorder** POs are a plain **name list + one grand total, no codes, no per-card qty** (e.g. "36,000 total, here is the list:" + 36 names). Claude couldn't extract code/name/qty rows → returned no usable cards → guard rejected it. The skip message ALWAYS said "not a purchase order" even though it's a catch-all for THREE different failures (is_po false / bad 6-digit PO# / no card names) — so the label misled us into thinking Claude judged the doc, when really the card extraction failed. **The PDF literally said "PURCHASE ORDER" across the top — recognition wasn't the problem, format extraction was.**

**Fix (2026-07-01, commit 629616):** (1) parser now accepts `email_text` and gets the EMAIL BODY too (reorder details live in Ben's body, not just the PDF); (2) prompt teaches BOTH formats — itemized AND reorder (name list + grand total, codes optional) — and returns `total_qty`; (3) if cards lack per-card qty but a grand total is given, `check_hof_emails` splits it evenly across named cards (remainder one-per to the first few); (4) code-less cards price at the standard type rate via new `_type_rate`/`_card_price` (all plaque $0.228) instead of $0; (5) the blanket "not a purchase order" skip is replaced with the SPECIFIC failing reason.

**PO 044322 (the trigger case):** reorder, 36 plaque postcards @ 1,000 = 36,000, $0.228 = $8,208 cards + $592.85 freight = **$8,800.85**. I entered it manually as **draft invoice 200241** (ref "PO 044322", using Ben's card names, no codes — auto-matching 36 nicknames to formal catalog names like "HENRY LOUIS GEHRIG" risked wrong cards) + added it to the blob tracker. DJ sends HOF invoices himself AFTER the job ships — never auto-send.

**Also fixed same session:** PO 044303 had 3 draft invoices; consolidated onto numbered invoice **200240** (added the missing $100 back-design line → $4,071.17: 4 designs + 4 backs @ $25 + freight $323.17), deleted the two junk drafts, synced blob amount. See [[project_saunders_invoice_send_view]].
