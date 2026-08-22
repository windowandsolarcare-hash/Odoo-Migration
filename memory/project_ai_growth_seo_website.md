---
name: project_ai_growth_seo_website
description: "STRATEGY (planning, not started 2026-06-11): AI-heavy growth/SEO direction. DJ wants to convert WordPress site → Odoo Website module, then AI-driven SEO. Review engine is the first independent build. Gemini Pro Business features = DJ's by-hand CMO track."
metadata:
  node_type: memory
  type: project
  originSessionId: c0973c3f-5a8d-4598-9d90-206422a88ce0
---

**Direction set 2026-06-11 (DJ "not ready to build yet" — this is the plan).** DJ has Gemini Pro, wants to automate the top of the funnel (getting found + reviews) the way ops is already automated. Triggered by Google's Jun-2026 Gemini Business features (GBP connect + Business notebooks).

## Two tracks (keep separate)
- **Track A — Gemini app (DJ operates by hand, no build):** the new Gemini GBP-connect + Business notebooks are *consumer-app* features with **no API** to bolt into Render. They make DJ faster as CMO: review replies in brand voice, GBP posts, monthly profile insights, pricing/positioning by city, campaign ideation. Setup = connect Google Business Profile to his Gemini Pro. Recommend he just does this.
- **Track B — we build into Render/Odoo (24/7, integrated):** the data-grounded automations only our stack can do because we own the live job data + the "Done" event + Twilio SMS + field photos.

## Highest-ROI first build: REVIEW ENGINE (independent of website)
Auto-SMS a Google review link a few hours after each `x_studio_x_studio_workiz_status='Done'` job. Review velocity = #1 local-SEO lever for home services. We own the trigger; reuses reactivation/Twilio plumbing (A2P registered — see [[project_twilio_a2p_and_entity]]). **Not blocked by the website migration — can go first whenever DJ says go.** Gemini (Track A) then drafts the responses.

## Website: WordPress → Odoo Website module (DJ's chosen foundation)
**Verified 2026-06-11 on window-solar-care.odoo.com — modules already INSTALLED:** `website`, `mass_mailing` (Email Marketing), `marketing_automation`, `social_media`. Available but UNINSTALLED: `website_blog`, `website_crm` (Contact Form), `website_links`, `website_sale` (eCommerce). So Website is already on his plan — **no new app cost**.
- Why move the site into Odoo: today the WP site is an island (no access to jobs/customers/revenue, needs plugin glue). In Odoo, **Claude can generate AND publish SEO pages/blog via the same JSON-RPC**, grounded in real data; contact form → `crm.lead` feeds reactivation/booking; email+social+automation already installed. One brain (DJ's whole philosophy).
- **Migration roadmap:** (1) inventory current WP page/URL list, (2) rebuild in Odoo Website (block-based; can't import WP theme — rebuild), (3) **⚠ 301-redirect every old URL → new Odoo URL or lose existing Google rankings** (Odoo supports natively), (4) point domain/DNS at Odoo, (5) then turn on programmatic per-city × per-service landing pages + auto-blog + GBP feeds.
- **Need from DJ when go:** current WP URL list (redirect map), domain/DNS access, branding to carry over.

## Other Track-B AI plays (ranked, after review engine + site move)
1. GBP **API** auto-posting (weekly posts/FAQ from real job data — distinct from the Gemini app).
2. Programmatic local-SEO landing pages (cities: Palm Springs, Palm Desert, Rancho Mirage, Indian Wells, Cathedral City, Indio, La Quinta, Hemet × window/solar/gutter).
3. Photo→content pipeline (field before/after photos → captioned GBP/social posts; photos already captured, unused).

## Architecture guardrails (from CLAUDE.md)
No new Odoo seats, no custom models, one Odoo instance, all features scale across the 3 companies.
