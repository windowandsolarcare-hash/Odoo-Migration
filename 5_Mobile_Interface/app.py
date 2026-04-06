# ==============================================================================
# WINDOW & SOLAR CARE — MOBILE VOICE INTERFACE BACKEND (v2 — Agent Architecture)
# Author: DJ Sanders
# Deploy: Render.com (env vars: ODOO_API_KEY, WORKIZ_TOKEN, WORKIZ_SECRET, OPENAI_API_KEY, ACCESS_CODE)
# ==============================================================================

import os, json, re, datetime, urllib.parse
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config — all from environment variables
# ---------------------------------------------------------------------------
ODOO_URL      = os.environ.get('ODOO_URL',        'https://window-solar-care.odoo.com')
ODOO_DB       = os.environ.get('ODOO_DB',         'window-solar-care')
ODOO_USER_ID  = int(os.environ.get('ODOO_USER_ID', '2'))
ODOO_API_KEY  = os.environ.get('ODOO_API_KEY',    '')
WORKIZ_TOKEN  = os.environ.get('WORKIZ_TOKEN',    '')
WORKIZ_SECRET = os.environ.get('WORKIZ_SECRET',   'sec_334084295850678330105471548')
OPENAI_KEY    = os.environ.get('OPENAI_API_KEY',  '')
ACCESS_CODE   = os.environ.get('ACCESS_CODE',     'wsc2026')

app = FastAPI()

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
    sep = '&' if '?' in endpoint else '?'
    url = f'https://api.workiz.com/api/v1/{WORKIZ_TOKEN}/{endpoint}{sep}auth_secret={WORKIZ_SECRET}'
    resp = httpx.post(url, json=data, timeout=20)
    if resp.status_code == 204:
        return {'success': True}
    resp.raise_for_status()
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
    return date_str, date_str  # assume YYYY-MM-DD


# ---------------------------------------------------------------------------
# READ TOOL IMPLEMENTATIONS — GPT calls these freely, no confirmation needed
# ---------------------------------------------------------------------------

def tool_search_customers(query: str) -> list:
    """Search Odoo customers by name. Returns up to 5 matches with SO/job info."""
    clean = re.sub(r"'s\s*$", '', query, flags=re.IGNORECASE).strip()
    partners = odoo_rpc('res.partner', 'search_read',
        [[['name', 'ilike', clean], ['active', '=', True]]],
        {'fields': ['id', 'name', 'city', 'street', 'x_studio_x_studio_record_category'], 'limit': 8})
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
            'record_category': p.get('x_studio_x_studio_record_category') or '',
            'so_id': so.get('id'),
            'so_name': so.get('name') or '',
            'workiz_uuid': so.get('x_studio_x_studio_workiz_uuid') or '',
            'job_date': (so.get('date_order') or '')[:16],
            'amount': so.get('amount_total') or 0,
            'workiz_status': so.get('x_studio_x_studio_workiz_status') or ''
        })
    return results


def tool_get_job_details(partner_id: int) -> dict:
    """Get full job details: SO info + Workiz job info for a customer."""
    sos = odoo_rpc('sale.order', 'search_read',
        [[['partner_id', '=', partner_id], ['state', 'in', ['sale', 'done']]]],
        {'fields': ['id', 'name', 'date_order', 'amount_total', 'amount_untaxed',
                    'x_studio_x_studio_workiz_uuid', 'x_studio_x_studio_workiz_status',
                    'x_studio_x_studio_workiz_tech', 'x_studio_x_gate_snapshot',
                    'x_studio_x_studio_pricing_snapshot', 'x_studio_x_studio_type_of_service_so',
                    'x_studio_x_studio_notes_snapshot1'],
         'order': 'date_order desc', 'limit': 1})
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
                result['workiz_notes'] = job.get('JobNotes') or ''
                result['workiz_substatus'] = job.get('SubStatus') or job.get('Status') or ''
                result['workiz_address'] = f"{job.get('Address','')  } {job.get('City','')}".strip()
    return result


def tool_get_schedule(date: str) -> str:
    """Get all jobs scheduled for a given date."""
    date_iso, label = resolve_date(date)
    sos = odoo_rpc('sale.order', 'search_read',
        [[['date_order', '>=', date_iso + ' 00:00:00'],
          ['date_order', '<=', date_iso + ' 23:59:59'],
          ['state', 'in', ['sale', 'done']],
          ['x_studio_x_studio_workiz_uuid', '!=', False]]],
        {'fields': ['name', 'date_order', 'partner_id', 'amount_total',
                    'x_studio_x_studio_workiz_status'],
         'order': 'date_order asc'})
    if not sos:
        return f"No jobs scheduled for {label} ({date_iso})."
    lines = [f"Schedule for {label} ({date_iso}) — {len(sos)} job(s):"]
    total = 0.0
    for so in sos:
        customer = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
        time_str = so['date_order'][11:16] if so.get('date_order') else '?'
        status = so.get('x_studio_x_studio_workiz_status') or ''
        amount = float(so.get('amount_total') or 0)
        total += amount
        lines.append(f"  {time_str} | {customer} | ${amount:.0f} | {status}")
    lines.append(f"Total: ${total:.2f}")
    return '\n'.join(lines)


def tool_get_next_job() -> dict:
    """Get the next upcoming job today — returns customer, time, address, SO info."""
    now_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
    customer = so['partner_id'][1].split(',')[0].strip() if so.get('partner_id') else 'Unknown'
    partner_id = so['partner_id'][0] if so.get('partner_id') else None
    result = {
        'customer': customer,
        'partner_id': partner_id,
        'time_utc': so['date_order'][11:16],
        'so_name': so['name'],
        'so_id': so['id'],
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
    """Get total sales revenue for a given date."""
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


def tool_navigate_to(partner_id: int, customer_name: str = '') -> str:
    """Get a Google Maps navigation button for a customer's address. Returns HTML."""
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
# WRITE TOOL IMPLEMENTATIONS — called after user confirms
# ---------------------------------------------------------------------------

def execute_write_tool(tool_name: str, args: dict) -> str:
    name = args.get('partner_name', 'customer')

    if tool_name == 'update_workiz_gate_code':
        workiz_post(f'job/update/{args["uuid"]}/', {'gate_code': args['gate_code']})
        so_id = args.get('so_id')
        if so_id:
            odoo_rpc('sale.order', 'write', [[so_id], {'x_studio_x_gate_snapshot': args['gate_code']}])
        return f"Gate code updated for {name}: {args['gate_code']}"

    if tool_name == 'update_workiz_pricing':
        workiz_post(f'job/update/{args["uuid"]}/', {'pricing': args['pricing']})
        so_id = args.get('so_id')
        if so_id:
            odoo_rpc('sale.order', 'write', [[so_id], {'x_studio_x_studio_pricing_snapshot': args['pricing']}])
        return f"Pricing updated for {name}: {args['pricing']}"

    if tool_name == 'update_workiz_notes':
        workiz_post(f'job/update/{args["uuid"]}/', {'JobNotes': args['notes']})
        return f"Job notes updated for {name}"

    if tool_name == 'update_workiz_substatus':
        workiz_post(f'job/update/{args["uuid"]}/', {'SubStatus': args['substatus']})
        return f"Job status updated for {name}: {args['substatus']}"

    if tool_name == 'post_odoo_note':
        odoo_rpc('sale.order', 'message_post', [[args['so_id']]], {'body': f'[Voice] {args["note"]}'})
        return f"Note posted to {name} chatter: \"{args['note']}\""

    if tool_name == 'create_todo':
        days = int(args.get('days', 7))
        due_dt = datetime.datetime.now() + datetime.timedelta(days=days)
        due_str = due_dt.strftime('%Y-%m-%d 12:00:00')
        due_display = due_dt.strftime('%m-%d-%Y')
        note = args.get('note', 'Follow-up')
        todo_id = odoo_rpc('project.task', 'create', [{
            'name': f'Follow-up: {name}',
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
                'body': f'[Voice] To-Do created | Customer: {name} | Due: {due_display} | {todo_url}'
            })
        return f"To-do created for {name} due {due_display}: \"{note}\""

    if tool_name == 'mark_job_done':
        workiz_post(f'job/update/{args["uuid"]}/', {'Status': 'Done'})
        return f"Marked job Done for {name}"

    return f"Unknown write action: {tool_name}"


def _describe_write(tool_name: str, args: dict) -> str:
    name = args.get('partner_name', 'customer')
    if tool_name == 'update_workiz_gate_code':
        return f"Update gate code for {name} to: {args.get('gate_code')}"
    if tool_name == 'update_workiz_pricing':
        return f"Update pricing for {name} to: {args.get('pricing')}"
    if tool_name == 'update_workiz_notes':
        return f"Update Workiz job notes for {name} to: {args.get('notes')}"
    if tool_name == 'update_workiz_substatus':
        return f"Update job status for {name} to: {args.get('substatus')}"
    if tool_name == 'post_odoo_note':
        return f"Post note to {name}'s chatter: \"{args.get('note')}\""
    if tool_name == 'create_todo':
        return f"Create follow-up To-do for {name} in {args.get('days', 7)} days: \"{args.get('note')}\""
    if tool_name == 'mark_job_done':
        return f"Mark job Done for {name}"
    return f"Execute {tool_name} for {name}"


# ---------------------------------------------------------------------------
# Tool definitions for OpenAI
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_customers",
            "description": "Search for customers by name. Always call this first when you need to act on a specific customer — it returns their partner_id, SO info, and Workiz UUID needed for other tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Customer name or partial name. Strip possessives: 'Rigo's' → 'Rigo'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_details",
            "description": "Get full job details for a customer: SO status, pricing, gate code, notes, Workiz status and notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer", "description": "Odoo partner ID from search_customers"}
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
                    "date": {"type": "string", "description": "today, tomorrow, monday, tuesday, wednesday, thursday, friday, saturday, sunday, or YYYY-MM-DD"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_next_job",
            "description": "Get the next upcoming job today — customer name, time, address, SO info.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales",
            "description": "Get total sales revenue for a given day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "today, tomorrow, day name, or YYYY-MM-DD"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "navigate_to",
            "description": "Get a Google Maps navigation button for a customer's address. Use partner_id from search_customers or get_next_job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer", "description": "Odoo partner ID"},
                    "customer_name": {"type": "string", "description": "Customer display name for the button label"}
                },
                "required": ["partner_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_workiz_gate_code",
            "description": "Update the gate/access code for a customer's Workiz job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "Workiz job UUID from search_customers"},
                    "gate_code": {"type": "string"},
                    "partner_name": {"type": "string", "description": "Full customer name for confirmation"},
                    "so_id": {"type": "integer", "description": "Odoo SO ID to also update snapshot field"}
                },
                "required": ["uuid", "gate_code", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_workiz_pricing",
            "description": "Update the pricing notes for a customer's Workiz job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "pricing": {"type": "string"},
                    "partner_name": {"type": "string"},
                    "so_id": {"type": "integer"}
                },
                "required": ["uuid", "pricing", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_workiz_notes",
            "description": "Update the job notes on a customer's Workiz job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "notes": {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["uuid", "notes", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_workiz_substatus",
            "description": "Update the job SubStatus in Workiz (e.g. Scheduled, STOP, Lead, API SMS Test Trigger).",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "substatus": {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["uuid", "substatus", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "post_odoo_note",
            "description": "Post a note to the Odoo sales order chatter (internal log).",
            "parameters": {
                "type": "object",
                "properties": {
                    "so_id": {"type": "integer"},
                    "note": {"type": "string"},
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
            "description": "Create a follow-up To-do task in Odoo for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer"},
                    "note": {"type": "string", "description": "What the follow-up is about"},
                    "days": {"type": "integer", "description": "Days from today when due (default 7)"},
                    "partner_name": {"type": "string"},
                    "so_id": {"type": "integer", "description": "Optional — post link to chatter"}
                },
                "required": ["partner_id", "note", "days", "partner_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_job_done",
            "description": "Mark a customer's Workiz job as Done.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string"},
                    "partner_name": {"type": "string"}
                },
                "required": ["uuid", "partner_name"]
            }
        }
    }
]

WRITE_TOOLS = {
    'update_workiz_gate_code', 'update_workiz_pricing', 'update_workiz_notes',
    'update_workiz_substatus', 'post_odoo_note', 'create_todo', 'mark_job_done'
}

READ_TOOL_MAP = {
    'search_customers': lambda a: tool_search_customers(a['query']),
    'get_job_details':  lambda a: tool_get_job_details(a['partner_id']),
    'get_schedule':     lambda a: tool_get_schedule(a['date']),
    'get_next_job':     lambda a: tool_get_next_job(),
    'get_sales':        lambda a: tool_get_sales(a['date']),
    'navigate_to':      lambda a: tool_navigate_to(a['partner_id'], a.get('customer_name', '')),
}


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a field assistant for Window & Solar Care, a window and solar panel cleaning company in Southern California. DJ Sanders is the owner and sole technician — he talks to you by voice while driving or at job sites.

You have tools to read from and write to his Odoo (business system) and Workiz (job scheduling) accounts.

HOW TO RESPOND:
- Be very concise — DJ is on the road
- Always call search_customers before updating or navigating to a customer
- If search returns multiple matches, list them briefly and ask which one
- For navigation requests: search_customers → navigate_to with the partner_id
- For "navigate to next job": get_next_job → navigate_to with the partner_id from the result
- Times in the database are UTC. Pacific Time is UTC-7 (Mar–Nov) or UTC-8 (Nov–Mar)
- If a customer has no active SO, tell DJ clearly
"""


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------
def run_agent(user_input: str, mode: str = 'confirm') -> dict:
    client = OpenAI(api_key=OPENAI_KEY)
    today_str = datetime.datetime.now().strftime('%A, %B %d, %Y — current UTC time: %H:%M')
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT + f'\nToday: {today_str}'},
        {'role': 'user',   'content': user_input}
    ]

    for _ in range(10):
        resp = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            tools=TOOLS,
            tool_choice='auto',
            max_tokens=800
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            return {'status': 'done', 'message': msg.content or 'Done.'}

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
                    return {'status': 'done', 'message': result}
                else:
                    return {
                        'status': 'pending',
                        'confirmation': _describe_write(name, args),
                        'write_action': {'tool': name, 'args': args}
                    }

            elif name in READ_TOOL_MAP:
                try:
                    result = READ_TOOL_MAP[name](args)
                except Exception as e:
                    result = {'error': str(e)}

                # navigate_to returns HTML — return immediately, don't feed back to GPT
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
• What's the status of [customer]  (checks Odoo + Workiz)

NAVIGATE
• Navigate to [customer]
• Take me to my next job

UPDATE WORKIZ
• Gate code for [customer] is [code]
• Pricing for [customer] is [amount/description]
• Update job notes for [customer] to [text]
• Change status of [customer] to [substatus]
• Mark [customer] job done

LOG & TASKS
• Add a note to [customer]: [text]  (Odoo chatter)
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
    mode       = body.get('mode', 'confirm')

    if not user_input:
        return JSONResponse({'error': 'No input provided'})

    if user_input.lower().strip('?.! ') in HELP_PHRASES:
        return JSONResponse({'status': 'done', 'message': HELP_TEXT})

    try:
        result = run_agent(user_input, mode=mode)
        return JSONResponse(result)
    except Exception as ex:
        return JSONResponse({'status': 'error', 'message': str(ex)})


@app.post('/execute')
async def execute(request: Request):
    body = await request.json()
    if body.get('access_code') != ACCESS_CODE:
        raise HTTPException(status_code=401, detail='Invalid access code')

    write_action = body.get('write_action', {})
    tool_name = write_action.get('tool', '')
    args      = write_action.get('args', {})

    try:
        result = execute_write_tool(tool_name, args)
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
