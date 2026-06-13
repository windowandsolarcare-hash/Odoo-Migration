# Odoo Server Action: "Saunders: Email Invoice to HOF"
# Model: account.move (id 534)
# Triggered from the Render printing tracker one-tap "Send Invoice" button via
#   ir.actions.server run with context {active_id: <inv_id>, active_model: 'account.move', hof_po: '043859', hof_to: '<override recipients, optional for testing>'}
#
# Renders the invoice PDF server-side (XML-RPC can't call _render_qweb_pdf), attaches it,
# and emails it to the HOF AP recipients using the proven 2026-05-09 template.
# Odoo 19 server-action rules: no imports, no docstrings, datetime is the module,
# no 'response'/'result' var names, end with action = False, no HTML in chatter.

move = env['account.move'].browse(env.context.get('active_id'))
if move and move.move_type == 'out_invoice':
    if move.state == 'draft':
        move.action_post()

    pdf_data = env['ir.actions.report']._render_qweb_pdf('account.report_invoice', move.ids)[0]

    att = env['ir.attachment'].create({
        'name': 'Invoice_%s.pdf' % move.name,
        'type': 'binary',
        'raw': pdf_data,
        'mimetype': 'application/pdf',
    })

    po = env.context.get('hof_po') or ''
    to_addr = env.context.get('hof_to') or 'bhatton@baseballhall.org, retailinvoices@baseballhall.org'
    subject = 'Invoice #%s' % move.name
    if po:
        subject = 'Invoice #%s — PO #%s' % (move.name, po)

    body = (
        '<p>Attached is our invoice #%s%s. Please pay at your convenience. '
        'Also please note our NEW remittance address:</p>'
        '<p>Saunders Printing<br>41995 Boardwalk Ste J<br>Palm Desert, CA 92211</p>'
        '<p>Thank You,</p>'
        '<p>Dan Saunders<br>Saunders Printing<br>dan@scenicartprint.com<br>800-283-8765</p>'
    ) % (move.name, (' for your PO #%s' % po) if po else '')

    mail = env['mail.mail'].create({
        'subject': subject,
        'email_from': 'Dan Saunders <dan@scenicartprint.com>',
        'reply_to': 'dan@scenicartprint.com',
        'email_to': to_addr,
        'body_html': body,
        'attachment_ids': [(6, 0, [att.id])],
        'auto_delete': False,
    })
    mail.send()

    # Silent copy to DJ — Odoo 19 has no BCC field, so send as a separate mail.mail.
    copy_mail = env['mail.mail'].create({
        'subject': '[COPY] ' + subject,
        'email_from': 'Dan Saunders <dan@scenicartprint.com>',
        'reply_to': 'dan@scenicartprint.com',
        'email_to': 'windowandsolarcare@gmail.com',
        'body_html': body,
        'attachment_ids': [(6, 0, [att.id])],
        'auto_delete': False,
    })
    copy_mail.send()

    move.message_post(body='✅ Invoice emailed to %s (silent copy to windowandsolarcare@gmail.com) | Subject: %s' % (to_addr, subject))

action = False
