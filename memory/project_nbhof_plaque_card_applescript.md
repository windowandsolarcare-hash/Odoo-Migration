---
name: project_nbhof_plaque_card_applescript
description: "NBHOF 'plaque card' back-copy update in QuarkXPress on DJ's Mac — the manual workflow we're automating via AppleScript (find .qxd → open → page 2 → update 'Printed <Month Year>' + copyright year → save → export 2 PDFs via the 'zoo printing' preset). Zoo upload is DJ's, out of scope. Started 2026-08-29."
metadata:
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-29T18:23:41.257Z
---

**Project (started 2026-08-29): automate DJ's NBHOF plaque-card BACK-copy update in QuarkXPress via AppleScript.** DJ works this on his **Mac** (Mac Pro 2012); AppleScript is Mac-only, so Lead WRITES the script, DJ RUNS it in Script Editor / `osascript`, iterate. Lead can't test (Lead is on the Windows Surface).

**The cards:** NBHOF postcards = "plaque cards." Each has a **C-number** (card number, e.g. C38677). The Saunders app already extracts every C-number off the NBHOF PO into the Odoo invoice lines — so the authoritative **C-number list for a PO = that invoice's lines** (e.g. invoice 200239 / PO 044167 had C38660–C38681). That list is our batch input.

**DJ's current MANUAL workflow (per card) — what we're automating (steps 1–8; Zoo upload is his, out of scope):**
1. From the PO, copy the first **C-number**.
2. Open **Find Any File** (Mac search app), paste the C-number. Search is scoped to the **NBHOF folder only** (not whole drive).
3. It finds the file/folder → click the folder → now in the right card folder.
4. In the folder, open the **.qxd** (QuarkXPress doc) → launches Quark.
5. Quark doc = **2 pages**: page 1 = FRONT (NEVER changes), page 2 = BACK (has copy).
6. Go to **page 2**. In the **upper-left area, at the bottom of the paragraph**, text reads "**Printed <Month> <Year>**" (e.g. "Printed August 2026"). Highlight the old date → type the **actual print/ship month** (e.g. this run = "**September 2026**").
7. At the **very lower bottom**: a **copyright year** = year last printed. Update to current (e.g. **2026**).
8. **Save.**
9. **Export** Quark → PDF using a predetermined **"zoo printing" preset**: adds **bleed + crop marks** and **splits into 2 files** (front + back).
10. Output filenames ≈ `<cardnumber> (page 1).pdf` and `<cardnumber> (page 2).pdf`.
11. DJ uploads to Zoo himself — DIFFERENT process, OUT OF SCOPE.

**Automation scope:** from finding the file (step 2) through exporting the 2 PDFs (step 10). The two batch parameters are constant across a print run: **print Month+Year** (e.g. "September 2026") and **copyright year** (e.g. 2026). AppleScript replaces Find Any File with a scoped `mdfind`/`find` over the NBHOF folder. Plan: get it rock-solid on ONE card, THEN batch the whole C-number list.

**OPEN QUESTIONS blocking runnable code (asked DJ 2026-08-29):**
- **QuarkXPress version** (About QuarkXPress) — its AppleScript dictionary varies a lot by version; governs the whole export path.
- **"zoo printing" export**: is it a named **PDF Output Style** DJ picks by name (scriptable), and does the STYLE itself produce the 2 separate files, or is the split done another way (e.g. export page 1 and page 2 separately)?
- **Exact text of the two edits**: the "Printed …" line literal (anchor on "Printed "?) and the copyright literal (e.g. "© 2025" — anchor on "©"?) so find/replace targets reliably and doesn't hit a stray "2025".
- **Folder/file layout**: one parent NBHOF folder path; is each .qxd named by its C-number (or the folder named by C-number)? Where should exported PDFs land?

Related: [[project_saunders_printing_odoo]], [[project_saunders_invoice_send_view]].
