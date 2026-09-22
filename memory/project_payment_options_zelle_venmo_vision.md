---
name: project_payment_options_zelle_venmo_vision
description: "DJ's payment-options roadmap vision (2026-09-21): a branded customer payment page that breaks out Zelle vs Venmo (separate sections/buttons per method) + an outbound payment-request message offering BOTH options. Inbound method-detection is already done. To scope AFTER the Venmo journal fix; pairs with per-method journal routing."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-22T00:19:52.626Z
---

**DJ's payment-options vision (relayed via Operator→Dispatcher 2026-09-21). NOT urgent — design + sequence AFTER the Venmo journal fix Specialists is building; Lead scopes the plan + flags Dispatcher when ready.** Three parts:

1. **Branded customer PAYMENT PAGE with Zelle-vs-Venmo breakout:** extend the existing "copy my Zelle info" branded page to have SEPARATE sections/buttons per method — "paying by Zelle? here's the info/buttons" and "paying by Venmo? here's the info/buttons" — so the customer picks their method cleanly. (The Zelle page already exists; this adds a Venmo section + a method chooser.)
2. **Outbound PAYMENT-REQUEST MESSAGE offering BOTH options:** like DJ's old Workiz combined text ("Zelle → this info / Venmo → this info"), customer responds/pays. This is the customer-facing OUTBOUND side.
3. **Inbound method-detection is ALREADY DONE** (Venmo detection confirmed working) — the hard part. This work is only the customer-facing outbound side.

**Pairs with the per-method JOURNAL ROUTING (DJ-corrected 2026-09-21):** ★ Zelle does NOT get its own journal — Zelle payments deposit straight into CHASE (journal 6, BNK1) like a normal deposit, so **Zelle STAYS j6, NOT j19**. **ONLY Venmo breaks out** to its own journal (29, VENMO) + its own report bucket, because Venmo funds sit in a separate Venmo account (DJ manually transfers Venmo→Chase). So the flow: customer picks method → pays → inbound detects → Venmo posts to j29, Zelle posts to j6 (Chase). (The CLAUDE.md journal table's old "Zelle=j19→Zelle bucket" line is WRONG for the payment flow — corrected in the bible.) The customer-facing page still offers Zelle vs Venmo (unchanged) — only the INTERNAL journal mapping has Zelle=Chase. Owner of the payment page + booking/customer-portal branded pages = Specialists/Portal. See [[project_branded_receipt_page]], [[feedback_ported_means_twilio]].
