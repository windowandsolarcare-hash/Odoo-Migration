---
name: project_thumbtack_proxy_numbers
description: "Thumbtack proxy/masked customer numbers ARE a usable permanent channel because DJ's Twilio number is registered to the Thumbtack account — store the proxy as the customer's phone; getting the real number is optional."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T06:18:18.878Z
---

**Established 2026-08-21 (new Thumbtack lead Bob Lis; DJ corrected Lead's wrong assumption).** Thumbtack assigns each lead a **masked proxy phone number** (e.g. Bob's `(256) 645-4462` — an Alabama area code, NOT the customer's real cell in Rancho Mirage). Calls/texts to the proxy route to the customer ONLY from a phone **registered to the Thumbtack account**.

**★ KEY FACT: DJ has REGISTERED his Twilio (business) number with Thumbtack.** So our app's automation (Twilio `messaging.send` — confirmations, ETA, pay-link texts) DOES reach Thumbtack-proxy customers, and their replies come back as a normal thread. **Do NOT claim "our Twilio can't reach the proxy"** — that was Lead's wrong assumption on 2026-08-21; DJ corrected it. The proxy is a **working, PERMANENT two-way text channel** (Thumbtack numbers don't expire).

**BEST-PRACTICE WORKFLOW for a Thumbtack lead:**
- Just **store the Thumbtack proxy number as the customer's `phone`** (person + property) — automation works through it. Capturing the customer's REAL cell is **optional** (nice if volunteered, not required).
- **EMAIL is separate** — the proxy is text/call only, so a real EMAIL is still needed for email pay-links/invoices.
- **Refund nuance:** asking for a real number / going off-platform BEFORE the customer responds forfeits Thumbtack's 72-hr no-response refund on that paid lead. Moot once they've engaged (replied/booking).
- **Only fragility (researched 2026-08-21):** proxy numbers are POOLED + RECYCLED (Twilio-masking model — one number serves many pro↔customer pairs via "sessions"; released back to the pool when a relationship goes dormant). So they're "permanent WHILE your Thumbtack account is ACTIVE," NOT permanent forever. If DJ stops paying / deactivates Thumbtack, Bob's proxy number very likely STOPS routing and gets reassigned to another pro-customer pair. (Thumbtack doesn't officially document the cancel behavior — this is inference from how masking works, the safe assumption.) ⇒ **The proxy is a free channel we don't OWN.** Practical rule: run on the proxy while paying Thumbtack; but BEFORE ever winding down / pausing Thumbtack long-term, do a sweep to capture REAL phone+email for all Thumbtack customers so none go dark. This is the concrete reason to eventually convert TT leads into our own contact info.

**Bob Lis setup (reference):** person 27192, property 27193 (29 Victoria Falls Drive, Rancho Mirage 92270, gate "Lis", Desert), job SO **264956** Solar Panel Cleaning $200 scheduled Mon 2026-08-24 08:00 PT. Phone = proxy `2566454462`. Created via direct Odoo RPC (Lead) — new post-Workiz SO name from the 26xxxx sequence (max+1). Related: [[project_thumbtack_automation]] (auto-responder), [[project_new_order_parked_surfacing]].
