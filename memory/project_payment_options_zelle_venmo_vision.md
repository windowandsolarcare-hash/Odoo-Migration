---
name: project_payment_options_zelle_venmo_vision
description: "DJ's payment-options roadmap vision (2026-09-21): a branded customer payment page that breaks out Zelle vs Venmo (separate sections/buttons per method) + an outbound payment-request message offering BOTH options. Inbound method-detection is already done. To scope AFTER the Venmo journal fix; pairs with per-method journal routing."
metadata:
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-22T00:16:45.935Z
---

**DJ's payment-options vision (relayed via Operator→Dispatcher 2026-09-21). NOT urgent — design + sequence AFTER the Venmo journal fix Specialists is building; Lead scopes the plan + flags Dispatcher when ready.** Three parts:

1. **Branded customer PAYMENT PAGE with Zelle-vs-Venmo breakout:** extend the existing "copy my Zelle info" branded page to have SEPARATE sections/buttons per method — "paying by Zelle? here's the info/buttons" and "paying by Venmo? here's the info/buttons" — so the customer picks their method cleanly. (The Zelle page already exists; this adds a Venmo section + a method chooser.)
2. **Outbound PAYMENT-REQUEST MESSAGE offering BOTH options:** like DJ's old Workiz combined text ("Zelle → this info / Venmo → this info"), customer responds/pays. This is the customer-facing OUTBOUND side.
3. **Inbound method-detection is ALREADY DONE** (Venmo detection confirmed working) — the hard part. This work is only the customer-facing outbound side.

**Pairs with the per-method JOURNAL ROUTING** (Zelle→Zelle journal id=19, Venmo→Venmo journal id=29 — see CLAUDE.md journal table) so the whole Zelle-vs-Venmo flow is correct end-to-end (customer picks method → pays → inbound detects → posts to the right journal). Owner of the payment page + booking/customer-portal branded pages = Specialists/Portal. See [[project_branded_receipt_page]], [[feedback_ported_means_twilio]].
