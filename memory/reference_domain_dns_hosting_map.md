---
name: reference_domain_dns_hosting_map
description: "★ WHERE EACH DOMAIN LIVES (DNS + hosting map) — DJ + sessions keep forgetting who manages what. wscare.pro = Cloudflare DNS → Render app. windowandsolarcare.com = DreamHost. scenicartprint.com = DreamHost (Saunders Printing). www.windowandsolarcare.com = CNAME → Odoo. Check HERE before touching any domain/DNS/SSL so you go to the right control panel."
metadata:
  node_type: memory
  type: reference
  originSessionId: 7a4f4487-5a08-47dc-8b9b-7761235acbe9
  modified: 2026-09-12T21:51:04.999Z
---

**Verified 2026-09-12 (live DNS/curl). Before changing ANY domain, DNS record, redirect, or SSL cert — come here first to know WHICH control panel to use.** DJ has forgotten "who Cloudflare is" more than once; this is the map.

## wscare.pro — the APP domain
- **DNS: Cloudflare** (nameservers rocky.ns.cloudflare.com / vivienne.ns.cloudflare.com). ← DNS records for wscare.pro + any subdomain (e.g. cheryl.wscare.pro) are added in **Cloudflare** (dash.cloudflare.com), NOT DreamHost.
- **Points to: Render** (216.24.57.x anycast) → the app service `wsc-field-assistant.onrender.com` (srv-d78le0fkijhs738dsli0). Custom domains are added in the **Render dashboard** (Settings → Custom Domains), which hands back a DNS target you then put in Cloudflare + Render auto-provisions SSL.
- Serves: the field app + owner ERP (`wscare.pro/owner/...`), booking (`wscare.pro/c/<token>`, `/book`), and **Cheryl's app (`wscare.pro/cheryl`)**. healthz 200.
- **cheryl.wscare.pro** (the separate-address / independent-login for Cheryl) = a NEW subdomain: add it in Render (custom domain) + Cloudflare (DNS record → the Render target). NOT set up yet as of 2026-09-12.

## windowandsolarcare.com — the marketing/brand domain (→ Odoo site)
- **Managed at: DreamHost** (panel.dreamhost.com). Registrar + DNS + the redirect + SSL all at DreamHost here.
- **apex `windowandsolarcare.com`**: a DreamHost **"Redirect"** entry → 301 to `https://www.windowandsolarcare.com/`, with a **free Let's Encrypt SSL** cert (added 2026-09-12 via panel → red-padlock → Add SSL → Select this Certificate; $0). Before the cert it served DreamHost's placeholder `sni.dreamhost.com` = the "not private" warning.
- **`www.windowandsolarcare.com`**: CNAME → `window-solar-care.odoo.com` (the Odoo website), Let's Encrypt cert. This is the live marketing site.

## scenicartprint.com — Saunders Printing (separate business)
- **Managed at: DreamHost** (Shared Unlimited hosting, server iad1-shared-b8-36; IP 173.236.255.144). Green lock / valid SSL.
- As of 2026-09-12 it returns **HTTP 403 "Access denied."** on both apex + www (a hosting/directory/permissions issue, NOT SSL) — pending DJ's steer on whether it should host a real site.

## Which panel for which change (quick key)
- Add/change a **wscare.pro subdomain or DNS** → **Cloudflare**. Add a **wscare.pro custom domain / see the app** → **Render**.
- Anything on **windowandsolarcare.com or scenicartprint.com** (redirect, SSL, hosting, DNS) → **DreamHost**.
- The **Odoo site** itself (content of www.windowandsolarcare.com) → Odoo (window-solar-care.odoo.com).
Related: [[project_calendly_retired]] (booking = wscare.pro), the app service IDs live in CLAUDE.md SYSTEM CONSTANTS.
