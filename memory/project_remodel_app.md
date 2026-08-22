---
name: project_remodel_app
description: "Cheryl+DJ \"Home Remodel Planner\" app — plan, data source (CubiCasa SVG), phased roadmap; lives in Cheryl repo"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
---

New project started 2026-07-13 (DJ + Cheryl): a **home remodel planner** web app for THEIR OWN house (they want to remodel it). Cheryl's original framing was "interior design," but the real scope is **remodel** — edit the floor plan (knock down / add walls) with construction+material costs attached to each change, then per-room finishes and furniture, each priced, rolling up to a total remodel budget. **Lives in the Cheryl repo** (real-estate side, company 2 world), its own web app — NOT part of Window & Solar Care / this Odoo project.

**Data source decision — CubiCasa.** The floor plan comes from a phone scan, DIY, no photographer needed (photographers just resell CubiCasa in listing bundles). Cost: app free, first 2D plan free, ~$15 basic, **~$30 "Plus" tier which includes the SVG** (editable vector — walls as real shapes), ~$99–149 for 3D (not needed). One-time per plan, not subscription. ★ We take the **SVG export** and import the file directly — do NOT need CubiCasa's enterprise Conversion/Exporter API to start. CubiCasa also exports PNG/JPG/PDF; SVG is the one that matters. Matterport (immersive) and iGuide (most accurate measurements) are alternatives; CubiCasa chosen for DIY + editable SVG + speed (~24h turnaround, ~95-97% accurate).

**Phased roadmap** (see artifact https://claude.ai/code/artifact/2d280a13-84d4-42f8-b9a9-abe2dc8e5aa4):
- P0 Capture (DJ, this week): scan house → SVG + dimensions; I verify walls are clean editable shapes.
- P1 See our house: app loads the real SVG floor plan (rooms, walls, dimensions).
- P2 Move walls + live cost (**the core / real engineering**): remove wall=demo cost, add wall=framing+drywall+labor per LF, flag load-bearing, running total. Prices from an **editable price list DJ+Cheryl control**.
- P3 Room finishes: per-room flooring/paint/counters/cabinets/fixtures auto-costed off real sq-ft.
- P4 Furnish/design: place furniture+fixtures, each priced + buy link.
- P5 Budget: structure+finishes+furniture total, by room+category, printable/contractor-shareable.

**STATUS:** waiting on DJ to do P0 (scan + send SVG). Nothing built yet. When the SVG arrives, first task = open it and confirm walls import as separate editable paths before promising P2 interactivity. See [[reference_cheryl_email]].
