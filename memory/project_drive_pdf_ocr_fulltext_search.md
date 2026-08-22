---
name: project_drive_pdf_ocr_fulltext_search
description: "Google Drive auto-OCRs uploaded PDFs/images and full-text-indexes their inner content — Vault search can find words printed inside scanned docs, not just titles"
metadata: 
  node_type: memory
  type: project
  originSessionId: ac2aeda5-6609-487b-94e3-132715d60520
---

**Google Drive automatically OCRs and full-text-indexes every PDF and image uploaded to it** — so search finds words printed INSIDE the file (including scanned/image-only PDFs), not just the filename or a Doc body.

**Verified 2026-06-28:** uploaded a scanned Farmers insurance card as `Saunders Pruis EOI.pdf` (no "Farmers" in the filename); a Drive API query `files.list(q="fullText contains 'Farmers'")` matched it within minutes → Drive OCR'd the scan and indexed the interior text. DJ's pre-existing Drive PDFs (homeowners/flood/BMW insurance, etc.) likewise return on interior-content searches.

**How to apply (Vault):**
- Keep imported attachments as their **original PDF/image** (full fidelity) — do NOT convert to Google Docs for searchability; Drive's background OCR already makes the original searchable.
- The Vault search UI should query the Drive API with **`q="fullText contains '<term>'"`** — this searches Doc bodies AND OCR'd PDF/image content AND titles in one shot. Add `and '<folder>' in parents` / `and trashed=false` as needed.
- Caveats: OCR indexing is background/async (minutes, sometimes longer after upload); OCR quality tracks scan clarity (clean print great, handwriting hit-or-miss). `fullText contains` is a substring/token match, not fuzzy.

Relates to [[project_vault_evernote_drive]] (the Evernote→Drive import) and the future Vault browse/search UI.
