---
name: project_payment_link_nameerror
description: "payments.py /api/stripe/payment_link crashed with NameError '_force_lines_deliverable' for any job WITHOUT an existing invoice — broke Send Stripe Link + Charge at Door. Fixed 2026-08-13 by importing it from field.py."
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
  modified: 2026-08-14T01:31:22.381Z
---

**Bug (found 2026-08-13):** `POST /owner/api/stripe/payment_link` (routers/owner/payments.py) returned `{ok:false, error:"name '_force_lines_deliverable' is not defined"}` whenever the SO had NO existing draft/posted invoice — i.e. the normal case at point of payment. It hit the `if not inv:` branch and called `_force_lines_deliverable(so_id)`, but that helper is defined in **routers/owner/field.py** (~L3138) and was NEVER imported into payments.py. So BOTH the field-app "Send Stripe Link" (Record Payment → Stripe method → button) AND "💳 Charge Card at Door" silently failed — the button appeared to do nothing (frontend showed only a small error status). This is why DJ's link to customer Bart "didn't go": no draft invoice, no SO chatter, no text — the backend threw before creating anything.

**Fix:** added an inline import right before the call (matches this repo's circular-import-avoidance pattern, e.g. reactivation.py's `from routers.owner.new_job import _next_job_name`):
```
if not inv:
    from routers.owner.field import _force_lines_deliverable
    _force_lines_deliverable(so_id)
```
field.py does NOT import payments.py, so no circular risk; field.py is already loaded by the app.

**How to apply / verify:** `_force_lines_deliverable(so_id)` forces `qty_delivered=product_uom_qty` on real lines so the delivered-basis invoice wizard doesn't refuse "No items available to invoice" (idempotent; skips qty=0/price=0 soft-deletes + display_type lines). To test the endpoint end-to-end: `POST https://wsc-field-assistant.onrender.com/owner/api/stripe/payment_link` JSON `{so_id, amount}` (endpoint does NOT check access_code) → expect `{ok:true, url, sms_body, invoice_id, phone}` and a new DRAFT invoice on the SO (marked narration=STRIPE_PENDING, auto-cleaned by daily cron if abandoned). NOTE: creating a link mutates (draft invoice + chatter). **Send behavior CHANGED 2026-08-13:** "Send Stripe Link" USED to open the phone's native sms composer (sms: URI) → text went from DJ's PERSONAL cell. DJ wanted it from the BUSINESS line. Now `doStripeLink()` (v2_field.html) POSTs to the new **`/owner/api/stripe/send_sms`** (payments.py) which texts the link via `sms._send_sms` → goes out on the **WSC Sender messaging service (pinned to 760-334-5355)**, server-side, and logs to SO chatter ("💳📱 …texted…from the business line"). The endpoint normalizes the Odoo raw phone (e.g. "2069154331") to E.164 (+1…) before sending (raw 10-digit would fail Twilio). So payment-link texts NOW appear in Twilio logs from 5355. See [[project_stripe_payment_methods]] and [[project_twilio_port_complete]] (pool pinned to 5355).
