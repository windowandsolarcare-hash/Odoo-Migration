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

        # Find most recent open/active SO for this partner
        sos = odoo_rpc('sale.order', 'search_read',
            [[['partner_id', '=', partner['id']], ['x_studio_x_studio_workiz_uuid', '!=', False]]],
            {'fields': ['id', 'name', 'x_studio_x_studio_workiz_uuid', 'state', 'date_order'],
             'order': 'date_order desc', 'limit': 5})

        if sos:
            # Prefer confirmed/sale state, fallback to most recent
            confirmed = [s for s in sos if s.get('state') in ('sale', 'done')]
            best = confirmed[0] if confirmed else sos[0]
            result['so_id'] = best['id']
            result['so_name'] = best['name']
            result['workiz_uuid'] = best.get('x_studio_x_studio_workiz_uuid') or ''

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
- get_info: Read-only lookup of job/customer status
- update_workiz_notes: Update Workiz job Notes field
- update_workiz_substatus: Change Workiz job SubStatus
- update_odoo_gate_code: Update gate code on the contact (x_studio_x_gate_code)
- update_odoo_pricing: Update pricing notes on contact (x_studio_x_pricing)
- update_odoo_contact_note: Update any plain text note on contact
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
- update_odoo_gate_code: {"gate_code": "<code>"}
- update_odoo_pricing: {"pricing": "<pricing text>"}
- update_odoo_contact_note: {"field": "<field_name>", "value": "<value>"}
- create_todo: {"note": "<what the to-do is about>", "days": <number of days from now, default 7>}
- add_chatter_note: {"note": "<the note text>"}
- get_info: {}
- mark_job_done: {}

EXAMPLES:
Input: "update Kenneth's notes to gate code is 1234"
Output: {"action":"update_workiz_notes","customer_name":"Kenneth","so_number":null,"params":{"notes":"gate code 1234"},"confirmation_text":"Update Workiz job notes for Kenneth to: gate code 1234","is_read_only":false}

Input: "what's the status of Barbara Williams"
Output: {"action":"get_info","customer_name":"Barbara Williams","so_number":null,"params":{},"confirmation_text":"Look up job info for Barbara Williams","is_read_only":true}

Input: "add a note to P00123 says customer was not home"
Output: {"action":"add_chatter_note","customer_name":null,"so_number":"P00123","params":{"note":"Customer was not home"},"confirmation_text":"Post chatter note on SO P00123: Customer was not home","is_read_only":false}

Input: "gate code for the Smith property is pound 4567"
Output: {"action":"update_odoo_gate_code","customer_name":"Smith","so_number":null,"params":{"gate_code":"#4567"},"confirmation_text":"Update gate code for Smith to: #4567","is_read_only":false}

Input: "create a follow-up to-do for Williams in two weeks"
Output: {"action":"create_todo","customer_name":"Williams","so_number":null,"params":{"note":"Follow-up","days":14},"confirmation_text":"Create a To-do for Williams due in 14 days","is_read_only":false}
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

    elif action == 'update_odoo_gate_code':
        if not partner_id:
            return f"No contact found for {partner_name}. Cannot update."
        gate_code = params.get('gate_code', '')
        odoo_rpc('res.partner', 'write', [[partner_id], {'x_studio_x_gate_code': gate_code}])
        if so_id:
            odoo_rpc('sale.order', 'message_post', [[so_id]], {
                'body': f'[Voice] Gate code updated | {gate_code}'
            })
        return f"Updated gate code for {partner_name} to: {gate_code}"

    elif action == 'update_odoo_pricing':
        if not partner_id:
            return f"No contact found for {partner_name}. Cannot update."
        pricing = params.get('pricing', '')
        odoo_rpc('res.partner', 'write', [[partner_id], {'x_studio_x_pricing': pricing}])
        if so_id:
            odoo_rpc('sale.order', 'message_post', [[so_id]], {
                'body': f'[Voice] Pricing updated | {pricing}'
            })
        return f"Updated pricing for {partner_name} to: {pricing}"

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

    elif action == 'mark_job_done':
        if not uuid:
            return f"No Workiz UUID found for {partner_name}. Cannot mark Done."
        workiz_post(f'job/update/{uuid}/', {'Status': 'Done'})
        return f"Marked Workiz job for {partner_name} ({uuid}) as Done."

    return f"Unknown action: {action}"


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.post('/ask')
async def ask(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        raise HTTPException(status_code=401, detail='Invalid access code')

    user_input = body.get('input', '').strip()
    mode       = body.get('mode', 'confirm')   # 'confirm' or 'immediate'

    if not user_input:
        return JSONResponse({'error': 'No input provided'})

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

    # 2. Resolve customer
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
