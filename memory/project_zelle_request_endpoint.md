---
name: project_zelle_request_endpoint
description: POST /api/job/zelle_request — itemized Venmo/Zelle request text from a field job (services + total + Zelle handle + pay-page link); preview→send via messaging.send; arms paywatch via _mark_asked.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-06T00:30:10.752Z
---

**Built 2026-08-05 (specialist_billing.py) — my half of the lead's "Text Zelle request" field button.**

`POST /owner/api/job/zelle_request {so_id, send:bool, edited_body?}`:
- **send:false = PREVIEW** → `{ok, preview:true, text, to, name, amount, has_phone}`. Reads services from `order_line` (skips display_type section/note lines) + total from `amount_total` by so_id, resolves recipient phone off the CONTACT (parent-preferring, `_zelle_recipient`). Caller passes ONLY so_id.
- **send:true = SEND** → `messaging.send(to, body, partner_id, so_id, kind='zelle_request', idem='zelle:<so_id>')` (STOP/DNC/quiet-hours enforced) → `{ok, held}`. Then **`_mark_asked(so_id, so_name, name, amount, 'zelle')`** — THE arm helper (sets `wsc.billing.awaiting.<so_id>` + chatter + the awaiting glance card) so specialist_paywatch's Gmail watcher catches the payment and pops the record-payment card. `_mark_asked` IS the armer — never hand-set `wsc.billing.awaiting.*`.

**Text format** (`_zelle_request_text`): greeting + `• service` lines + `Total: $X` (`_fmt_amount`) + `Zelle: windowandsolarcare@gmail.com` + `Or tap to pay (Zelle or card): https://wscare.pro/owner/api/zelle/pay?so_id=<id>` (lead's pay page, public-whitelisted in authz) + signature. Reuses the canonical handle/amount-format/signature from the existing `_fill_template`; the itemized structure is new (the old template isn't itemized). Verified preview on SO 17389 → John & Dawson Bullock, $330, 2 service lines.

**Lead builds the field UI** (v2_field Process Payment button, preview→approve→send, per DJ's approve-first) + the branded Zelle pay page (already live). Endpoint is DJ-facing/PROTECTED. Related: [[project_send_invoice_plan]], [[project_quiet_hours_hold_queue]].
