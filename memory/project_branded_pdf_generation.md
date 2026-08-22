---
name: project_branded_pdf_generation
description: "How to generate firm-branded PDFs (Employee Handbook, etc.) — HTML in the firm template rendered to PDF via local Edge headless; firm navy blue ="
metadata: 
  node_type: memory
  type: project
  originSessionId: ac2aeda5-6609-487b-94e3-132715d60520
---

To make a firm-branded PDF document (e.g. the Employee Handbook, 2026-06-28):

**Brand:** DJ's preferred firm accent = **dark navy `#1e5aa8`** (NOT the lighter `#0090d0` used in the HR Job Description / Offer Letter template). DJ loves the **"blue bar"** section-header style from the WC Worksheet (`C:\Users\dj\wc_worksheet.html`): section titles are a **filled #1e5aa8 rectangle, white uppercase bold text, border-radius 4px, padding 6px 12px** (`background:#1e5aa8;color:#fff;...;print-color-adjust:exact`). White pages, the letterhead with logo + a navy `border-bottom`. Placeholders highlighted yellow (`.ph{background:#fff6d6}`), attorney-review notes in light callout boxes.

**Letterhead (matches Job Description / Offer Letter):** logo `https://wsc-field-assistant.onrender.com/static/brand/logo_window_solar_care.png`, contact line `windowandsolarcare@gmail.com · (855) 245-2273 · Hemet & Coachella Valley, CA`, navy bottom border.

**HTML → PDF (no Python PDF lib needed):** use local **Edge headless** —
`"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 --print-to-pdf="out.pdf" "file:///<abs html path>"`.
`--virtual-time-budget` lets the remote logo image load; `--no-pdf-header-footer` drops the browser URL/date header; CSS `@page{margin:.6in}` + `print-color-adjust:exact` keep colors. Use `<h2 class="pb">` with `break-before:page` for clean section page breaks.

**Employee Handbook source** lives at `scratchpad/handbook_branded.html` (12-page CA-compliant draft; content pulled from the uploaded draft PDF Odoo att 1723 via pypdf). Branded PDF uploaded to Drive (anyone-with-link) + emailed to Cheryl as a DRAFT. Reuse this HTML as the template for future branded company docs. See [[feedback_brand_dark_blue_accents]].
