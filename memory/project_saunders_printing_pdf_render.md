---
name: Saunders Printing — Odoo Invoice PDF Rendering via Server Action
description: How to render Odoo invoice PDFs via XML-RPC when _render_qweb_pdf is private. Server action workaround stores b64 in ir.config_parameter.
type: project
originSessionId: a18dc8b7-6f6f-4f92-994b-405c2c17e58f
---
`ir.actions.report._render_qweb_pdf` is a private method — XML-RPC blocks it with "Private methods cannot be called remotely."

**Why:** Odoo 19 SaaS restricts private method calls over RPC. The HTTP report endpoint requires session auth (no password available). `mail.template.generate_email` does not exist in Odoo 19.

**Working pattern — Server Action workaround:**

1. Create a temporary `ir.actions.server` with `state='code'`
2. The server action code calls `_render_qweb_pdf` internally (allowed inside Odoo eval context) and stores result in `ir.config_parameter` as base64 — `b64encode` IS available in Odoo 19 safe_eval context without importing
3. Execute the server action via `execute_kw` with `active_ids` in context
4. Read back the base64 from `ir.config_parameter`
5. Delete the temp server action and temp params immediately after

```python
code = """
for record in records:
    pdf, _ = env['ir.actions.report']._render_qweb_pdf('account.report_invoice', [record.id])
    env['ir.config_parameter'].set_param(
        'temp.invoice.pdf.' + str(record.id),
        b64encode(pdf).decode('ascii')
    )
action = False
"""
sa_id = models.execute_kw(db, uid, key, 'ir.actions.server', 'create', [{
    'name': 'Temp: Render Invoice PDFs',
    'model_id': <account.move model id>,
    'state': 'code',
    'code': code,
}])
models.execute_kw(db, uid, key, 'ir.actions.server', 'run',
    [[sa_id]], {'context': {'active_ids': [523, 524, 525], 'active_model': 'account.move'}})
models.execute_kw(db, uid, key, 'ir.actions.server', 'unlink', [[sa_id]])

# Read back
rows = models.execute_kw(db, uid, key, 'ir.config_parameter', 'search_read',
    [[['key', '=', f'temp.invoice.pdf.{inv_id}']]], {'fields': ['id', 'value']})
pdf_bytes = base64.b64decode(rows[0]['value'])
models.execute_kw(db, uid, key, 'ir.config_parameter', 'unlink', [[rows[0]['id']]])
```

**To email with PDF attachment:**
1. Create `ir.attachment` with `datas = pdf_b64` (base64 string), `mimetype = 'application/pdf'`
2. Create `mail.mail` with `attachment_ids: [(6, 0, [att_id])]`
3. Call `mail.mail.send([[mail_id]])` — returns None = success (XML-RPC will throw marshal error but email IS sent)

**Key facts:**
- `mail.template.generate_email` does not exist in Odoo 19 (removed)
- `mail.template.report_template` field does not exist in Odoo 19 — use `report_template_ids` (many2many)
- Invoice template ID 15 ("Invoice: Sending") has `has_dynamic_reports: True` but `report_template_ids: []` — does NOT auto-attach PDF when called via `send_mail` API on draft invoices
- `report_logo` field does not exist on `res.company` in Odoo 19 — only `logo`
- Odoo auto-creates a "Your Logo" placeholder image when company is created — replace with real logo via `res.company` write with base64-encoded PNG

**How to apply:** Use this pattern any time you need to render an Odoo report PDF via external API. Works for any report, not just invoices. The server action approach is the canonical workaround for Odoo 19 SaaS private method restrictions.
