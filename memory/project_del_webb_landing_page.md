---
name: project_del_webb_landing_page
description: "Del Webb (Rancho Mirage) EDDM postcard landing page — LIVE static page wscare.pro/dw (static/dw/index.html in saunders-render-app). Pricing bands + Voyage, Essential/Premium/Signature, add-on upsell + the EXACT-label contract with the /book/api/request/addons endpoint. Web owns the page."
metadata:
  node_type: memory
  type: project
  originSessionId: a6200401-4a1b-4492-894c-629c161de653
  modified: 2026-10-08T20:07:42.361Z
---

**Page:** `static/dw/index.html` (+ `dw_hero.jpg`, `dw_logo.png`) in `saunders-render-app`; QR target **wscare.pro/dw** (307 → `/static/dw/index.html`, route built by Specialists). Pure static, same-origin, books via `/book/api/*` (availability, addr, `POST /api/request` → a Submitted SO DJ prices/confirms, `quote_src=delwebb-eddm`). Build rule: real standalone page, own doctype+viewport, NOT artifact-first (see WEB.md).

**Floor plans / prices (DJ 2026-10-02; Signature bumped 2026-10-08):** Premium is the level on the postcard. Bands: Sanctuary·Preserve·Haven·**Getaway** $210 | Refuge·Expedition·Solitude $260 | Serenity·Journey $290 | **Voyage** $380. **Signature = Premium + $65** (was +$50 until 2026-10-08, DJ raised it via Design → Web; live Signature column now 275 / 325 / 355 / 445). Essential = Premium − $35 (175/225/255/345; selectable, tagged "Not recommended", "Window cleaning only — too basic for a Del Webb home"). Prices live in the `plans:[…]` JS array at `static/dw/index.html` ~line 308 (one `signature:` value per band), rendered via `priceKey:"signature"` — change the array, not hardcoded text. Postcard shows Premium only, so a Signature change does NOT touch the card. **"Gateway" was a typo — the real plan is "Getaway"** (delwebb.com); fixed on page + card back. Voyage is not on the card yet (Design/DJ call).

**Flow:** floor plan → service level → address → day (live scheduler, growing load bar) → details → Review (chips tappable to go back; hint shown on Review only) → Request → "You're on the schedule, <name>!" + add-ons upsell. Address autocomplete: client appends " Rancho Mirage CA", keeps only California results, re-adds the typed house number. Defaults city Rancho Mirage / ZIP 92270.

**Add-ons upsell (confirmation screen) — current (2026-10-02):** 6 items, Odoo list prices: Mirrors cleaned $10, Ceiling fans cleaned $5, Shower glass cleaned $25, Skylights cleaned $15, Hard-water stain removal $75 (qty steppers) + **Solar panel cleaning** = a "# panels" number box, **$5/panel, $100 MINIMUM** (<=20 panels = $100; server bills max(panels,20) x $5 on product 125). Cobweb + Garage were REMOVED (DJ). Button reads "Submit my additional service request". No duplicate Call/Text inside the confirmation card (footer only).
- Button posts `POST /book/api/request/addons` `{so_id, so_name, phone, name, items[], addons_total, base_total}`. Specialists built it (phone-verified, adds sale.order.lines at the PRODUCT's price — client prices ignored, exact-label matching, idempotent). **★ CONTRACT: the add-on labels above (incl. exactly "Solar panel cleaning") are matched EXACTLY — if you change ANY label text, tell Specialists first (unknown labels are dropped, never mis-mapped).**
- **LIVE + VERIFIED 2026-10-02** (hotfix a5e2fc76: res.partner has no `mobile` field — the first deploy 500'd on that): wrong phone → 403, right phone → 200 with sale.order.lines at product prices + [CUSTOMER ADD-ONS] chatter, repeat → already. The `sms:` "Text my extras to Dan" link remains only as an ERROR fallback.
- **SMS consent checkbox (Review step):** UNCHECKED by default + the EXACT registered A2P wording ("Yes, please text me. I agree to receive text messages from Window & Solar Care about my appointments, service, and account… Reply STOP to opt out, HELP for help. Consent is not a condition of purchase."). Do NOT pre-check it or reword it — the server stores consent PROOF quoting that exact text, and carriers/Twilio require unchecked + affirmative. Spec: [[project_booking_sms_optin_a2p]].

**Testing note:** never submit the live page to test (it creates a real contact + SO). Test the confirmation/upsell by loading the page and replacing the `LIVE` host regex in a document.write copy.

Related: [[project_wscare_pro_email_routing]], [[reference_domain_dns_hosting_map]], [[project_wsc_address_do_not_publish]].
