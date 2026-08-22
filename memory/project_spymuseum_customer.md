---
name: project_spymuseum_customer
description: International Spy Museum = a Saunders Printing customer (no automation set up yet). AP/billing contact + the new billing-submission email RetailAP@spymuseum.org (effective 2026-06-25).
metadata: 
  node_type: memory
  type: reference
  originSessionId: 57a5d5b6-d220-4ead-9bfc-19b24ea92237
---

**International Spy Museum** is a **Saunders Printing** customer (Saunders Printing = separate company, Odoo company_id=3; emails come to **dan@scenicartprint.com**). No watcher/automation built for them yet (unlike NBHOF/HOF and Zoo) — this is just the customer record DJ wants on file. As of 2026-06-25 nothing is "set up" for them in the system.

**Billing / Accounts Payable (per their 2026-06-25 email "Update to Billing Submission Email Address"):**
- **Send ALL billing documents — invoices, credit memos, statements — to: `RetailAP@spymuseum.org`** (effective immediately).
- **STOP** sending billing docs to `hmurray@spymuseum.org` and `aemerson@spymuseum.org`.
- If you include the **associated buyer** on billing communications, keep doing so (CC the buyer).

**AP contact:** Hannah-May Murray (she/her), Accounts Payable Specialist — `hmurray@spymuseum.org`, office **202.654.0959**.
**Address:** International Spy Museum, 700 L'Enfant Plaza, SW, Washington, DC 20024. Site: spymuseum.org.

**How to apply:** When Saunders Printing eventually invoices the Spy Museum, the invoice/statement email must go to `RetailAP@spymuseum.org` (+ buyer CC if applicable), NOT to Hannah-May or aemerson. If/when a Spy Museum invoice flow is built (mirroring the HOF SA-1335 send), hard-code `RetailAP@spymuseum.org` as the AP recipient. Related Saunders Printing infra: [[project_hof_watcher_non_po_guard]], [[project_saunders_invoice_send_view]], [[project_zoo_printing_automation]], [[session_jun14_saunders_printing]].
