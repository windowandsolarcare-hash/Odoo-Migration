---
name: project_del_webb_landing_page
description: "Del Webb (Rancho Mirage) EDDM postcard landing page — LIVE static page wscare.pro/dw (static/dw/index.html in saunders-render-app). Pricing bands + Voyage, Essential/Premium/Signature, add-on upsell + the EXACT-label contract with the /book/api/request/addons endpoint. Web owns the page."
metadata:
  node_type: memory
  type: project
  originSessionId: a6200401-4a1b-4492-894c-629c161de653
  modified: 2026-10-03T03:20:11.358Z
---

**Page:** `static/dw/index.html` (+ `dw_hero.jpg`, `dw_logo.png`) in `saunders-render-app`; QR target **wscare.pro/dw** (307 → `/static/dw/index.html`, route built by Specialists). Pure static, same-origin, books via `/book/api/*` (availability, addr, `POST /api/request` → a Submitted SO DJ prices/confirms, `quote_src=delwebb-eddm`). Build rule: real standalone page, own doctype+viewport, NOT artifact-first (see WEB.md).

**Floor plans / prices (DJ 2026-10-02):** Premium is the level on the postcard. Bands: Sanctuary·Preserve·Haven·**Getaway** $210 | Refuge·Expedition·Solitude $260 | Serenity·Journey $290 | **Voyage** $380. Signature = Premium + $50. Essential = Premium − $35 (selectable, tagged "Not recommended", "Window cleaning only — too basic for a Del Webb home"). **"Gateway" was a typo — the real plan is "Getaway"** (delwebb.com); fixed on page + card back. Voyage is not on the card yet (Design/DJ call).

**Flow:** floor plan → service level → address → day (live scheduler, growing load bar) → details → Review (chips tappable to go back; hint shown on Review only) → Request → "You're on the schedule, <name>!" + add-ons upsell. Address autocomplete: client appends " Rancho Mirage CA", keeps only California results, re-adds the typed house number. Defaults city Rancho Mirage / ZIP 92270.

**Add-ons upsell (confirmation screen):** 6 items w/ qty steppers + running total, prices = Odoo list prices: Mirrors cleaned $10, Ceiling fans cleaned $5, Shower glass cleaned $25, Skylights cleaned $15, Hard-water stain removal $75, and Cobweb cleaning $55 (Standard/Essential) OR Garage door windows $10 (Signature, since Signature already includes cobweb-clean frames).
- Button posts `POST /book/api/request/addons` `{so_id, so_name, phone, name, items[], addons_total, base_total}`. Specialists built it (phone-verified, adds sale.order.lines at the PRODUCT's price — client prices ignored, exact-label matching, idempotent). **★ CONTRACT: the 7 add-on labels above are matched EXACTLY — if you change ANY label text, tell Specialists first (unknown labels are dropped, never mis-mapped).**
- Until the endpoint ships (needs Lead QC + DJ "deploy"), the page falls back to a pre-filled `sms:` "Text my extras to Dan" link — nothing is lost.

**Testing note:** never submit the live page to test (it creates a real contact + SO). Test the confirmation/upsell by loading the page and replacing the `LIVE` host regex in a document.write copy.

Related: [[project_wscare_pro_email_routing]], [[reference_domain_dns_hosting_map]], [[project_wsc_address_do_not_publish]].
