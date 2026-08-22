---
name: reference_wsc_letterhead_brand
description: Window & Solar Care official branding for letterhead / branded PDFs
metadata: 
  node_type: memory
  type: reference
  originSessionId: d90ccd3d-e7c6-409d-a9dd-f3d770122077
---

**Window & Solar Care official brand assets (from Odoo `res.company` id=1, fetched 2026-07-03):**
- **Logo:** stored in the `logo` field of res.company id=1 (base64 PNG, ~171KB). Full color wordmark: "WINDOW & SOLAR Care" in blue with tagline "We don't just Clean, We Care!". Pull via `res.company.read([1],{'fields':['logo']})` → base64-decode. The render app (booking.py ~L94) uses it as `data:image/png;base64,` + logo.
- **Legal name:** Window & Solar Care, LLC (Odoo name = "Window and Solar Care"; entity is now a CA LLC — see [[project_wsc_llc_formation]]).
- **Business address:** 41995 Boardwalk, Ste. J, Palm Desert, CA 92211.
- **Company phone on Odoo:** (951) 972-6946. **BUT for the Twilio/business line DJ prefers (855) 245-2273** on customer/official docs — confirmed 2026-07-03 for the tenant-verification letter. Ask which he wants if unsure.
- **Email:** windowandsolarcare@gmail.com · **Web:** windowandsolarcare.com
- **Brand colors:** primary `#5e4766` (plum), secondary `#010101` (black).

**Letterhead recipe that worked (2026-07-03, Daniel Saunders IV tenant-verification letter):** HTML → Edge headless PDF (see [[project_branded_pdf_generation]]). Center the logo (height ~90px, it already contains the name so don't repeat it in text), thin plum rule under a small Arial contact line (name · address · phone · email), Georgia body 11.5pt, @page margin 0.7in 0.9in to keep to ONE page. Render: `msedge --headless=new --disable-gpu --user-data-dir=<temp> --print-to-pdf=<out> --no-pdf-header-footer file:///<abs html>`; must launch via PowerShell Start-Process -PassThru and Stop-Process the PID after the file appears (plain headless call HANGS when DJ's Edge is already open; a unique --user-data-dir is required). Count pages by regex-matching `/Type /Page` in the PDF bytes.
