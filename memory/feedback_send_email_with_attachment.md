---
name: How to send email with PDF attachment via Odoo JSON-RPC
description: Exact pattern for creating and sending an email with a file attachment through Odoo mail.mail using JSON-RPC (not XML-RPC)
type: feedback
originSessionId: 936707e4-1c52-44fd-bcfd-9208535c32e1
---
# Sending Email with Attachment via Odoo

Use JSON-RPC (not XML-RPC — XML-RPC fails because `send` returns None which can't be marshaled).

**Why:** XML-RPC raises `TypeError: cannot marshal None` when `mail.mail.send()` returns None. JSON-RPC handles None gracefully.

**How to apply:** Use this pattern any time you need to send an email with or without an attachment from a local Python script.

```python
import requests, base64

ODOO_URL = 'https://window-solar-care.odoo.com'
ODOO_DB = 'window-solar-care'
ODOO_USER_ID = 2
ODOO_API_KEY = '7e92006fd5c71e4fab97261d834f2e6004b61dc6'

def rpc(model, method, args, kwargs=None):
    payload = {
        'jsonrpc': '2.0', 'method': 'call', 'id': 1,
        'params': {
            'service': 'object', 'method': 'execute_kw',
            'args': [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args, kwargs or {}]
        }
    }
    r = requests.post(f'{ODOO_URL}/jsonrpc', json=payload)
    result = r.json()
    if 'error' in result:
        raise Exception(result['error']['data']['message'])
    return result.get('result')  # use .get() — send() returns None, that's normal

# Read and base64-encode the file
with open(r'C:\path\to\file.pdf', 'rb') as f:
    file_data = base64.b64encode(f.read()).decode()

# Create the mail record with attachment inline
mail_id = rpc('mail.mail', 'create', [{
    'subject': 'Your subject here',
    'email_to': 'recipient@example.com',
    'email_from': 'windowandsolarcare@gmail.com',
    'body_html': '<p>HTML body here</p>',
    'attachment_ids': [(0, 0, {
        'name': 'Filename.pdf',
        'datas': file_data,
        'mimetype': 'application/pdf',
    })],
}])

# Send it — returns None, that's expected
rpc('mail.mail', 'send', [[mail_id]])
```

**Verification:** After sending, Odoo deletes the mail record from the queue. If `search_read` for that mail_id returns None, the email was sent successfully — not an error.

**PDF generation:** Use `reportlab` (already installed). Generate the PDF locally, then attach via the pattern above.
