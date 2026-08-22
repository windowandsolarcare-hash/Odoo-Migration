---
name: Saunders Printing — Commercial Web-to-Print Plan
description: Full plan for Saunders Printing commercial print business — web-to-print site, file prep automation, Odoo accounting, Stripe payments
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Saunders Printing — Commercial Web-to-Print

**Decided:** 2026-04-18
**Status:** Planning complete. Nothing built yet.

---

## BUSINESS MODEL

Commercial print shop — business cards, flyers, postcards, banners, etc.
DJ has his own printer. He enters jobs, prints, and ships under Saunders Printing brand.
AI handles everything else: order taking, file checking, file prep, payment, accounting.

---

## THREE CUSTOMER PATHS

### 1. Customer uploads their own file
- Customer uploads design file on website
- Claude checks: resolution (300 DPI min), bleed (0.125" standard), color mode (RGB→CMYK), file format, safe zone
- Auto-converts to print-ready PDF
- Flags issues or approves
- Order placed, DJ receives production-ready PDF

### 2. Customer wants to design their own
- Embed Canva (free embed SDK) or simple template builder on site
- Customer designs, exports, uploads
- Same file check/prep as path 1
- V1: skip this — launch with upload + custom design only. Add self-design later.

### 3. Customer wants Saunders Printing to design it
- Customer fills out brief on site (colors, style, text, examples)
- Pays design fee upfront
- Claude drafts using DALL-E 3 / Flux
- DJ reviews and approves design
- File prepped, order fulfilled

---

## FILE PRODUCTION PROCESS (automated)

Claude handles via Python libraries:
- Resolution check: 300 DPI minimum — flag/reject low-res
- Bleed: 0.125" on all sides — add programmatically if missing
- Color mode: RGB → CMYK conversion
- Format: convert to print-ready PDF
- Safe zone: flag text/logos too close to trim edge
- Output: production-ready PDF delivered to DJ

DJ's only job: enter PDF into printer software, print, ship.

---

## PAYMENTS

- Stripe for credit card processing on site
- Odoo has native Stripe connector (included in DJ's full package)
- Customer pays on site → Stripe → bank
- Claude logs payment in Odoo automatically

---

## WEBSITE

- Platform: Odoo Website (already included in DJ's subscription)
- eCommerce native: product pages, cart, checkout, Stripe built in
- Orders flow directly into Odoo SOs automatically
- No manual order entry needed
- Design tool: Canva embed SDK (v2+), or skip for v1

---

## ODOO SETUP

- Third company: "Saunders Printing" (multi-company, same instance)
- Completely separate: chart of accounts, P&L, invoices, bank account
- Product catalog: business cards, flyers, postcards, banners — pricing tiers by quantity
- Revenue: logged per order
- Expenses: paper, ink, shipping supplies, design API costs
- Same pattern as W&SC and artwork businesses — no new seats

---

## LAUNCH STRATEGY (v1)

1. Build Odoo company + product catalog
2. Build Odoo website storefront with Stripe
3. File upload + automated file check/prep
4. "We design it" path with brief form + design fee
5. Skip self-design tool for v1

---

## DJ'S ROLE (the 5%)

1. Review and approve custom design jobs
2. Receive production-ready PDF
3. Enter job in printer software
4. Print and ship under Saunders Printing

---

## ARCHITECTURE FIT

```
One Render Service
    └── [future: Saunders admin route for order management]

One Odoo Instance
    ├── Company: Window & Solar Care (live)
    ├── Company: Artwork/Prints (planned)
    └── Company: Saunders Printing (planned)

Odoo Website
    ├── W&SC marketing site (planned)
    ├── Cheryl real estate site (planned)
    └── Saunders Printing storefront (planned)
```
