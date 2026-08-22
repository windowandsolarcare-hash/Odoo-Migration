---
name: Saunders Printing Odoo Setup
description: Saunders Printing is company ID 3 in Odoo, 3rd multi-company alongside W&SC (1) and Cheryl Johnson (2)
type: project
originSessionId: a18dc8b7-6f6f-4f92-994b-405c2c17e58f
---
Saunders Printing is Odoo company ID 3. Created 2026-05-08.

**Why:** DJ runs Saunders Printing (also known historically as Scenic Art Print) as a separate business under Saunders Business Group. Needed separate P&L accounting without additional Odoo seats/cost.

**Company details:**
- Address: 41995 Boardwalk Ste. J, Palm Desert, CA 92211 (PO Box — use this, NOT Thousand Palms)
- Currency: USD
- 50 accounts auto-provisioned (full chart of accounts)
- 8 journals: Sales (INV, ID:21), Purchases (BILL, ID:22), Bank (BNK1, ID:26), MISC, CABA, EXCH, TAX, Salaries
- Key accounts: AR = ID 233 (Accounts Receivable), Revenue = ID 266 (Product Sales)
- DJ (user ID 2) has access — company_ids includes 1, 2, 3
- Sales journal (ID 21) has manual sequencing ENABLED — invoices use plain numeric names (200234, 200235...)

**Invoice numbering:**
- Continues from QuickBooks history. Last QB invoice was 200233.
- Odoo starts at 200234. Never reuse QB invoice numbers.

**Pricing structure (National Baseball Hall of Fame):**
- Plaque postcards: $0.18/card
- Local view postcards: $0.25/card
- Banding charge: $0.025/card (ALL HOF orders, banded in 50s)
- Freight: see freight table in CLAUDE.md or memory — table is in thousands of cards, prorate linearly between data points

**Freight table (# cards in thousands → total freight):**
1→$22.27, 2→$44.50, 3→$66.80, 4→$85.85, 9→$187.00, 12→$249.00, 15→$307.00, 18→$355.50, 20→$385.00, 25→$483.00, 30→$562.50, 32→$592.85

**Only customer so far:** National Baseball Hall of Fame
- Odoo partner ID: 26947
- Address: 25 Main St, Cooperstown, NY 13326, (877) 290-1300
- Ben Hatton = contact (bhatton@baseballhall.org)
- HOF invoice recipients: bhatton@baseballhall.org + retailinvoices@baseballhall.org (TO), windowandsolarcare@gmail.com (silent copy — send as separate mail.mail, no BCC field in Odoo 19)
- Invoices always come FROM dan@scenicartprint.com — configured via ir.mail_server ID 1, Gmail SMTP, app password set 2026-05-09

**Active invoices (all draft, pending DJ review before sending):**
- 200234 (Odoo ID 523): PO 043221, 3,000 plaque postcards, $681.80, invoice date 2/10/2026
- 200235 (Odoo ID 524): PO 043736, 17,000 plaque postcards, $3,824.33, invoice date 5/1/2026
- 200236 (Odoo ID 525): PO 043762, 4,000 local view postcards, $1,185.85, invoice date 5/1/2026

**Pending (not yet entered):**
- PO 043859 (Andre Dawson, 1,000 cards, $227.27) — not shipped, not entered into Zoo yet. Will become invoice 200237.

**Workflow steps per PO (Render tracker planned):**
1. PO received (email + PDF saved)
2. Estimate from Zoo (printing vendor)
3. Art changes to card backs (or fronts for special cases like Dawson)
4. Upload files to Zoo
5. Invoice customer
6. Receive payment

**QB Desktop migration:** Historical data from QuickBooks Desktop 2010. Low priority. Last invoice in QB was 200233. DJ has the QB file.

**How to apply:** When creating invoices for Saunders Printing, use company_id=3, journal_id=21, partner_id=26947 for HOF. Always use manual sequence numbers. NEVER send invoices without DJ approving draft first.
