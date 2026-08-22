---
name: Multi-Business Architecture Plan
description: Full plan for expanding DJ's Odoo/Render platform to multiple businesses and users — Cheryl real estate, payroll, artwork eCommerce
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Multi-Business Architecture

**Decided:** 2026-04-18
**Updated:** 2026-04-19
**Status:** Scaffold LIVE. Login system built. saunders-render-app repo live on Render.

---

## MASTER ARCHITECTURE

```
One Render Service (existing, paid plan)
    ├── Login/routing screen → routes by user/access code
    ├── DJ    → W&SC field assistant (current app, already live)
    ├── Danny → Payroll clock-in/out (planned)
    ├── Cheryl → Real estate assistant (planned)
    └── [future users/businesses]

One Odoo Instance (existing subscription, full package)
    ├── Company: Window & Solar Care (existing)
    ├── Company: Cheryl Real Estate (planned - multi-company)
    ├── Company: Artwork / AI Prints (planned - multi-company)
    └── Company: Saunders Printing (planned - multi-company)

Odoo Website (included in full package)
    ├── W&SC marketing site (planned)
    ├── Cheryl real estate site (planned)
    └── Saunders Printing storefront (planned — primary eCommerce)
```

---

## ODOO MULTI-COMPANY SETUP

- Odoo natively supports multiple companies in one instance
- Each company has completely separate: chart of accounts, P&L, invoices, bank accounts, tax settings
- One login, switch between companies from top menu
- DO NOT touch existing `x_studio_x_studio_record_category` field — build a NEW field for business type tagging

---

## CHERYL — 3-PHASE LOGIN PROGRESSION

**Phase 1:** Render only — Odoo is invisible backend. Cheryl uses her own access code on Render. No Odoo user needed. No extra cost.

**Phase 2:** Render primary + her own Odoo login under DJ's account. She can access Odoo directly if needed. Still DJ's subscription, added user.

**Phase 3:** Her own Odoo account entirely. I migrate all her data (contacts, accounting, history, documents). Update Render env vars to point to her new Odoo URL. Clean separation.

Transition between phases: any time, DJ's call, I handle it.

---

## ODOO WEBSITE MODULE

DJ has full Odoo package including Website module. Plan:
- Build W&SC website in Odoo (marketing + booking)
- Build Cheryl's real estate website in Odoo
- All landing pages through Odoo
- eCommerce when ready (already included in plan)
- Key advantage: lead forms → Odoo CRM automatically, no Zapier

Odoo supports MULTIPLE websites from one instance — one per business/company.

---

## PAYROLL TRACKER

**Workers:** DJ + Danny, both hourly
**Stack:** Render screen for clock-in/out → Odoo timesheets (account.analytic.line)
**Payroll processing:** Stay on Gusto for now. Odoo tracks hours, DJ manually enters into Gusto. Future: switch to Odoo payroll if Claude can automate enough.
**Access:** Danny sees only his own hours. DJ sees everything (both workers, weekly totals, what's owed).
**Status:** Ready to build. No blockers.

---

## ARTWORK / eCOMMERCE BUSINESS

**Concept:** AI artwork using Midjourney → sell on Etsy + Shopify/Odoo

**API access:**
- Midjourney: NO official API. Use manually. Workarounds exist but against ToS.
- Etsy: ✅ Official API — create/update listings, manage orders, upload images
- Shopify: ✅ Excellent API — full store automation
- Alternative art generation: DALL-E 3 or Stable Diffusion have real APIs Claude can call

**Platforms:**
- Etsy = marketplace traffic/discovery
- Shopify OR Odoo eCommerce = branded store, higher margin
- Sync inventory between platforms, manage in Odoo

**Claude's role after art is approved:**
1. Resize/optimize images for each platform
2. Write title, description, tags (SEO)
3. Create listing on Etsy + Shopify/Odoo simultaneously
4. Set pricing, categories, shipping
5. Order comes in → log, update inventory, trigger fulfillment

**Status:** Green-lighted as future project. Not started. Revisit when other priorities are done.

---

## BUILD PRIORITY ORDER

1. W&SC accounting migration (QB → Odoo) — waiting on DJ's file exports
2. Cheryl Odoo company setup — need her business name
3. Cheryl real estate Render screen — need MLS info + stage checklist
4. Cheryl accounting setup — need her expense categories + bank info
5. DJ + Danny payroll tracker — ready to build anytime
6. Artwork eCommerce — future, after above complete
7. Saunders Printing — web-to-print site, Odoo eCommerce, Stripe, file prep automation
8. W&SC website in Odoo — future
9. Cheryl website in Odoo — future

## BUSINESSES SUMMARY

| Business | Status | Platform | Notes |
|---|---|---|---|
| Window & Solar Care | LIVE | Render + Odoo | Field assistant, full automation |
| Cheryl Real Estate | Planning | Render + Odoo multi-company | Need info from Cheryl |
| Artwork / AI Prints | Green-lighted | Odoo + Etsy/Shopify APIs | Flux/DALL-E 3, Printify fulfillment |
| Saunders Printing | Green-lighted | Odoo Website + Stripe | Web-to-print, DJ prints/ships |
| Payroll (DJ+Danny) | Ready to build | Render + Odoo timesheets | No blockers |
