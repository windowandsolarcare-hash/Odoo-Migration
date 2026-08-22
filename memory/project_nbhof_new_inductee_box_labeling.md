---
name: project_nbhof_new_inductee_box_labeling
description: "STANDING COMMITMENT to NBHOF (emailed to Ben Hatton 2026-08-04): the FIRST order of new inductee plaque postcards each year ships with NO sample card on the outside of the boxes (unreleased plaque images). All re-orders unchanged."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8f0313dc-02cc-482c-833a-0ab0d7a6b313
  modified: 2026-08-04T12:59:49.158Z
---

**Promised in writing to Ben Hatton (bhatton@baseballhall.org, NBHOF) — DJ sent 2026-08-04.**

**THE RULE — applies every year, forever:**
- **FIRST order of NEW INDUCTEE plaque postcards each year → NO sample postcard on the outside of
  the boxes.** The plaque images are confidential until publicly released, and the boxes travel a
  delivery chain before they reach Cooperstown.
- **ALL re-orders → unchanged.** Sample card stays on the outside so NBHOF's warehouse crew can
  identify contents at a glance. Ben explicitly did NOT want the long-standing process changed
  generally — only this one carve-out.
- **Banding stays** — Ben said 2026-07-28 the banding "is actually quite helpful to our staff for
  multiple reasons." Do not remove it.

**WHY (Ben's reason, worth knowing so nobody "optimizes" it away):** around 2022–2023 a first
shipment of new plaque postcards was being unloaded from the truck while a member of NBHOF senior
staff was outside. He saw the un-released plaque image on the outside of a box, photographed it,
and showed the rest of senior staff — **Ben and his boss were reprimanded.** No images actually
leaked, but it created real internal concern about the plaque art being visible along the delivery
chain. Ben raised it only after the July 2026 lost-shipment incident (a box's outside card appears
to have been removed in transit).

★ DJ's email promised this "carries forward automatically instead of depending on anyone
remembering it." **AUTOMATED 2026-08-04** (commits watcher 37c44d82, tracker a7a14ac7):
- `routers/printing/watcher.py` — `NEW_INDUCTEE_HANDLING` constant + `_is_new_inductee(subject, body)`
  (fires when the subject/body contains **"confidential"** or **"inductee"** — Ben marks these POs
  CONFIDENTIAL himself, which is the signal). `check_hof_emails()` sets `job['confidential']` and
  `job['handling']` on the tracker job, and the "New HOF PO Received" alert to DJ gets a `[CONFIDENTIAL]`
  subject tag plus an amber special-handling block above the card list.
- `static/printing/index.html` — `.conf-strip` banner on the job card, rendered OUTSIDE `.job-body`
  so it shows **without expanding** the card.
- Detector regression-tested against Ben's 7 real subject lines from the 2026 cycle: correctly flags
  "PO #044303 CONFIDENTIAL", "CONFIDENTIAL: 2026 Plaques", "New inductee postcards ETA"; correctly
  does NOT flag the re-stock PO #044322 (its body says "induction weekend" — "induction" != "inductee"),
  #044510, #044515, #044433. Verified live: tracker 200, /printing/api/jobs OK (proves clean import).
⚠ It FLAGS, it does not enforce — DJ still has to pass the instruction to the plant when ordering.

**TIMING (2026 cycle, use as the template):** plaques for new inductees arrived via Google Drive
link ~Jun 30; PO #044303 (CONFIDENTIAL) for new-inductee cards ~Jun 30; re-stock PO #044322 (36,000
cards) Jul 1; induction weekend late July. So the confidential first run lands **late June / early
July** each year — that is when this rule fires.

**Related NBHOF working facts from the same period:** POs arrive by email from Ben as PDF
attachments (watcher: [[project_nbhof_watcher_reorder_po]]); Spanish-language versions exist for
some inductees (Beltrán 2026) and NBHOF's own graphic designer creates the foreign-language art;
new-inductee emails are marked CONFIDENTIAL in the subject. See [[project_zoo_printing_automation]]
for the Zoo order/ship/invoice pipeline and [[project_nbhof_postcard_c_numbers]] for item numbering.

**Why:** a customer-facing commitment that recurs annually and involves a confidentiality concern
NBHOF has already been burned by — exactly the kind of thing lost between sessions and years.
**How to apply:** when the new-inductee PO comes in each June/July, the order to the plant must
carry the no-card-on-the-outside instruction. Re-orders after it revert to normal.
