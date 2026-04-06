API_TOKEN = 'api_1hu6lroiy5zxomcpptuwsg8heju97iwg'
AUTH_SECRET = 'sec_334084295850678330105471548'

workiz_uuid = record.x_studio_x_studio_workiz_uuid
if not workiz_uuid:
    raise UserError('No Workiz UUID on this sales order.')

url = 'https://api.workiz.com/api/v1/' + API_TOKEN + '/job/get/' + str(workiz_uuid) + '/?auth_secret=' + AUTH_SECRET
_resp = requests.get(url, timeout=15)

if _resp.status_code != 200:
    raise UserError('Workiz API returned HTTP ' + str(_resp.status_code))

_raw = _resp.json()
if isinstance(_raw, dict) and 'data' in _raw:
    _data = _raw['data']
    job = _data[0] if isinstance(_data, list) and _data else _data
elif isinstance(_raw, list) and _raw:
    job = _raw[0]
elif isinstance(_raw, dict) and 'UUID' in _raw:
    job = _raw
else:
    raise UserError('Unexpected Workiz API response.')

if not job:
    raise UserError('No job data returned from Workiz for UUID: ' + str(workiz_uuid))

updates = {}
log_lines = []

job_type = str(job.get('JobType') or '')
if job_type:
    updates['x_studio_x_studio_x_studio_job_type'] = job_type
    log_lines.append('Job Type: ' + job_type)

job_dt_str = str(job.get('JobDateTime') or '')
if job_dt_str and len(job_dt_str) >= 16:
    try:
        dt = datetime.datetime.strptime(job_dt_str[:16], '%Y-%m-%d %H:%M')
        utc_offset = 7 if 3 <= dt.month <= 11 else 8
        dt_utc = dt + datetime.timedelta(hours=utc_offset)
        updates['date_order'] = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
        log_lines.append('Job Date: ' + job_dt_str + ' PT -> ' + updates['date_order'] + ' UTC')
    except Exception as e:
        log_lines.append('Date parse skipped: ' + str(e))

team = job.get('Team') or []
if team:
    tech_names = [t.get('Name', '') for t in team if t.get('Name')]
    if tech_names:
        updates['x_studio_x_studio_workiz_tech'] = ', '.join(tech_names)
        log_lines.append('Tech: ' + updates['x_studio_x_studio_workiz_tech'])

gate_code = str(job.get('gate_code') or '')
if gate_code:
    updates['x_studio_x_gate_snapshot'] = gate_code
    log_lines.append('Gate Code: ' + gate_code)

pricing = str(job.get('pricing') or '')
if pricing:
    updates['x_studio_x_studio_pricing_snapshot'] = pricing
    log_lines.append('Pricing: ' + pricing)

type_of_service = str(job.get('type_of_service_2') or '')
if type_of_service:
    updates['x_studio_x_studio_type_of_service_so'] = type_of_service
    log_lines.append('Type of Service: ' + type_of_service)

job_notes = str(job.get('JobNotes') or '')
comments = str(job.get('Comments') or '')
notes_parts = []
if job_notes:
    notes_parts.append(job_notes)
if comments:
    notes_parts.append(comments)
if notes_parts:
    updates['x_studio_x_studio_notes_snapshot1'] = ' | '.join(notes_parts)
    log_lines.append('Notes updated')

updates['x_studio_x_workiz_link'] = 'https://app.workiz.com/root/job/' + str(workiz_uuid) + '/'

status = str(job.get('Status') or '')
substatus = str(job.get('SubStatus') or '')
workiz_status_val = substatus if substatus else status
if workiz_status_val:
    updates['x_studio_x_studio_workiz_status'] = workiz_status_val
if status or substatus:
    log_lines.append('Workiz Status: ' + status + ' / ' + substatus)

job_amount_due = job.get('JobAmountDue')
try:
    job_amount_due = float(job_amount_due) if job_amount_due is not None else None
except Exception:
    job_amount_due = None

if job_amount_due is not None and job_amount_due == 0 and status.lower() != 'done':
    updates['x_studio_pricing_mismatch'] = '<span class="bg-warning text-dark"><b>Credit Card Payment Received - Invoice in Odoo using Credit method</b></span>'
    log_lines.append('Credit Card Payment Received')
else:
    workiz_total = job.get('JobTotalPrice') or job.get('TotalPrice') or job.get('SubTotal') or 0
    try:
        workiz_total = float(workiz_total)
    except Exception:
        workiz_total = 0
    odoo_total = float(record.amount_untaxed or 0)
    if workiz_total > 0:
        if abs(workiz_total - odoo_total) < 0.02:
            updates['x_studio_pricing_mismatch'] = '<span class="text-success"><b>OK - Workiz: $' + '{:.2f}'.format(workiz_total) + ' | Odoo: $' + '{:.2f}'.format(odoo_total) + '</b></span>'
            log_lines.append('Pricing Check: OK')
        else:
            updates['x_studio_pricing_mismatch'] = '<span class="text-danger"><b>MISMATCH - Workiz: $' + '{:.2f}'.format(workiz_total) + ' | Odoo: $' + '{:.2f}'.format(odoo_total) + ' - Change status to Scheduled in Workiz to force Phase 4 sync</b></span>'
            log_lines.append('Pricing Check: MISMATCH - Workiz $' + '{:.2f}'.format(workiz_total) + ' vs Odoo $' + '{:.2f}'.format(odoo_total))

# Tags: Workiz job tags mapped to crm.tag + contact partner categories (mirrors Phase 4 logic)
_workiz_tags_raw = job.get('Tags') or job.get('JobTags') or []
_workiz_tag_names = []
if isinstance(_workiz_tags_raw, list):
    for _t in _workiz_tags_raw:
        if isinstance(_t, dict):
            _tname = _t.get('Name') or _t.get('name') or ''
        else:
            _tname = str(_t) if _t else ''
        if _tname.strip():
            _workiz_tag_names.append(_tname.strip())

_all_tag_ids = []
for _tag_name in _workiz_tag_names:
    _tag_rec = env['crm.tag'].search([('name', '=', _tag_name)], limit=1)
    if not _tag_rec:
        _tag_rec = env['crm.tag'].search([('name', 'ilike', _tag_name)], limit=1)
    if _tag_rec:
        _all_tag_ids.append(_tag_rec.id)

_contact_partner = record.partner_id.parent_id if record.partner_id else None
if _contact_partner and _contact_partner.category_id:
    _all_tag_ids += _contact_partner.category_id.ids

_all_tag_ids = sorted(set(_all_tag_ids))
if _all_tag_ids:
    updates['tag_ids'] = [(6, 0, _all_tag_ids)]
    log_lines.append('Tags: ' + str(len(_all_tag_ids)) + ' tag(s) synced')

if updates:
    record.write(updates)

# --- Remove tasks if job is back to Submitted (unscheduled) ---
# Also sets flag to skip all task creation/sync below
_job_is_submitted = (status == 'Submitted')
if _job_is_submitted:
    _tasks_to_remove = env['project.task'].search([('sale_line_id', 'in', record.order_line.ids)])
    if _tasks_to_remove:
        _del_count = len(_tasks_to_remove)
        _tasks_to_remove.unlink()
        log_lines.append(str(_del_count) + ' task(s) removed - job unscheduled (Submitted)')

# --- Build task tag IDs (project.tags model, not crm.tag) ---
# Must happen before backfill so new tasks get tags on creation.
_task_tag_ids = []
for _tag_name in _workiz_tag_names:
    _ptag = env['project.tags'].search([('name', '=', _tag_name)], limit=1)
    if not _ptag:
        _ptag = env['project.tags'].search([('name', 'ilike', _tag_name)], limit=1)
    if _ptag:
        _task_tag_ids.append(_ptag.id)
    else:
        # project.tags record doesn't exist yet — create it so task tags stay in sync
        _new_ptag = env['project.tags'].create({'name': _tag_name})
        _task_tag_ids.append(_new_ptag.id)

# --- Build task date updates ---
# Must happen before backfill so new tasks get correct dates on creation.
_task_date_updates = {}

_job_start_utc = updates.get('date_order')
if _job_start_utc:
    _task_date_updates['planned_date_begin'] = _job_start_utc
    _task_date_updates['planned_date_start'] = _job_start_utc

_job_end_str = str(job.get('JobEndDateTime') or '')
if _job_end_str and len(_job_end_str) >= 16:
    try:
        _dt_end = datetime.datetime.strptime(_job_end_str[:16], '%Y-%m-%d %H:%M')
        _utc_offset_end = 7 if 3 <= _dt_end.month <= 11 else 8
        _dt_end_utc = _dt_end + datetime.timedelta(hours=_utc_offset_end)
        _job_end_utc = _dt_end_utc.strftime('%Y-%m-%d %H:%M:%S')
        _task_date_updates['date_deadline'] = _job_end_utc
        _task_date_updates['date_end'] = _job_end_utc
        log_lines.append('Job End: ' + _job_end_str + ' PT -> ' + _job_end_utc + ' UTC')
        if _job_start_utc:
            try:
                _delta_hours = (_dt_end_utc - datetime.datetime.strptime(_job_start_utc, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600.0
                if _delta_hours > 0:
                    _num_lines = max(len(record.order_line), 1)
                    _task_date_updates['allocated_hours'] = round(_delta_hours / _num_lines, 2)
            except Exception:
                pass
    except Exception as _e:
        log_lines.append('End date parse skipped: ' + str(_e))

# --- Compute task name (used by both backfill and existing task sync) ---
_first_name = str(job.get('FirstName') or '')
_last_name = str(job.get('LastName') or '')
_city = str(job.get('City') or '')
_task_customer = (_first_name + ' ' + _last_name).strip() or (record.partner_id.parent_id.name if record.partner_id.parent_id else record.partner_id.name)
_task_name = (_task_customer + ' - ' + _city).strip(' -') if _city else _task_customer

# --- Backfill: create tasks if SO is confirmed and has none ---
# Runs BEFORE tag/date sync so that newly created tasks are found by the sync blocks below.
_existing_tasks = env['project.task'].search([('sale_line_id', 'in', record.order_line.ids)], limit=1)
if not _job_is_submitted and not _existing_tasks and record.state == 'sale':
    _tech_user_ids = [2]
    _backfill_count = 0
    _per_task_hours = _task_date_updates.get('allocated_hours', 0)
    _per_task_secs = _per_task_hours * 3600 if _per_task_hours else 0
    _bf_start_dt = datetime.datetime.strptime(_job_start_utc, '%Y-%m-%d %H:%M:%S') if _job_start_utc else None
    for _bf_i, _line in enumerate(record.order_line):
        _task_vals = {
            'name': _task_name,
            'project_id': 2,
            'sale_line_id': _line.id,
            'user_ids': [(6, 0, _tech_user_ids)],
            'partner_id': record.partner_id.id,
        }
        if _bf_start_dt and _per_task_secs:
            _t_start = _bf_start_dt + datetime.timedelta(seconds=_bf_i * _per_task_secs)
            _t_end = _t_start + datetime.timedelta(seconds=_per_task_secs)
            _task_vals['planned_date_begin'] = _t_start.strftime('%Y-%m-%d %H:%M:%S')
            _task_vals['planned_date_start'] = _t_start.strftime('%Y-%m-%d %H:%M:%S')
            _task_vals['date_deadline'] = _t_end.strftime('%Y-%m-%d %H:%M:%S')
            _task_vals['date_end'] = _t_end.strftime('%Y-%m-%d %H:%M:%S')
            _task_vals['allocated_hours'] = _per_task_hours
        elif _task_date_updates.get('planned_date_begin'):
            _task_vals['planned_date_begin'] = _task_date_updates['planned_date_begin']
            _task_vals['planned_date_start'] = _task_date_updates['planned_date_begin']
        if _task_tag_ids:
            _task_vals['tag_ids'] = [(6, 0, _task_tag_ids)]
        if _line.name:
            _desc_parts = _line.name.split('\n', 1)
            if len(_desc_parts) > 1:
                _task_vals['description'] = _desc_parts[1].strip()
        env['project.task'].create(_task_vals)
        _backfill_count += 1
    if _backfill_count:
        log_lines.append('Backfilled ' + str(_backfill_count) + ' missing task(s)')

# --- Ensure property partner has country_id set (required for FSM Navigate To) ---
if record.partner_id and not record.partner_id.country_id:
    _us_country = env['res.country'].search([('code', '=', 'US')], limit=1)
    if _us_country:
        record.partner_id.write({'country_id': _us_country.id})

# --- Sync name, user_ids, and partner_id to existing tasks ---
_linked_tasks_users = env['project.task'].search([('sale_line_id', 'in', record.order_line.ids)]) if not _job_is_submitted else []
if _linked_tasks_users:
    _linked_tasks_users.write({'name': _task_name, 'user_ids': [(6, 0, [2])], 'partner_id': record.partner_id.id})
    log_lines.append(str(len(_linked_tasks_users)) + ' task(s) name/tech updated')

# --- Sync tags to existing tasks ---
if not _job_is_submitted and _task_tag_ids:
    _linked_tasks = env['project.task'].search([('sale_line_id', 'in', record.order_line.ids)])
    if _linked_tasks:
        _linked_tasks.write({'tag_ids': [(6, 0, _task_tag_ids)]})
        log_lines.append(str(len(_linked_tasks)) + ' task(s) tags updated')

# --- Sync start/end dates to existing tasks (staggered per task) ---
if not _job_is_submitted and _task_date_updates:
    _linked_tasks_dates = env['project.task'].search([('sale_line_id', 'in', record.order_line.ids)], order='id asc')
    if _linked_tasks_dates:
        _per_task_hours = _task_date_updates.get('allocated_hours', 0)
        _per_task_secs = _per_task_hours * 3600 if _per_task_hours else 0
        _sync_start_dt = datetime.datetime.strptime(_job_start_utc, '%Y-%m-%d %H:%M:%S') if _job_start_utc else None
        for _si, _stask in enumerate(_linked_tasks_dates):
            _stask_vals = dict(_task_date_updates)
            if _sync_start_dt and _per_task_secs and len(_linked_tasks_dates) > 1:
                _t_start = _sync_start_dt + datetime.timedelta(seconds=_si * _per_task_secs)
                _t_end = _t_start + datetime.timedelta(seconds=_per_task_secs)
                _stask_vals['planned_date_begin'] = _t_start.strftime('%Y-%m-%d %H:%M:%S')
                _stask_vals['planned_date_start'] = _t_start.strftime('%Y-%m-%d %H:%M:%S')
                _stask_vals['date_deadline'] = _t_end.strftime('%Y-%m-%d %H:%M:%S')
                _stask_vals['date_end'] = _t_end.strftime('%Y-%m-%d %H:%M:%S')
            _stask.write(_stask_vals)
        log_lines.append(str(len(_linked_tasks_dates)) + ' task(s) start/end updated')

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if log_lines:
    record.message_post(body='✅ [' + timestamp + '] Synced from Workiz: ' + ' | '.join(log_lines))
else:
    record.message_post(body='✅ [' + timestamp + '] Synced from Workiz - no changes detected.')

action = {'type': 'ir.actions.act_window_close'}