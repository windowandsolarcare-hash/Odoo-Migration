---
name: project_nbhof_data_driven_card_rebuild
description: "NBHOF bigger idea (DJ, 2026-11-03): RETIRE QuarkXPress by storing each card's BACK copy as DATA and making Design the layout engine (HTML→300dpi CMYK press PDF) — front TIFF just placed, routine date/copyright changes become data edits. Design feasibility read + extraction plan."
metadata:
  node_type: memory
  type: project
  originSessionId: 9e757d4b-c2ad-4e84-9c81-2f3aa11f1c2e
  modified: 2026-11-03T20:40:39.617Z
---

**Concept (DJ via Dispatcher, 2026-11-03): get rid of QuarkXPress as the NBHOF plaque-card layout program.** Front of each card = a TIFF (image, picked up as-is). Back = DATA (the copy as data points, not a Quark layout). Extract all back-of-card data out of the existing Quark files, STORE it, and have **Design become the layout engine** that rebuilds the back from stored data + the front TIFF. Then routine changes (print date each run, copyright year) are just data edits — no Quark. This supersedes the per-card date-patch automation in [[project_nbhof_plaque_card_applescript]] (that tool stays useful meanwhile).

**Design feasibility read (given to DJ 2026-11-03):**
- **Layout engine = YES, high confidence.** It's the same thing Design already does for postcards: build a layout → output true 300-DPI CMYK press-ready PDF (bleed + crop). A plaque-card BACK is mostly text (name, bio/plaque copy, induction year, "Date of Printing <Month>, <Year>", "Copyright © <year>", logo) → ideal data-driven template. Store copy as data, place the front TIFF, generate the card. Also kills the recurring Quark headaches (legacy formats, missing "Helvetica Bold").
- **Extraction = YES for modern cards, via Quark, NOT binary parsing.** The reliable path is the SAME method "NBHOF Auto" already uses: Quark (on DJ's Mac, AppleScript) opens each card and hands over the text of every box; reading ALL boxes → dump JSON/CSV is a small extension of proven code (`text of story 1 of text box i of document 1`). **Nuance:** that gives TEXT + which field reliably; it does NOT cleanly export fonts/sizes/exact positions — but we re-create the look ONCE in the new template, so we don't need per-card styling. **Cannot reliably crack the raw .qxd binary without Quark** → extraction runs through Quark on the Mac (one library pass). Legacy 2003 cards with no modern .qxd (the `.FC/BU` format, e.g. Mantle C34260) → fall back to OCR the archived print PDF or DJ supplies.
- **KEY UNKNOWN that drives effort:** are all card BACKS one shared layout (just different words) or do they differ card-to-card? Uniform → big win, low ongoing effort (one template + data). Varied → more template work. Need a few sample backs to confirm.
- **Also need (not blockers):** real fonts (Helvetica etc., standard); confirm front TIFFs are press-resolution (existing print files, almost certainly yes); NBHOF reprint-fidelity sign-off is DJ's call.
- **Recommended de-risk (offered, awaiting DJ greenlight):** 2–3 representative cards → extract back data via Quark read → Design rebuilds back + places front TIFF → output PDF → DJ compares side-by-side to the Quark version. If they match, scale to the whole library.

**★ REFINEMENT (DJ via Dispatcher, 2026-11-03) — only 3 fields vary; leanest path avoids Quark entirely.** DJ confirmed ALL card backs are the SAME format/layout; the ONLY per-card differences are **(1) player NAME, (2) YEAR elected to the HOF, (3) the COMMITTEE that elected them.** All other structure + words are identical → ONE shared template + 3 data columns. DJ wants ZERO hand-pulling of documents.

**Leanest path (Design recommendation, given 2026-11-03):**
- **NAME = from Odoo, already in hand** — each NBHOF invoice line's description carries the player name keyed to the C-number (e.g. "Mickey Charles Mantle Plaque Postcard"). No extraction needed.
- **YEAR + COMMITTEE = online** — published for every inductee (baseballhall.org / Baseball-Reference). Pull as a dataset keyed by name.
- **FRONT TIFF = copied from the card's folder** (folder named by C-number); just placed in the layout.
- **BACK = one template + the 3 fields.**
- Net: Odoo (name) + online (year, committee) + folder TIFF + one template = whole library, NO Quark extraction pass, no document hand-pulling.
- **Still needed (one-time, tiny):** (1) ONE real sample back (an archived print PDF is fine, or read one card via Quark) to build the template with EXACT fixed wording/fonts/logo/layout — can't invent the boilerplate. (2) A validation pass: generate ~6–8 cards, DJ compares to the real printed cards. **RISK FIELD = COMMITTEE** — HOF committee names changed over the decades (BBWAA / Veterans Committee / Era committees / Negro Leagues Committee); online naming may not match the card's exact phrasing. Name format (full plaque name) is a smaller version of the same risk. Validate, build a mapping if needed, then batch.
- **Cannot parse .qxd directly** (proprietary binary) — any Quark read runs through Quark/AppleScript on the Mac; this path mostly avoids it (only the one reference back).

Status 2026-11-03: refined feasibility + leanest-path recommendation relayed to DJ via Dispatcher. Design ready to build the template the moment DJ sends ONE sample back + greenlights, then a sample validation (esp. committee wording) before the full run. Related: [[project_nbhof_plaque_card_applescript]], [[project_saunders_printing_odoo]], [[project_wsc_print_build_pipeline]].
