# ==============================================================================
# WINDOW & SOLAR CARE — MOBILE VOICE INTERFACE BACKEND (v3)
# Deploy: Render.com (env vars: ODOO_API_KEY, WORKIZ_TOKEN, WORKIZ_SECRET, ANTHROPIC_API_KEY, ACCESS_CODE)
# AI: Anthropic Claude (migrated from OpenAI 2026-04-15)
# ==============================================================================

import os, json, re, datetime, urllib.parse, base64, threading
from zoneinfo import ZoneInfo
_PT = ZoneInfo('America/Los_Angeles')

def today_pt() -> datetime.date:
    """Today's date in Pacific Time — avoids jobs disappearing at 5 PM UTC."""
    return datetime.datetime.now(tz=_PT).date()
import httpx
import anthropic
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ODOO_URL       = os.environ.get('ODOO_URL',         'https://window-solar-care.odoo.com')
ODOO_DB        = os.environ.get('ODOO_DB',          'window-solar-care')
ODOO_USER_ID   = int(os.environ.get('ODOO_USER_ID', '2'))
ODOO_API_KEY   = os.environ.get('ODOO_API_KEY',     '')
WORKIZ_TOKEN   = os.environ.get('WORKIZ_TOKEN',     '')
WORKIZ_SECRET  = os.environ.get('WORKIZ_SECRET',    'sec_334084295850678330105471548')
ANTHROPIC_KEY  = os.environ.get('ANTHROPIC_API_KEY','')
CLAUDE_MODEL   = os.environ.get('CLAUDE_MODEL',     'claude-sonnet-4-6')
ACCESS_CODE    = os.environ.get('ACCESS_CODE',      'wsc2026')
OWNER_EMAIL    = os.environ.get('OWNER_EMAIL',      '')
GITHUB_TOKEN   = os.environ.get('GITHUB_TOKEN',    '')
GITHUB_REPO    = os.environ.get('GITHUB_REPO',    'windowandsolarcare-hash/Odoo-Migration')
SHARED_MEMORY_PATH = os.environ.get('SHARED_MEMORY_PATH', '3_Documentation/SHARED_MEMORY.md')

app = FastAPI()

# ---------------------------------------------------------------------------
# Shared memory — loaded from GitHub SHARED_MEMORY.md
# Cached on startup, auto-refreshed every 60 min, manual refresh on demand
# GITHUB_REPO and SHARED_MEMORY_PATH are env vars — update on Render to switch projects
# ---------------------------------------------------------------------------
_shared_memory_cache: dict = {'content': '', 'last_loaded': None}
_shared_memory_lock = threading.Lock()

def _fetch_shared_memory() -> str:
    """Fetch SHARED_MEMORY.md from GitHub. Returns content string or empty."""
    if not GITHUB_TOKEN:
        return ''
    try:
        headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
        resp = httpx.get(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{SHARED_MEMORY_PATH}',
            headers=headers, timeout=10
        )
        if resp.status_code == 404:
            return ''
        resp.raise_for_status()
        return base64.b64decode(resp.json()['content'].replace('\n', '')).decode('utf-8')
    except Exception:
        return _shared_memory_cache.get('content', '')  # return stale on error

def refresh_shared_memory():
    """Refresh the shared memory cache from GitHub."""
    content = _fetch_shared_memory()
    with _shared_memory_lock:
        _shared_memory_cache['content'] = content
        _shared_memory_cache['last_loaded'] = datetime.datetime.utcnow()

def get_shared_memory() -> str:
    """Return cached shared memory content."""
    with _shared_memory_lock:
        return _shared_memory_cache.get('content', '')

def _auto_refresh_loop():
    """Background thread: refresh shared memory every 60 minutes."""
    while True:
        threading.Event().wait(3600)  # 60 minutes
        refresh_shared_memory()

# Load on startup in background so it doesn't block server start
threading.Thread(target=refresh_shared_memory, daemon=True).start()
# Start auto-refresh loop
threading.Thread(target=_auto_refresh_loop, daemon=True).start()

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
    # Never start mid-turn — orphaned tool_result blocks cause Anthropic errors.
    # Always trim from the front until we land on a plain user text message.
    while trimmed and (trimmed[0].get('role') != 'user' or isinstance(trimmed[0].get('content'), list)):
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
    today = today_pt()
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
                    'x_studio_x_studio_workiz_status', 'x_studio_x_studio_workiz_uuid',
                    'x_studio_x_workiz_link'],
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
            'workiz_link': so.get('x_studio_x_workiz_link') or '',
            'time_utc': so['date_order'][11:16] if so.get('date_order') else '?',
            'amount': amount,
            'status': so.get('x_studio_x_studio_workiz_status') or ''
        })

    # Attach open tasks to each job so timer start/stop needs no extra lookup
    so_ids = [j['so_id'] for j in jobs]
    if so_ids:
        all_tasks = odoo_rpc('project.task', 'search_read',
            [[['sale_order_id', 'in', so_ids]]],
            {'fields': ['id', 'name', 'sale_order_id', 'stage_id', 'effective_hours'], 'order': 'id asc'})
        tasks_by_so = {}
        for t in all_tasks:
            sid = t['sale_order_id'][0] if t.get('sale_order_id') else None
            if sid:
                tasks_by_so.setdefault(sid, []).append({
                    'task_id': t['id'], 'task_name': t['name'],
                    'stage': t['stage_id'][1] if t.get('stage_id') else '',
                    'effective_hours': float(t.get('effective_hours') or 0),
                    'timer_running': False, 'timer_start': ''
                })
        # Check Render-owned timer (ir.config_parameter keys render.timer.{task_id})
        all_task_ids = [t['task_id'] for tlist in tasks_by_so.values() for t in tlist]
        if all_task_ids:
            param_keys = [f'render.timer.{tid}' for tid in all_task_ids]
            timer_params = odoo_rpc('ir.config_parameter', 'search_read',
                [[['key', 'in', param_keys]]],
                {'fields': ['key', 'value']})
            running = {int(p['key'].replace('render.timer.', '')): p['value']
                       for p in timer_params if p.get('value', '').strip()}
            for tlist in tasks_by_so.values():
                for t in tlist:
                    if t['task_id'] in running:
                        t['timer_running'] = True
                        t['timer_start'] = running[t['task_id']]
        for job in jobs:
            job['tasks'] = tasks_by_so.get(job['so_id'], [])

    return {'label': label, 'date': date_iso, 'count': len(jobs), 'jobs': jobs, 'total': total}


def tool_get_next_job() -> dict:
    now_str   = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    today_iso = today_pt().isoformat()
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

    # Fetch open tasks linked to this SO so timer start/stop needs no extra lookup
    so_id = result.get('so_id')
    if so_id:
        tasks = odoo_rpc('project.task', 'search_read',
            [[['sale_order_id', '=', so_id],
              ['stage_id', 'not in', [19]]]],  # exclude Done (stage 19)
            {'fields': ['id', 'name', 'stage_id', 'timer_start'], 'order': 'id asc'})
        result['tasks'] = [
            {'task_id': t['id'], 'task_name': t['name'],
             'stage': t['stage_id'][1] if t.get('stage_id') else '',
             'timer_running': bool(t.get('timer_start'))}
            for t in tasks
        ]
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
    """Returns total sales for the work week (Mon–Fri) containing the given date. Weekends excluded."""
    date_iso, _ = resolve_date(date if date else 'today')
    try:
        d = datetime.date.fromisoformat(date_iso)
    except Exception:
        d = datetime.date.today()
    monday = d - datetime.timedelta(days=d.weekday())
    friday = monday + datetime.timedelta(days=4)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', monday.isoformat() + ' 00:00:00'],
          ['date_order', '<=', friday.isoformat() + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']]]],
        {'fields': ['amount_total', 'date_order', 'partner_id']})
    if not sos:
        return f"No sales for week of {monday} – {friday}."
    by_day = {}
    for so in sos:
        day = (so.get('date_order') or '')[:10]
        dow = datetime.date.fromisoformat(day).weekday()
        if dow >= 5:  # skip Saturday(5) / Sunday(6)
            continue
        by_day[day] = by_day.get(day, 0) + float(so.get('amount_total') or 0)
    total = sum(by_day.values())
    count = len([s for s in sos if datetime.date.fromisoformat((s.get('date_order') or '2000-01-01')[:10]).weekday() < 5])
    day_lines = ', '.join(f"{k}: ${v:.0f}" for k, v in sorted(by_day.items()) if v > 0)
    return f"Week of {monday} – {friday}: ${total:.2f} across {count} job(s). By day: {day_lines}"


def tool_get_sales_month() -> dict:
    """Returns month-to-date (Done jobs) and full-month forecast (all scheduled Mon-Fri SOs).
    Forecast = done + future scheduled — no extrapolation."""
    import calendar
    today = today_pt()
    month_start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    month_end = today.replace(day=last_day)

    # All confirmed SOs for the entire month (Mon–Fri only)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', month_start.isoformat() + ' 00:00:00'],
          ['date_order', '<=', month_end.isoformat() + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']]]],
        {'fields': ['amount_total', 'date_order', 'x_studio_x_studio_workiz_status']})

    mtd_total = 0.0
    mtd_count = 0
    forecast_total = 0.0
    forecast_count = 0
    days = {}  # {iso_date: {'amount': float, 'count': int}}

    for so in sos:
        raw_dt_str = so.get('date_order') or ''
        if not raw_dt_str:
            continue
        try:
            # date_order is UTC — convert to Pacific to get the correct calendar day
            dt_utc = datetime.datetime.strptime(raw_dt_str[:19], '%Y-%m-%d %H:%M:%S')
            dt_pt  = dt_utc.replace(tzinfo=datetime.timezone.utc).astimezone(_PT)
            d      = dt_pt.date()
        except Exception:
            continue
        if d.weekday() >= 5:  # skip Saturday(5) and Sunday(6)
            continue
        amt = float(so.get('amount_total') or 0)
        status = (so.get('x_studio_x_studio_workiz_status') or '').lower()
        # Count ALL Mon-Fri confirmed SOs — no Workiz status filter (Done, Scheduled, etc. all count)
        # Only exclusion: weekend (handled above) and Odoo-cancelled (handled by query state filter)
        iso = d.isoformat()
        if iso not in days:
            days[iso] = {'amount': 0.0, 'count': 0}
        days[iso]['amount'] += amt
        days[iso]['count']  += 1
        forecast_total += amt
        forecast_count += 1
        if d <= today and status == 'done':
            mtd_total += amt
            mtd_count += 1

    # Round amounts in days dict
    for v in days.values():
        v['amount'] = round(v['amount'])

    return {
        'mtd': round(mtd_total),
        'mtd_count': mtd_count,
        'forecast': round(forecast_total),
        'forecast_count': forecast_count,
        'month_label': today.strftime('%B %Y'),
        'days': days,
    }


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


def tool_refresh_shared_memory() -> str:
    """Force-refresh shared memory from GitHub right now."""
    refresh_shared_memory()
    content = get_shared_memory()
    last = _shared_memory_cache.get('last_loaded')
    last_str = last.strftime('%H:%M UTC') if last else 'unknown'
    lines = len(content.splitlines()) if content else 0
    return f"Shared memory refreshed at {last_str} — {lines} lines loaded."


def tool_odoo_query(model: str, method: str, args: list, kwargs: dict = None) -> any:
    """Execute any read operation on any Odoo model."""
    SAFE_METHODS = {'search_read', 'read', 'search', 'search_count', 'fields_get',
                    'name_search', 'name_get', 'default_get', 'get_views', 'get_view'}
    if method not in SAFE_METHODS:
        return {'error': f"Method '{method}' not allowed in odoo_query. Use odoo_write for modifications."}
    return odoo_rpc(model, method, args, kwargs or {})


def tool_github_read_file(file_path: str) -> str:
    """Read any file from the GitHub repo."""
    if not GITHUB_TOKEN:
        return 'GITHUB_TOKEN env var not set on Render.'
    headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    resp = httpx.get(
        f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}',
        headers=headers, timeout=20
    )
    if resp.status_code == 404:
        return f'File not found: {file_path}'
    resp.raise_for_status()
    data = resp.json()
    return base64.b64decode(data['content'].replace('\n', '')).decode('utf-8')


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
        payload['State'] = state_val or 'CA'  # required by Workiz
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
            if not sos:
                # partner_id may be the Contact — look up its Property children and search those
                children = odoo_rpc('res.partner', 'search_read',
                    [[['parent_id', '=', partner_id],
                      ['x_studio_x_studio_record_category', '=', 'Property']]],
                    {'fields': ['id'], 'limit': 20})
                child_ids = [c['id'] for c in children]
                if child_ids:
                    sos = odoo_rpc('sale.order', 'search_read',
                        [[['partner_id', 'in', child_ids], ['state', 'in', ['sale', 'done']],
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
        payload['State'] = str(job.get('State') or 'CA')  # required by Workiz
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

    # --- Start timer on an Odoo task ---
    if tool_name == 'start_task_timer':
        task_id = args.get('task_id')
        task_name = args.get('task_name', '')
        if not task_id and task_name:
            tasks = odoo_rpc('project.task', 'search_read',
                [[['name', 'ilike', task_name]]],
                {'fields': ['id', 'name'], 'limit': 5})
            if not tasks:
                return f"No task found matching '{task_name}'"
            if len(tasks) > 1:
                names = ', '.join(f"{t['name']} (ID {t['id']})" for t in tasks)
                return f"Multiple tasks match — be more specific: {names}"
            task_id = tasks[0]['id']
            task_name = tasks[0]['name']
        if not task_id:
            return "No task ID or name provided."
        _render_timer_start(task_id)
        return f"[ODOO] ✅ Timer started on task: {task_name or task_id} — task moved to In Progress"

    # --- Stop timer on an Odoo task ---
    if tool_name == 'stop_task_timer':
        task_id = args.get('task_id')
        task_name = args.get('task_name', '')
        if not task_id and task_name:
            tasks = odoo_rpc('project.task', 'search_read',
                [[['name', 'ilike', task_name]]],
                {'fields': ['id', 'name'], 'limit': 5})
            if not tasks:
                return f"No task found matching '{task_name}'"
            if len(tasks) > 1:
                names = ', '.join(f"{t['name']} (ID {t['id']})" for t in tasks)
                return f"Multiple tasks match — be more specific: {names}"
            task_id = tasks[0]['id']
            task_name = tasks[0]['name']
        if not task_id:
            return "No task ID or name provided."
        result = _render_timer_stop(task_id)
        if not result['ok']:
            return f"[ODOO] {result['message']}"
        return f"[ODOO] ✅ Timer stopped on task: {task_name or task_id} — {result['message']}"

    # --- Record payment: create invoice → confirm → pay → Phase 6 fires ---
    if tool_name == 'record_check_payment':
        so_id   = args['so_id']
        so_name = args.get('so_name', '')
        amount  = float(args['amount'])
        today   = datetime.date.today().isoformat()
        payment_date = str(args.get('payment_date') or today)

        # Map payment method to Odoo payment_method_line_id (all on Bank journal ID=6)
        PAYMENT_METHOD_LINE = {
            'check':  8,   # Check (Bank)
            'cash':   6,   # Cash
            'zelle':  6,   # Cash journal, memo = Zelle
            'venmo':  6,   # Cash journal, memo = Venmo
            'credit': 7,   # Credit
        }
        raw_method          = str(args.get('payment_method', 'check')).lower().strip()
        payment_method_line = PAYMENT_METHOD_LINE.get(raw_method, 8)
        memo                = str(args.get('memo', args.get('check_number', raw_method.title())))
        # Normalize payment method keywords to title case (e.g. "zelle" → "Zelle")
        if memo.lower() in ('zelle', 'venmo', 'cash', 'check', 'credit'):
            memo = memo.title()
        check_number        = memo  # keep variable name for return message

        # Check for existing draft invoice on this SO first (avoid duplicates)
        so_data = odoo_rpc('sale.order', 'read', [[so_id]], {'fields': ['invoice_ids', 'name']})
        if not so_data:
            return f"Sales order not found: {so_id}"
        existing_inv_ids = so_data[0].get('invoice_ids', [])
        draft_inv = []
        if existing_inv_ids:
            draft_inv = odoo_rpc('account.move', 'search_read',
                [[['id', 'in', existing_inv_ids], ['state', '=', 'draft'],
                  ['move_type', '=', 'out_invoice']]],
                {'fields': ['id', 'name', 'amount_total'], 'limit': 1})

        if not draft_inv:
            # Create invoice from SO via wizard (action_create_invoices removed in Odoo 19)
            inv_ctx = {'active_ids': [so_id], 'active_model': 'sale.order', 'active_id': so_id}
            inv_wiz = odoo_rpc('sale.advance.payment.inv', 'create',
                [{'advance_payment_method': 'delivered'}], {'context': inv_ctx})
            odoo_rpc('sale.advance.payment.inv', 'create_invoices', [[inv_wiz]], {'context': inv_ctx})
            so_data2     = odoo_rpc('sale.order', 'read', [[so_id]], {'fields': ['invoice_ids']})
            new_inv_ids  = so_data2[0].get('invoice_ids', []) if so_data2 else []
            draft_inv    = odoo_rpc('account.move', 'search_read',
                [[['id', 'in', new_inv_ids], ['state', '=', 'draft'],
                  ['move_type', '=', 'out_invoice']]],
                {'fields': ['id', 'name', 'amount_total'], 'limit': 1})

        if not draft_inv:
            return f"[ODOO] Could not create or find a draft invoice for {so_name}. Check Odoo."
        invoice_id    = draft_inv[0]['id']
        invoice_total = float(draft_inv[0].get('amount_total') or 0)

        # Confirm the invoice first — assigns the INV/2026/xxxxx number
        odoo_rpc('account.move', 'action_post', [[invoice_id]])

        # Read name after confirm (draft name is False before action_post)
        confirmed = odoo_rpc('account.move', 'read', [[invoice_id]], {'fields': ['name']})
        invoice_name = confirmed[0]['name'] if confirmed else ''

        # Chatter on SO: audit trail for invoice creation
        odoo_rpc('sale.order', 'message_post', [[so_id]], {
            'body': f'[Render] Invoice {invoice_name} created | Customer: {pname} | Amount: ${invoice_total:.2f} | {today}'
        })

        # Register payment via wizard — handles reconciliation with invoice automatically
        wizard_ctx = {'active_model': 'account.move', 'active_ids': [invoice_id], 'active_id': invoice_id}
        wizard_id  = odoo_rpc('account.payment.register', 'create', [{
            'payment_date':           payment_date,
            'amount':                 amount,
            'communication':          memo,
            'journal_id':             6,   # Bank
            'payment_method_line_id': payment_method_line,
        }], {'context': wizard_ctx})
        odoo_rpc('account.payment.register', 'action_create_payments', [[wizard_id]],
                 {'context': wizard_ctx})

        # Chatter on invoice: audit trail for payment
        odoo_rpc('account.move', 'message_post', [[invoice_id]], {
            'body': f'[Render] Payment recorded | Customer: {pname} | ${amount:.2f} | Method: {raw_method.title()} | Ref: {memo} | Date: {payment_date} | {today}'
        })

        partial_note = f' (partial — invoice total ${invoice_total:.2f})' if abs(amount - invoice_total) > 0.01 else ''
        ref_label = 'Check #' if raw_method == 'check' else f'{raw_method.title()} ref: ' if check_number.lower() != raw_method else ''
        return (f"[ODOO] ✅ Invoice {invoice_name} created & paid\n"
                f"  Customer: {pname}\n"
                f"  {ref_label}{check_number} | ${amount:.2f}{partial_note} | {payment_date}\n"
                f"  Phase 6 will sync to Workiz automatically.")

    # --- Update SHARED_MEMORY.md on GitHub ---
    if tool_name == 'update_shared_memory':
        if not GITHUB_TOKEN:
            return 'GITHUB_TOKEN env var not set on Render.'
        new_content = args['content']
        headers     = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
        get_resp    = httpx.get(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{SHARED_MEMORY_PATH}',
            headers=headers, timeout=10
        )
        sha     = get_resp.json().get('sha', '') if get_resp.status_code == 200 else ''
        today   = datetime.date.today().isoformat()
        payload = {
            'message': f'{today} | SHARED_MEMORY.md | {args.get("summary", "update shared memory")}',
            'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
            'branch':  'main'
        }
        if sha:
            payload['sha'] = sha
        put_resp = httpx.put(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{SHARED_MEMORY_PATH}',
            headers=headers, json=payload, timeout=20
        )
        put_resp.raise_for_status()
        # Update local cache immediately
        with _shared_memory_lock:
            _shared_memory_cache['content'] = new_content
            _shared_memory_cache['last_loaded'] = datetime.datetime.utcnow()
        return f"[GITHUB] SHARED_MEMORY.md updated and cache refreshed."

    # --- General Odoo write/create/unlink/action ---
    if tool_name == 'odoo_write':
        result = odoo_rpc(args['model'], args['method'], args['args'], args.get('kwargs') or {})
        return f"[ODOO] {args['method']} on {args['model']}: {json.dumps(result)[:300]}"

    # --- Push a file to GitHub main ---
    if tool_name == 'github_push_file':
        if not GITHUB_TOKEN:
            return 'GITHUB_TOKEN env var not set on Render.'
        file_path  = args['file_path']
        content    = args['content']
        commit_msg = args['commit_message']
        headers    = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
        get_resp   = httpx.get(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}',
            headers=headers, timeout=20
        )
        sha     = get_resp.json().get('sha', '') if get_resp.status_code == 200 else ''
        payload = {
            'message': commit_msg,
            'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            'branch':  'main'
        }
        if sha:
            payload['sha'] = sha
        put_resp = httpx.put(
            f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}',
            headers=headers, json=payload, timeout=30
        )
        put_resp.raise_for_status()
        return f"[GITHUB] Pushed {file_path} to main: {commit_msg}"

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
    if tool_name == 'start_task_timer':
        task_ref = args.get('task_name') or f"ID {args.get('task_id')}"
        return f"[ODOO] Start timer on task: {task_ref}"
    if tool_name == 'stop_task_timer':
        task_ref = args.get('task_name') or f"ID {args.get('task_id')}"
        return f"[ODOO] Stop timer on task: {task_ref}"
    if tool_name == 'record_check_payment':
        method = str(args.get('payment_method','check')).title()
        memo   = str(args.get('memo',''))
        return (f"[ODOO] Create invoice + register payment\n"
                f"  Customer: {pname} | SO: {args.get('so_name')}\n"
                f"  Method: {method} | Memo: {memo} | ${float(args.get('amount',0)):.2f} | {datetime.date.today().isoformat()}\n"
                f"  Phase 6 will sync to Workiz automatically")
    if tool_name == 'update_shared_memory':
        return f"[GITHUB] Update SHARED_MEMORY.md: {args.get('summary','')}"
    if tool_name == 'odoo_write':
        return f"[ODOO] {args.get('method','write')} on {args.get('model')}\n  {args.get('description','')}\n  args: {json.dumps(args.get('args',''))[:200]}"
    if tool_name == 'github_push_file':
        return f"[GITHUB] Push to main: {args.get('file_path')}\n  Commit: {args.get('commit_message')}"
    return f"Execute {tool_name} for {pname}"


# ---------------------------------------------------------------------------
# Tool definitions — Anthropic native format
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "search_customers",
        "description": "Search for customers by name. Returns partner_id, Workiz UUID, Workiz ClientId, and active SO info.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_customer_profile",
        "description": "Get full contact profile: address, phone, pricing, frequency, type_of_service, alternating, gate_code, ok_to_text, confirmation_method, last_date_cleaned, service_area, workiz_client_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer"}
            },
            "required": ["partner_id"]
        }
    },
    {
        "name": "get_job_details",
        "description": "Get current job details for a customer: SO info, Workiz status, gate code, pricing, notes, all job-level fields.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id": {"type": "integer"}
            },
            "required": ["partner_id"]
        }
    },
    {
        "name": "get_schedule",
        "description": "Get all jobs scheduled for a given day.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "today, tomorrow, monday–sunday, or YYYY-MM-DD"}
            },
            "required": ["date"]
        }
    },
    {
        "name": "get_next_job",
        "description": "Get the next upcoming job today.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_sales",
        "description": "Get total sales revenue for a single day.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"}
            },
            "required": ["date"]
        }
    },
    {
        "name": "get_sales_week",
        "description": "Get total sales revenue for the work week (Mon–Sat) containing a date. Use for 'this week', 'weekly sales', 'how much this week'. Filters by scheduled job date in Odoo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Any date in the week (YYYY-MM-DD or 'today'). Defaults to current week."}
            }
        }
    },
    {
        "name": "get_jobs_list",
        "description": "Fetch a list of Workiz jobs. For browsing open jobs — NOT for revenue/sales questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date":  {"type": "string", "description": "YYYY-MM-DD"},
                "records":     {"type": "integer", "description": "Max per page (default 50, max 100)"},
                "only_open":   {"type": "boolean", "description": "Exclude Done/Canceled (default true)"},
                "offset":      {"type": "integer", "description": "Page: 0=first 100, 1=next 100"},
                "status":      {"type": "array", "items": {"type": "string"}}
            },
            "required": ["start_date"]
        }
    },
    {
        "name": "navigate_to",
        "description": "Get a Google Maps navigation button for a customer's address.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id":    {"type": "integer"},
                "customer_name": {"type": "string"}
            },
            "required": ["partner_id"]
        }
    },
    {
        "name": "update_workiz_field",
        "description": "Update a field on a Workiz job. Valid field_name values: gate_code, pricing, notes, substatus, type_of_service, frequency, alternating, last_date_cleaned, ok_to_text, confirmation_method. gate_code and pricing also sync the Odoo SO snapshot.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid":         {"type": "string"},
                "field_name":   {"type": "string"},
                "value":        {"type": "string"},
                "partner_name": {"type": "string"},
                "so_id":        {"type": "integer", "description": "Odoo SO ID for snapshot sync (gate_code/pricing)"}
            },
            "required": ["uuid", "field_name", "value", "partner_name"]
        }
    },
    {
        "name": "update_odoo_contact",
        "description": "Update a field on the Odoo contact record (permanent profile). Valid field_name values: pricing, frequency, type_of_service, alternating, gate_code, ok_to_text, confirmation_method, last_date_cleaned, notes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id":   {"type": "integer"},
                "field_name":   {"type": "string"},
                "value":        {"type": "string"},
                "partner_name": {"type": "string"}
            },
            "required": ["partner_id", "field_name", "value", "partner_name"]
        }
    },
    {
        "name": "post_odoo_note",
        "description": "Post a note to the Odoo sales order chatter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "so_id":        {"type": "integer"},
                "note":         {"type": "string"},
                "partner_name": {"type": "string"}
            },
            "required": ["so_id", "note", "partner_name"]
        }
    },
    {
        "name": "create_todo",
        "description": "Create a follow-up To-do in Odoo for a customer.",
        "input_schema": {
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
    },
    {
        "name": "mark_job_done",
        "description": "Mark a Workiz job as Done.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uuid":         {"type": "string"},
                "partner_name": {"type": "string"}
            },
            "required": ["uuid", "partner_name"]
        }
    },
    {
        "name": "create_workiz_job",
        "description": "Create a new job in Workiz for an existing customer. Call get_customer_profile first to get client_id, address, phone, and defaults. Zapier will sync to Odoo automatically — do NOT create an Odoo SO separately.",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_id":           {"type": "string"},
                "first_name":          {"type": "string"},
                "last_name":           {"type": "string"},
                "phone":               {"type": "string"},
                "address":             {"type": "string"},
                "city":                {"type": "string"},
                "state":               {"type": "string", "description": "Default: CA"},
                "postal_code":         {"type": "string"},
                "job_type":            {"type": "string", "description": "e.g. Window Cleaning, Solar Panel Cleaning"},
                "service_area":        {"type": "string"},
                "job_datetime":        {"type": "string", "description": "YYYY-MM-DD HH:MM:SS Pacific. Omit for unscheduled."},
                "type_of_service":     {"type": "string", "description": "Maintenance, On Request, or Unknown"},
                "frequency":           {"type": "string"},
                "confirmation_method": {"type": "string"},
                "ok_to_text":          {"type": "string"},
                "notes":               {"type": "string"},
                "pricing":             {"type": "string"},
                "gate_code":           {"type": "string"},
                "partner_name":        {"type": "string"}
            },
            "required": ["client_id", "first_name", "last_name", "phone",
                         "address", "city", "postal_code", "job_type", "partner_name"]
        }
    },
    {
        "name": "duplicate_workiz_job",
        "description": "Duplicate an existing Workiz job for a customer with a new date. Copies all fields. Use for 'duplicate', 'copy', 'make another job like the last one'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id":   {"type": "integer"},
                "partner_name": {"type": "string"},
                "new_datetime": {"type": "string", "description": "YYYY-MM-DD HH:MM:SS Pacific"},
                "source_uuid":  {"type": "string", "description": "UUID to copy. Omit to use most recent job."}
            },
            "required": ["partner_id", "partner_name", "new_datetime"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to DJ. Use when DJ says 'email me' or 'send me that'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject":  {"type": "string"},
                "body":     {"type": "string"},
                "to_email": {"type": "string", "description": "Omit to use DJ's default address"}
            },
            "required": ["subject", "body"]
        }
    },
    {
        "name": "save_memory",
        "description": "Save a fact to persistent memory across all future conversations. Use for 'remember that...'",
        "input_schema": {
            "type": "object",
            "properties": {
                "key":   {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["key", "value"]
        }
    },
    {
        "name": "delete_memory",
        "description": "Remove a saved memory. Use for 'forget that...'",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string"}
            },
            "required": ["key"]
        }
    },
    {
        "name": "start_task_timer",
        "description": "Start the timer on an Odoo To-Do or task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id":   {"type": "integer"},
                "task_name": {"type": "string"}
            }
        }
    },
    {
        "name": "stop_task_timer",
        "description": "Stop the timer on an Odoo To-Do or task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id":   {"type": "integer"},
                "task_name": {"type": "string"}
            }
        }
    },
    # ---- POWER TOOLS ----
    {
        "name": "odoo_query",
        "description": "Execute any read operation on any Odoo model — search_read, read, search, search_count, fields_get. Use when the specific tools above don't cover what you need.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model":  {"type": "string", "description": "e.g. 'sale.order', 'res.partner', 'account.move', 'ir.actions.server'"},
                "method": {"type": "string", "description": "search_read, read, search, search_count, fields_get"},
                "args":   {"type": "array",  "description": "Positional args e.g. [[['name','ilike','Smith']]]"},
                "kwargs": {"type": "object", "description": "e.g. {'fields': ['id','name'], 'limit': 10}"}
            },
            "required": ["model", "method", "args"]
        }
    },
    {
        "name": "odoo_write",
        "description": "Execute any write/create/unlink/action on any Odoo model. Requires confirmation. Use for bug fixes, data corrections, running server actions, updating any field not covered by specific tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model":       {"type": "string"},
                "method":      {"type": "string", "description": "write, create, unlink, action_confirm, run, execute, message_post, etc."},
                "args":        {"type": "array"},
                "kwargs":      {"type": "object"},
                "description": {"type": "string", "description": "Plain English description of what this does — shown to DJ for confirmation"}
            },
            "required": ["model", "method", "args", "description"]
        }
    },
    {
        "name": "github_read_file",
        "description": "Read any file from the GitHub repo windowandsolarcare-hash/Odoo-Migration. Use to inspect current code before making changes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "e.g. '1_Production_Code/zapier_phase4_FLATTENED_FINAL.py'"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "github_push_file",
        "description": "Push a file to GitHub main branch. Deploying to main = Zapier picks it up immediately. For Odoo server actions, also call odoo_write to update the live action.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path":      {"type": "string"},
                "content":        {"type": "string", "description": "Full file content"},
                "commit_message": {"type": "string", "description": "Format: YYYY-MM-DD | filename | description"}
            },
            "required": ["file_path", "content", "commit_message"]
        }
    },
    {
        "name": "record_check_payment",
        "description": (
            "Create an invoice from a Sales Order, confirm it, and register a payment. "
            "Handles: check, cash, Zelle, Venmo, credit card. "
            "Use when DJ says 'received check/cash/Zelle/Venmo/credit [amount] from [customer]'. "
            "First call search_customers, then odoo_query for their confirmed SOs "
            "(sale.order where partner_id=X and state in [sale,done]). "
            "If multiple SOs, list them and ask DJ which one. "
            "Phase 6 fires automatically — no Workiz action needed. "
            "Payment method mapping: check→Check(Bank), cash→Cash, zelle→Cash+memo=Zelle, "
            "venmo→Cash+memo=Venmo, credit→Credit."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "partner_id":      {"type": "integer"},
                "partner_name":    {"type": "string"},
                "so_id":           {"type": "integer", "description": "The SO to invoice"},
                "so_name":         {"type": "string",  "description": "e.g. S04400"},
                "amount":          {"type": "number",  "description": "Payment amount in dollars"},
                "payment_method":  {"type": "string",  "description": "check | cash | zelle | venmo | credit"},
                "memo":            {"type": "string",  "description": "Check number, 'Zelle', 'Venmo', 'Cash', etc. Goes in memo field."},
                "payment_date":    {"type": "string",  "description": "Date payment was received, YYYY-MM-DD. Defaults to today if not provided."}
            },
            "required": ["partner_id", "partner_name", "so_id", "so_name", "amount", "payment_method", "memo"]
        }
    },
    {
        "name": "refresh_shared_memory",
        "description": "Force-refresh shared memory from GitHub right now. Use when DJ says 'refresh your memory' or 'refresh memory'.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "update_shared_memory",
        "description": "Write updated content to SHARED_MEMORY.md on GitHub — the shared brain accessible by both Render Claude and Claude Code. Use when DJ says 'save that to shared memory' or after important context changes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Full new content of SHARED_MEMORY.md"},
                "summary": {"type": "string", "description": "One-line description of what changed"}
            },
            "required": ["content", "summary"]
        }
    }
]

WRITE_TOOLS = {
    'update_workiz_field', 'update_odoo_contact', 'post_odoo_note',
    'create_todo', 'mark_job_done', 'create_workiz_job', 'duplicate_workiz_job',
    'start_task_timer', 'stop_task_timer',
    'odoo_write', 'github_push_file', 'update_shared_memory', 'record_check_payment'
}

READ_TOOL_MAP = {
    'search_customers':     lambda a: tool_search_customers(a['query']),
    'get_customer_profile': lambda a: tool_get_customer_profile(a['partner_id']),
    'get_job_details':      lambda a: tool_get_job_details(a['partner_id']),
    'get_schedule':         lambda a: tool_get_schedule(a['date']),
    'get_next_job':         lambda a: tool_get_next_job(),
    'get_sales':            lambda a: tool_get_sales(a['date']),
    'get_sales_week':       lambda a: tool_get_sales_week(a.get('date', '')),
    'get_jobs_list':        lambda a: tool_get_jobs_list(
        a['start_date'], a.get('records', 50),
        a.get('only_open', True), a.get('offset', 0), a.get('status')
    ),
    'navigate_to':          lambda a: tool_navigate_to(a['partner_id'], a.get('customer_name', '')),
    'send_email':           lambda a: tool_send_email(a['subject'], a['body'], a.get('to_email', '')),
    'save_memory':          lambda a: tool_save_memory(a['key'], a['value']),
    'delete_memory':        lambda a: tool_delete_memory(a['key']),
    'odoo_query':              lambda a: tool_odoo_query(a['model'], a['method'], a['args'], a.get('kwargs')),
    'github_read_file':        lambda a: tool_github_read_file(a['file_path']),
    'refresh_shared_memory':   lambda a: tool_refresh_shared_memory(),
}


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are Claude, a powerful field assistant and business operator for Window & Solar Care — a window and solar panel cleaning company in Southern California. DJ Sanders is the owner and sole technician, often speaking by voice while driving or on job sites.

WHAT YOU CAN ACCESS:
- Odoo (window-solar-care.odoo.com) — CRM, sales orders, contacts, invoicing, server actions, all business data
- Workiz — job scheduling, statuses, customer fields
- GitHub repo windowandsolarcare-hash/Odoo-Migration (main) — all automation code; push to main = instant Zapier deploy
- Zapier — runs Phases 3–6; fetches code from GitHub main on every trigger

ODOO FACTS:
- After action_confirm() on a SO, always write date_order back — Odoo resets it internally
- date_order = Workiz JobDateTime (start time, UTC). Never use end time.
- Server action deploy requires BOTH: push to GitHub AND write code to live Odoo action via odoo_write on ir.actions.server. Key IDs: LAUNCH=563
- No imports in server action code. No 'response' or 'result' variable names (reserved in Odoo 19).
- Chatter: plain text with | separators. Unicode emoji works. HTML gets escaped.
- Property partners: x_studio_x_studio_record_category = "Property"
- Custom field on SO: x_studio_x_studio_workiz_uuid (Workiz UUID)

WORKIZ FACTS:
- Everything except Done/Canceled/In Progress/Submitted is SubStatus with Status=Pending. Filter on SubStatus.
- Job GET response: data is a list — job = data[0]
- Deleted job = HTTP 204. Custom field = type_of_service_2 (not type_of_service).
- Defaults: type_of_service_2='On Request', frequency='Unknown', confirmation_method='Cell Phone', JobSource='Referral'

CORE FIELD WORKFLOW (make this seamless — no bumps):
1. "What's my next job" → get_next_job. Returns customer, address, so_id, partner_id, AND tasks[].
2. "Navigate" → navigate_to with partner_id from step 1. Never re-search.
3. "Start the timer" → start_task_timer using task_id from tasks[] in step 1.
   - If one task: start it immediately.
   - If multiple tasks: list them briefly, ask which one.
   - If timer already running on a task: say so, ask if they want to start a different one.
4. "Stop the timer" → stop_task_timer using task_id from session context. Never re-search.
5. "Received [method] for $[amount] from [customer]" → record_check_payment.
   - Customer already known from session: use partner_id and so_id directly.
   - Only search/ask if genuinely ambiguous.

PAYMENT FOR NON-TODAY JOBS (multi-step — follow exactly):
When DJ asks to process payment for a job not on today's schedule, or says "find SO for [name]" / "process payment for [name]":
Step 1 — Find the customer: call search_customers with their name.
Step 2 — Find their SOs: call odoo_query on sale.order with domain [['partner_id','in', PROPERTY_CHILD_IDS], ['state','in',['sale','done']]], order='date_order desc', limit=5, fields=['id','name','date_order','amount_total','x_studio_x_studio_workiz_uuid'].
  NOTE: SOs are on Property child partners, not the Contact directly. To get property children: odoo_query res.partner where parent_id=contact_id AND x_studio_x_studio_record_category='Property', fields=['id']. Then query SOs on those child IDs AND the contact_id directly (some SOs may be on the contact). Use city field (not x_studio_x_studio_service_area which is empty) for location queries.
Step 3 — Present options: Show SO name, date (formatted nicely), and amount. Ask DJ "Is this the right one?" if there's one obvious recent one, or list top options if ambiguous.
Step 4 — Confirm the SO: Wait for DJ to confirm before proceeding.
Step 5 — Ask for payment details: "What's the payment method (check/cash/Zelle/Venmo/credit), amount, date received, and memo/reference?"
  - If DJ says "same amount" or doesn't specify, use the SO's amount_total.
  - If DJ says "today" for date, use today's date. If they give a day like "last Tuesday" or "April 10th", convert to YYYY-MM-DD.
  - Accept voice-style answers like "$250 check April 10th, number 1042" → amount=250, method=check, payment_date='2026-04-10', memo='1042'
Step 6 — Call record_check_payment with the confirmed so_id, partner_id, amount, payment_method, memo, payment_date.
Be conversational and brief — DJ is often in the field. Confirm the final result clearly (invoice number + amount + method).

GENERAL TOOL GUIDANCE:
- Use partner_id and so_id from session context — never re-search for something already known
- get_sales / get_sales_week for revenue — never get_jobs_list for financial questions
- odoo_query for any data lookup not covered by specific tools
- odoo_write for any Odoo change
- For code fixes: github_read_file → fix → github_push_file → odoo_write if server action

CUSTOMERS WITHOUT FUTURE JOBS (common reactivation query):
When DJ asks for customers in a city with no upcoming job (e.g. "Hemet customers serviced in 2024/2025 with no open job"), follow these exact steps.
Use `city` field (ilike, case-insensitive) — x_studio_x_studio_service_area is empty for all contacts.
Workiz status field on sale.order is: x_studio_x_studio_workiz_status (values: 'Done', 'Canceled', 'Submitted', 'Pending', 'In Progress').

Step 1 — Get contacts: odoo_query res.partner where [city ilike 'Hemet', customer_rank>0, x_studio_activelead!='Do Not Contact', parent_id=False]. Fields: id, name, x_studio_x_type_of_service, x_studio_x_frequency, phone.
Step 2 — Get property children: odoo_query res.partner where [parent_id in [contact_ids], x_studio_x_studio_record_category='Property']. Fields: id, parent_id.
Step 3a — Done SOs in the requested year range: odoo_query sale.order where [partner_id in [all_ids], x_studio_x_studio_workiz_status='Done', date_order>='2024-01-01', date_order<='2025-12-31']. Fields: id, name, partner_id, date_order, amount_total.
Step 3b — Open future SOs: odoo_query sale.order where [partner_id in [all_ids], state='sale', date_order>=TODAY, x_studio_x_studio_workiz_status not in ['Done','Canceled']]. Fields: id, partner_id, date_order.
Step 4 — Map all partner_ids back to contact IDs via prop_to_contact. Group Done SOs and future SOs by contact.
Step 5 — Return contacts that: (a) have at least one Done SO in the date range, AND (b) have NO open future SOs.
Display: name, date of last Done job, SO name, amount, service type, frequency, phone. Sort by last Done date descending.

NEW JOB FOR EXISTING CUSTOMER (critical — follow this exactly):
- Jobs sync ONE WAY: Workiz → Odoo. Never create an Odoo SO directly for a new job.
- When DJ asks to create/schedule a new job for an existing customer:
  1. Search Odoo SOs for open jobs (state in ['draft','sale']) — if found, offer to use it
  2. If no open job: use duplicate_workiz_job with the customer's partner_id — it auto-finds their most recent UUID
  3. NEVER use create_workiz_job for existing customers — duplicate_workiz_job copies all fields correctly
  4. Zapier Phase 3 will sync the new Workiz job to Odoo automatically — tell DJ this

MONTHLY JOB LISTS (stats screen grand total, email lists, etc.):
- Source: Odoo sale.order ONLY — never use Workiz API for monthly job counts/lists (Workiz only_open=True excludes Done jobs).
- Criteria: state in ['sale','done'], date_order in the month, Mon–Fri only (skip weekday() >= 5 after UTC→PT conversion), ALL Workiz statuses count (Done, Submitted, Scheduled, Pending — everything except Odoo-cancelled SOs).
- The stats screen grand total uses this exact logic. When DJ asks you to list the jobs behind that number, query Odoo SOs with the same filter.

Pacific Time: UTC-7 (Mar–Nov), UTC-8 (Nov–Mar). Be concise — DJ is in the field."""


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


def run_agent(user_input: str, mode: str = 'confirm', session_id: str = '') -> dict:
    client    = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    today_str = datetime.datetime.utcnow().strftime('%A, %B %d, %Y — current UTC time: %H:%M')

    # Inject shared memory from GitHub (cached, refreshed every 60 min)
    shared_mem = get_shared_memory()
    shared_mem_text = f'\n\nSHARED MEMORY (synced from GitHub — known facts about this business and project):\n{shared_mem}' if shared_mem else ''

    # Legacy Odoo memories (kept for backward compat — will phase out)
    memories = load_agent_memory()
    odoo_mem_text = ''
    if memories:
        odoo_mem_text = '\n\nADDITIONAL MEMORIES (Odoo store):\n'
        for k, v in memories.items():
            odoo_mem_text += f'- {k}: {v}\n'

    system_prompt = SYSTEM_PROMPT + shared_mem_text + odoo_mem_text + f'\nToday: {today_str}'

    # Load session history — Anthropic messages contain only user/assistant roles (no system)
    history = get_history(session_id) if session_id else []
    turn_start_idx = len(history)  # index in combined list where this turn begins

    messages = list(history)
    messages.append({'role': 'user', 'content': user_input})

    for _ in range(12):
        resp = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
            tools=TOOLS
        )

        if resp.stop_reason == 'end_turn':
            # Claude is done — extract text from content blocks
            content = next((b.text for b in resp.content if hasattr(b, 'text')), 'Done.')
            if session_id:
                new_turn = messages[turn_start_idx:]
                new_turn.append({'role': 'assistant', 'content': content})
                save_history(session_id, history + new_turn)
            return {'status': 'done', 'message': content}

        if resp.stop_reason == 'tool_use':
            # Add Claude's response (with tool_use blocks) to messages
            # Anthropic requires the raw content list as the assistant message
            assistant_content = [
                b.model_dump() if hasattr(b, 'model_dump') else b
                for b in resp.content
            ]
            messages.append({'role': 'assistant', 'content': assistant_content})

            tool_results = []
            pending_write = None

            for block in resp.content:
                if not hasattr(block, 'type') or block.type != 'tool_use':
                    continue

                name = block.name
                args = block.input  # already a dict in Anthropic (not a JSON string)

                if name in WRITE_TOOLS:
                    if mode == 'immediate':
                        result = execute_write_tool(name, args)
                        if session_id:
                            clear_history(session_id)
                        return {'status': 'done', 'message': result}
                    else:
                        # Return pending confirmation — caller will re-submit with mode='immediate'
                        pending_write = {
                            'status': 'pending',
                            'confirmation': _describe_write(name, args),
                            'write_action': {'tool': name, 'args': args},
                            'session_id': session_id
                        }
                        # Still need to send a tool_result so Anthropic doesn't error on resume
                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': block.id,
                            'content': 'Awaiting user confirmation.'
                        })

                elif name in READ_TOOL_MAP:
                    try:
                        result = READ_TOOL_MAP[name](args)
                    except Exception as e:
                        result = {'error': str(e)}

                    # navigate_to returns HTML — return immediately
                    if name == 'navigate_to' and isinstance(result, str) and '<a href=' in result:
                        return {'status': 'done', 'message': result}

                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': block.id,
                        'content': json.dumps(result) if not isinstance(result, str) else result
                    })

                else:
                    tool_results.append({
                        'type': 'tool_result',
                        'tool_use_id': block.id,
                        'content': f'Unknown tool: {name}'
                    })

            # All tool results go into a single user message (Anthropic requirement)
            if tool_results:
                messages.append({'role': 'user', 'content': tool_results})

            # Return pending write confirmation after tool results are appended
            if pending_write:
                return pending_write

        else:
            # Unexpected stop reason
            break

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

    # Handle explicit memory refresh
    lower_input = user_input.lower().strip('?.! ')
    if any(p in lower_input for p in ('refresh your memory', 'refresh memory', 'update your memory', 'reload memory')):
        refresh_shared_memory()
        last = _shared_memory_cache.get('last_loaded')
        last_str = last.strftime('%H:%M UTC') if last else 'now'
        content  = get_shared_memory()
        lines    = len(content.splitlines()) if content else 0
        return JSONResponse({'status': 'done', 'message': f"Memory refreshed at {last_str} — {lines} lines loaded from GitHub."})

    # Handle "what do you remember" directly
    if any(p in lower_input for p in ('what do you remember', 'what have you remembered', 'show me your memory', 'what do you know about me')):
        shared = get_shared_memory()
        odoo_mems = load_agent_memory()
        lines = []
        if shared:
            lines.append('SHARED MEMORY (GitHub):\n' + shared)
        if odoo_mems:
            lines.append('\nODOO MEMORIES:')
            for k, v in odoo_mems.items():
                lines.append(f'• {k}: {v}')
        if not lines:
            return JSONResponse({'status': 'done', 'message': "No saved memories yet. Say 'remember that...' to save something."})
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
def _batch_addresses(jobs: list) -> dict:
    """Batch-fetch addresses for a list of jobs. Returns {partner_id: address_string}."""
    pids = list({j['partner_id'] for j in jobs if j.get('partner_id')})
    if not pids:
        return {}
    try:
        partners = odoo_rpc('res.partner', 'read', [pids],
            {'fields': ['id', 'street', 'city', 'state_id', 'zip']})
        result = {}
        for p in partners:
            parts = [p.get('street') or '', p.get('city') or '', p.get('zip') or '']
            result[p['id']] = ', '.join(x for x in parts if x)
        return result
    except Exception:
        return {}


def _execute_payment(so_id: int, amount: float, payment_method: str, memo: str, payment_date: str = '') -> dict:
    """Record payment on an SO. Returns {'ok': bool, 'message': str}."""
    PAYMENT_METHOD_LINE = {'check': 8, 'cash': 6, 'zelle': 6, 'venmo': 6, 'credit': 7}
    raw_method          = str(payment_method or 'check').lower().strip()
    pml                 = PAYMENT_METHOD_LINE.get(raw_method, 8)
    if not memo:
        memo = raw_method.title()
    # Normalize payment method keywords to title case (e.g. "zelle" → "Zelle")
    if memo.lower() in ('zelle', 'venmo', 'cash', 'check', 'credit'):
        memo = memo.title()
    today = datetime.date.today().isoformat()
    payment_date = payment_date or today

    so_data = odoo_rpc('sale.order', 'read', [[so_id]],
        {'fields': ['invoice_ids', 'name', 'partner_id']})
    if not so_data:
        return {'ok': False, 'message': f'SO {so_id} not found'}
    so_name  = so_data[0].get('name', '')
    partner  = so_data[0].get('partner_id') or [None, '']
    customer = partner[1].split(',')[0].strip() if partner else ''

    existing = so_data[0].get('invoice_ids', [])
    draft_inv = []
    if existing:
        draft_inv = odoo_rpc('account.move', 'search_read',
            [[['id', 'in', existing], ['state', '=', 'draft'], ['move_type', '=', 'out_invoice']]],
            {'fields': ['id', 'name', 'amount_total'], 'limit': 1})
    if not draft_inv:
        # Create invoice from SO via wizard (action_create_invoices removed in Odoo 19)
        inv_ctx2 = {'active_ids': [so_id], 'active_model': 'sale.order', 'active_id': so_id}
        inv_wiz2 = odoo_rpc('sale.advance.payment.inv', 'create',
            [{'advance_payment_method': 'delivered'}], {'context': inv_ctx2})
        odoo_rpc('sale.advance.payment.inv', 'create_invoices', [[inv_wiz2]], {'context': inv_ctx2})
        so2      = odoo_rpc('sale.order', 'read', [[so_id]], {'fields': ['invoice_ids']})
        new_ids  = so2[0].get('invoice_ids', []) if so2 else []
        draft_inv = odoo_rpc('account.move', 'search_read',
            [[['id', 'in', new_ids], ['state', '=', 'draft'], ['move_type', '=', 'out_invoice']]],
            {'fields': ['id', 'name', 'amount_total'], 'limit': 1})
    if not draft_inv:
        return {'ok': False, 'message': f'Could not create draft invoice for {so_name}'}

    inv_id    = draft_inv[0]['id']
    inv_total = float(draft_inv[0].get('amount_total') or 0)

    # Confirm invoice first — assigns the INV/2026/xxxxx number (draft name is False)
    odoo_rpc('account.move', 'action_post', [[inv_id]])

    # Read name after confirm
    confirmed2 = odoo_rpc('account.move', 'read', [[inv_id]], {'fields': ['name']})
    inv_name   = confirmed2[0]['name'] if confirmed2 else ''

    # Chatter on SO: audit trail for invoice creation
    odoo_rpc('sale.order', 'message_post', [[so_id]], {
        'body': f'[Render] Invoice {inv_name} created | Customer: {customer} | Amount: ${inv_total:.2f} | {today}'
    })
    ctx = {'active_model': 'account.move', 'active_ids': [inv_id], 'active_id': inv_id}
    wiz = odoo_rpc('account.payment.register', 'create', [{
        'payment_date': payment_date, 'amount': amount, 'communication': memo,
        'journal_id': 6, 'payment_method_line_id': pml,
    }], {'context': ctx})
    odoo_rpc('account.payment.register', 'action_create_payments', [[wiz]], {'context': ctx})

    # Chatter on invoice: audit trail for payment
    odoo_rpc('account.move', 'message_post', [[inv_id]], {
        'body': f'[Render] Payment recorded | Customer: {customer} | ${amount:.2f} | Method: {raw_method.title()} | Ref: {memo} | Date: {payment_date} | {today}'
    })

    partial = f' (partial — inv ${inv_total:.2f})' if abs(amount - inv_total) > 0.01 else ''
    return {'ok': True, 'message': f'{inv_name} | {customer} | {raw_method.title()} ${amount:.2f}{partial} | {payment_date} | Phase 6 syncing'}


@app.get('/api/dashboard')
async def api_dashboard(access_code: str = ''):
    if access_code != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    try:
        schedule = tool_get_schedule('today')
        addr_map = _batch_addresses(schedule.get('jobs', []))
        for job in schedule.get('jobs', []):
            if job.get('partner_id') and not job.get('address'):
                job['address'] = addr_map.get(job['partner_id'], '')
    except Exception:
        schedule = {'count': 0, 'total': 0, 'jobs': []}
    try:
        next_job_raw = tool_get_next_job()
        next_job = {
            'customer':   next_job_raw.get('customer', ''),
            'address':    next_job_raw.get('address', ''),
            'time_utc':   next_job_raw.get('time_utc', ''),
            'amount':     next_job_raw.get('amount', 0),
            'so_id':      next_job_raw.get('so_id'),
            'partner_id': next_job_raw.get('partner_id'),
        } if not next_job_raw.get('error') else {}
    except Exception:
        next_job = {}
    try:
        week_sales = tool_get_sales_week('')
    except Exception:
        week_sales = ''
    try:
        month_data = tool_get_sales_month()
    except Exception:
        month_data = {}
    return {'schedule': schedule, 'next_job': next_job, 'week_sales': week_sales, 'month_data': month_data}


ODOO_EMPLOYEE_ID = 1   # Dan Saunders — hr.employee ID for user 2
ODOO_PROJECT_ID  = 2   # Field Service project

# ---------------------------------------------------------------------------
# Render-owned timer helpers — bypasses Odoo's action_timer_start/stop entirely.
# Odoo's timer is unreliable (timer_start doesn't clear, duplicate log entries).
# We store our own start time in ir.config_parameter and create the timesheet
# entry ourselves on stop. GPS reverse-geocode gives the actual address worked at.
# ---------------------------------------------------------------------------

def _reverse_geocode(lat, lon) -> str:
    """Return a human-readable address from lat/lon using OpenStreetMap Nominatim."""
    try:
        resp = httpx.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={'lat': lat, 'lon': lon, 'format': 'json'},
            headers={'User-Agent': 'WindowSolarCare/1.0'},
            timeout=5
        )
        data = resp.json()
        addr = data.get('address', {})
        parts = []
        if addr.get('house_number'): parts.append(addr['house_number'])
        if addr.get('road'):         parts.append(addr['road'])
        city = addr.get('city') or addr.get('town') or addr.get('village') or ''
        if city:                     parts.append(city)
        if addr.get('state'):        parts.append(addr['state'])
        if addr.get('postcode'):     parts.append(addr['postcode'])
        return ', '.join(parts) if parts else data.get('display_name', f'{lat:.5f},{lon:.5f}')
    except Exception:
        return f'{lat:.5f},{lon:.5f}'


def _render_timer_start(task_id: int, lat=None, lon=None) -> dict:
    """Start our own timer for a task. Stores UTC start in ir.config_parameter.
    Clears any existing Odoo timer_start. Moves task to In Progress (18)."""
    start_utc = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    odoo_rpc('ir.config_parameter', 'set_param', [f'render.timer.{task_id}', start_utc])
    # Clear Odoo's own timer so it never runs (avoids stuck timer in UI)
    try:
        odoo_rpc('project.task', 'write', [[task_id], {'timer_start': False}])
    except Exception:
        pass
    # Move to In Progress
    odoo_rpc('project.task', 'write', [[task_id], {'stage_id': 18}])
    loc_note = ''
    if lat is not None and lon is not None:
        loc_note = f' | GPS: {lat:.5f},{lon:.5f}'
    return {'ok': True, 'message': f'Timer started{loc_note}', 'start_utc': start_utc}


def _render_timer_stop(task_id: int, lat=None, lon=None) -> dict:
    """Stop our timer, create the timesheet entry, clean up.
    If GPS provided, reverse-geocodes to get actual address worked at."""
    param_key   = f'render.timer.{task_id}'
    start_utc   = odoo_rpc('ir.config_parameter', 'get_param', [param_key]) or ''
    if not start_utc:
        return {'ok': False, 'message': 'No Render timer running for this task.'}
    try:
        start_dt      = datetime.datetime.strptime(start_utc[:19], '%Y-%m-%d %H:%M:%S')
        elapsed_hours = max(round((datetime.datetime.utcnow() - start_dt).total_seconds() / 3600, 4), 0.0001)
    except Exception as e:
        return {'ok': False, 'message': f'Could not parse timer start: {e}'}
    # Build time label (Pacific)
    start_pt = datetime.datetime.strptime(start_utc[:19], '%Y-%m-%d %H:%M:%S') \
                   .replace(tzinfo=datetime.timezone.utc).astimezone(_PT)
    end_pt   = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(_PT)
    time_range = f"{start_pt.strftime('%-I:%M %p')} – {end_pt.strftime('%-I:%M %p')}"
    # Build timesheet description
    if lat is not None and lon is not None:
        address  = _reverse_geocode(lat, lon)
        log_name = f'[Render Timer] {address} | {time_range}'
    else:
        log_name = f'[Render Timer] | {time_range}'
    # Read task for project_id
    task_data = odoo_rpc('project.task', 'read', [[task_id]], {'fields': ['project_id', 'name']})
    proj_id   = ODOO_PROJECT_ID
    if task_data and task_data[0].get('project_id'):
        p = task_data[0]['project_id']
        proj_id = p[0] if isinstance(p, (list, tuple)) else p
    # Create timesheet entry
    odoo_rpc('account.analytic.line', 'create', [{
        'employee_id': ODOO_EMPLOYEE_ID,
        'project_id':  proj_id,
        'task_id':     task_id,
        'date':        datetime.date.today().isoformat(),
        'unit_amount': elapsed_hours,
        'name':        log_name,
    }])
    # Clear our timer param and any stale Odoo timer_start
    odoo_rpc('ir.config_parameter', 'set_param', [param_key, ''])
    try:
        odoo_rpc('project.task', 'write', [[task_id], {'timer_start': False}])
    except Exception:
        pass
    mins = round(elapsed_hours * 60)
    return {'ok': True, 'message': f'Timer stopped — {mins} min logged', 'elapsed_hours': elapsed_hours, 'log_name': log_name}


@app.post('/api/timer/start')
async def api_timer_start(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    task_id = int(body.get('task_id', 0))
    if not task_id:
        return JSONResponse({'status': 'error', 'message': 'task_id required'})
    lat = body.get('lat')
    lon = body.get('lon')
    try:
        result = _render_timer_start(task_id, lat, lon)
        return {'status': 'ok', 'message': result['message']}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.post('/api/timer/stop')
async def api_timer_stop(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    task_id = int(body.get('task_id', 0))
    if not task_id:
        return JSONResponse({'status': 'error', 'message': 'task_id required'})
    lat = body.get('lat')
    lon = body.get('lon')
    try:
        result = _render_timer_stop(task_id, lat, lon)
        if not result['ok']:
            return JSONResponse({'status': 'error', 'message': result['message']})
        return {'status': 'ok', 'message': result['message']}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.post('/api/attachment')
async def api_attachment(request: Request):
    """Upload a photo and attach it to the active SO in Odoo."""
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    so_id        = int(body.get('so_id', 0))
    filename     = str(body.get('filename', 'photo.jpg'))
    content_type = str(body.get('content_type', 'image/jpeg'))
    data_b64     = str(body.get('data', ''))  # base64 encoded image
    if not so_id or not data_b64:
        return JSONResponse({'status': 'error', 'message': 'so_id and data required'})
    try:
        att_id = odoo_rpc('ir.attachment', 'create', [{
            'name':      filename,
            'res_model': 'sale.order',
            'res_id':    so_id,
            'datas':     data_b64,
            'mimetype':  content_type,
        }])
        return {'status': 'ok', 'attachment_id': att_id, 'message': f'Photo saved: {filename}'}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.post('/api/payment')
async def api_payment(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    so_id          = int(body.get('so_id', 0))
    amount         = float(body.get('amount', 0))
    payment_method = str(body.get('payment_method', 'check'))
    memo           = str(body.get('memo', '') or '')
    payment_date   = str(body.get('payment_date', '') or '')
    if not so_id or amount <= 0:
        return JSONResponse({'status': 'error', 'message': 'so_id and amount required'})
    try:
        result = _execute_payment(so_id, amount, payment_method, memo, payment_date)
        status = 'ok' if result['ok'] else 'error'
        return {'status': status, 'message': result['message']}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.get('/api/upcoming')
async def api_upcoming(access_code: str = ''):
    if access_code != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    try:
        today  = today_pt()
        end    = today + datetime.timedelta(days=10)
        sos    = odoo_rpc('sale.order', 'search_read',
            [[['date_order', '>=', today.isoformat() + ' 00:00:00'],
              ['date_order', '<=', end.isoformat() + ' 23:59:59'],
              ['state', 'in', ['sale', 'done']]]],
            {'fields': ['id', 'name', 'date_order', 'partner_id', 'amount_total',
                        'x_studio_x_studio_workiz_status', 'x_studio_x_workiz_link'],
             'order': 'date_order asc'})
        # Fetch tasks for all these SOs to get service type (Solar/Window)
        all_so_ids = [so['id'] for so in sos]
        tasks_by_so_up = {}
        if all_so_ids:
            up_tasks = odoo_rpc('project.task', 'search_read',
                [[['sale_order_id', 'in', all_so_ids]]],
                {'fields': ['id', 'name', 'sale_order_id'], 'order': 'id asc'})
            for t in up_tasks:
                sid = t['sale_order_id'][0] if t.get('sale_order_id') else None
                if sid:
                    tasks_by_so_up.setdefault(sid, []).append(t['name'])

        by_day = {}
        for so in sos:
            day = (so.get('date_order') or '')[:10]
            if day not in by_day:
                by_day[day] = {'date': day, 'jobs': [], 'total': 0.0}
            customer = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
            amount   = float(so.get('amount_total') or 0)
            by_day[day]['total'] += amount
            by_day[day]['jobs'].append({
                'customer':    customer,
                'so_id':       so['id'],
                'workiz_link': so.get('x_studio_x_workiz_link') or '',
                'time_utc':    so['date_order'][11:16] if so.get('date_order') else '?',
                'amount':      amount,
                'status':      so.get('x_studio_x_studio_workiz_status') or '',
                'task_names':  tasks_by_so_up.get(so['id'], []),
            })
        days = []
        for d in sorted(by_day.keys()):
            entry = by_day[d]
            try:
                dt = datetime.date.fromisoformat(d)
                label = dt.strftime('%a %b %-d') if d != today.isoformat() else 'Today'
            except Exception:
                label = d
            entry['label'] = label
            days.append(entry)
        return {'days': days}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.get('/api/todos')
async def api_todos(access_code: str = ''):
    if access_code != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    try:
        acts = odoo_rpc('mail.activity', 'search_read',
            [[['user_id', '=', ODOO_USER_ID]]],
            {'fields': ['summary', 'date_deadline', 'activity_type_id', 'res_name', 'note'],
             'order': 'date_deadline asc', 'limit': 30})
        todos = []
        for a in acts:
            todos.append({
                'summary': a.get('summary') or '',
                'type':    a['activity_type_id'][1] if a.get('activity_type_id') else '',
                'date':    a.get('date_deadline') or '',
                'record':  a.get('res_name') or '',
                'note':    (a.get('note') or '').replace('<p>', '').replace('</p>', ' ').strip()[:120],
            })
        return {'todos': todos}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.get('/api/search')
async def api_search(q: str = '', access_code: str = ''):
    if access_code != ACCESS_CODE:
        return JSONResponse({'error': 'unauthorized'}, status_code=401)
    if not q or len(q) < 2:
        return {'results': []}
    try:
        partners = odoo_rpc('res.partner', 'search_read',
            [[['name', 'ilike', q], ['active', '=', True],
              ['x_studio_x_studio_record_category', '!=', 'Property']]],
            {'fields': ['id', 'name', 'street', 'city', 'phone',
                        'x_studio_x_type_of_service', 'x_studio_x_frequency'],
             'limit': 15, 'order': 'name asc'})
        if not partners:
            return {'results': []}

        partner_ids = [p['id'] for p in partners]
        today = today_pt().isoformat()

        # SOs are linked to Property children, not the Contact directly.
        # Find all Property children for these contacts in one call.
        children = odoo_rpc('res.partner', 'search_read',
            [[['parent_id', 'in', partner_ids],
              ['x_studio_x_studio_record_category', '=', 'Property']]],
            {'fields': ['id', 'parent_id'], 'limit': 150})
        child_to_contact = {}
        for c in children:
            if c.get('parent_id'):
                cid = c['parent_id'][0] if isinstance(c['parent_id'], (list, tuple)) else c['parent_id']
                child_to_contact[c['id']] = cid

        all_so_pids = list(set(partner_ids + list(child_to_contact.keys())))

        def pid_to_contact(pid):
            if pid in partner_ids: return pid
            return child_to_contact.get(pid)

        def fmt_date(date_order):
            try:
                d = datetime.date.fromisoformat((date_order or '')[:10])
                if d.year != datetime.date.today().year:
                    return d.strftime('%b %-d, %Y')
                return d.strftime('%b %-d')
            except Exception:
                return ''

        # Next scheduled job (today or future, not Done/Canceled)
        SKIP = {'done', 'canceled', 'cancelled'}
        next_sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_id', 'in', all_so_pids],
              ['state', 'in', ['sale', 'done']],
              ['date_order', '>=', today + ' 00:00:00']]],
            {'fields': ['partner_id', 'date_order', 'x_studio_x_studio_workiz_status'],
             'order': 'date_order asc', 'limit': 60})
        next_by = {}
        for so in next_sos:
            status = (so.get('x_studio_x_studio_workiz_status') or '').lower()
            if any(s in status for s in SKIP):
                continue
            pid = so['partner_id'][0] if isinstance(so.get('partner_id'), (list, tuple)) else so.get('partner_id')
            cid = pid_to_contact(pid)
            if cid and cid not in next_by:
                next_by[cid] = fmt_date(so.get('date_order'))

        # Last done job
        last_sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_id', 'in', all_so_pids],
              ['state', 'in', ['sale', 'done']],
              ['x_studio_x_studio_workiz_status', 'ilike', 'done']]],
            {'fields': ['partner_id', 'date_order'],
             'order': 'date_order desc', 'limit': 60})
        last_by = {}
        for so in last_sos:
            pid = so['partner_id'][0] if isinstance(so.get('partner_id'), (list, tuple)) else so.get('partner_id')
            cid = pid_to_contact(pid)
            if cid and cid not in last_by:
                last_by[cid] = fmt_date(so.get('date_order'))

        for p in partners:
            p['next_job'] = next_by.get(p['id'], '')
            p['last_job'] = last_by.get(p['id'], '')

        return {'results': partners}
    except Exception as e:
        return JSONResponse({'status': 'error', 'message': str(e)})


@app.get('/', response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()
