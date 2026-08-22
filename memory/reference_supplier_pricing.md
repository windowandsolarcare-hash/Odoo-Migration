---
name: W&SC supplier pricing files — locations
description: Where DJ's Window & Solar Care supplier price lists live in his local Documents folder. Use these when DJ asks about screen pricing, screen-door pricing, or any other supplier cost questions.
type: reference
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
DJ's W&SC supplier price lists are in `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\<supplier>\`.

## Active Window Products

Folder: `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\Active Window Products\`

- **Active Window 2025 Sec 1 Pricing - Window Screen Components.pdf** — saved 2026-04-29 from email upload `9f7db883-2025Sec1All040626.pdf`. 26 pages of **window screen component** pricing — raw frame extrusions, corners, splines, latches, clips, hardware. Pricing format: per-foot (or per-each), with 7 volume tiers (Standard L/T Carton → 25,000+). Finish codes: M/MF=Mill, A/AN=Anodized, AD=Adobe, AL=Almond, BL=Black, G/GR=Gray, T=Tan, W/WH=White, Z/BR=Bronze.
  - Frame stock by depth: 1-1/4" (1001), 1" (1002, 1003, 1025), 15/16" extruded (1004), 3/4" (1006, 1007), 3/8" slider (1019, 1005), **5/16" (1017)**, 1/4" (1008), 1/2" lip (1009), 5/16" lip (1010), 3/4" standoff (1013), 1/2" standoff (1014), 5/8" extruded standoff (1015)
  - Sample: 1017AL (5/16" Almond) = $1.017/ft single carton, $0.678/ft @ 1000-1999ft, $0.626/ft @ 10K-25K
  - Each frame line names matching corner + spline (e.g. 1017 → corner 1213M, spline .185)
- **Active Window 2025 Sec 11 Pricing - Screen Doors.pdf** — saved 2026-04-29 from email upload `3b3e6428-2025Sec11All_041926.pdf`. 19 pages of **sliding screen door** pricing (KD kits + assembled doors). Styles: Premier, Century, 1-3/4" Durango, Ateevo-Laguna. Sizes 30"-60" widths × 82" or 96" heights. Finishes: Clear Anodized / Dark Bronze Anodized / Painted (Adobe/Almond/Black/Bronze/Tan/White). Effective 4/16/2026.
  - Sample: Premier KD 30"×82" Clear = $165.27; Premier Assembled 60"×96" Bronze = ~$269
  - Premium screen-cloth upcharges: +$7 (Bettervue/Charcoal 18×14), +$22.50 (Fiberglass 20×20, Sun, Tuff), +$25 (Suntex 80% / Pet Screen)
  - SS roller upgrades: +$20-$24.50
- Other files in folder are application/credit-card forms (no pricing).

Email contact: orders@activewindowproducts.com  ·  Phone: (323) 245-5185  ·  Fax: (818) 246-5188

## Precision (PrecisionPLP.com)

Folder: `C:\Users\dj\Documents\Business\A Window and Solar Care\Supplies\Precision Screen CC App\Catalog\`

- **Window Screen Price List from Precision Catalog 2017.pdf** — 2017 (9+ years old, may be outdated). Has a useful **Window Screen W×H grid** (page 9): Almond/Bronze/Gray/White $33-$69, Mill $32-$68, sizes 1'6"×1'6" through 6'×6'. Includes vinyl pulltabs (2) + spring clips (2). Other sections cover frames, corners, spreader bars, fiberglass screening, hardware.
- **Price List from Precision Catalog 2017.pdf** — full price list (same vintage)
- **Precision Catalog 2017.pdf** — full catalog
- Section files: Section 8 Pet Accessories, Section 9 Screen Cloth, Section 10 Window Screen, Section 11 Tools

Phone: (909) 379-0123  ·  Fax: (909) 379-0169  ·  Toll Free: (866) 629-6636

## When DJ asks about supplier pricing

1. Active Window Products = screen DOORS (sliding patio doors)
2. Precision = window SCREENS (panels for windows) + frame components, hardware, screen cloth
3. Both folders also have credit-card forms, applications — those are NOT pricing.
4. If DJ uploads a new pricing PDF, save to the appropriate `Supplies/<supplier>/` folder with a clear name (e.g. `Active Window 2026 Pricing.pdf`) and update this memory file.

## Reading PDFs locally

Per `reference_pdf_reading.md`: pdftoppm.exe is at `C:/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftoppm.exe` (NOT on PATH). For text extraction, `pdftotext.exe` in the same folder gives clean output via `-layout` flag — preserves the table structure these price lists use. Run from Bash:
```
"C:/Users/dj/poppler/poppler-24.08.0/Library/bin/pdftotext.exe" -layout "<pdf_path>" "/tmp/output.txt"
```
Then grep/head the .txt. The Read tool's pages= mode also works for PDFs but uses pdftoppm which fails when not on PATH.
