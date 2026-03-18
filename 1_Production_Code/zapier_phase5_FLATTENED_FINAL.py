"""
ZAPIER PHASE 5 FLATTENED SCRIPT - FINAL
=======================================
Auto Job Scheduler: Maintenance & On Demand Follow-Up

Triggered by: Phase 6 (after payment → job marked Done).

Features:
- MAINTENANCE: Creates next scheduled job in Workiz (POST job/create). Does NOT assign tech; you assign and set time/status in Workiz. On 200, API returns UUID/ClientId/link per docs; we use that and only fall back to job/all when 204.
- ON DEMAND: Creates follow-up reminder in Odoo (mail.activity only; view in Activity/Calendar view for activities)
- City-aware scheduling (route-based like Calendly)
- Handles alternating service logic
- Stores line items reference in custom Workiz field

Generated: 2026-02-07
"""

import requests
import json
from datetime import datetime, timedelta
import re

# ==============================================================================
# CONFIGURATION & CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"


def odoo_rpc(model, method, args, kwargs=None):
    """Single JSON-RPC call to Odoo (for activity creation and lookups)."""
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def frequency_to_activity_days(frequency_str):
    """
    Convert frequency string to days for follow-up activity due date.
    Used when type is NOT maintenance: On Demand / On Request / Unknown.
    - 3 Months -> 90, 4 Months -> 120, 6 Months -> 180, 12 Months -> 365
    - Unknown or empty or unparseable -> 180 (6 months default; was 1 year)
    """
    DEFAULT_DAYS = 180  # 6 months when frequency unknown or missing
    if not frequency_str or not str(frequency_str).strip():
        return DEFAULT_DAYS
    s = str(frequency_str).strip().lower()
    if s == 'unknown':
        return DEFAULT_DAYS
    match = re.search(r'(\d+)\s*(month|week)', s)
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()
        if unit == 'month':
            return value * 30  # ~30 days per month
        if unit == 'week':
            return value * 7
    return DEFAULT_DAYS  # default 6 months if unparseable


def calculate_next_service_date(frequency_str, customer_city, base_date=None):
    """Calculate next service date based on frequency and city routing.
    
    Args:
        frequency_str: e.g., "3 Months", "4 Months", "6 Months"
        customer_city: City name for routing
        base_date: datetime object of completed job (if None, uses today)
    """
    # Use completed job date as base, not today's date
    if base_date is None:
        base_date = datetime.now()
        print(f"[*] No base_date provided, using today: {base_date.strftime('%Y-%m-%d')}")
    else:
        print(f"[*] Using completed job date as base: {base_date.strftime('%Y-%m-%d')}")
    
    # Parse frequency (e.g., "3 Months", "4 Months", "6 Months")
    match = re.search(r'(\d+)\s*(month|week)', frequency_str, re.IGNORECASE)
    
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit == 'month':
            target_date = base_date + timedelta(days=value * 30)
        elif unit == 'week':
            target_date = base_date + timedelta(weeks=value)
    else:
        # Default: 3 months
        print(f"[!] Could not parse frequency '{frequency_str}', defaulting to 3 months")
        target_date = base_date + timedelta(days=90)
    
    # Apply city-aware scheduling
    scheduled_date = apply_city_schedule(target_date, customer_city)
    
    # We use 10:00 AM fixed; we do not check Workiz schedule/calendar for slot availability
    return scheduled_date.strftime('%Y-%m-%d 10:00:00')


def apply_city_schedule(target_date, city):
    """Find best service day based on city routing (matching Calendly)."""
    city_schedule = {
        'palm springs': 4,      # Friday
        'rancho mirage': 3,     # Thursday (primary, also Fri available)
        'palm desert': 3,       # Thursday
        'indian wells': 2,      # Wednesday (primary, also Thu available)
        'indio': 2,             # Wednesday
        'la quinta': 2,         # Wednesday
        'hemet': 1              # Tuesday
    }
    
    city_lower = city.lower() if city else ''
    preferred_weekday = None
    
    for city_name, weekday in city_schedule.items():
        if city_name in city_lower:
            preferred_weekday = weekday
            print(f"[*] City '{city}' -> {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][weekday]}")
            break
    
    if preferred_weekday is None:
        print(f"[*] City '{city}' not in routing map - using target date")
        return target_date
    
    # Find nearest preferred day (±7 days)
    target_weekday = target_date.weekday()
    days_diff = preferred_weekday - target_weekday
    
    if days_diff < -3:
        days_diff += 7
    elif days_diff > 3:
        days_diff -= 7
    
    scheduled_date = target_date + timedelta(days=days_diff)
    print(f"[*] Target: {target_date.strftime('%Y-%m-%d (%A)')}, Adjusted: {scheduled_date.strftime('%Y-%m-%d (%A)')}")
    
    return scheduled_date


def format_line_items_for_custom_field(line_items):
    """Format line items as text for Workiz custom field."""
    if not line_items:
        return ""
    
    lines = []
    for item in line_items:
        name = item.get('Name', 'Service')
        price = item.get('Price', 0)
        quantity = item.get('Quantity', 1)
        
        if quantity > 1:
            lines.append(f"{name} (x{quantity}): ${float(price) * float(quantity):.2f}")
        else:
            lines.append(f"{name}: ${float(price):.2f}")
    
    return "\n".join(lines)


# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

def _service_area_for_job(completed_job_data):
    """Return ServiceArea for job/create: from job data or derived from City (Hemet vs desert)."""
    area = completed_job_data.get('ServiceArea') or completed_job_data.get('service_area') or ''
    if area and str(area).strip():
        return str(area).strip()
    city = (completed_job_data.get('City') or '').lower()
    if 'hemet' in city:
        return 'Hemet'
    return 'desert'


def get_job_details(job_uuid):
    """Fetch full job details from Workiz API."""
    url = f'{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}'
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('flag'):
            return result['data'][0]
        else:
            print(f"[ERROR] Workiz API: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch job: {e}")
        return None


def job_all_list(start_date=None, records=25, only_open=True):
    """GET /job/all/ - returns (list of jobs, None) or ([], error_message). Jobs sorted by JobDateTime desc."""
    if start_date is None:
        start_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
    url = (
        f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/"
        f"?auth_secret={WORKIZ_AUTH_SECRET}&start_date={start_date}&records={records}&only_open={str(only_open).lower()}"
    )
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return [], r.text[:500]
        data = r.json()
        if isinstance(data, list):
            return data, None
        jobs = data.get("data", data) if isinstance(data, dict) else []
        return (jobs if isinstance(jobs, list) else []), None
    except Exception as e:
        return [], str(e)


def find_new_job_uuid_after_create(client_id, scheduled_datetime):
    """
    After job/create (which returns no UUID), find the new job via job/all.
    Match: same ClientId, next_job_line_items contains 'AUTO-SCHEDULED', and JobDateTime on same date.
    Returns job UUID string or None.
    """
    target_date = scheduled_datetime[:10] if scheduled_datetime else ""  # YYYY-MM-DD
    if not target_date:
        return None
    jobs, err = job_all_list(start_date=target_date, records=30, only_open=True)
    if err or not jobs:
        print(f"[*] job/all after create: {err or 'no jobs'}")
        return None
    for j in jobs:
        j = j if isinstance(j, dict) else j
        if str(j.get("ClientId")) != str(client_id):
            continue
        notes = (j.get("next_job_line_items") or "") + (j.get("JobNotes") or "")
        if "AUTO-SCHEDULED" not in notes:
            continue
        jdt = j.get("JobDateTime") or ""
        j_date = jdt[:10] if len(jdt) >= 10 else ""
        if j_date == target_date:
            return j.get("UUID")
    return None


def assign_job_team(job_uuid, completed_job_data):
    """POST /job/assign/ to assign first team member from completed job (if any)."""
    team = completed_job_data.get('Team') or completed_job_data.get('team') or []
    if not team or not isinstance(team, list):
        return False
    first = team[0]
    # Workiz may expect User as id or as object; try Id/UserId first, else pass name or first element
    user_value = None
    if isinstance(first, dict):
        user_value = first.get('Id') or first.get('UserId') or first.get('id') or first.get('Name') or first.get('name')
    if user_value is None and first:
        user_value = first
    if not user_value:
        return False
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/assign/"
    payload = {"auth_secret": WORKIZ_AUTH_SECRET, "UUID": job_uuid, "User": user_value}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code in (200, 201, 204):
            print(f"[OK] Team assigned (first member)")
            return True
        print(f"[!] job/assign returned {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        print(f"[!] job/assign failed: {e}")
        return False


def update_job_status(job_uuid, job_datetime, job_type, status="Pending", substatus="Next Appointment - Text"):
    """POST /job/update/ to set Status and SubStatus (e.g. so customer gets text)."""
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "JobDateTime": job_datetime,
        "JobType": job_type or "Windows Inside & Outside Plus Screens",
        "Status": status,
        "SubStatus": substatus,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code in (200, 201, 204):
            print(f"[OK] Job status set to: {substatus}")
            return True
        print(f"[!] job/update returned {r.status_code}: {r.text[:300]}")
        return False
    except Exception as e:
        print(f"[!] job/update failed: {e}")
        return False


def create_next_maintenance_job(completed_job_data, scheduled_datetime, line_items_text):
    """Create new maintenance job in Workiz."""
    # Format the line items reference with context
    line_items_reference = f"""AUTO-SCHEDULED - Next {completed_job_data.get('frequency', '3 Months')} service

Previous Job UUID: {completed_job_data.get('UUID')}

LINE ITEMS TO ADD:
{line_items_text}"""
    
    new_job_data = {
        'auth_secret': WORKIZ_AUTH_SECRET,
        
        # Required fields
        'ClientId': completed_job_data.get('ClientId'),
        'FirstName': completed_job_data.get('FirstName'),
        'LastName': completed_job_data.get('LastName'),
        'Address': completed_job_data.get('Address'),
        'City': completed_job_data.get('City'),
        'State': completed_job_data.get('State', 'CA'),
        'PostalCode': completed_job_data.get('PostalCode'),
        'Phone': completed_job_data.get('Phone'),
        'JobDateTime': scheduled_datetime,
        'JobType': get_next_job_type(completed_job_data),
        
        # Service area: desert vs Hemet (required for routing)
        'ServiceArea': _service_area_for_job(completed_job_data),
        
        # Custom fields (Workiz expects strings for these)
        'frequency': str(completed_job_data.get('frequency') or ''),
        'alternating': str(completed_job_data.get('alternating') or ''),
        'type_of_service': str(completed_job_data.get('type_of_service') or 'Maintenance'),
        'gate_code': str(completed_job_data.get('gate_code') or ''),
        'pricing': str(completed_job_data.get('pricing') or ''),
        
        # LINE ITEMS REFERENCE (with context) - adjust field name to match your Workiz custom field
        'next_job_line_items': line_items_reference,
        
        # Job notes - preserve from previous job
        'JobNotes': str(completed_job_data.get('JobNotes') or '')
    }
    
    # Add optional fields only if they have valid values (Workiz expects strings)
    email = completed_job_data.get('Email', '')
    if email:
        new_job_data['Email'] = str(email)
    
    second_phone = completed_job_data.get('SecondPhone', '')
    if second_phone:
        new_job_data['SecondPhone'] = str(second_phone)
    
    unit = completed_job_data.get('Unit', '')
    if unit:
        new_job_data['Unit'] = str(unit)
    
    job_source = completed_job_data.get('JobSource', '')
    if job_source:
        new_job_data['JobSource'] = str(job_source)
    
    create_url = f'{WORKIZ_BASE_URL}/job/create/'
    
    print(f"[*] Creating job for {new_job_data['FirstName']} {new_job_data['LastName']}")
    
    # NOTE: Team and Tags are NOT included in create payload per Workiz API:
    # - Team: Must be assigned via /job/assign/ endpoint after creation
    # - Tags: Can only be updated via /job/update/ endpoint after creation
    
    try:
        response = requests.post(create_url, json=new_job_data, timeout=10)
        created_ok = False

        # Per Workiz API: 200 = success and returns job resource (UUID, ClientId, link); 204 = No Content.
        new_uuid = None
        if response.status_code == 204:
            print("[OK] Job created successfully (HTTP 204)")
            created_ok = True
        elif response.status_code == 200:
            try:
                result = response.json()
                # Docs: { "flag": true, "data": [ { "UUID", "ClientId", "link" } ] } (or array wrapping that)
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                if result.get('flag') == True:
                    data = result.get('data')
                    if data and isinstance(data, list) and len(data) > 0:
                        first = data[0]
                        new_uuid = first.get('UUID')
                        _link = first.get('link')
                        print(f"[OK] Job created (HTTP 200); UUID: {new_uuid}; link: {_link or 'n/a'}")
                    else:
                        print(f"[OK] Job created (HTTP 200): {result.get('msg', '')}")
                    created_ok = True
                elif (result.get('msg') or '').lower().find('created') >= 0:
                    print(f"[OK] Job created (HTTP 200): {result.get('msg')}")
                    created_ok = True
                else:
                    return {'success': False, 'message': result.get('msg'), 'details': result.get('details')}
            except Exception:
                return {'success': False, 'message': "HTTP 200 but invalid JSON"}
        else:
            try:
                error_result = response.json()
                return {'success': False, 'message': error_result.get('msg'), 'details': error_result.get('details')}
            except Exception:
                return {'success': False, 'message': f"HTTP {response.status_code}"}

        if created_ok:
            return {'success': True, 'message': 'Job created', 'new_job_uuid': new_uuid}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


# ==============================================================================
# ODOO API FUNCTIONS
# ==============================================================================

def get_property_city(property_id):
    """Get city from property record."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "read",
                [[property_id]],
                {"fields": ["city"]}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result", [])
        
        if result and len(result) > 0:
            return result[0].get('city', '')
        return ''
    except:
        return ''


def search_all_sales_orders_for_property(property_id):
    """Get all sales orders for property (for alternating logic). Property as brain: match partner_id or partner_shipping_id."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "search_read",
                [[
                    "|",
                    ["partner_id", "=", property_id],
                    ["partner_shipping_id", "=", property_id],
                    ["state", "in", ["sale", "done"]]
                ]],
                {
                    "fields": ["id", "name", "x_studio_x_studio_workiz_uuid", "date_order"],
                    "order": "date_order desc"
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    return response.json().get("result", [])


def update_invoice_with_workiz_link(invoice_id, new_job_uuid, customer_name, scheduled_date):
    """Write Workiz job link to invoice custom field."""
    if not invoice_id or not new_job_uuid:
        return
    
    workiz_url = f"https://app.workiz.com/root/job/{new_job_uuid}/1"
    
    try:
        # Update invoice with Workiz link in custom field
        odoo_rpc("account.move", "write", [[invoice_id], {"x_studio_workiz_job_link": workiz_url}])
        print(f"[OK] Updated invoice with Workiz link: {workiz_url}")
        
        # Also post notification to chatter
        message_body = f"""<p><strong>✅ Next Maintenance Job Created</strong></p>
<p>Customer: <strong>{customer_name}</strong><br/>
Scheduled: <strong>{scheduled_date}</strong></p>
<p>Job UUID: <strong>{new_job_uuid}</strong></p>
<p><em>Click the "Workiz Job Link" field on this invoice to open the job in Workiz.</em></p>"""
        
        odoo_rpc("account.move", "message_post", [[invoice_id]], {
            "body": message_body,
            "message_type": "comment",
            "subtype_xmlid": "mail.mt_note"
        })
        print(f"[OK] Posted notification to invoice chatter")
    except Exception as e:
        print(f"[!] Failed to update invoice: {e}")


def create_followup_activity(workiz_job, contact_id, days_until_followup=180):
    """Create follow-up activity in Odoo. Due date = now + days_until_followup (from job frequency), adjusted to Sunday."""
    try:
        res_id = int(contact_id) if contact_id is not None else 0
    except (TypeError, ValueError):
        res_id = 0
    if not res_id:
        return {'success': False, 'error': 'contact_id (res_id) is required and must be a valid partner id'}

    try:
        # Odoo 19: use res_model_id (ir.model id) so res_id is accepted; also verify partner exists
        partner_exists = odoo_rpc("res.partner", "read", [[res_id]], {"fields": ["id"]})
        if not partner_exists:
            return {'success': False, 'error': f'Contact (res.partner) id {res_id} not found in Odoo'}
        models = odoo_rpc("ir.model", "search_read", [[["model", "=", "res.partner"]]], {"fields": ["id"], "limit": 1})
        res_model_id = models[0]["id"] if models else None
        if not res_model_id:
            return {'success': False, 'error': 'Could not get ir.model id for res.partner'}
    except Exception as e:
        return {'success': False, 'error': f'Odoo lookup failed: {e}'}

    # Due date = follow-up date (e.g. 180 days from now), optionally adjusted to Sunday. Must not be today.
    now = datetime.now()
    today = now.date()
    days_out = max(1, int(days_until_followup))
    followup_date = now + timedelta(days=days_out)
    days_to_sunday = 6 - followup_date.weekday()  # 0 if already Sunday
    followup_date = followup_date + timedelta(days=days_to_sunday)
    if followup_date.date() <= today:
        followup_date = now + timedelta(days=days_out)
    due_date_str = followup_date.strftime('%Y-%m-%d')

    customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
    service_address = workiz_job.get('Address', '')
    last_service_date = workiz_job.get('JobDateTime', '')
    line_items = workiz_job.get('LineItems', [])
    services = [item.get('Name', '') for item in line_items if 'tip' not in item.get('Name', '').lower()]
    services_text = ', '.join(services) if services else 'Service'
    description = f"""Follow-up with customer about next service visit.

Follow-up in {days_out} days (due {due_date_str}).
Last Service Date: {last_service_date}
Services Performed: {services_text}
Property: {service_address}

Action Required:
- Call or text customer to check property condition
- Ask if they'd like to schedule next visit
- Update service frequency if needed

Workiz Job: {workiz_job.get('UUID', 'N/A')}"""

    # Create activity: set date_deadline explicitly so Odoo shows the correct due date (not today).
    activity_vals = {
        "res_model_id": res_model_id,
        "res_id": res_id,
        "activity_type_id": 2,
        "summary": f"Follow-up: {customer_name}",
        "note": description,
        "date_deadline": due_date_str,
        "user_id": ODOO_USER_ID,
    }
    try:
        activity_id = odoo_rpc("mail.activity", "create", [activity_vals])
        if not activity_id:
            return {'success': False, 'error': 'Odoo returned no activity id'}
        print(f"[OK] Activity created: ID {activity_id}, Due: {due_date_str} (follow-up in {days_out} days)")
        return {'success': True, 'activity_id': activity_id, 'due_date': due_date_str}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_next_job_type(completed_job_data):
    """
    Determine next job type (handles alternating service).
    
    If alternating=Yes:
    - "Outside Windows and Screens" → "Windows Inside & Outside Plus Screens"
    - "Windows Inside & Outside Plus Screens" → "Outside Windows and Screens"
    
    Otherwise: keep same job type
    """
    current_job_type = completed_job_data.get('JobType', '')
    alternating = str(completed_job_data.get('alternating', '')).lower()
    is_alternating = alternating in ['yes', '1', 'true']
    
    if not is_alternating:
        return current_job_type
    
    # Alternating logic: toggle between inside+out and outside-only
    current_lower = current_job_type.lower()
    
    if 'outside windows and screens' == current_lower:
        next_type = 'Windows Inside & Outside Plus Screens'
        print(f"[*] Alternating Job Type: '{current_job_type}' → '{next_type}'")
        return next_type
    elif 'windows inside & outside plus screens' == current_lower:
        next_type = 'Outside Windows and Screens'
        print(f"[*] Alternating Job Type: '{current_job_type}' → '{next_type}'")
        return next_type
    else:
        # Unrecognized job type - keep same
        print(f"[!] Alternating enabled but job type '{current_job_type}' not recognized for toggle")
        return current_job_type


def get_line_items_for_next_job(workiz_job, property_id, next_job_type):
    """Get line items for next job (handles alternating logic)."""
    alternating = str(workiz_job.get('alternating', '')).lower()
    is_alternating = alternating in ['yes', '1', 'true']
    
    if is_alternating:
        print(f"[*] Alternating service - searching for most recent job matching next job type: {next_job_type}")
        
        all_sales_orders = search_all_sales_orders_for_property(property_id)
        
        # Search for the most recent job that matches the NEXT job type
        source_uuid = None
        for so in all_sales_orders:
            so_uuid = so.get('x_studio_x_studio_workiz_uuid')
            if not so_uuid:
                continue
            
            # Fetch job details to check job type
            job_details = get_job_details(so_uuid)
            if job_details:
                job_type = (job_details.get('JobType') or '').lower()
                next_type_lower = next_job_type.lower()
                
                # Match if job types are the same
                if job_type == next_type_lower:
                    source_uuid = so_uuid
                    print(f"[*] Found matching job type: {so_uuid} ({job_details.get('JobType')})")
                    break
        
        if source_uuid:
            source_job = get_job_details(source_uuid)
            line_items = source_job.get('LineItems', []) if source_job else workiz_job.get('LineItems', [])
        else:
            print(f"[!] No matching job type found in history - using current job line items")
            line_items = workiz_job.get('LineItems', [])
    else:
        print("[*] Regular service - using current job")
        line_items = workiz_job.get('LineItems', [])
    
    # Filter out tips, discounts
    filtered = [item for item in line_items 
                if not any(x in item.get('Name', '').lower() for x in ['tip', 'discount', 'quote', 'legacy'])]
    
    print(f"[*] Found {len(filtered)} line items for next job")
    return filtered


# ==============================================================================
# PHASE 5A: MAINTENANCE PATH
# ==============================================================================

def schedule_next_maintenance_job(workiz_job, property_id, customer_city, invoice_id=None):
    """Create next maintenance job in Workiz."""
    print("\n" + "="*70)
    print("PHASE 5A: MAINTENANCE AUTO-SCHEDULER")
    print("="*70)
    
    frequency = workiz_job.get('frequency', '3 Months')
    print(f"\n[*] Frequency: {frequency}")
    
    # Extract completed job date as base for next service calculation
    job_datetime_str = workiz_job.get('JobDateTime', '')
    base_date = None
    if job_datetime_str:
        try:
            base_date = datetime.strptime(job_datetime_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                base_date = datetime.strptime(job_datetime_str.split(' ')[0], '%Y-%m-%d')
            except ValueError:
                print(f"[WARN] Could not parse JobDateTime: {job_datetime_str}")
    
    # Calculate next date from completed job date (not today)
    scheduled_datetime = calculate_next_service_date(frequency, customer_city, base_date)
    print(f"[OK] Next service: {scheduled_datetime}")
    
    # Determine next job type (for alternating)
    next_job_type = get_next_job_type(workiz_job)
    
    # Get line items (pass next job type for alternating matching)
    line_items = get_line_items_for_next_job(workiz_job, property_id, next_job_type)
    line_items_text = format_line_items_for_custom_field(line_items)
    
    print(f"\n[*] Line items reference:\n{line_items_text}")
    
    # Create job
    result = create_next_maintenance_job(workiz_job, scheduled_datetime, line_items_text)
    
    if result['success']:
        print("[OK] Job created and tech assigned. Manually: add line items, set time slot from schedule, then set status to 'Next Appointment - Text' to send the text.")
        
        # Update invoice with Workiz link if we have invoice_id and new job UUID
        new_uuid = result.get('new_job_uuid')
        if invoice_id and new_uuid:
            customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
            update_invoice_with_workiz_link(invoice_id, new_uuid, customer_name, scheduled_datetime)
    else:
        print(f"[ERROR] Failed: {result['message']}")
    
    print("="*70)
    return result


# ==============================================================================
# PHASE 5B: ON DEMAND PATH
# ==============================================================================

def create_ondemand_followup(workiz_job, contact_id, days_until_followup=180, invoice_id=None):
    """Create follow-up reminder in Odoo (no Workiz job). Default 6 months when unknown."""
    print("\n" + "="*70)
    print("PHASE 5B: FOLLOW-UP ACTIVITY (no Workiz job)")
    print("="*70)
    
    customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
    print(f"\n[*] Creating reminder for: {customer_name} (due in {days_until_followup} days)")
    
    result = create_followup_activity(workiz_job, contact_id, days_until_followup=days_until_followup)
    
    if result['success']:
        print(f"[OK] Reminder created!")
        print("    NO Workiz job created (keeps schedule clean)")
        
        # Update invoice with activity link (if invoice_id provided)
        activity_id = result.get('activity_id')
        if invoice_id and activity_id:
            try:
                activity_url = f"https://window-solar-care.odoo.com/web#id={activity_id}&model=mail.activity&view_type=form"
                odoo_rpc("account.move", "write", [[invoice_id], {"x_studio_workiz_job_link": activity_url}])
                print(f"[OK] Updated invoice with activity link: {activity_url}")
                
                # Post notification to invoice chatter
                message_body = f"""<p><strong>🔔 Follow-Up Activity Created</strong></p>
<p>Customer: <strong>{customer_name}</strong><br/>
Due Date: <strong>{result.get('due_date', 'N/A')}</strong></p>
<p>Activity ID: <strong>{activity_id}</strong></p>
<p><em>Click the "Workiz Job Link" field on this invoice to open the activity in Odoo.</em></p>"""
                
                odoo_rpc("account.move", "message_post", [[invoice_id]], {
                    "body": message_body,
                    "message_type": "notification",
                    "subtype_xmlid": "mail.mt_note"
                })
                print(f"[OK] Posted activity notification to invoice chatter")
            except Exception as e:
                print(f"[WARNING] Could not update invoice with activity link: {e}")
    else:
        print(f"[ERROR] Failed: {result.get('error')}")
    
    print("="*70)
    return result


# ==============================================================================
# MAIN ROUTER
# ==============================================================================

def main(input_data):
    """
    Phase 5 Main Router.
    
    Expected input from Zapier:
    {
        'job_uuid': 'ABC123',              # Workiz job UUID
        'property_id': 12345,              # Odoo property ID
        'contact_id': 67890,               # Odoo contact ID
        'customer_city': 'Palm Springs',    # Property city
        'invoice_id': 101                  # Odoo invoice ID (optional, for posting link to chatter)
    }
    """
    print("\n" + "="*70)
    print("PHASE 5: AUTO-SCHEDULER")
    print("="*70)
    
    # Extract input
    job_uuid = input_data.get('job_uuid')
    property_id = input_data.get('property_id')
    contact_id = input_data.get('contact_id')
    customer_city = input_data.get('customer_city', '')
    invoice_id = input_data.get('invoice_id')
    
    # DEBUG: Print what we received
    print(f"\n[DEBUG] Input data received:")
    print(f"  job_uuid: {job_uuid}")
    print(f"  property_id: {property_id} (type: {type(property_id)})")
    print(f"  contact_id: {contact_id} (type: {type(contact_id)})")
    print(f"  customer_city: '{customer_city}' (type: {type(customer_city)})")
    print(f"  invoice_id: {invoice_id} (type: {type(invoice_id) if invoice_id else 'None'})")
    
    # Convert string IDs to integers if needed
    if property_id and isinstance(property_id, str):
        try:
            property_id = int(property_id)
            print(f"[*] Converted property_id to integer: {property_id}")
        except:
            pass
    
    if contact_id is not None:
        try:
            contact_id = int(contact_id)
            if contact_id:
                print(f"[*] Converted contact_id to integer: {contact_id}")
        except (TypeError, ValueError):
            contact_id = None
    
    if invoice_id and isinstance(invoice_id, str):
        try:
            invoice_id = int(invoice_id)
            print(f"[*] Converted invoice_id to integer: {invoice_id}")
        except:
            pass
    
    if not job_uuid:
        return {'success': False, 'error': 'Missing job_uuid'}
    
    # Get Workiz job details
    print(f"\n[*] Fetching job: {job_uuid}")
    workiz_job = get_job_details(job_uuid)
    
    if not workiz_job:
        return {'success': False, 'error': 'Failed to fetch Workiz job'}
    
    # Check service type
    type_of_service = workiz_job.get('type_of_service', '').lower()
    print(f"[*] Service Type: {type_of_service}")
    
    # Route based on service type
    if 'maintenance' in type_of_service:
        # MAINTENANCE PATH
        if not property_id or not customer_city:
            return {'success': False, 'error': 'Missing property_id or customer_city'}
        
        result = schedule_next_maintenance_job(workiz_job, property_id, customer_city, invoice_id=invoice_id)
        return {'success': result['success'], 'path': '5A_maintenance', 'result': result}
    
    elif 'on demand' in type_of_service or 'on-demand' in type_of_service:
        # ON DEMAND PATH: Odoo activity, due date from frequency (no Workiz job)
        if not contact_id or contact_id == 0:
            return {'success': False, 'error': 'Missing or invalid contact_id (required for Odoo activity)'}
        
        freq = workiz_job.get('frequency', '') or ''
        days = frequency_to_activity_days(freq)
        print(f"[*] On Demand -> follow-up activity in {days} days (frequency: {freq or 'unknown'})")
        result = create_ondemand_followup(workiz_job, contact_id, days_until_followup=days, invoice_id=invoice_id)
        return {'success': result['success'], 'path': '5B_ondemand', 'result': result}
    
    elif 'on request' in type_of_service or 'unknown' in type_of_service or not (type_of_service or '').strip():
        # ON REQUEST / UNKNOWN: Odoo activity, due date from frequency; unknown/missing = 6 months (no Workiz job)
        if not contact_id or contact_id == 0:
            return {'success': False, 'error': 'Missing or invalid contact_id (required for Odoo activity)'}
        
        freq = workiz_job.get('frequency', '') or ''
        days = frequency_to_activity_days(freq)
        print(f"[*] Type '{type_of_service or 'empty'}' -> follow-up activity in {days} days (frequency: {freq or 'unknown'})")
        result = create_ondemand_followup(workiz_job, contact_id, days_until_followup=days, invoice_id=invoice_id)
        return {'success': result['success'], 'path': '5B_on_request_unknown', 'result': result}
    
    else:
        # Truly unrecognized type - default to maintenance only as fallback
        print(f"[!] Unrecognized service type '{type_of_service}' - defaulting to maintenance")
        
        if not property_id or not customer_city:
            return {'success': False, 'error': 'Cannot default to maintenance'}
        
        result = schedule_next_maintenance_job(workiz_job, property_id, customer_city, invoice_id=invoice_id)
        return {'success': result['success'], 'path': '5A_maintenance_default', 'result': result}


# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {
        'job_uuid': 'IC3ZC9',  # Blair Becker
        'property_id': 24169,
        'contact_id': 23621,
        'customer_city': 'Palm Springs'
    }
    
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2))
    print("="*70)
else:
    # For Zapier deployment (Zapier injects input_data into the run environment)
    try:
        output = main(input_data)
    except NameError:
        output = None  # input_data not defined when script is imported (e.g. for local testing)
