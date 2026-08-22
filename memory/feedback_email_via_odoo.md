---
name: Send emails via Odoo mail server
description: Use Odoo mail.mail JSON-RPC to send emails — not Gmail MCP (Gmail MCP can only draft, not send)
type: feedback
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
Always send emails via Odoo's mail server using `mail.mail` JSON-RPC, not the Gmail MCP.

**Why:** Gmail MCP can only create drafts, not send. Odoo has a configured outbound mail server and can send directly.

**How to apply:**
```python
mail_id = rpc('mail.mail', 'create', [{
    'subject': '...',
    'body_html': '<p>...</p>',
    'email_to': 'windowandsolarcare@gmail.com',
    'auto_delete': True,
}])
rpc('mail.mail', 'send', [[mail_id]])
# auto_delete=True means the record disappears after send — that's expected/success
# send() returns no result key in JSON-RPC response — that's normal, not an error
```

**Why:** DJ confirmed this is the standard approach going forward (2026-04-19).
