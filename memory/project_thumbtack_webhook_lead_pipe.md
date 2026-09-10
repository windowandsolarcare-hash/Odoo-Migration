---
name: project_thumbtack_webhook_lead_pipe
description: "Thumbtack has a native FREE one-way webhook (Apps -> Manage webhooks) that sends leads (name+phone, NO email)/messages/reviews to any URL — additive, coexists w/ partner apps. DJ's dead Workiz integration still shows 'Connected' and CANNOT be self-disconnected on Thumbtack. Spec to pipe TT leads into the live app: THUMBTACK_WEBHOOK_BRIEF.md."
metadata:
  node_type: memory
  type: project
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-10T20:58:17.128Z
---

**Discovered 2026-09-10 (DJ asked to look at his Thumbtack Apps screen; DJ gets most of his business via Thumbtack + Angie's).**

**The problem:** Thumbtack -> Apps still shows the **Workiz** partner integration as "Connected" ("Thumbtack leads and messages are being sent to your account"). Workiz went dark 2026-08-03, so DJ's Thumbtack leads/messages have been flowing into a dead system.

**Key facts (confirmed on DJ's live account + Thumbtack help):**
- Thumbtack has **NO self-serve disconnect** for a connected partner app. The Workiz card's only control is "Go to partner site" (routes to dead Workiz). Disconnect normally happens on the PARTNER's side (impossible — Workiz is dark) or by contacting Thumbtack support / teampartnerships@thumbtack.com. NOT urgent — see next.
- Thumbtack has a native, **FREE, one-way webhook**: Apps -> bottom "Webhooks" card -> **Manage webhooks** -> **Create webhook** (`thumbtack.com/pro/webhooks/list`). Was EMPTY (none set up). Also a "Developer Portal" low-code option next to it.
- Webhook sends **leads (customer NAME + PHONE only, NO email), messages, or reviews** to any URL you choose. **Match res.partner by PHONE**, not email.
- It is **ADDITIVE** — "you can use it with other tools," so it coexists with the dead Workiz link. **No Workiz disconnect is needed to capture leads.**
- Auth field default = **None**; protect the endpoint with a **secret token in the URL path** (STOP-webhook style). One webhook per business profile. Has a "Test this webhook" button + "Recent deliveries" log; test leads are tagged "test lead".
- Thumbtack marks any non-200 as "Failure" and retries; a URL edited by one char fails.

**How to apply / the plan:** capture Thumbtack leads into the LIVE app via the webhook. Recommended: a namespaced native endpoint `POST /webhooks/thumbtack/<secret>` (log raw body first -> skip test leads -> match partner by phone `company_id in [1,False]` -> create crm.lead company 1, source "Thumbtack" -> surface in lead inbox + My Day so DJ SEES it -> idempotent on TT lead id -> 200). Fallback = TT -> Zapier catch hook -> Odoo (Thumbtack-documented; DJ already runs Zapier). Sequencing is chicken-and-egg (need the real payload shape): build log-first endpoint, DJ registers URL + hits Test, read shape, then finalize parser. **Full build brief:** `saunders-render-app/3_Documentation/THUMBTACK_WEBHOOK_BRIEF.md`. Handed to Specialists via AGENT_MAIL 2026-09-10.

Related: [[project_workiz_retirement]] (Workiz dead), [[feedback_ported_means_twilio]].
