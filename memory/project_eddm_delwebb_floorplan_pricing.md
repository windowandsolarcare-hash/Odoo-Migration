---
name: project_eddm_delwebb_floorplan_pricing
description: "Del Webb EDDM card prices windows BY FLOOR PLAN (grouped into 4 bands). Postcard price = PREMIUM tier. First-time clean = that price + $50. Operator looks up the caller's plan and inserts the price on the job. Authoritative table from Design 2026-11-03."
metadata:
  node_type: memory
  type: reference
  originSessionId: c4c6184d-7f8f-4870-868c-f108044fcc77
  modified: 2026-11-03T20:09:25.364Z
---

**The Del Webb (Rancho Mirage) EDDM mailer quotes window-cleaning price BY FLOOR PLAN**, grouped into 4 price bands. Callers coming off that card cite their floor plan; Operator looks up the plan's price and inserts it as the job's service-line price when booking.

**Two important rules (from Design, who owns the card):**
- **The price printed on the postcard is the PREMIUM tier.** (Three tiers exist per plan: Essential=GOOD = window cleaning only; Premium=BETTER = the card price = glass in/out, tracks vacuumed, sills, screens dry-brushed; Signature=BEST = adds wet-washed screens, cobweb frames, 2 mirrors.)
- **A FIRST-TIME clean = the maintenance (recurring) price + $50.** So a brand-new customer's first job uses the "first-time" column below; repeat/maintenance visits use the plain band price.

## Plan → price table (authoritative, Design 2026-11-03)

| Band | Plans | Essential | **Premium (card price)** | Signature | Premium FIRST-TIME |
|---|---|---|---|---|---|
| 1 | Sanctuary, Preserve, Haven, Getaway | $175 | **$210** | $285 | $260 |
| 2 | Refuge, Expedition, Solitude | $225 | **$260** | $335 | $310 |
| 3 | Serenity, Journey | $255 | **$290** | $365 | $340 |
| 4 | Voyage | $315 | **$350** | $425 | $400 |

**Quick plan → Premium lookup:** Sanctuary / Preserve / Haven / Getaway = $210 · Refuge / Expedition / Solitude = $260 · Serenity / Journey = $290 · Voyage = $350.

## Operator workflow
1. Caller names their Del Webb floor plan (or DJ relays it).
2. Find the plan in the table. Default tier = **Premium** (the card price). If it's their **first** clean with us, use the **Premium first-time** column (+$50).
3. Book via the app endpoints (contact → property → create-job) with that price on the service line (standard line = product 141 "Windows In & Out - Full Service"). If plan is unknown, leave price TBD and DJ quotes on site.

**Mira Gralnik** (57 Claret, Rancho Mirage — new customer, booked Mon 2026-11-16 10 AM, SO 265054): DJ thinks ~$210 = a **Band 1** plan (Sanctuary / Preserve / Haven / Getaway). Since she's NEW, her first clean at Premium = **$260** (not $210). Plan unconfirmed → left price TBD; DJ to confirm which Band-1 plan she has.

See [[project_eddm_mailing_rules]].
