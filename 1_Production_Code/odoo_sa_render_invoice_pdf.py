# Odoo Server Action: "Saunders: Render Invoice PDF to Attachment"
# Model: account.move (id 534)
# Called by the printing tracker "View Invoice" endpoint via ir.actions.server run
#   with context {active_id: <inv_id>, active_model: 'account.move'}.
# Renders the (draft or posted) invoice to PDF and stores it as a single ir.attachment
# on the move so the Render app can stream it. Does NOT post or email. View-only.
# Odoo 19 server-action rules: no imports, datetime is the module, end with action = False.

move = env['account.move'].browse(env.context.get('active_id'))
if move and move.move_type == 'out_invoice':
    pdf_data = env['ir.actions.report']._render_qweb_pdf('account.report_invoice', move.ids)[0]
    fname = 'Invoice_%s.pdf' % (move.name or move.id)
    old = env['ir.attachment'].search([
        ('res_model', '=', 'account.move'),
        ('res_id', '=', move.id),
        ('name', '=', fname),
    ])
    if old:
        old.unlink()
    env['ir.attachment'].create({
        'name': fname,
        'type': 'binary',
        'raw': pdf_data,
        'mimetype': 'application/pdf',
        'res_model': 'account.move',
        'res_id': move.id,
    })

action = False
