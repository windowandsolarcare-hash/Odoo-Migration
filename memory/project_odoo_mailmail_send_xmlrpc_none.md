---
name: project_odoo_mailmail_send_xmlrpc_none
description: "Odoo mail.mail send() over XML-RPC ALWAYS throws \"cannot marshal None\" on return but the send SUCCEEDS — verify state, never auto-retry (retry = duplicate email)."
metadata:
  node_type: memory
  type: project
  originSessionId: e3071731-f37a-4440-a358-34be556223c2
  modified: 2026-10-03T08:27:47.287Z
---

Sending email via Odoo `mail.mail` over XML-RPC (`xmlrpc/2/object` execute_kw, 'mail.mail','send',[[id]]) from a local Python script, 2026-10-03:

- **`send()` returns None, and Odoo's server-side `OdooMarshaller(allow_none=False)` refuses to serialize None in the XML-RPC RESPONSE** → the call raises `xmlrpc.client.Fault: <Fault 1: ... TypeError: cannot marshal None unless allow_none is enabled>`. **Setting `allow_none=True` on the CLIENT ServerProxy does NOT fix it** — the refusal is server-side on the response, not the request.
- **The exception is NOT a failure.** `create` + `send` execute server-side BEFORE the None return, so the email actually goes out. The CLAUDE.md note "Returns None = success" is this.
- **How to apply:** wrap the `send()` call in try/except and swallow the None-marshal Fault, THEN confirm by reading the record: `mail.mail.read([id],['state','failure_reason'])` → `state == 'sent'` and `failure_reason == False` = delivered. Do NOT treat the exception as a reason to re-run the whole script.
- **★ DUPLICATE-SEND TRAP:** a shell `python ... || python3 ...` fallback (or any auto-retry on the nonzero exit) re-runs the WHOLE script after the harmless Fault → creates a SECOND mail.mail + SECOND send → the recipient gets TWO identical emails (hit 2026-10-03: DJ got 2 copies of the candidate email). Never chain a retry on a mail-send script; run it ONCE, then verify by state.
- Set `email_from='windowandsolarcare@gmail.com'` (see [[feedback_wsc_email_from_domain]]); attach PDFs by creating ir.attachment ({name,datas=b64,mimetype,type:'binary'}) then mail.mail attachment_ids=[(6,0,ids)] (see [[feedback_send_email_with_attachment]]).
