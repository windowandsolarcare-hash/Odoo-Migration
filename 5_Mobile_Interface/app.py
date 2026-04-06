# ==============================================================================
# WINDOW & SOLAR CARE — MOBILE VOICE INTERFACE BACKEND
# Author: DJ Sanders
# Handles natural language voice commands → Odoo / Workiz API actions
# Deploy: Render.com (set env vars: ODOO_API_KEY, WORKIZ_TOKEN, OPENAI_API_KEY, ACCESS_CODE)
# ==============================================================================

import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config — all from environment variables
# ---------------------------------------------------------------------------
ODOO_URL        = os.environ.get('ODOO_URL',      'https://window-solar-care.odoo.com')
ODOO_DB         = os.environ.get('ODOO_DB',       'window-solar-care')
ODOO_USER_ID    = int(os.environ.get('ODOO_USER_ID', '2'))
ODOO_API_KEY    = os.environ.get('ODOO_API_KEY',  '')
WORKIZ_TOKEN    = os.environ.get('WORKIZ_TOKEN',  '')
OPENAI_KEY      = os.environ.get('OPENAI_API_KEY', '')
ACCESS_CODE     = os.environ.get('ACCESS_CODE',   'wsc2026')   # change in Render env vars

app = FastAPI()

# ---------------------------------------------------------------------------
# Odoo JSON-RPC helper
# ---------------------------------------------------------------------------
def odoo_rpc(model, method, args, kwargs=None):
    if kwargs is None:
        kwargs = {}
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'id': 1,
        'params': {
            'service': 'object',
            'method': 'execute_kw',
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
    url = f'https://api.workiz.com/api/v1/{WORKIZ_TOKEN}/{endpoint}'
    resp = httpx.get(url, timeout=20)
    if resp.status_code in (204, 404):
        return None
    resp.raise_for_status()
    return resp.json()


def workiz_post(endpoint, data):
    url = f'https://api.workiz.com/api/v1/{WORKIZ_TOKEN}/{endpoint}'
    resp = httpx.post(url, json=data, timeout=20)
    if resp.status_code == 204:
        return {'success': True}
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Customer resolution: name or SO number → {partner_id, partner_name, so_id, so_name, workiz_uuid}
# ---------------------------------------------------------------------------
def resolve_customer(customer_name=None, so_number=None):
    result = {
        'partner_id': None,
        'partner_name': None,
        'so_id': None,
        'so_name': None,
        'workiz_uuid': None,
        'error': None,
        'candidates': []
    }

    # --- Resolve by SO number (e.g. "P00123") ---
    if so_number:
        so_number_clean = so_number.strip().upper()
        sos = odoo_rpc('sale.order', 'search_read',
            [[['name', 'ilike', so_number_clean]]],
            {'fields': ['id', 'name', 'partner_id', 'x_studio_x_studio_workiz_uuid'], 'limit': 5})
        if not sos:
            result['error'] = f"No sales order found matching '{so_number}'"
            return result
        so = sos[0]
        result['so_id'] = so['id']
        result['so_name'] = so['name']
        result['workiz_uuid'] = so.get('x_studio_x_studio_workiz_uuid') or ''
        if so.get('partner_id'):
            result['partner_id'] = so['partner_id'][0]
            result['partner_name'] = so['partner_id'][1]
        return result

    # --- Resolve by customer name ---
    if customer_name:
        name_clean = customer_name.strip()
        partners = odoo_rpc('res.partner', 'search_read',
            [[['name', 'ilike', name_clean], ['active', '=', True]]],
            {'fields': ['id', 'name', 'phone', 'x_studio_x_studio_record_category'], 'limit': 10})

        if not partners:
            result['error'] = f"No contact found matching '{customer_name}'"
            return result

        # Filter out pure property records if there's a person match
        non_prop = [p for p in partners if p.get('x_studio_x_studio_record_category') != 'Property']
        candidates = non_prop if non_prop else partners

        if len(candidates) > 3:
            result['error'] = f"Too many matches for '{customer_name}'. Be more specific."
            result['candidates'] = [p['name'] for p in candidates[:6]]
            return result

        if len(candidates) > 1:
            result['error'] = f"Found {len(candidates)} matches. Which one?"
            result['candidates'] = [f"{p['name']} ({p.get('phone','no phone')})" for p in candidates]
            return result

        partner = candidates[0]
        result['partner_id'] = partner['id']
        result['partner_name'] = partner['name']

        # Find most recent SO — search via commercial_partner_id to catch property child records
        sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_id.commercial_partner_id', '=', partner['id']], ['x_studio_x_studio_workiz_uuid', '!=', False]]],
            {'fields': ['id', 'name', 'x_studio_x_studio_workiz_uuid', 'state', 'date_order'],
             'order': 'date_order desc', 'limit': 5})

        if sos:
            # Prefer confirmed/sale state, fallback to most recent
            confirmed = [s for s in sos if s.get('state') in ('sale', 'done')]
            best = confirmed[0] if confirmed else sos[0]
            result['so_id'] = best['id']
            result['so_name'] = best['name']
            result['workiz_uuid'] = best.get('x_studio_x_studio_workiz_uuid') or ''
            # SO's partner_id is the property record
            if best.get('partner_id'):
                result['property_id'] = best['partner_id'][0]
                result['property_name'] = best['partner_id'][1]

        return result

    result['error'] = 'No customer name or SO number provided'
    return result


# ---------------------------------------------------------------------------
# Claude intent parser
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a voice assistant for Window & Solar Care, a window cleaning business.
The owner DJ uses you in the field via voice commands on his phone.
Your job: parse the voice input and return a JSON action object.

AVAILABLE ACTIONS:
- get_info: Read-only lookup of a specific customer's job status
- get_schedule: List all jobs scheduled for a given day (today, tomorrow, Monday, etc.)
- get_next_job: Show the next upcoming job on today's schedule
- get_sales_today: Total revenue across all jobs today
- update_workiz_notes: Update Workiz job Notes field
- update_workiz_substatus: Change Workiz job SubStatus
- update_workiz_gate_code: Update gate code on the Workiz job (syncs to Odoo via Phase 4)
- update_workiz_pricing: Update pricing on the Workiz job (syncs to Odoo via Phase 4)
- create_todo: Create an Odoo To-do for DJ (follow-up, callback, etc.)
- add_chatter_note: Post a plain text note to the SO chatter log
- mark_job_done: Mark the Workiz job Status=Done

WORKIZ VALID SUBSTATUSES:
Submitted, Pending, Scheduled, Lead, Send Confirmation - Text, STOP - Do not Call or Text,
In Progress, Done, Canceled, Follow-Up Needed, No Answer, Left Message

OUTPUT: Return ONLY valid JSON, no other text.
{
  "action": "<action_name>",
  "customer_name": "<name as spoken or null>",
  "so_number": "<like P00123 or null>",
  "params": { <action-specific params> },
  "confirmation_text": "<one sentence: what will happen>",
  "is_read_only": <true or false>
}

PARAMS by action:
- update_workiz_notes: {"notes": "<the notes text>"}
- update_workiz_substatus: {"substatus": "<exact SubStatus name>"}
- update_workiz_gate_code: {"gate_code": "<code>"}
- update_workiz_pricing: {"pricing": "<pricing text>"}
- create_todo: {"note": "<what the to-do is about>", "days": <number of days from now, default 7>}
- add_chatter_note: {"note": "<the note text>"}
- get_info: {}
- get_schedule: {"date": "today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|YYYY-MM-DD"}
- get_next_job: {}
- get_sales_today: {"date": "today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|YYYY-MM-DD"}
- navigate_to: {}
- mark_job_done: {}

CUSTOMER NAME RULES:
- Always strip possessives: "Rigo's" → "Rigo", "Smith's" → "Smith", "Kenneth's" → "Kenneth"
- Strip filler words: "the", "job", "place", "house", "property" are not part of the name
- Be flexible: "Rigo", "rigo", "RIGO" all mean the same customer

IMPORTANT ROUTING RULES:
- "navigate", "directions", "take me to", "how do I get to", "go to" → use navigate_to
- "navigate to next job", "take me to my next job", "directions to next job" → use get_next_job (navigate=true in params)
- "gate code" → ALWAYS use update_odoo_gate_code, never add_chatter_note
- "pricing" or "price" or "charges" → ALWAYS use update_odoo_pricing, never add_chatter_note
- "note", "comment", "log", "record that" → use add_chatter_note
- "job notes" or "workiz notes" → use update_workiz_notes
- "status", "substatus" → use update_workiz_substatus
- "to-do", "follow up", "remind me", "callback" → use create_todo

EXAMPLES:
Input: "gate code for Kenneth is 1234"
Output: {"action":"update_workiz_gate_code","customer_name":"Kenneth","so_number":null,"params":{"gate_code":"1234"},"confirmation_text":"Update gate code for Kenneth to: 1234 (Workiz → syncs to Odoo)","is_read_only":false}

Input: "Kenneth's gate code is pound 5678"
Output: {"action":"update_workiz_gate_code","customer_name":"Kenneth","so_number":null,"params":{"gate_code":"#5678"},"confirmation_text":"Update gate code for Kenneth to: #5678 (Workiz → syncs to Odoo)","is_read_only":false}

Input: "update Kenneth's job notes to double story needs ladder"
Output: {"action":"update_workiz_notes","customer_name":"Kenneth","so_number":null,"params":{"notes":"double story needs ladder"},"confirmation_text":"Update Workiz job notes for Kenneth to: double story needs ladder","is_read_only":false}

Input: "what's the status of Barbara Williams"
Output: {"action":"get_info","customer_name":"Barbara Williams","so_number":null,"params":{},"confirmation_text":"Look up job info for Barbara Williams","is_read_only":true}

Input: "what's my schedule for Monday"
Output: {"action":"get_schedule","customer_name":null,"so_number":null,"params":{"date":"monday"},"confirmation_text":"Show all jobs scheduled for Monday","is_read_only":true}

Input: "what's on my schedule today"
Output: {"action":"get_schedule","customer_name":null,"so_number":null,"params":{"date":"today"},"confirmation_text":"Show all jobs scheduled for today","is_read_only":true}

Input: "what's my next job"
Output: {"action":"get_next_job","customer_name":null,"so_number":null,"params":{},"confirmation_text":"Show next upcoming job today","is_read_only":true}

Input: "what are my sales today"
Output: {"action":"get_sales_today","customer_name":null,"so_number":null,"params":{"date":"today"},"confirmation_text":"Show total sales for today","is_read_only":true}

Input: "what are my sales for next Wednesday"
Output: {"action":"get_sales_today","customer_name":null,"so_number":null,"params":{"date":"wednesday"},"confirmation_text":"Show total sales for Wednesday","is_read_only":true}

Input: "what time does Kenneth start today"
Output: {"action":"get_info","customer_name":"Kenneth","so_number":null,"params":{},"confirmation_text":"Look up job info for Kenneth","is_read_only":true}

Input: "add a note to P00123 says customer was not home"
Output: {"action":"add_chatter_note","customer_name":null,"so_number":"P00123","params":{"note":"Customer was not home"},"confirmation_text":"Post chatter note on SO P00123: Customer was not home","is_read_only":false}

Input: "pricing for Smith is 150 for full house"
Output: {"action":"update_workiz_pricing","customer_name":"Smith","so_number":null,"params":{"pricing":"150 for full house"},"confirmation_text":"Update pricing for Smith to: 150 for full house (Workiz → syncs to Odoo)","is_read_only":false}

Input: "create a follow-up to-do for Williams in two weeks"
Output: {"action":"create_todo","customer_name":"Williams","so_number":null,"params":{"note":"Follow-up","days":14},"confirmation_text":"Create a To-do for Williams due in 14 days","is_read_only":false}

Input: "navigate to Kenneth"
Output: {"action":"navigate_to","customer_name":"Kenneth","so_number":null,"params":{},"confirmation_text":"Open Google Maps directions to Kenneth","is_read_only":true}

Input: "take me to the Smith job"
Output: {"action":"navigate_to","customer_name":"Smith","so_number":null,"params":{},"confirmation_text":"Open Google Maps directions to Smith","is_read_only":true}

Input: "navigate to Rigo's"
Output: {"action":"navigate_to","customer_name":"Rigo","so_number":null,"params":{},"confirmation_text":"Open Google Maps directions to Rigo","is_read_only":true}

Input: "navigate to my next job"
Output: {"action":"get_next_job","customer_name":null,"so_number":null,"params":{"navigate":true},"confirmation_text":"Navigate to next job","is_read_only":true}

Input: "take me to my next job"
Output: {"action":"get_next_job","customer_name":null,"so_number":null,"params":{"navigate":true},"confirmation_text":"Navigate to next job","is_read_only":true}

Input: "directions to next job"
Output: {"action":"get_next_job","customer_name":null,"so_number":null,"params":{"navigate":true},"confirmation_text":"Navigate to next job","is_read_only":true}
"""


def claude_parse_intent(user_input: str) -> dict:
    client = OpenAI(api_key=OPENAI_KEY)
    resp = client.chat.completions.create(
        model='gpt-4o-mini',
        max_tokens=400,
        temperature=0,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_input}
        ]
    )
    raw = resp.choices[0].message.content.strip()
    # Strip markdown code blocks if present
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Date resolver helper
# ---------------------------------------------------------------------------
def resolve_date(date_str: str) -> str:
    import datetime
    today = datetime.date.today()
    ds = date_str.lower().strip()
    if ds in ('today', ''):
        return today.isoformat()
    if ds == 'tomorrow':
        return (today + datetime.timedelta(days=1)).isoformat()
    day_names = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    if ds in day_names:
        target_wd = day_names.index(ds)
        days_ahead = (target_wd - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7  # next occurrence if today is that day
        return (today + datetime.timedelta(days=days_ahead)).isoformat()
    return date_str  # assume already YYYY-MM-DD


def utc_to_pacific(utc_str: str) -> str:
    import datetime
    # PDT = UTC-7 (Mar-Nov), PST = UTC-8 (Nov-Mar)
    # Determine offset by month
    try:
        dt = datetime.datetime.strptime(utc_str[:16], '%Y-%m-%d %H:%M')
        offset = -7 if 3 <= dt.month <= 11 else -8
        pacific = dt + datetime.timedelta(hours=offset)
        return pacific.strftime('%I:%M %p').lstrip('0')  # e.g. "8:30 AM"
    except Exception:
        return utc_str[11:16]


def get_schedule_for_date(date_iso: str) -> str:
    import datetime
    # Odoo stores UTC — to capture a Pacific day we need to search UTC+7/8 range
    # e.g. Monday Pacific = Monday 07:00 UTC to Tuesday 06:59 UTC
    d = datetime.date.fromisoformat(date_iso)
    offset_hours = 7 if 3 <= d.month <= 11 else 8  # PDT=7, PST=8
    date_start = date_iso + f' {offset_hours:02d}:00:00'
    next_day = (d + datetime.timedelta(days=1)).isoformat()
    date_end = next_day + f' {offset_hours - 1:02d}:59:59'

    # Query by task date_deadline (always correct) rather than SO date_order (can be stale)
    tasks = odoo_rpc('project.task', 'search_read',
        [[['project_id', '=', 2],
          ['planned_date_begin', '>=', date_start],
          ['planned_date_begin', '<=', date_end],
          ['sale_line_id', '!=', False]]],
        {'fields': ['name', 'planned_date_begin', 'sale_line_id'], 'order': 'planned_date_begin asc'})

    if not tasks:
        return f"No jobs found for {date_iso}"

    # Deduplicate by SO — keep earliest task start per SO
    so_map = {}  # so_name -> {'start': ..., 'task_name': ..., 'line_id': ...}
    for t in tasks:
        line_ref = t.get('sale_line_id')
        if not line_ref:
            continue
        line_id = line_ref[0]
        line_display = line_ref[1]  # e.g. "004324 - Includes: ..."
        so_name = line_display.split(' - ')[0].strip()
        start = t.get('planned_date_begin', '')
        if so_name not in so_map or start < so_map[so_name]['start']:
            so_map[so_name] = {'start': start, 'task_name': t['name'], 'line_id': line_id}

    if not so_map:
        return f"No jobs found for {date_iso}"

    # Fetch SOs by name for UUID and Odoo price
    so_names = list(so_map.keys())
    sos = odoo_rpc('sale.order', 'search_read',
        [[['name', 'in', so_names], ['state', 'in', ['sale', 'done']]]],
        {'fields': ['name', 'partner_id', 'x_studio_x_studio_workiz_uuid', 'amount_total']})
    so_by_name = {s['name']: s for s in sos}

    lines = [f"Schedule for {date_iso} ({len(so_map)} job{'s' if len(so_map) != 1 else ''}):"]
    total = 0
    for so_name, info in sorted(so_map.items(), key=lambda x: x[1]['start']):
        so = so_by_name.get(so_name, {})
        uuid = so.get('x_studio_x_studio_workiz_uuid', '')
        # Customer name comes from task title ("FirstName LastName - City")
        task_name = info['task_name']
        customer_short = task_name.split(' - ')[0].strip() if ' - ' in task_name else task_name
        time_str = utc_to_pacific(info['start'])
        amount = float(so.get('amount_total', 0) or 0)  # Odoo as primary price source
        wstatus = ''
        if uuid:
            raw = workiz_get(f'job/get/{uuid}/')
            if raw and 'error' not in raw:
                job = raw.get('data', {})
                job = job[0] if isinstance(job, list) else job
                workiz_price = float(job.get('JobTotalPrice', 0) or 0)
                if workiz_price > 0:
                    amount = workiz_price
                wstatus = f" [{job.get('SubStatus', job.get('Status', '?'))}]"
        total += amount
        lines.append(f"  {time_str} | {customer_short} | ${amount:.0f}{wstatus} | {so_name}")
    lines.append(f"Total: ${total:.0f}")
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Action executor
# ---------------------------------------------------------------------------
def execute_action(action: str, params: dict, resolved: dict) -> str:
    partner_id   = resolved.get('partner_id')
    partner_name = resolved.get('partner_name', 'Unknown')
    so_id        = resolved.get('so_id')
    so_name      = resolved.get('so_name', '')
    uuid         = resolved.get('workiz_uuid', '')

    if action == 'get_info':
        lines = [f"Customer: {partner_name}"]
        if so_name:
            lines.append(f"SO: {so_name}")
        if uuid:
            raw = workiz_get(f'job/get/{uuid}/')
            if raw:
                data = raw.get('data', {})
                job = data[0] if isinstance(data, list) else data
                lines.append(f"Status: {job.get('Status','?')} / {job.get('SubStatus','?')}")
                lines.append(f"Job Date: {job.get('JobDateTime','?')}")
                lines.append(f"Notes: {job.get('Notes','(none)')}")
                lines.append(f"Tech: {job.get('WorkerName','?')}")
                lines.append(f"Amount: ${job.get('JobTotalPrice','?')}")
            else:
                lines.append("Workiz job not found (204/404)")
        else:
            lines.append("No Workiz job linked")
        return '\n'.join(lines)

    elif action == 'update_workiz_notes':
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot update."
        notes = params.get('notes', '')
        workiz_post(f'job/update/{uuid}/', {'Notes': notes})
        # Mirror to chatter
        if so_id:
            odoo_rpc('sale.order', 'write', [[so_id], {
                'x_studio_x_studio_pricing_snapshot': f'{partner_name} notes updated via voice'
            }])
            sos = odoo_rpc('sale.order', 'browse', [[so_id]])
            odoo_rpc('sale.order', 'message_post', [[so_id]], {
                'body': f'[Voice] Notes updated | {notes}'
            })
        return f"Updated Workiz notes for {partner_name} ({uuid}):\n\"{notes}\""

    elif action == 'update_workiz_substatus':
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot update."
        substatus = params.get('substatus', '')
        workiz_post(f'job/update/{uuid}/', {'SubStatus': substatus})
        return f"Updated SubStatus for {partner_name} ({uuid}) to: {substatus}"

    elif action in ('update_workiz_gate_code', 'update_odoo_gate_code'):
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot update."
        gate_code = params.get('gate_code', '')
        workiz_post(f'job/update/{uuid}/', {'gate_code': gate_code})
        return f"Gate code set to {gate_code} on Workiz job {uuid}\nPhase 4 will sync to Odoo property within 5 min."

    elif action in ('update_workiz_pricing', 'update_odoo_pricing'):
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot update."
        pricing = params.get('pricing', '')
        workiz_post(f'job/update/{uuid}/', {'pricing': pricing})
        return f"Pricing set to '{pricing}' on Workiz job {uuid}\nPhase 4 will sync to Odoo within 5 min."

    elif action == 'get_schedule':
        date_raw = params.get('date', 'today')
        date_iso = resolve_date(date_raw)
        return get_schedule_for_date(date_iso)

    elif action == 'get_next_job':
        import datetime
        today_iso = datetime.date.today().isoformat()
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sos = odoo_rpc('sale.order', 'search_read',
            [[['date_order', '>=', now_str],
              ['date_order', '<=', today_iso + ' 23:59:59'],
              ['state', 'in', ['sale', 'done']],
              ['x_studio_x_studio_workiz_uuid', '!=', False]]],
            {'fields': ['name', 'date_order', 'x_studio_x_studio_workiz_uuid',
                        'partner_id', 'amount_total'],
             'order': 'date_order asc', 'limit': 1})
        if not sos:
            return "No more jobs scheduled for today."
        so = sos[0]
        customer = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
        time_str = so['date_order'][11:16]
        uuid_next = so.get('x_studio_x_studio_workiz_uuid', '')
        winfo = ''
        if uuid_next:
            raw = workiz_get(f'job/get/{uuid_next}/')
            if raw:
                job = raw.get('data', {})
                job = job[0] if isinstance(job, list) else job
                winfo = f"\nAddress: {job.get('Address','')} {job.get('City','')}\nStatus: {job.get('SubStatus', job.get('Status',''))}"
        # If navigate=true in params, chain into navigate_to using the partner from this job
        if params.get('navigate'):
            nav_partner_id = so['partner_id'][0] if so.get('partner_id') else None
            nav_partner_name = customer
            if nav_partner_id:
                addr_parts = []
                p = odoo_rpc('res.partner', 'read', [[nav_partner_id]],
                    {'fields': ['street', 'street2', 'city', 'state_id', 'zip']})
                if p:
                    rec = p[0]
                    if rec.get('street'):   addr_parts.append(rec['street'])
                    if rec.get('street2'):  addr_parts.append(rec['street2'])
                    if rec.get('city'):     addr_parts.append(rec['city'])
                    if rec.get('state_id'): addr_parts.append(rec['state_id'][1] if isinstance(rec['state_id'], list) else '')
                    if rec.get('zip'):      addr_parts.append(rec['zip'])
                if addr_parts:
                    full_address = ', '.join(a for a in addr_parts if a)
                    import urllib.parse
                    maps_url = 'https://maps.google.com/?q=' + urllib.parse.quote(full_address)
                    return (
                        f'<div style="margin-bottom:8px;font-size:15px;">'
                        f'<b>Next job: {nav_partner_name} at {time_str}</b><br>'
                        f'<span style="color:#94a3b8;font-size:13px;">{full_address}</span>'
                        f'</div>'
                        f'<a href="{maps_url}" target="_blank" rel="noopener" '
                        f'style="display:block;padding:16px;background:#16a34a;color:white;'
                        f'font-size:18px;font-weight:700;text-align:center;border-radius:12px;'
                        f'text-decoration:none;">Open in Google Maps</a>'
                    )
            return f"Next job: {nav_partner_name} at {time_str} — no address on file."

        return f"Next job: {customer} at {time_str}\nSO: {so['name']} | ${so.get('amount_total',0):.0f}{winfo}"

    elif action == 'get_sales_today':
        date_raw = params.get('date', 'today')
        date_iso = resolve_date(date_raw)
        return get_schedule_for_date(date_iso)

    elif action == 'add_chatter_note':
        if not so_id:
            return f"No SO found for {partner_name}. Cannot post note."
        note = params.get('note', '')
        odoo_rpc('sale.order', 'message_post', [[so_id]], {'body': f'[Voice] {note}'})
        return f"Posted note to {so_name} chatter:\n\"{note}\""

    elif action == 'create_todo':
        if not partner_id:
            return f"No contact found for {partner_name}. Cannot create To-do."
        import datetime
        note = params.get('note', 'Follow-up')
        days = int(params.get('days', 7))
        due_dt = datetime.datetime.now() + datetime.timedelta(days=days)
        due_str = due_dt.strftime('%Y-%m-%d 12:00:00')
        due_display = due_dt.strftime('%m-%d-%Y')
        todo_id = odoo_rpc('project.task', 'create', [{
            'name': f'Follow-up: {partner_name}',
            'description': note,
            'project_id': False,
            'user_ids': [(4, ODOO_USER_ID)],
            'partner_id': partner_id,
            'date_deadline': due_str,
            'priority': '0',
        }])
        if so_id:
            todo_url = f'https://window-solar-care.odoo.com/odoo/to-do/{todo_id}'
            odoo_rpc('sale.order', 'message_post', [[so_id]], {
                'body': f'[Voice] To-Do created | Customer: {partner_name} | Due: {due_display} | To-Do: {todo_url}'
            })
        return f"Created To-do for {partner_name} due {due_display}:\n\"{note}\""

    elif action == 'navigate_to':
        # Get address from the property (SO partner_id) or contact
        addr_parts = []
        lookup_id = resolved.get('property_id') or resolved.get('partner_id')
        if lookup_id:
            p = odoo_rpc('res.partner', 'read', [[lookup_id]],
                {'fields': ['street', 'street2', 'city', 'state_id', 'zip']})
            if p:
                rec = p[0]
                if rec.get('street'):   addr_parts.append(rec['street'])
                if rec.get('street2'):  addr_parts.append(rec['street2'])
                if rec.get('city'):     addr_parts.append(rec['city'])
                if rec.get('state_id'): addr_parts.append(rec['state_id'][1] if isinstance(rec['state_id'], list) else '')
                if rec.get('zip'):      addr_parts.append(rec['zip'])
        if not addr_parts:
            return f"No address found for {partner_name}."
        full_address = ', '.join(a for a in addr_parts if a)
        import urllib.parse
        maps_url = 'https://maps.google.com/?q=' + urllib.parse.quote(full_address)
        return (
            f'<div style="margin-bottom:8px;font-size:15px;">'
            f'<b>{partner_name}</b><br>'
            f'<span style="color:#94a3b8;font-size:13px;">{full_address}</span>'
            f'</div>'
            f'<a href="{maps_url}" target="_blank" rel="noopener" '
            f'style="display:block;padding:16px;background:#16a34a;color:white;'
            f'font-size:18px;font-weight:700;text-align:center;border-radius:12px;'
            f'text-decoration:none;">Open in Google Maps</a>'
        )

    elif action == 'mark_job_done':
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot mark Done."
        workiz_post(f'job/update/{uuid}/', {'Status': 'Done'})
        return f"Marked Workiz job for {partner_name} ({uuid}) as Done."

    return f"Unknown action: {action}"


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

HELP_TEXT = """Here's what I can do:

SCHEDULE & INFO
• What's my schedule today / tomorrow / Monday / next Wednesday
• What's my next job
• What are my sales today / tomorrow / next Friday
• What's the status of [customer]
• Navigate to [customer]  (opens Google Maps)

UPDATE WORKIZ
• Gate code for [customer] is [code]
• Pricing for [customer] is [amount]
• Update job notes for [customer] to [text]
• Change status of [customer] to [substatus]
• Mark [customer] job done

LOG & TASKS
• Add a note to [customer] — [text]  (posts to Odoo SO chatter)
• Update Workiz job notes for [customer] — [text]  (updates Workiz job)
• Create a follow-up to-do for [customer] in [N] days"""

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
    mode       = body.get('mode', 'confirm')   # 'confirm' or 'immediate'

    if not user_input:
        return JSONResponse({'error': 'No input provided'})

    # Help shortcut — no AI call needed
    if user_input.lower().strip('?.!') in HELP_PHRASES:
        return JSONResponse({'status': 'done', 'message': HELP_TEXT})

    # 1. Parse intent via Claude
    try:
        intent = claude_parse_intent(user_input)
    except Exception as ex:
        return JSONResponse({'error': f'Could not parse intent: {str(ex)}'})

    action          = intent.get('action', '')
    customer_name   = intent.get('customer_name')
    so_number       = intent.get('so_number')
    params          = intent.get('params', {})
    confirmation    = intent.get('confirmation_text', '')
    is_read_only    = intent.get('is_read_only', False)

    # Actions that don't need a customer lookup
    NO_CUSTOMER_ACTIONS = {'get_schedule', 'get_next_job', 'get_sales_today'}

    # 2. Resolve customer (skip for schedule/global actions)
    resolved = {}
    if action not in NO_CUSTOMER_ACTIONS:
        resolved = resolve_customer(customer_name=customer_name, so_number=so_number)
        if resolved.get('error'):
            resp = {'status': 'error', 'message': resolved['error']}
            if resolved.get('candidates'):
                resp['candidates'] = resolved['candidates']
            return JSONResponse(resp)

        # Enrich confirmation with resolved name
        if resolved.get('partner_name') and customer_name and resolved['partner_name'].lower() != customer_name.lower():
            confirmation = confirmation.replace(customer_name, resolved['partner_name'])
        if resolved.get('so_name'):
            confirmation += f" (SO: {resolved['so_name']})"

    # 3. Execute immediately if read-only or immediate mode
    if is_read_only or mode == 'immediate':
        try:
            result = execute_action(action, params, resolved)
        except Exception as ex:
            return JSONResponse({'status': 'error', 'message': str(ex)})
        return JSONResponse({'status': 'done', 'message': result})

    # 4. Confirm mode: return pending action for user to approve
    return JSONResponse({
        'status': 'pending',
        'confirmation': confirmation,
        'action': action,
        'params': params,
        'resolved': resolved
    })


@app.post('/execute')
async def execute(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        raise HTTPException(status_code=401, detail='Invalid access code')

    action   = body.get('action', '')
    params   = body.get('params', {})
    resolved = body.get('resolved', {})

    try:
        result = execute_action(action, params, resolved)
    except Exception as ex:
        return JSONResponse({'status': 'error', 'message': str(ex)})

    return JSONResponse({'status': 'done', 'message': result})


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

@app.get('/', response_class=HTMLResponse)
async def index():
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()
