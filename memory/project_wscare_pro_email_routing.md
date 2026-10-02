---
name: project_wscare_pro_email_routing
description: "wscare.pro email (set up 2026-10-02): Cloudflare Email Routing FORWARDING only (no mailbox). dan@ + info@ -> windowandsolarcare@gmail.com; cheryl@ pending Cheryl's verify click (cjcherylcj@gmail.com). Free. MX/SPF/DKIM added in Cloudflare. Alias-domain-on-Workspace + ERP-inbox ideas ON HOLD."
metadata:
  node_type: memory
  type: project
  originSessionId: a6200401-4a1b-4492-894c-629c161de653
  modified: 2026-10-02T21:46:24.773Z
---

**State (Web, 2026-10-02), done live in DJ's Cloudflare via Chrome:**
- Cloudflare Email Routing enabled for **wscare.pro** (DNS is at Cloudflare; Render serves the app — separate records, app unaffected). Added 3 MX (route1/2/3.mx.cloudflare.net), 1 SPF TXT, 1 DKIM TXT (`cf2024-1._domainkey`). Records show "Locked". Verified MX live via DoH; wscare.pro/dw still 307.
- Routing rules (Active): **dan@wscare.pro** and **info@wscare.pro** -> **windowandsolarcare@gmail.com** (verified destination).
- **cheryl@wscare.pro: NOT created yet.** Destination **cjcherylcj@gmail.com** (Cheryl's REAL email — DJ confirmed; NOT markethouses@gmail.com, which is just the Odoo company-2 email) added as destination = **Pending** until Cheryl clicks Cloudflare's verification email. Then create rule cheryl@ -> that address (destination dropdown only lists VERIFIED addresses).
- Catch-all rule exists but is Disabled/Drop (left as is). Cost: Cloudflare Email Routing was free; no price prompt seen.
- Routing is RECEIVE/forward only — it is not a mailbox and cannot send. Sending as dan@wscare.pro needs a mailbox host or SMTP (Cloudflare "Email Sending" beta exists in the dashboard; not evaluated).

**DJ's goal:** a short address (not windowandsolarcare@gmail.com), not crowding that Gmail, ONE place to check, communication tool (him+customers+Cheryl), not promotional.

**Options discussed / ON HOLD (DJ 2026-10-02):**
- DJ already has Google Workspace for scenicartprint.com (dan@scenicartprint.com). Adding wscare.pro as a USER ALIAS DOMAIN is free per Google (user alias domains cost no extra per user; secondary domain = separate paid users). DJ said hold off. Doing it would REPLACE the Cloudflare MX with Google's (one MX set per domain).
- Standalone client (Thunderbird) = just a client; needs a mailbox (IMAP). Can unify several accounts in one inbox = the cheapest "one place to check".
- ERP-native inbox idea (DJ): build a customizable inbox in the app. Thoughts: build a LAYER (customer-linked threads, AI drafts, HUD cards), not a from-scratch mail client; Cloudflare Email Workers could ingest inbound to the app. Needs Lead/Specialists design; durable-foundation rule applies (surface shortcut-vs-durable). Not started.

Related: [[reference_domain_dns_hosting_map]] (wscare.pro = Cloudflare DNS + Render), [[project_wsc_address_do_not_publish]].
