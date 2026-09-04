---
name: project_website_cutover_dns
description: "Website cutover DNS state (2026-09-03): windowandsolarcare.com moved off old WordPress to the Odoo site. DreamHost site DEACTIVATED (DNS-Only, reversible); www CNAME → window-solar-care.odoo.com is LIVE + propagated. Apex still TODO."
metadata:
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-04T02:51:48.372Z
---

**Cutover of windowandsolarcare.com from the old WordPress site → the new Odoo site (`window-solar-care.odoo.com`). Executed live by Lead 2026-09-03 (DJ authorized each outward step).**

**DNS hosting:** DreamHost (ns1/2/3.dreamhost.com). **No MX** — email is @gmail.com, untouched.

**What was done (DreamHost panel → Manage DNS):**
1. Tried to add `www` CNAME → blocked: *"The record cannot co-exist with another record"* because DreamHost was **fully hosting** the domain (old WP site on A → 173.236.255.144). CNAME on a hosted `www` is refused.
2. Clicked **Deactivate Website** (DJ approved). DreamHost confirmed this is **reversible + non-destructive**: does NOT cancel the hosting plan, does NOT delete files, does NOT remove DNS records, email/MX intact. Domain is now **"DNS Only"**. Can be set back to Fully Hosted from Manage Websites.
3. After deactivation, submitted the pending record. **`www` → CNAME → `window-solar-care.odoo.com`** is now in Custom Records and **applied**.

**★ VERIFIED PROPAGATED (both public resolvers, 2026-09-03):** Cloudflare + Google DoH both return `www.windowandsolarcare.com` CNAME → `window-solar-care.odoo.com` → A `104.154.179.196` (Odoo/GCP). DreamHost TTL = 5 min; propagation took only a few minutes. **How to check headlessly:** `curl -s -H "accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=www.windowandsolarcare.com&type=CNAME"` (and `dns.google/resolve?...`).

**Sequence is DNS-FIRST (Web flagged, confirmed):** DNS must resolve to Odoo BEFORE clicking Odoo's **Verify → "I confirm, it's done"**, because Odoo issues the Let's Encrypt cert via ACME which needs the hostname already pointing at Odoo.

**REMAINING TODO:**
- **DJ:** click **Verify → "I confirm, it's done"** in the Odoo panel (accounts.odoo.com → database → Domain Names) → SSL provisions (~mins). Expect a brief cert warning on https until then.
- **Apex** (`windowandsolarcare.com`, no www): still has the old A → 173.236.255.144 (now dead post-deactivation). Need `apex → www` handling — CNAME can't sit on root (use DreamHost **ALIAS** → odoo, or a URL redirect apex→https://www). Coordinate with Web on whether Odoo should also carry the apex. **www is the canonical Odoo domain.**
- **Web:** after SSL live, flip `website.domain = https://www.windowandsolarcare.com`, re-verify the 52 redirects + canonicals (see [[project_twilio_a2p_registration_facts]] cutover-safe note, and the [[project_localbusiness_schema_todo]] + legal-name tasks).
- **DreamHost AutoPay card is EXPIRED** (banner) — DJ to update so the account doesn't lapse.
