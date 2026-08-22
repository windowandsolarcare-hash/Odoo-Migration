---
name: reference_brand_logo
description: Official Window & Solar Care logo file — canonical locations (local + both GitHub repos + Render static URL) and brand palette.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**Official Window & Solar Care logo** (DJ-provided 2026-06-14). PNG 500×235, RGBA (alpha channel), white background, full color "WINDOW & SOLAR Care" with tagline **"We don't just Clean, We Care!"**. Use this for any customer-facing / branded output.

## Canonical locations (all 3 kept in sync — use whichever fits the context)
- **Local (durable):** `C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\4_Reference_Data\brand\logo_window_solar_care_white_bg_500x235.png`
- **GitHub (Odoo-Migration, reference):** `4_Reference_Data/brand/logo_window_solar_care_white_bg_500x235.png`
- **GitHub (saunders-render-app, servable):** `static/brand/logo_window_solar_care.png` → live URL **`https://wsc-field-assistant.onrender.com/static/brand/logo_window_solar_care.png`** (Render Claude / web pages can hot-link this).

## Brand palette — CORRECTED 2026-06-21
- **TRUE brand color = water-blue `#0090d0`** (the dominant color in the LOGO — "WINDOW" droplet-blue lettering; DJ: "my company color is blue like in water"). Use THIS for UI accent/branding. Supporting shades used in the ERP design system: dark-mode accent `#35aee6`, light-mode accent `#0077b3`, header/buttons `#0090d0`.
- ⚠️ Odoo `res.company` id=1 `primary_color` is mis-set to `#5e4766` (plum) — this is WRONG for branding and is where earlier work wrongly picked up plum. Do NOT use the Odoo primary_color field as the brand color. (Could fix the Odoo setting to #0090d0, but it may affect Odoo invoice/email theming — leave unless DJ asks.) Secondary/near-black `#010101`.
- Brand name customer-facing = **"Window & Solar Care"** (ampersand), NOT "Window and Solar Care" / "A Window..." — see [[feedback_company_name_no_a]].
- Phone (951) 972-6946 · windowandsolarcare@gmail.com · Windowandsolarcare.com · 41995 Boardwalk Ste. J, Palm Desert 92211.

## CAVEAT — white background on dark headers
The file has a WHITE background. On the booking page's plum (`#5e4766`) header it shows as a white block. Options when placing on a dark bg: put the logo on a white/light header band, OR get a transparent-bg version from DJ. The booking page ([[project_customer_portal_booking]]) currently pulls the logo from Odoo company record (data-URI via `/book/api/brand`); switching it to this file is a TODO if DJ wants this exact logo there.
