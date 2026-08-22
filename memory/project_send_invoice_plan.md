---
name: project_send_invoice_plan
description: "Send-invoice-to-customer plan (DJ wants: pay-link + PDF invoice, email or text). Pay-link+email EXISTS; text = small add; PDF = the hard part (Odoo 19 locks PDF render over the API — use account.move.send / native invoice-send wizard)."
metadata:
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-04T02:30:18.504Z
---

DJ wants a "Send invoice" action on a (now-priceable) job: **create an invoice and email a PDF + a pay-link, OR text a pay-link to a portal.** Chose format = **pay-link + PDF invoice**. "Not very often but important." This is the last billing gap from the lifecycle map.

**What already EXISTS (reuse, don't rebuild — verified 2026-08-03 via Explore survey):**
- **`dashboard._create_stripe_tip_link(so_id, amount, shorten=True)`** = THE safe primitive. Creates/reuses a DRAFT `out_invoice` (no premature post, no charge) + returns `{ok,url,phone,email,customer,so_name,amount,sms_body,invoice_id}`. `url` = the customer-facing ITEMIZED pay page = the "portal" (`https://wscare.pro/owner/api/stripe/tip_page?...`, tip options + card pay via Stripe). Itemized from sale.order.line.
- **Email a pay-link (LIVE):** `POST /owner/api/stripe/send_email {so_id, tip_url, so_name, amount}` (dashboard.py:5270) — emails from `Window & Solar Care <windowandsolarcare@gmail.com>`. Also `POST /owner/api/billing/send_cc` (specialist_billing.py:608) = DJ-approved draft-first preview→send, parent-preferring email.
- **Text a pay-link (NOT wired, small):** `messaging.send(to=link['phone'], body=link['sms_body'], partner_id=<billing partner>, so_id=so_id, kind='invoice', idem=f'paylink:{so_id}')` — honors STOP/DNC/quiet-hold.
- **ROUTING:** dashboard.py registers before payments.py, so dashboard's stripe routes WIN; payments.py's dupes are DEAD except `payment_link` (only in payments.py). LIVE Stripe payment journal = **7** (cash/zelle/check = 6). LIVE `create_checkout` POSTS the invoice before pay + `cancel` doesn't void → abandoned checkout strands a posted-unpaid invoice (daily reaper is retired). Keep invoices DRAFT until paid where possible.

**The PDF = the hard part (Odoo 19 API lockdown — VERIFIED 2026-08-03):**
- `ir.actions.report._render_qweb_pdf` → **AccessError: private methods can't be called remotely.** Public `render_qweb_pdf` → AttributeError (gone). `sale.order._create_invoices` → private. `mail.template.generate_email` → doesn't exist in 19.
- Posted invoices do NOT auto-store a PDF ir.attachment (checked: none, message_main_attachment_id False).
- There IS an **"Invoice: Sending" mail.template id=15** (model account.move) + Odoo's **`account.move.send`** wizard / `account.move.action_invoice_sent` — the native send-&-print path that DOES render the PDF. That's the route to get the PDF, but it's wizard-based (create `account.move.send` with the move in context, call its send action) and sends via Odoo's mail server (verify from-address = windowandsolarcare@gmail.com per [[feedback_wsc_email_from_domain]]). Alternatively `mail.template.send_mail(15, move_id, {'force_send':False})` creates a queued mail.mail WITH the rendered PDF attachment → read its attachment datas → reuse in my own email, then unlink the queued mail (UNVERIFIED — send_mail may still be reachable; test on a throwaway posted invoice, not a real one).

**PLAN:** (1) ship pay-link email+text now (reuse above) = gets DJ paid + matches "email/text a link to a portal"; (2) PDF: wire `mail.template.send_mail(15, move_id, force_send=False)` → grab the PDF attachment → attach to MY email (W&SC from + pay-link) → unlink the queued Odoo mail; if that's blocked, use the `account.move.send` wizard. ALWAYS preview-before-send (money + customer). See [[project_so_full_start_time_edit]] (pricing the job — done), lifecycle map billing gap.

---
**BUILT (pay-link half) 2026-08-03.** `POST /api/job/send_invoice {so_id, method:'email'|'text', send, message?, force_now?}` in brain.py: `send:false`=PREVIEW (returns url/email/phone/customer/amount/sms_body/has_email/has_phone); `send:true` → EMAIL (mail.mail from `Window & Solar Care <windowandsolarcare@gmail.com>`, body = pay-link) or TEXT (`messaging.send`, kind='invoice', idem=`invoice:<so>`, honors STOP/DNC/quiet-hold). Reuses `dashboard._create_stripe_tip_link(so_id, amount)`. Frontend v2_field: "📧 Send invoice / pay-link" button under the line editor → preview panel (editable message + the pay-link + Email/Text buttons, always preview-first). Also: **line-items editor MOVED to the TOP of the Pricing section** (was at bottom). Verified on a CONFIRMED throwaway SO: preview returns wscare.pro pay page + contact; email sent (ok:true,via:email); text reached Twilio (twilio_failed only on the fake number = path OK). NOTE: `_create_stripe_tip_link` needs the SO **confirmed** (state sale) — a draft 500s "No items available to invoice" (real jobs are confirmed, fine). **PDF still TODO** (this sends the pay-link only; PDF attach = the Odoo-19 native-send fast-follow above).
