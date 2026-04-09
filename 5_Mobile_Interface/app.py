# ==============================================================================
# WINDOW & SOLAR CARE — MOBILE VOICE INTERFACE BACKEND (v3)
# Deploy: Render.com (env vars: ODOO_API_KEY, WORKIZ_TOKEN, WORKIZ_SECRET, OPENAI_API_KEY, ACCESS_CODE)
# ==============================================================================

import os, json, re, datetime, urllib.parse
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ODOO_URL      = os.environ.get('ODOO_URL',        'https://window-solar-care.odoo.com')
ODOO_DB       = os.environ.get('ODOO_DB',         'window-solar-care')
ODOO_USER_ID  = int(os.environ.get('ODOO_USER_ID', '2'))
ODOO_API_KEY  = os.environ.get('ODOO_API_KEY',    '')
WORKIZ_TOKEN  = os.environ.get('WORKIZ_TOKEN',    '')
WORKIZ_SECRET = os.environ.get('WORKIZ_SECRET',   'sec_334084295850678330105471548')
OPENAI_KEY    = os.environ.get('OPENAI_API_KEY',  '')
ACCESS_CODE   = os.environ.get('ACCESS_CODE',     'wsc2026')
OWNER_EMAIL   = os.environ.get('OWNER_EMAIL',     '')

app = FastAPI()

# ---------------------------------------------------------------------------
# Session memory — keyed by session_id, stores conversation history
# Cleared per session when a write is confirmed or session closes
# ---------------------------------------------------------------------------
_sessions: dict = {}

# ---------------------------------------------------------------------------
# Persistent agent memory — stored in Odoo ir.config_parameter
# Survives Render restarts, deploys, and everything else
# ---------------------------------------------------------------------------
_MEMORY_KEY = 'wsc.agent.memory'

def load_agent_memory() -> dict:
    try:
        params = odoo_rpc('ir.config_parameter', 'search_read',
            [[['key', '=', _MEMORY_KEY]]],
            {'fields': ['value'], 'limit': 1})
        if params and params[0].get('value'):
            return json.loads(params[0]['value'])
    except Exception:
        pass
    return {}

def save_agent_memory(memories: dict):
    try:
        existing = odoo_rpc('ir.config_parameter', 'search',
            [[['key', '=', _MEMORY_KEY]]])
        if existing:
            odoo_rpc('ir.config_parameter', 'write',
                [existing, {'value': json.dumps(memories)}])
        else:
            odoo_rpc('ir.config_parameter', 'create',
                [{'key': _MEMORY_KEY, 'value': json.dumps(memories)}])
    except Exception:
        pass

def get_history(session_id: str) -> list:
    return list(_sessions.get(session_id, []))

def save_history(session_id: str, messages: list):
    trimmed = messages[-40:]  # generous buffer
    # Never start mid-turn — an orphaned tool message causes OpenAI 400 errors.
    # Always trim from the front until we land on a user message.
    while trimmed and trimmed[0].get('role') != 'user':
        trimmed = trimmed[1:]
    _sessions[session_id] = trimmed

def clear_history(session_id: str):
    _sessions.pop(session_id, None)


# ---------------------------------------------------------------------------
# Odoo JSON-RPC helper
# ---------------------------------------------------------------------------
def odoo_rpc(model, method, args, kwargs=None):
    if kwargs is None:
        kwargs = {}
    payload = {
        'jsonrpc': '2.0', 'method': 'call', 'id': 1,
        'params': {
            'service': 'object', 'method': 'execute_kw',
            'args': [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args, kwargs]
        }
    }
    resp = httpx.post(f'{ODOO_URL}/jsonrpc', json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if 'error' in data:
        raise ValueError(f"Odoo error: {data['error']}")
    return data.get('result')


# ---------------------------------------------------------------------------
# Workiz helpers
# ---------------------------------------------------------------------------
def workiz_get(endpoint):
    sep = '&' if '?' in endpoint else '?'
    url = f'https://api.workiz.com/api/v1/{WORKIZ_TOKEN}/{endpoint}{sep}auth_secret={WORKIZ_SECRET}'
    resp = httpx.get(url, timeout=20)
    if resp.status_code in (204, 404):
        return None
    resp.raise_for_status()
    return resp.json()


def workiz_post(endpoint, data):
    url = f'https://api.workiz.com/api/v1/{WORKIZ_TOKEN}/{endpoint}'
    data['auth_secret'] = WORKIZ_SECRET
    resp = httpx.post(url, json=data, timeout=20)
    if resp.status_code == 204:
        return {'success': True}
    if not resp.is_success:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise ValueError(f"Workiz API {resp.status_code}: {detail}")
    return resp.json()


# ---------------------------------------------------------------------------
# Date resolver
# ---------------------------------------------------------------------------
def resolve_date(date_str: str):
    today = datetime.date.today()
    ds = (date_str or 'today').lower().strip()
    if ds in ('today', ''):
        return today.isoformat(), 'Today'
    if ds == 'tomorrow':
        return (today + datetime.timedelta(days=1)).isoformat(), 'Tomorrow'
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if ds in day_names:
        target_wd = day_names.index(ds)
        days_ahead = (target_wd - today.weekday()) % 7 or 7
        return (today + datetime.timedelta(days=days_ahead)).isoformat(), ds.capitalize()
    return date_str, date_str


# ---------------------------------------------------------------------------
# Field name maps
# ---------------------------------------------------------------------------
# Workiz job fields (used with job/update/)
WORKIZ_JOB_FIELDS = {
    'gate_code':            'gate_code',
    'pricing':              'pricing',
    'notes':                'JobNotes',
    'job_notes':            'JobNotes',
    'substatus':            'SubStatus',
    'status':               'SubStatus',
    'type_of_service':      'type_of_service_2',
    'frequency':            'frequency',
    'alternating':          'alternating',
    'last_date_cleaned':    'last_date_cleaned',
    'ok_to_text':           'ok_to_text',
    'confirmation_method':  'confirmation_method',
}

# Odoo partner fields (used with res.partner write)
ODOO_CONTACT_FIELDS = {
    'pricing':              'x_studio_x_pricing',
    'frequency':            'x_studio_x_frequency',
    'type_of_service':      'x_studio_x_type_of_service',
    'alternating':          'x_studio_x_alternating',
    'gate_code':            'x_studio_x_gate_code',
    'ok_to_text':           'x_studio_x_studio_ok_to_text',
    'confirmation_method':  'x_studio_x_studio_confirm_send',
    'last_date_cleaned':    'x_studio_x_studio_last_service_date',
    'notes':                'comment',
    'internal_notes':       'comment',
    'comment':              'comment',
}

# Odoo SO snapshot fields (synced from Workiz on job update)
ODOO_SO_SNAPSHOT_FIELDS = {
    'gate_code':    'x_studio_x_gate_snapshot',
    'pricing':      'x_studio_x_studio_pricing_snapshot',
}


# ---------------------------------------------------------------------------
# READ TOOL IMPLEMENTATIONS
# ---------------------------------------------------------------------------

def tool_search_customers(query: str) -> list:
    clean = re.sub(r"'s\s*$", '', query, flags=re.IGNORECASE).strip()

    # Detect SO number (e.g. "4400", "004400", "S04400") and look up directly
    so_match = re.match(r'^[Ss]?0*(\d{3,6})$', clean)
    if so_match:
        so_num = so_match.group(1)
        sos = odoo_rpc('sale.order', 'search_read',
            [[['name', 'ilike', so_num]]],
            {'fields': ['id', 'name', 'partner_id', 'date_order', 'amount_total',
                        'x_studio_x_studio_workiz_uuid', 'x_studio_x_studio_workiz_status',
                        'state'], 'limit': 3})
        if sos:
            results = []
            for so in sos:
                pid = so['partner_id'][0] if so.get('partner_id') else None
                pname = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else ''
                results.append({
                    'partner_id': pid,
                    'name': pname,
                    'so_id': so['id'],
                    'so_name': so['name'],
                    'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or '',
                    'job_date': (so.get('date_order') or '')[:16],
                    'amount': so.get('amount_total') or 0,
                    'workiz_status': so.get('x_studio_x_studio_workiz_status') or '',
                    'state': so.get('state') or ''
                })
            return results

    _search_fields = ['id', 'name', 'city', 'street', 'phone', 'email',
                      'ref', 'x_studio_x_studio_record_category']

    partners = odoo_rpc('res.partner', 'search_read',
        [[['name', 'ilike', clean], ['active', '=', True]]],
        {'fields': _search_fields, 'limit': 8})

    # Fuzzy fallback: if full query returns nothing and has multiple words,
    # try each word individually (handles misspellings like "Sussman" → "Zusman")
    if not partners and ' ' in clean:
        for word in clean.split():
            if len(word) > 2:
                partners = odoo_rpc('res.partner', 'search_read',
                    [[['name', 'ilike', word], ['active', '=', True]]],
                    {'fields': _search_fields, 'limit': 8})
                if partners:
                    break  # use first word that returns results

    if not partners:
        return [{'error': f'No customers found matching "{query}"'}]
    results = []
    for p in partners:
        sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_id', '=', p['id']], ['state', 'in', ['sale', 'done']]]],
            {'fields': ['id', 'name', 'x_studio_x_studio_workiz_uuid', 'date_order',
                        'amount_total', 'x_studio_x_studio_workiz_status'],
             'order': 'date_order desc', 'limit': 1})
        so = sos[0] if sos else {}
        results.append({
            'partner_id': p['id'],
            'name': p['name'],
            'city': p.get('city') or '',
            'street': p.get('street') or '',
            'phone': p.get('phone') or p.get('mobile') or '',
            'email': p.get('email') or '',
            'workiz_client_id': p.get('ref') or '',
            'record_category': p.get('x_studio_x_studio_record_category') or '',
            'so_id': so.get('id'),
            'so_name': so.get('name') or '',
            'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or '',
            'job_date': (so.get('date_order') or '')[:16],
            'amount': so.get('amount_total') or 0,
            'workiz_status': so.get('x_studio_x_studio_workiz_status') or ''
        })
    return results


def tool_get_customer_profile(partner_id: int) -> dict:
    """Get full contact profile including all custom fields and address — used before creating a job."""
    p = odoo_rpc('res.partner', 'read', [[partner_id]], {
        'fields': ['name', 'street', 'street2', 'city', 'state_id', 'zip', 'country_id',
                   'phone', 'email', 'ref',
                   'x_studio_x_pricing', 'x_studio_x_frequency', 'x_studio_x_type_of_service',
                   'x_studio_x_alternating', 'x_studio_x_gate_code',
                   'x_studio_x_studio_ok_to_text', 'x_studio_x_studio_confirm_send',
                   'x_studio_x_studio_last_service_date', 'x_studio_x_studio_service_area',
                   'x_studio_x_studio_record_category']
    })
    if not p:
        return {'error': 'Customer not found'}
    rec = p[0]
    state_name = rec['state_id'][1] if isinstance(rec.get('state_id'), list) else ''
    return {
        'partner_id': partner_id,
        'name': rec.get('name') or '',
        'first_name': (rec.get('name') or '').split()[0] if rec.get('name') else '',
        'last_name': ' '.join((rec.get('name') or '').split()[1:]) if rec.get('name') else '',
        'street': rec.get('street') or '',
        'street2': rec.get('street2') or '',
        'city': rec.get('city') or '',
        'state': state_name,
        'zip': rec.get('zip') or '',
        'phone': rec.get('phone') or '',
        'email': rec.get('email') or '',
        'workiz_client_id': rec.get('ref') or '',
        'pricing': rec.get('x_studio_x_pricing') or '',
        'frequency': rec.get('x_studio_x_frequency') or '',
        'type_of_service': rec.get('x_studio_x_type_of_service') or '',
        'alternating': rec.get('x_studio_x_alternating') or '',
        'gate_code': rec.get('x_studio_x_gate_code') or '',
        'ok_to_text': rec.get('x_studio_x_studio_ok_to_text') or '',
        'confirmation_method': rec.get('x_studio_x_studio_confirm_send') or '',
        'last_date_cleaned': rec.get('x_studio_x_studio_last_service_date') or '',
        'service_area': rec.get('x_studio_x_studio_service_area') or '',
        'record_category': rec.get('x_studio_x_studio_record_category') or '',
    }


def tool_get_job_details(partner_id: int) -> dict:
    # Search by billing partner first, then by shipping/property partner
    # Odoo SOs can have either the contact or the property as partner_id
    fields = ['id', 'name', 'date_order', 'amount_total',
              'x_studio_x_studio_workiz_uuid', 'x_studio_x_studio_workiz_status',
              'x_studio_x_studio_workiz_tech', 'x_studio_x_gate_snapshot',
              'x_studio_x_studio_pricing_snapshot', 'x_studio_x_studio_type_of_service_so',
              'x_studio_x_studio_notes_snapshot1']
    sos = odoo_rpc('sale.order', 'search_read',
        [[['partner_id', '=', partner_id], ['state', 'in', ['sale', 'done']]]],
        {'fields': fields, 'order': 'date_order desc', 'limit': 1})
    if not sos:
        # Try as shipping/property partner
        sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_shipping_id', '=', partner_id], ['state', 'in', ['sale', 'done']]]],
            {'fields': fields, 'order': 'date_order desc', 'limit': 1})
    if not sos:
        # Last resort: search all partners under same parent (contact → properties)
        parent = odoo_rpc('res.partner', 'read', [[partner_id]], {'fields': ['parent_id', 'child_ids']})
        if parent:
            rec = parent[0]
            related_ids = [partner_id]
            if rec.get('parent_id'):
                related_ids.append(rec['parent_id'][0])
            if rec.get('child_ids'):
                related_ids.extend(rec['child_ids'])
            if len(related_ids) > 1:
                sos = odoo_rpc('sale.order', 'search_read',
                    [[['partner_id', 'in', related_ids], ['state', 'in', ['sale', 'done']]]],
                    {'fields': fields, 'order': 'date_order desc', 'limit': 1})
                if not sos:
                    sos = odoo_rpc('sale.order', 'search_read',
                        [[['partner_shipping_id', 'in', related_ids], ['state', 'in', ['sale', 'done']]]],
                        {'fields': fields, 'order': 'date_order desc', 'limit': 1})
    if not sos:
        return {'error': 'No active sales order found for this customer'}
    so = sos[0]
    result = {
        'so_id': so['id'],
        'so_name': so['name'],
        'date': (so.get('date_order') or '')[:16],
        'amount': so.get('amount_total') or 0,
        'status': so.get('x_studio_x_studio_workiz_status') or '',
        'tech': so.get('x_studio_x_studio_workiz_tech') or '',
        'gate_code': so.get('x_studio_x_gate_snapshot') or '',
        'pricing': so.get('x_studio_x_studio_pricing_snapshot') or '',
        'type_of_service': so.get('x_studio_x_studio_type_of_service_so') or '',
        'notes': so.get('x_studio_x_studio_notes_snapshot1') or '',
        'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or ''
    }
    uuid = result['workiz_uuid']
    if uuid:
        raw = workiz_get(f'job/get/{uuid}/')
        if raw:
            job_data = raw.get('data', {})
            job = job_data[0] if isinstance(job_data, list) else job_data
            if job:
                result['workiz_notes']     = job.get('JobNotes') or ''
                result['workiz_substatus'] = job.get('SubStatus') or job.get('Status') or ''
                result['workiz_frequency'] = job.get('frequency') or ''
                result['workiz_alternating'] = job.get('alternating') or ''
                result['workiz_ok_to_text'] = job.get('ok_to_text') or ''
                result['workiz_confirmation'] = job.get('confirmation_method') or ''
                result['workiz_last_cleaned'] = job.get('last_date_cleaned') or ''
                result['workiz_address'] = f"{job.get('Address', '')} {job.get('City', '')}".strip()
    return result


def tool_get_schedule(date: str) -> dict:
    """Returns structured schedule data including partner_ids so follow-up queries don't need to re-search."""
    date_iso, label = resolve_date(date)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', date_iso + ' 00:00:00'],
          ['date_order', '<=', date_iso + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']]]],
        {'fields': ['id', 'name', 'date_order', 'partner_id', 'amount_total',
                    'x_studio_x_studio_workiz_status', 'x_studio_x_studio_workiz_uuid'],
         'order': 'date_order asc'})
    if not sos:
        return {'label': label, 'date': date_iso, 'count': 0, 'jobs': [], 'total': 0}
    jobs = []
    total = 0.0
    for so in sos:
        customer = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
        partner_id = so['partner_id'][0] if so.get('partner_id') else None
        amount = float(so.get('amount_total') or 0)
        total += amount
        jobs.append({
            'customer': customer,
            'partner_id': partner_id,
            'so_id': so['id'],
            'so_name': so['name'],
            'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or '',
            'time_utc': so['date_order'][11:16] if so.get('date_order') else '?',
            'amount': amount,
            'status': so.get('x_studio_x_studio_workiz_status') or ''
        })
    return {'label': label, 'date': date_iso, 'count': len(jobs), 'jobs': jobs, 'total': total}


def tool_get_next_job() -> dict:
    now_str   = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    today_iso = datetime.date.today().isoformat()
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', now_str],
          ['date_order', '<=', today_iso + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']],
          ['x_studio_x_studio_workiz_uuid', '!=', False]]],
        {'fields': ['name', 'date_order', 'partner_id', 'amount_total',
                    'x_studio_x_studio_workiz_uuid', 'x_studio_x_studio_workiz_status'],
         'order': 'date_order asc', 'limit': 1})
    if not sos:
        return {'error': 'No more jobs scheduled for today'}
    so = sos[0]
    customer   = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
    partner_id = so['partner_id'][0] if so.get('partner_id') else None
    result = {
        'customer': customer, 'partner_id': partner_id,
        'time_utc': so['date_order'][11:16], 'so_name': so['name'], 'so_id': so['id'],
        'amount': float(so.get('amount_total') or 0),
        'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or '',
        'status': so.get('x_studio_x_studio_workiz_status') or ''
    }
    if partner_id:
        p = odoo_rpc('res.partner', 'read', [[partner_id]],
            {'fields': ['street', 'city', 'state_id', 'zip']})
        if p:
            rec = p[0]
            parts = [rec.get('street') or '', rec.get('city') or '', rec.get('zip') or '']
            result['address'] = ', '.join(x for x in parts if x)
    return result


def tool_get_sales(date: str) -> str:
    date_iso, label = resolve_date(date)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', date_iso + ' 00:00:00'],
          ['date_order', '<=', date_iso + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']]]],
        {'fields': ['amount_total']})
    if not sos:
        return f"No sales for {label}."
    total = sum(float(so.get('amount_total') or 0) for so in sos)
    return f"Sales for {label}: ${total:.2f} across {len(sos)} job(s)"


def tool_get_sales_week(date: str = '') -> str:
    """Returns total sales for the work week (Mon–Sat) containing the given date. Sundays excluded."""
    date_iso, _ = resolve_date(date if date else 'today')
    try:
        d = datetime.date.fromisoformat(date_iso)
    except Exception:
        d = datetime.date.today()
    monday = d - datetime.timedelta(days=d.weekday())
    saturday = monday + datetime.timedelta(days=5)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', monday.isoformat() + ' 00:00:00'],
          ['date_order', '<=', saturday.isoformat() + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']]]],
        {'fields': ['amount_total', 'date_order', 'partner_id']})
    if not sos:
        return f"No sales for week of {monday} – {saturday}."
    by_day = {}
    for so in sos:
        day = (so.get('date_order') or '')[:10]
        by_day[day] = by_day.get(day, 0) + float(so.get('amount_total') or 0)
    total = sum(by_day.values())
    day_lines = ', '.join(f"{k}: ${v:.0f}" for k, v in sorted(by_day.items()) if v > 0)
    return f"Week of {monday} – {saturday}: ${total:.2f} across {len(sos)} job(s). By day: {day_lines}"


def tool_get_jobs_list(start_date: str = '', records: int = 50,
                       only_open: bool = True, offset: int = 0,
                       status: list = None) -> list:
    """Fetch jobs from Workiz with pagination. offset=0 → records 1-100, offset=1 → 101-200."""
    params = f'start_date={start_date}&records={records}&only_open={str(only_open).lower()}&offset={offset}'
    if status:
        for s in status:
            params += f'&status[]={urllib.parse.quote(s)}'
    raw = workiz_get(f'job/all/?{params}')
    if not raw:
        return []
    jobs = raw if isinstance(raw, list) else raw.get('data', [])
    result = []
    for j in jobs:
        result.append({
            'uuid': j.get('UUID') or '',
            'client_id': j.get('ClientId') or '',
            'name': f"{j.get('FirstName','')} {j.get('LastName','')}".strip(),
            'date': (j.get('JobDateTime') or '')[:16],
            'status': j.get('Status') or '',
            'substatus': j.get('SubStatus') or '',
            'type_of_service': j.get('type_of_service_2') or '',
            'city': j.get('City') or '',
        })
    return result


def tool_save_memory(key: str, value: str) -> str:
    memories = load_agent_memory()
    memories[key.strip()] = value.strip()
    save_agent_memory(memories)
    return f"Remembered: {key} = {value}"

def tool_delete_memory(key: str) -> str:
    memories = load_agent_memory()
    if key.strip() in memories:
        del memories[key.strip()]
        save_agent_memory(memories)
        return f"Forgot: {key}"
    # Try case-insensitive match
    lower_key = key.strip().lower()
    for k in list(memories.keys()):
        if k.lower() == lower_key:
            del memories[k]
            save_agent_memory(memories)
            return f"Forgot: {k}"
    return f"No memory found for: {key}"


def tool_send_email(subject: str, body: str, to_email: str = '') -> str:
    """Send an email via Odoo's mail system."""
    # Resolve recipient — use provided address, env var, or fall back to owner's Odoo email
    recipient = (to_email or OWNER_EMAIL or '').strip()
    if not recipient:
        # Look up owner email from Odoo user record
        try:
            user = odoo_rpc('res.users', 'read', [[ODOO_USER_ID]], {'fields': ['email', 'name']})
            if user and user[0].get('email'):
                recipient = user[0]['email']
        except Exception:
            pass
    if not recipient:
        return "Cannot send email: no recipient address found. Set OWNER_EMAIL env var on Render or say 'remember that my email is you@example.com'."

    # Check persistent memory for email if still not set
    if not recipient:
        memories = load_agent_memory()
        recipient = memories.get('email') or memories.get('owner_email') or ''

    # Send via Odoo mail.mail
    mail_id = odoo_rpc('mail.mail', 'create', [{
        'subject':       subject,
        'body_html':     f'<pre style="font-family:monospace;font-size:14px;">{body}</pre>',
        'email_to':      recipient,
        'email_from':    'noreply@window-solar-care.odoo.com',
        'auto_delete':   True,
    }])
    odoo_rpc('mail.mail', 'send', [[mail_id]])
    return f"Email sent to {recipient}: \"{subject}\""


def tool_navigate_to(partner_id: int, customer_name: str = '') -> str:
    p = odoo_rpc('res.partner', 'read', [[partner_id]],
        {'fields': ['name', 'street', 'street2', 'city', 'state_id', 'zip']})
    if not p:
        return 'No address found.'
    rec = p[0]
    display_name = customer_name or rec.get('name', '')
    addr_parts = []
    if rec.get('street'):   addr_parts.append(rec['street'])
    if rec.get('street2'):  addr_parts.append(rec['street2'])
    if rec.get('city'):     addr_parts.append(rec['city'])
    if rec.get('state_id'): addr_parts.append(rec['state_id'][1] if isinstance(rec['state_id'], list) else '')
    if rec.get('zip'):      addr_parts.append(rec['zip'])
    if not addr_parts:
        return f'No address on file for {display_name}.'
    full_address = ', '.join(a for a in addr_parts if a)
    maps_url = 'https://maps.google.com/?q=' + urllib.parse.quote(full_address)
    return (
        f'<div style="margin-bottom:8px;font-size:15px;">'
        f'<b>{display_name}</b><br>'
        f'<span style="color:#94a3b8;font-size:13px;">{full_address}</span>'
        f'</div>'
        f'<a href="{maps_url}" target="_blank" rel="noopener" '
        f'style="display:block;padding:16px;background:#16a34a;color:white;'
        f'font-size:18px;font-weight:700;text-align:center;border-radius:12px;'
        f'text-decoration:none;">Open in Google Maps</a>'
    )


# ---------------------------------------------------------------------------
# WRITE TOOL IMPLEMENTATIONS — executed after confirmation
# ---------------------------------------------------------------------------

def execute_write_tool(tool_name: str, args: dict) -> str:
    pname = args.get('partner_name', 'customer')

    # --- Update a Workiz job field ---
    if tool_name == 'update_workiz_field':
        field_key   = args['field_name'].lower().replace(' ', '_')
        workiz_field = WORKIZ_JOB_FIELDS.get(field_key, field_key)
        value       = args['value']
        uuid        = args['uuid']
        workiz_post(f'job/update/{uuid}/', {workiz_field: str(value)})
        # Also sync snapshot to Odoo SO if applicable
        so_id = args.get('so_id')
        if so_id and field_key in ODOO_SO_SNAPSHOT_FIELDS:
            odoo_rpc('sale.order', 'write', [[so_id],
                {ODOO_SO_SNAPSHOT_FIELDS[field_key]: str(value)}])
            return f"[WORKIZ + Odoo] {args['field_name'].title()} updated for {pname}: {value}"
        return f"[WORKIZ] {args['field_name'].title()} updated for {pname}: {value}"

    # --- Update an Odoo contact profile field ---
    if tool_name == 'update_odoo_contact':
        field_key   = args['field_name'].lower().replace(' ', '_')
        odoo_field  = ODOO_CONTACT_FIELDS.get(field_key)
        if not odoo_field:
            return f"Unknown contact field: {args['field_name']}"
        odoo_rpc('res.partner', 'write', [[args['partner_id']],
            {odoo_field: str(args['value'])}])
        return f"[ODOO] Contact {args['field_name'].title()} updated for {pname}: {args['value']}"

    # --- Post a note to Odoo chatter ---
    if tool_name == 'post_odoo_note':
        odoo_rpc('sale.order', 'message_post', [[args['so_id']]],
            {'body': f'[Render] {args["note"]}'})
        return f"[ODOO] Note posted to {pname} chatter: \"{args['note']}\""

    # --- Create a follow-up To-do ---
    if tool_name == 'create_todo':
        days = int(args.get('days', 7))
        note = args.get('note', 'Follow-up')
        due_dt  = datetime.datetime.now() + datetime.timedelta(days=days)
        due_str = due_dt.strftime('%Y-%m-%d 12:00:00')
        due_disp = due_dt.strftime('%m-%d-%Y')
        todo_id = odoo_rpc('project.task', 'create', [{
            'name': f'[Render] Follow-up: {pname}',
            'description': note,
            'project_id': False,
            'user_ids': [(4, ODOO_USER_ID)],
            'partner_id': args['partner_id'],
            'date_deadline': due_str,
        }])
        so_id = args.get('so_id')
        if so_id and todo_id:
            todo_url = f'https://window-solar-care.odoo.com/odoo/to-do/{todo_id}'
            odoo_rpc('sale.order', 'message_post', [[so_id]], {
                'body': f'[Render] To-Do | Customer: {pname} | Due: {due_disp} | {todo_url}'
            })
        return f"[ODOO] To-do created for {pname} due {due_disp}: \"{note}\""

    # --- Mark job Done ---
    if tool_name == 'mark_job_done':
        workiz_post(f'job/update/{args["uuid"]}/', {'Status': 'Done'})
        return f"[WORKIZ] Job marked Done for {pname}"

    # --- Create a new Workiz job ---
    if tool_name == 'create_workiz_job':
        # ClientId must be a valid positive integer — catch bad values early
        try:
            client_id_int = int(args['client_id'])
            if client_id_int <= 0:
                return "Cannot create job: no valid Workiz ClientId. Search for the customer first using search_customers, then get_customer_profile to get their ClientId."
        except (ValueError, TypeError):
            return "Cannot create job: ClientId is missing or invalid. Get the customer profile first."

        # Phone is required by Workiz — must be a valid phone string
        phone_val = str(args.get('phone') or '').strip()
        if not phone_val:
            return "Cannot create job: phone number is required by Workiz. Get the customer profile first to retrieve their phone number."

        # postal_code may come from get_customer_profile as 'zip' — accept both
        postal = str(args.get('postal_code') or args.get('zip') or '').strip()

        # If still missing, look up directly from Odoo using ClientId (ref field)
        addr_fallback = {}
        if not postal or not args.get('address') or not args.get('city'):
            try:
                partners = odoo_rpc('res.partner', 'search_read',
                    [[['ref', '=', str(client_id_int)]]],
                    {'fields': ['street', 'city', 'state_id', 'zip'], 'limit': 1})
                if partners:
                    rec = partners[0]
                    addr_fallback['address'] = rec.get('street') or ''
                    addr_fallback['city']    = rec.get('city') or ''
                    addr_fallback['state']   = rec['state_id'][1] if isinstance(rec.get('state_id'), list) else ''
                    addr_fallback['postal']  = rec.get('zip') or ''
                    if not postal:
                        postal = addr_fallback['postal']
            except Exception:
                pass

        payload = {
            'ClientId':           client_id_int,
            'FirstName':          str(args.get('first_name') or ''),
            'LastName':           str(args.get('last_name') or ''),
            'Phone':              phone_val,
            'Country':            'US',
            'JobType':            str(args.get('job_type') or 'Window Cleaning'),
            'type_of_service_2':  str(args.get('type_of_service') or 'On Request') if str(args.get('type_of_service') or '').lower() in ('maintenance', 'on request', 'unknown', '') else 'On Request',
            'frequency':          str(args.get('frequency') or 'Unknown'),
            'confirmation_method': str(args.get('confirmation_method') or 'Cell Phone'),
            'ok_to_text':         str(args.get('ok_to_text') or 'Yes'),
            'JobSource':          'Referral',
        }
        # Only include address fields if non-empty — Workiz rejects empty required strings
        # Use GPT-provided values first, fall back to Odoo lookup
        address_val = str(args.get('address') or addr_fallback.get('address') or '')
        city_val    = str(args.get('city')    or addr_fallback.get('city')    or '')
        state_val   = str(args.get('state')   or addr_fallback.get('state')   or '')
        if address_val: payload['Address'] = address_val
        if city_val:    payload['City']    = city_val
        if state_val:   payload['State']   = state_val
        if postal:                payload['PostalCode'] = postal
        if args.get('service_area'): payload['ServiceArea'] = str(args['service_area'])
        if args.get('job_datetime'):
            payload['JobDateTime'] = args['job_datetime']
        if args.get('notes'):
            payload['JobNotes'] = args['notes']
        if args.get('pricing'):
            payload['pricing'] = str(args['pricing'])
        if args.get('gate_code'):
            payload['gate_code'] = str(args['gate_code'])

        raw = workiz_post('job/create/', payload)
        # Response: {"flag": true, "data": [{"UUID": "...", "link": "..."}], "code": 201}
        uuid = ''
        link = ''
        if isinstance(raw, dict):
            data = raw.get('data', [])
        elif isinstance(raw, list) and raw:
            data = raw[0].get('data', []) if isinstance(raw[0], dict) else raw
        else:
            data = []
        if isinstance(data, list) and data:
            uuid = data[0].get('UUID') or ''
            link = data[0].get('link') or ''
        if uuid:
            return f"[WORKIZ] Job created for {pname} — UUID: {uuid}\nWorkiz link: {link}\n(Zapier will sync to Odoo automatically)"
        return f"[WORKIZ] Job created for {pname} (no UUID returned — check Workiz)"

    # --- Duplicate an existing Workiz job with a new date ---
    if tool_name == 'duplicate_workiz_job':
        # Resolve source UUID
        uuid = str(args.get('source_uuid') or '').strip()
        partner_id = args.get('partner_id')
        if not uuid and partner_id:
            sos = odoo_rpc('sale.order', 'search_read',
                [[['partner_id', '=', partner_id], ['state', 'in', ['sale', 'done']],
                  ['x_studio_x_studio_workiz_uuid', '!=', False]]],
                {'fields': ['x_studio_x_studio_workiz_uuid'], 'order': 'date_order desc', 'limit': 1})
            if not sos:
                sos = odoo_rpc('sale.order', 'search_read',
                    [[['partner_shipping_id', '=', partner_id], ['state', 'in', ['sale', 'done']],
                      ['x_studio_x_studio_workiz_uuid', '!=', False]]],
                    {'fields': ['x_studio_x_studio_workiz_uuid'], 'order': 'date_order desc', 'limit': 1})
            if sos:
                uuid = sos[0].get('x_studio_x_studio_workiz_uuid') or ''
        if not uuid:
            return "Cannot duplicate: no Workiz job found for this customer."

        # Fetch source job from Workiz
        raw_job = workiz_get(f'job/get/{uuid}/')
        if not raw_job:
            return f"Cannot duplicate: could not fetch job {uuid} from Workiz."
        job_data = raw_job.get('data', {})
        job = job_data[0] if isinstance(job_data, list) and job_data else job_data
        if not job:
            return "Cannot duplicate: no job data returned from Workiz."

        # Validate ClientId
        try:
            client_id_int = int(str(job.get('ClientId') or '').replace('CL-', '').strip())
            if client_id_int <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return f"Cannot duplicate: invalid ClientId on source job."

        phone = str(job.get('Phone') or job.get('Phone2') or '').strip()
        if not phone:
            return "Cannot duplicate: source job has no phone number."

        new_dt = str(args.get('new_datetime') or '').strip()
        if not new_dt:
            return "Cannot duplicate: no new date/time provided."

        payload = {
            'ClientId':            client_id_int,
            'FirstName':           str(job.get('FirstName') or ''),
            'LastName':            str(job.get('LastName') or ''),
            'Phone':               phone,
            'Country':             'US',
            'JobType':             str(job.get('JobType') or 'Window Cleaning'),
            'type_of_service_2':   str(job.get('type_of_service_2') or 'On Request'),
            'frequency':           str(job.get('frequency') or 'Unknown'),
            'confirmation_method': str(job.get('confirmation_method') or 'Cell Phone'),
            'ok_to_text':          str(job.get('ok_to_text') or 'Yes'),
            'JobSource':           'Referral',
            'JobDateTime':         new_dt,
        }
        if job.get('Address'):    payload['Address']    = str(job['Address'])
        if job.get('City'):       payload['City']       = str(job['City'])
        if job.get('State'):      payload['State']      = str(job['State'])
        if job.get('PostalCode'): payload['PostalCode'] = str(job['PostalCode'])
        if job.get('gate_code'):  payload['gate_code']  = str(job['gate_code'])
        if job.get('pricing'):    payload['pricing']    = str(job['pricing'])
        if job.get('JobNotes'):   payload['JobNotes']   = str(job['JobNotes'])

        raw_result = workiz_post('job/create/', payload)
        new_uuid = ''
        new_link = ''
        if isinstance(raw_result, dict):
            data = raw_result.get('data', [])
        elif isinstance(raw_result, list) and raw_result:
            data = raw_result[0].get('data', []) if isinstance(raw_result[0], dict) else raw_result
        else:
            data = []
        if isinstance(data, list) and data:
            new_uuid = data[0].get('UUID') or ''
            new_link = data[0].get('link') or ''

        cust = pname or f"{job.get('FirstName', '')} {job.get('LastName', '')}".strip()
        if new_uuid:
            return (f"[WORKIZ] Job duplicated for {cust} — UUID: {new_uuid}\n"
                    f"  Copied from: {uuid}\n"
                    f"  New date: {new_dt}\n"
                    f"  Workiz link: {new_link}\n"
                    f"  (Zapier will sync to Odoo automatically)")
        return f"[WORKIZ] Job duplicated for {cust} (no UUID returned — check Workiz)"

    return f"Unknown write action: {tool_name}"


def _describe_write(tool_name: str, args: dict) -> str:
    pname = args.get('partner_name', 'customer')
    if tool_name == 'update_workiz_field':
        sys = '[WORKIZ + Odoo]' if args.get('field_name', '').lower() in ('gate_code', 'pricing') else '[WORKIZ]'
        return f"{sys} Update {args.get('field_name','').title()} for {pname} to: {args.get('value')}"
    if tool_name == 'update_odoo_contact':
        return f"[ODOO] Update contact {args.get('field_name','').title()} for {pname} to: {args.get('value')}"
    if tool_name == 'post_odoo_note':
        return f"[ODOO] Post note to {pname} chatter: \"{args.get('note')}\""
    if tool_name == 'create_todo':
        return f"[ODOO] Create follow-up To-do for {pname} in {args.get('days', 7)} days: \"{args.get('note')}\""
    if tool_name == 'mark_job_done':
        return f"[WORKIZ] Mark job Done for {pname}"
    if tool_name == 'create_workiz_job':
        dt = args.get('job_datetime') or 'unscheduled'
        svc = args.get('type_of_service') or args.get('job_type') or ''
        return (f"[WORKIZ] Create new job for {pname}\n"
                f"  Date/Time: {dt}\n"
                f"  Service: {svc}\n"
                f"  Notes: {args.get('notes') or '(none)'}\n"
                f"  Pricing: {args.get('pricing') or '(none)'}\n"
                f"  Zapier will sync to Odoo automatically")
    if tool_name == 'duplicate_workiz_job':
        return (f"[WORKIZ] Duplicate job for {pname}\n"
                f"  New date/time: {args.get('new_datetime')}\n"
                f"  Copied from: {args.get('source_uuid') or 'most recent job'}\n"
                f"  All fields (address, gate code, pricing, notes) will be copied\n"
                f"  Zapier will sync to Odoo automatically")
    return f"Execute {tool_name} for {pname}"


# ---------------------------------------------------------------------------
# Tool definitions for OpenAI
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_customers",
            "description": "Search for customers by name. Call this first whenever you need to act on a specific customer. Returns partner_id, Workiz UUID, Workiz ClientId, and active SO info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Name or partial name to search. Strip possessives automatically."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_profile",
            "description": "Get full contact profile: address, phone, all custom fields (pricing, frequency, type_of_service, alternating, gate_code, ok_to_text, confirmation_method, last_date_cleaned, service_area). Call this before creating a new job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer"}
                },
                "required": ["partner_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_details",
            "description": "Get current job details for a customer: SO info, Workiz status, all job-level fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer"}
                },
                "required": ["partner_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedule",
            "description": "Get all jobs scheduled for a given day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "today, tomorrow, monday–sunday, or YYYY-MM-DD"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_job",
            "description": "Get the next upcoming job today.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales",
            "description": "Get total sales revenue for a single specific day. For weekly totals use get_sales_week instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_week",
            "description": "Get total sales revenue for the week (Monday–Sunday) containing a given date. Use this for 'this week', 'last week', 'weekly sales', or 'how much did I make this week' questions. Filters by scheduled job date in Odoo — do NOT use get_jobs_list for revenue questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Any date in the week (YYYY-MM-DD or 'today'). Defaults to current week if omitted."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_jobs_list",
            "description": "Fetch a list of Workiz jobs with filtering. offset=0 returns first 100, offset=1 returns next 100, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date":  {"type": "string", "description": "YYYY-MM-DD — fetch jobs from this date until today"},
                    "records":     {"type": "integer", "description": "Max records per page (max 100, default 50)"},
                    "only_open":   {"type": "boolean", "description": "Exclude Done and Canceled jobs (default true)"},
                    "offset":      {"type": "integer", "description": "Page number: 0=first 100, 1=next 100, etc."},
                    "status":      {"type": "array", "items": {"type": "string"}, "description": "Filter by status values e.g. ['Pending','Submitted']"}
                },
                "required": ["start_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigate_to",
            "description": "Get a Google Maps navigation button for a customer's address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id":    {"type": "integer"},
                    "customer_name": {"type": "string"}
                },
                "required": ["partner_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_workiz_field",
            "description": (
                "Update any field on a Workiz job. "
                "Valid field_name values: gate_code, pricing, notes, substatus, type_of_service, "
                "frequency, alternating, last_date_cleaned, ok_to_text, confirmation_method. "
                "gate_code and pricing also sync the Odoo SO snapshot."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid":         {"type": "string", "description": "Workiz job UUID"},
                    "field_name":   {"type": "string", "description": "Field to update"},
                    "value":        {"type": "string", "description": "New value"},
                    "partner_name": {"type": "string"},
                    "so_id":        {"type": "integer", "description": "Odoo SO ID for snapshot sync (gate_code/pricing)"}
                },
                "required": ["uuid", "field_name", "value", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_odoo_contact",
            "description": (
                "Update a field on the Odoo contact/partner record (permanent profile, not job-specific). "
                "Valid field_name values: pricing, frequency, type_of_service, alternating, gate_code, "
                "ok_to_text, confirmation_method, last_date_cleaned, notes (internal notes — permanent reminders like 'has a dog', 'prefers morning appointments')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id":   {"type": "integer"},
                    "field_name":   {"type": "string"},
                    "value":        {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["partner_id", "field_name", "value", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "post_odoo_note",
            "description": "Post a note to the Odoo sales order chatter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "so_id":        {"type": "integer"},
                    "note":         {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["so_id", "note", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_todo",
            "description": "Create a follow-up To-do in Odoo for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id":   {"type": "integer"},
                    "note":         {"type": "string"},
                    "days":         {"type": "integer", "description": "Days from today (default 7)"},
                    "partner_name": {"type": "string"},
                    "so_id":        {"type": "integer"}
                },
                "required": ["partner_id", "note", "days", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_job_done",
            "description": "Mark a Workiz job as Done.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid":         {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["uuid", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_workiz_job",
            "description": (
                "Create a new job in Workiz for an existing customer. "
                "Call get_customer_profile first to get client_id, name, address, phone, and default field values. "
                "Ask DJ for: date/time (or leave unscheduled), type_of_service, pricing, and any notes. "
                "Zapier will automatically sync the new job to Odoo — do NOT create an Odoo SO separately."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id":          {"type": "string",  "description": "Workiz numeric ClientId (from get_customer_profile)"},
                    "first_name":         {"type": "string"},
                    "last_name":          {"type": "string"},
                    "phone":              {"type": "string"},
                    "address":            {"type": "string"},
                    "city":               {"type": "string"},
                    "state":              {"type": "string",  "description": "Default: CA"},
                    "postal_code":        {"type": "string", "description": "ZIP code — use the 'zip' field from get_customer_profile"},
                    "job_type":           {"type": "string",  "description": "e.g. Window Cleaning, Solar Panel Cleaning"},
                    "service_area":       {"type": "string"},
                    "job_datetime":       {"type": "string",  "description": "YYYY-MM-DD HH:MM:SS in Pacific Time. Omit for unscheduled."},
                    "type_of_service":    {"type": "string",  "description": "Valid values: Maintenance, On Request, Unknown. Default to On Request if unsure. Do NOT use job_type value here."},
                    "frequency":          {"type": "string"},
                    "confirmation_method": {"type": "string"},
                    "ok_to_text":         {"type": "string"},
                    "notes":              {"type": "string"},
                    "pricing":            {"type": "string"},
                    "gate_code":          {"type": "string"},
                    "partner_name":       {"type": "string"}
                },
                "required": ["client_id", "first_name", "last_name", "phone",
                             "address", "city", "postal_code", "job_type", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "duplicate_workiz_job",
            "description": (
                "Duplicate an existing Workiz job for a customer and schedule it on a new date. "
                "Copies all fields from the source job (address, gate code, pricing, notes, service type, etc). "
                "Use when DJ says 'duplicate', 'copy', 'reschedule', or 'make another job like the last one'. "
                "Call search_customers first to get partner_id. Source UUID is optional — if omitted, uses the customer's most recent job."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id":   {"type": "integer", "description": "From search_customers"},
                    "partner_name": {"type": "string"},
                    "new_datetime": {"type": "string", "description": "New scheduled date/time: YYYY-MM-DD HH:MM:SS in Pacific Time"},
                    "source_uuid":  {"type": "string", "description": "UUID of the job to copy. Omit to use most recent job."}
                },
                "required": ["partner_id", "partner_name", "new_datetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "Send an email to DJ with any content — reports, schedules, customer details, summaries. "
                "Call this when DJ says 'email me', 'send me', or 'email that to me'. "
                "Generate the full readable content as the body first, then call this tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "subject":   {"type": "string", "description": "Email subject line"},
                    "body":      {"type": "string", "description": "Plain text email body — full content, well formatted"},
                    "to_email":  {"type": "string", "description": "Recipient email — omit to use DJ's default address"}
                },
                "required": ["subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": (
                "Save a fact to persistent memory that will be remembered across all future conversations. "
                "Call this when DJ says 'remember that...', 'always remember...', or provides info worth keeping forever. "
                "Use a short descriptive key (e.g. 'home_city', 'preferred_greeting', 'default_service_area')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key":   {"type": "string", "description": "Short identifier for this memory (snake_case)"},
                    "value": {"type": "string", "description": "The value to remember"}
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "Remove a previously saved memory. Call when DJ says 'forget that...' or 'stop remembering...'",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The memory key to remove"}
                },
                "required": ["key"]
            }
        }
    }
]

WRITE_TOOLS = {
    'update_workiz_field', 'update_odoo_contact', 'post_odoo_note',
    'create_todo', 'mark_job_done', 'create_workiz_job', 'duplicate_workiz_job'
}

READ_TOOL_MAP = {
    'search_customers':    lambda a: tool_search_customers(a['query']),
    'get_customer_profile': lambda a: tool_get_customer_profile(a['partner_id']),
    'get_job_details':     lambda a: tool_get_job_details(a['partner_id']),
    'get_schedule':        lambda a: tool_get_schedule(a['date']),
    'get_next_job':        lambda a: tool_get_next_job(),
    'get_sales':           lambda a: tool_get_sales(a['date']),
    'get_sales_week':      lambda a: tool_get_sales_week(a.get('date', '')),
    'get_jobs_list':       lambda a: tool_get_jobs_list(
        a['start_date'], a.get('records', 50),
        a.get('only_open', True), a.get('offset', 0), a.get('status')
    ),
    'navigate_to':         lambda a: tool_navigate_to(a['partner_id'], a.get('customer_name', '')),
    'send_email':          lambda a: tool_send_email(a['subject'], a['body'], a.get('to_email', '')),
    'save_memory':         lambda a: tool_save_memory(a['key'], a['value']),
    'delete_memory':       lambda a: tool_delete_memory(a['key']),
}


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a field assistant for Window & Solar Care, a window and solar panel cleaning company in Southern California. DJ Sanders is the owner and sole technician. He speaks to you by voice while driving or at job sites.

You have tools to read and write data in Odoo (business system) and Workiz (job scheduling).

GUIDELINES:
- Be very concise — DJ is on the road
- Always call search_customers before acting on a specific customer
- If multiple customers match, list them briefly and ask which one
- CONTEXT AWARENESS: get_schedule returns structured data including partner_id for each job. If a customer was already identified in this conversation (from a schedule result or previous search), use their partner_id DIRECTLY — do NOT search again. Example: if previous context shows Dana Zusman with partner_id 456, and DJ asks "does Dana have a gate code", call get_job_details(partner_id=456) immediately.
- For gate codes, notes, status, pricing — use get_job_details, not get_customer_profile.
- If you do need to search and get no exact match, consider the spelling may be off. Try the first name alone. Use context to pick the right result.
- For navigation: search_customers → navigate_to
- For next job navigation: get_next_job → navigate_to with the partner_id
- Before creating a new job: search_customers → get_customer_profile (to get client_id and defaults) → ask DJ for date/time and service type → create_workiz_job
- New jobs go to Workiz ONLY — Zapier handles the Odoo sync automatically
- NEVER attempt to create a job without a valid ClientId and phone number from get_customer_profile. ALWAYS call search_customers first, then get_customer_profile. Only if the customer genuinely does not exist in Odoo after searching should you tell DJ it can't be created.
- Times in Odoo are UTC. Pacific Time is UTC-7 (Mar–Nov) or UTC-8 (Nov–Mar)
- For multi-step tasks (like job creation), ask for missing info in a single message — collect everything before calling the write tool
- REVENUE QUERIES: Use get_sales for a single day, get_sales_week for any weekly total. NEVER use get_jobs_list for revenue or sales questions — it pulls from Workiz by job creation date, not scheduled date, and will give wrong numbers.
- get_jobs_list is only for browsing open Workiz jobs (e.g. "show me all pending jobs"). It is NOT a financial tool.
"""


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------
def _serialize_msg(msg) -> dict:
    """Convert an OpenAI message object to a plain dict for history storage."""
    if isinstance(msg, dict):
        return msg
    d = {'role': msg.role}
    if msg.content:
        d['content'] = msg.content
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        d['tool_calls'] = [
            {'id': tc.id, 'type': 'function',
             'function': {'name': tc.function.name, 'arguments': tc.function.arguments}}
            for tc in msg.tool_calls
        ]
    return d


def run_agent(user_input: str, mode: str = 'confirm', session_id: str = '') -> dict:
    client   = OpenAI(api_key=OPENAI_KEY)
    today_str = datetime.datetime.utcnow().strftime('%A, %B %d, %Y — current UTC time: %H:%M')

    # Load persistent memories and inject into system prompt
    memories = load_agent_memory()
    memory_text = ''
    if memories:
        memory_text = '\n\nPERSISTENT MEMORIES (facts DJ has asked you to remember across all conversations):\n'
        for k, v in memories.items():
            memory_text += f'- {k}: {v}\n'

    # Load session history
    history = get_history(session_id) if session_id else []

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT + memory_text + f'\nToday: {today_str}'}]
    messages += history
    messages.append({'role': 'user', 'content': user_input})
    turn_start = len(messages) - 1  # index of the user message that starts this turn

    for _ in range(12):
        resp = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            tools=TOOLS,
            tool_choice='auto',
            max_tokens=800
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            # GPT is asking a question or giving a final answer
            content = msg.content or 'Done.'
            # Save full turn to session — user msg + all tool calls/results + final response
            # This gives GPT full context in subsequent turns (e.g., partner_id from schedule)
            if session_id:
                new_turn = [_serialize_msg(m) for m in messages[turn_start:]]
                new_turn.append({'role': 'assistant', 'content': content})
                save_history(session_id, history + new_turn)
            return {'status': 'done', 'message': content}

        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except Exception:
                args = {}

            if name in WRITE_TOOLS:
                if mode == 'immediate':
                    result = execute_write_tool(name, args)
                    if session_id:
                        clear_history(session_id)
                    return {'status': 'done', 'message': result}
                else:
                    return {
                        'status': 'pending',
                        'confirmation': _describe_write(name, args),
                        'write_action': {'tool': name, 'args': args},
                        'session_id': session_id
                    }

            elif name in READ_TOOL_MAP:
                try:
                    result = READ_TOOL_MAP[name](args)
                except Exception as e:
                    result = {'error': str(e)}

                # navigate_to returns HTML — return immediately
                if name == 'navigate_to' and isinstance(result, str) and '<a href=' in result:
                    return {'status': 'done', 'message': result}

                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': json.dumps(result) if not isinstance(result, str) else result
                })

            else:
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'content': f'Unknown tool: {name}'
                })

    return {'status': 'error', 'message': 'Could not complete the request.'}


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

HELP_TEXT = """Here's what I can do:

SCHEDULE & INFO
• What's my schedule today / tomorrow / Monday
• What's my next job
• What are my sales today / this Friday
• What's the status of [customer]
• Get a list of open Workiz jobs since [date]

NAVIGATE
• Navigate to [customer]
• Take me to my next job

CREATE A JOB
• Create a job for [customer]
  (I'll ask for date, time, and service type — everything else I pull from the customer record)

UPDATE WORKIZ JOB FIELDS
• Gate code / pricing / notes / status for [customer] is [value]
• Update frequency / type of service / alternating / ok to text / confirmation method
  for [customer] to [value]

UPDATE ODOO CONTACT PROFILE
• Update [customer]'s contact pricing / frequency / type of service to [value]
  (permanent profile — affects all future jobs)

LOG & TASKS
• Add a note to [customer]: [text]
• Create a follow-up to-do for [customer] in [N] days

EMAIL
• Email me today's schedule
• Email me this week's sales report
• Email me [customer]'s job details
• Send me that (emails whatever was just shown)

MEMORY (persists forever across all conversations)
• Remember that [fact]
• Always remember [key info]
• Forget that [fact]
• What do you remember about me"""

HELP_PHRASES = {
    'what can you do', 'what do you do', 'help', 'commands', 'what are your commands',
    'what can i say', 'what are my options', 'show me what you can do',
    'what do you know how to do', 'capabilities'
}


@app.post('/ask')
async def ask(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        raise HTTPException(status_code=401, detail='Invalid access code')

    user_input = body.get('input', '').strip()
    mode       = body.get('mode', 'confirm')
    session_id = body.get('session_id', '')

    if not user_input:
        return JSONResponse({'error': 'No input provided'})

    if user_input.lower().strip('?.! ') in HELP_PHRASES:
        return JSONResponse({'status': 'done', 'message': HELP_TEXT})

    # Handle "what do you remember" directly
    lower_input = user_input.lower().strip('?.! ')
    if any(p in lower_input for p in ('what do you remember', 'what have you remembered', 'show me your memory', 'what do you know about me')):
        memories = load_agent_memory()
        if not memories:
            return JSONResponse({'status': 'done', 'message': "I don't have any saved memories yet. Say 'remember that...' to save something."})
        lines = ['Here\'s what I remember:\n']
        for k, v in memories.items():
            lines.append(f'• {k}: {v}')
        return JSONResponse({'status': 'done', 'message': '\n'.join(lines)})

    try:
        result = run_agent(user_input, mode=mode, session_id=session_id)
        return JSONResponse(result)
    except Exception as ex:
        return JSONResponse({'status': 'error', 'message': str(ex)})


@app.post('/execute')
async def execute(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        raise HTTPException(status_code=401, detail='Invalid access code')

    write_action = body.get('write_action', {})
    tool_name    = write_action.get('tool', '')
    args         = write_action.get('args', {})
    session_id   = body.get('session_id', '')

    try:
        result = execute_write_tool(tool_name, args)
        if session_id:
            clear_history(session_id)
        return JSONResponse({'status': 'done', 'message': result})
    except Exception as ex:
        return JSONResponse({'status': 'error', 'message': str(ex)})


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------
@app.get('/', response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()
