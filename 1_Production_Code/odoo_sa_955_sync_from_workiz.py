API_TOKEN = 'api_1hu6lroiy5zxomcpptuwsg8heju97iwg'

workiz_uuid = record.x_studio_x_studio_workiz_uuid
if not workiz_uuid:
    raise UserError('No Workiz UUID on this sales order.')

# ── Fetch Workiz job ──────────────────────────────────────────────────────────
_url = 'https://api.workiz.com/api/v1/' + API_TOKEN + '/job/get/' + str(workiz_uuid) + '/'
_resp = requests.get(_url, timeout=15)
if _resp.status_code != 200:
    raise UserError('Workiz API returned HTTP ' + str(_resp.status_code))
_raw = _resp.json()
if isinstance(_raw, dict) and 'data' in _raw:
    _d = _raw['data']
    job = _d[0] if isinstance(_d, list) and _d else _d
elif isinstance(_raw, list) and _raw:
    job = _raw[0]
elif isinstance(_raw, dict) and 'UUID' in _raw:
    job = _raw
else:
    raise UserError('Unexpected Workiz API response.')
if not job:
    raise UserError('No job data returned for UUID: ' + str(workiz_uuid))

log = []
updates = {}
_saved_ts = []

# ── Header fields ─────────────────────────────────────────────────────────────
_status    = str(job.get('SubStatus') or job.get('Status') or '')
_tech_list = [t.get('Name','') for t in (job.get('Team') or []) if t.get('Name')]
_tech      = ', '.join(_tech_list)
_gate      = str(job.get('gate_code') or job.get('GateCode') or '')
_pricing   = str(job.get('pricing') or job.get('Pricing') or '')
_notes     = str(job.get('JobNotes') or '')
_job_type  = str(job.get('JobType') or '')
_tos       = str(job.get('type_of_service_2') or '')
_source    = str(job.get('JobSource') or '')
_freq      = str(job.get('frequency') or '')

if _freq:     updates['x_studio_x_studio_frequency_so']         = _freq
if _status:   updates['x_studio_x_studio_workiz_status']       = _status
if _tech:     updates['x_studio_x_studio_workiz_tech']         = _tech
if _gate:     updates['x_studio_x_gate_snapshot']              = _gate
if _pricing:  updates['x_studio_x_studio_pricing_snapshot']    = _pricing
if _notes != str(record.x_studio_x_studio_notes_snapshot1 or ''):
              updates['x_studio_x_studio_notes_snapshot1']     = _notes
if _job_type: updates['x_studio_x_studio_x_studio_job_type']  = _job_type
if _tos:      updates['x_studio_x_studio_type_of_service_so'] = _tos
if _source:   updates['x_studio_x_studio_lead_source']        = _source

updates['x_studio_x_workiz_link'] = 'https://app.workiz.com/root/job/' + str(workiz_uuid) + '/'

# Date
_job_dt_str = str(job.get('JobDateTime') or '')
_job_start_utc = None
if _job_dt_str and len(_job_dt_str) >= 16:
    try:
        _dt = datetime.datetime.strptime(_job_dt_str[:16], '%Y-%m-%d %H:%M')
        _off = 7 if 3 <= _dt.month <= 11 else 8
        _dt_utc = _dt + datetime.timedelta(hours=_off)
        _job_start_utc = _dt_utc.strftime('%Y-%m-%d %H:%M:%S')
        updates['date_order'] = _job_start_utc
        log.append('Date: ' + _job_dt_str + ' PT')
    except Exception as _e:
        log.append('Date parse skipped: ' + str(_e))

# ── Line items (LineItems — not Items) ────────────────────────────────────────
_line_items_raw = [i for i in (job.get('LineItems') or []) if float(i.get('Quantity', 0)) > 0]
if _line_items_raw:
    _wkz_set = set()
    for _i in _line_items_raw:
        _wkz_set.add((_i.get('Name','').strip(), float(_i.get('Quantity',1)), float(_i.get('Price',0))))

    _odoo_lines = env['sale.order.line'].search([('order_id','=',record.id)])
    _odoo_set = set()
    for _l in _odoo_lines:
        if float(_l.product_uom_qty) > 0:
            _odoo_set.add((_l.name.split('\n')[0].strip() if _l.name else '', float(_l.product_uom_qty), float(_l.price_unit)))

    if _wkz_set != _odoo_set:
        _has_posted_inv = any(m.state == 'posted' for m in record.invoice_ids)
        if _has_posted_inv:
            log.append('Line items differ but invoice posted — line sync skipped (safe)')
        else:
            log.append('Line items differ — syncing ' + str(len(_line_items_raw)) + ' item(s)')
            _saved_date = _job_start_utc or (record.date_order.strftime('%Y-%m-%d %H:%M:%S') if record.date_order else False)

            if record.state == 'sale':
                record.action_cancel()
                record.action_draft()

            _all_lines = env['sale.order.line'].search([('order_id','=',record.id)])
            _all_lines.unlink()

            for _item in _line_items_raw:
                _name  = _item.get('Name','').strip()
                _qty   = float(_item.get('Quantity', 1))
                _price = float(_item.get('Price', 0))
                _prod  = env['product.product'].search([('name','=',_name)], limit=1)
                if not _prod:
                    _prod = env['product.product'].search([('name','ilike',_name)], limit=1)
                _vals = {'order_id': record.id, 'name': _name, 'product_uom_qty': _qty, 'price_unit': _price}
                if _prod:
                    _vals['product_id'] = _prod.id
                env['sale.order.line'].create(_vals)

            if record.state in ('draft', 'sent'):
                record.action_confirm()
                if _saved_date:
                    record.write({'date_order': _saved_date})
    else:
        log.append('Line items already match')
else:
    log.append('No LineItems from Workiz — skipping line sync')

# ── Pricing mismatch (computed after line sync so amount_untaxed is fresh) ──────
_job_amount_due = job.get('JobAmountDue')
try:
    _job_amount_due = float(_job_amount_due) if _job_amount_due is not None else None
except Exception:
    _job_amount_due = None

if _job_amount_due is not None and _job_amount_due == 0 and _status.lower() != 'done':
    updates['x_studio_pricing_mismatch'] = '<span class="bg-warning text-dark"><b>Credit Card Payment Received</b></span>'
else:
    _wkz_total = float(job.get('JobTotalPrice') or job.get('TotalPrice') or 0)
    _odoo_total = float(record.amount_untaxed or 0)
    if _wkz_total > 0:
        if abs(_wkz_total - _odoo_total) < 0.02:
            updates['x_studio_pricing_mismatch'] = '<span class="text-success"><b>OK - Workiz: $' + '{:.2f}'.format(_wkz_total) + ' | Odoo: $' + '{:.2f}'.format(_odoo_total) + '</b></span>'
        else:
            updates['x_studio_pricing_mismatch'] = '<span class="text-danger"><b>MISMATCH - Workiz: $' + '{:.2f}'.format(_wkz_total) + ' | Odoo: $' + '{:.2f}'.format(_odoo_total) + '</b></span>'
            log.append('Pricing MISMATCH: Workiz $' + '{:.2f}'.format(_wkz_total) + ' vs Odoo $' + '{:.2f}'.format(_odoo_total))

# ── Write header updates ──────────────────────────────────────────────────────
if updates:
    record.write(updates)
    log.append(str(len(updates)) + ' header field(s) updated')

# ── Roll-up to Property master ────────────────────────────────────────────────
# If THIS job is the property's most-recent non-canceled job, push its current values up to
# the Property master (gate/pricing/frequency/type-of-service). Older jobs DON'T touch the
# master, so fixing an old visit can't overwrite the current code. Non-empty values only, so
# a blank field never wipes the property.
_prop = record.partner_shipping_id
if _prop:
    _latest = env['sale.order'].search([
        ('partner_shipping_id', '=', _prop.id),
        ('state', 'in', ['sale', 'done']),
        ('x_studio_x_studio_workiz_status', '!=', 'Canceled'),
    ], order='date_order desc', limit=1)
    if _latest and _latest.id == record.id:
        _prop_updates = {}
        if _gate:    _prop_updates['x_studio_x_gate_code']       = _gate
        if _pricing: _prop_updates['x_studio_x_pricing']         = _pricing
        if _freq:    _prop_updates['x_studio_x_frequency']       = _freq
        if _tos:     _prop_updates['x_studio_x_type_of_service'] = _tos
        if _prop_updates:
            _prop.write(_prop_updates)
            log.append('Rolled up to property (latest job): ' + ', '.join(sorted(_prop_updates.keys())))

# ── Tags ──────────────────────────────────────────────────────────────────────
_wkz_tags_raw = job.get('Tags') or []
_wkz_tag_names = []
for _t in _wkz_tags_raw:
    _tn = (_t.get('Name') or _t.get('name') or '') if isinstance(_t, dict) else str(_t or '')
    if _tn.strip():
        _wkz_tag_names.append(_tn.strip())

_crm_tag_ids = []
for _tn in _wkz_tag_names:
    _ctag = env['crm.tag'].search([('name','=',_tn)], limit=1) or env['crm.tag'].search([('name','ilike',_tn)], limit=1)
    if _ctag:
        _crm_tag_ids.append(_ctag.id)
_contact = record.partner_id.parent_id if record.partner_id else None
if _contact and _contact.category_id:
    _crm_tag_ids += _contact.category_id.ids
if _crm_tag_ids:
    record.write({'tag_ids': [(6, 0, sorted(set(_crm_tag_ids)))]})
    log.append('Tags synced')

# ── Chatter ───────────────────────────────────────────────────────────────────
_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
_body = '✅ [' + _ts + '] Synced from Workiz | ' + (' | '.join(log) if log else 'no changes')
record.message_post(body=_body)

action = False
