---
name: project_eddm_mailing_rules
description: USPS Every Door Direct Mail rules a W&SC print piece must satisfy — flat-size minimum, indicia wording/placement, and the address-in-the-top-half rule. Design owns these.
metadata:
  type: project
---

DJ (2026-09-12) made it **Design's responsibility to know and apply the EDDM rules** — not his, and
not something to be discovered after a print run. Researched against USPS sources and applied to the
6x9 postcard. Anything mailed EDDM must clear every rule below.

## 1. ★★ SIZE — 9 x 6.5 in IS THE W&SC EDDM SIZE (DJ, 2026-09-12)
**Zoo Printing's EDDM postcard size is 9 x 6.5 in. That is the size. Do not design a W&SC EDDM
piece at anything else unless DJ says so.**
- Trim **9 x 6.5 in**
- Bleed .125 all round -> artwork **9.25 x 6.75 in**
- Artboard **2775 x 2025 px** at 300 DPI
- Press page 10 x 7.5 in (half an inch of room each side for the crop marks)

**Why the size matters — the rule that silently disqualifies a piece.** EDDM **Retail** (the
no-permit version carried into the post office) only accepts **flat-size** mail. A piece is
flat-size only if it **EXCEEDS at least ONE** of:
- more than **11.5 in long**, OR
- more than **6-1/8 in (6.125) high**, OR
- more than **1/4 in thick**

…and stays within **15 x 12 x 3/4 in** and **under 3.3 oz**.

**A 9 x 6 card exceeds NONE of them** — 6 in is *under* 6.125 — so a 9x6 is letter-size and is **NOT
EDDM-Retail eligible**; letter-size EDDM is BMEU only and needs a USPS permit. 9 x 6.5 clears the
6-1/8 bar with room to spare, which is exactly why Zoo sells that size for EDDM.
History: this piece was drawn 9x6, caught here, briefly re-cut to 9x6.25 (legal but not Zoo's
size), then settled at **9 x 6.5**. Old 9x6 PDFs are parked in Drive under
`z SUPERSEDED — 9x6 trim, NOT EDDM eligible` so the wrong size cannot be sent by mistake.

## 2. INDICIA (upper right of the address side)
Exact wording, four elements, **ALL CAPS**:
```
PRSRT STD
ECRWSS
U.S. POSTAGE
PAID
EDDM RETAIL
```
- **8 pt minimum** (we use ~9 pt), clean sans-serif.
- Minimum block **0.5 x 0.5 in**; at least **1/8 in clear of every edge**; keep graphics out of it.
- Printed on the piece — never handwritten or stamped.

## 3. ★ ADDRESS BLOCK — must be in the TOP HALF of the piece
USPS: *"the address must be in the top half of the piece."* Orientation (long/short side) does not
matter. On the 9 x 6.5 card the trimmed piece runs y=37.5..1987.5 in artboard px, so **everything in
the address block must sit above y=1012.5**. This is easy to miss — the build script draws an orange
guide line at exactly that point on the address side so it's visible in every proof.

Generic recipient line, no name:
```
****ECRWSSEDDM****
Local
Postal Customer
```

## 4. What EDDM does NOT require
No barcode clear zone and no bottom white band — EDDM is carrier-route bundled, not run through the
letter-automation equipment, so the usual OCR/barcode keep-out areas don't apply. DJ raised this
himself and he is right; a ghosted background running the full piece is fine.

## 5. Volume
EDDM Retail: up to **5,000 pieces per ZIP per day**, no permit. Target routes for this card are the
Rancho Mirage EDDM routes (see [[project_design_archive_drive_structure]] / the piece README).

Sources: USPS Postal Bulletin PB22312 (flat dimension standards) and the EDDM indicia guidance at
eddm.com. Verify against USPS before any NEW piece type — these are the rules as of 2026-09.
