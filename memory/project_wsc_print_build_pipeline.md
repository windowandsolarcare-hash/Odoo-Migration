---
name: project_wsc_print_build_pipeline
description: The W&SC print pipeline — _design_build.py turns .dc.html artboards into guide-line proofs and Zoo-ready CMYK press PDFs. Exact specs, tools and paths.
metadata:
  type: project
---

One script builds every W&SC print deliverable:
**`design/view-ad/_design_build.py`** — `dev` (guide proofs) · `clean` (clean PNGs + press PDFs) · `both`.
Same artboards feed both modes, so a proof and a press file can never disagree. See
[[feedback_design_end_to_end_workflow]] for when DJ wants which.

## The piece (postcard, EDDM)
| | |
|---|---|
| Trim | **9 x 6.5 in** (Zoo's EDDM size — [[project_eddm_mailing_rules]]) |
| Bleed | .125 all round -> artwork 9.25 x 6.75 in |
| Artboard | **2775 x 2025 px** @ 300 DPI |
| Trim line | 37.5 px in from each artboard edge |
| Safe margin | 112.5 px in (.25 in inside trim) |
| Press page | 10 x 7.5 in — the extra half inch is where crop marks live |
| Marks | .25 in long, .25 pt, **registration** (1,1,1,1) so they hit every plate |
| Colour | RGB -> CMYK via **US Web Coated (SWOP) v2**, perceptual |

## Tools on DJ's machine (all verified working)
- **Chrome** `C:\Program Files\Google\Chrome\Application\chrome.exe` — `--headless=new --screenshot`
  with `--window-size=W,H`; the window size IS the PNG size, so pass the artboard px and you get a
  true 300 DPI render. Add `--virtual-time-budget=12000` or Google Fonts may not land.
- **PyMuPDF (fitz) 1.27** — page, CMYK pixmap, crop marks, `set_trimbox` / `set_bleedbox`.
- **Pillow + ImageCms** — the ICC separation.
- **`C:\Windows\System32\spool\drivers\color\USWebCoatedSWOP.icc`** — the real SWOP profile.
- A `.dc.html` will NOT open standalone (its `support.js` is injected by the canvas editor); the
  script lifts `<helmet>` into `<head>` and the rest into `<body>`, serves it on 127.0.0.1:8731
  (the browser tooling refuses `file://`), then shoots it.

## Verify by content, never by assumption
After every build the script's output is checked by READING the PDFs back: MediaBox / TrimBox /
BleedBox in inches, image px, placed size -> computed DPI, and that `/DeviceCMYK` is present and
`/DeviceRGB` is absent. Do this every time — it caught nothing yet because it is run every time.

## Gotcha that bit once
Front A's headline box was 1800 px for a line measuring ~1750. A tiny render-width difference made
`CLEAN YOUR WINDOWS` wrap to two lines — a visible change to an APPROVED design. Box widened to
2150. **Leave real slack around a headline that must hold one line**, and compare a re-render to the
approved artwork before shipping it.

## * THE LOGO — what the master is, and the tagline rule (settled 2026-09-12 with Lead)
- **Master: `<Documents>\Business\A Window and Solar Care\Website\Logo\Logo-Org.png` — 2700 x 1110
  RGBA, transparent, NO tagline.** This is the real master and it is plenty for print.
- **There is NO vector logo and there probably never was one.** Lead searched local disk and Google
  Drive: no W&SC `.ai` / `.eps` / `.svg` anywhere. The mark has *photographic* fills (water droplets
  in WINDOW, solar-panel texture in SOLAR), so it was almost certainly built as a raster. Do not keep
  hunting for a vector, and do not tell DJ to "get the vector from the designer" as if one exists —
  Lead has asked him once whether a layered original survives.
- *** TAGLINE = LIVE TYPE, not artwork.** Every `Logo-Org-and-Tag-*` raster maxes out at **500 x 251**,
  which prints visibly soft in the thin tagline strokes at any real size. The standing solution is the
  sharp 2700px logo with **"We don't just Clean, We Care!"** set as live type beneath it, CENTRED under
  the logo (DJ 2026-09-12: centred, not right-justified), brand blue `#1e5aa8`, italic.
- **! DEAD-NUMBER LANDMINE.** `Logo\Logo-Web-Site-Header*.png` (4095 x 820 — the LARGEST logo files in
  the folder, so the tempting ones) have the **RETIRED toll-free (855) 245-2273** baked into the
  artwork. Current number is **760-334-5355**. Never place a Header logo on anything. Lead left a
  `_READ-ME-BRAND-WARNINGS.txt` in that folder; files were not renamed because the live site may
  reference them.
- **Full image library:** `...\A Window and Solar Care\Website\` — Logo, Solar, Windows, Gutter,
  Pressure Washing, Van, People, House, Screens, Squeege, Water Drops, Room, Equipment, Dan, Coupon,
  Pricing, Care Program, Stock Images. Use these canonical W&SC assets before generating anything new.

## Where things live
Working files: `design/view-ad/` (`Main.dc.html` = Front A, `FrontB.dc.html`, `Back.dc.html`,
`canvas.json`, `view.jpg`, `wsc-logo.png`, `_source/` originals, `PRINT/`, `PROOF/`).
Drive archive: `G:\My Drive\Window & Solar Care — Design\2026\<piece>\` with `1 SOURCE`,
`2 MASTER`, `3 PRINT READY — what goes to Zoo`, `4 PROOFS — with guide lines`.
