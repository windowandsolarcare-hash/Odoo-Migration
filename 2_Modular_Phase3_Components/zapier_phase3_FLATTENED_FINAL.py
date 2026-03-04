"""
ZAPIER PHASE 3 FLATTENED SCRIPT - FINAL
=======================================
Workiz -> Odoo Integration (Master Router)
Handles Paths A, B, and C based on ClientId and Property existence.

SO = Sales Order only when scheduled: we only confirm (and create a task) when Status or SubStatus
is one of: "Next appointment", "Send confirmation text", "Scheduled". Otherwise the SO stays a
quotation (draft) until you change status to one of those.

Generated: 2026-02-05
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import ast

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

# Odoo product field that stores Workiz product code (cross-reference for line item matching)
ODOO_PRODUCT_WORKIZ_CODE_FIELD = "x_studio_x_studio_workiz_product_number"

# Default project ID for SOs when products create tasks (Odoo requires project on quotation).
# Set to your Odoo project ID (integer). Find it: Project app → open project → URL has id=... or enable Developer Mode → View Metadata.
# Renaming the project in Odoo does not change its ID, so this won't break.
DEFAULT_PROJECT_ID = 2
ODOO_SO_PROJECT_FIELD = "project_id"
# Task fields (match Phase 4; change if your Field Service uses different names)
ODOO_TASK_PLANNED_DATE_FIELD = "date_deadline"
ODOO_TASK_ASSIGNEE_FIELD = "user_ids"
ODOO_TASK_TAG_IDS_FIELD = "tag_ids"
ODOO_TASK_PARTNER_FIELD = "partner_id"          # Contact (phone lives here)
ODOO_TASK_PHONE_FIELD = "partner_phone"         # Contact Number on task (Studio: partner_phone); we fill from Odoo Contact (Property.parent_id).
ODOO_TASK_PROPERTY_PARTNER_FIELD = False  # Odoo 19 FSM project.task has no 'partner_shipping_id'
ODOO_TASK_START_DATETIME_FIELD = "planned_date_begin"  # Odoo 19 FSM planned start datetime (UTC)
ODOO_TASK_END_DATETIME_FIELD = "date_end"   # Odoo 19 FSM planned end datetime (UTC)
WORKIZ_JOB_END_DATETIME_FIELD = ""          # set to Workiz key if API returns job end time


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def extract_job_from_input(input_data):
    """
    Extract job UUID and data from either:
    1. Workiz webhook format (nested under 'data')
    2. Zapier polling format (flat structure with 'job_uuid' or 'UUID')
    
    Returns: (job_uuid, workiz_job_data_or_none)
    - If webhook with full data: returns (uuid, full_job_dict)
    - If polling/simple: returns (uuid, None) - caller must fetch via API
    """
    # Check for Workiz webhook format (nested under 'data')
    if 'data' in input_data and isinstance(input_data['data'], dict):
        webhook_data = input_data['data']
        job_uuid = webhook_data.get('uuid')
        
        if job_uuid:
            print("[*] Detected Workiz webhook format (real-time)")
            # Map webhook structure to our expected format
            client_info = webhook_data.get('clientInfo', {})
            address_details = client_info.get('addressDetails', {})
            
            # Build job data dict matching our existing code expectations
            workiz_job = {
                'UUID': job_uuid,
                'SerialId': webhook_data.get('serialId'),
                'Status': webhook_data.get('status', ''),
                'SubStatus': webhook_data.get('subStatus', {}).get('name', '') if isinstance(webhook_data.get('subStatus'), dict) else webhook_data.get('subStatus', ''),
                'JobDateTime': webhook_data.get('date', ''),
                'JobType': webhook_data.get('jobType', {}).get('name', '') if isinstance(webhook_data.get('jobType'), dict) else '',
                'JobSource': webhook_data.get('adGroup', {}).get('name', '') if isinstance(webhook_data.get('adGroup'), dict) else '',
                'ClientId': client_info.get('clientId', '').replace('CL-', ''),  # Strip CL- prefix
                'FirstName': client_info.get('firstName', ''),
                'LastName': client_info.get('lastName', ''),
                'Phone': client_info.get('primaryPhone', ''),
                'Email': client_info.get('email', ''),
                'Address': address_details.get('address', ''),
                'City': address_details.get('city', ''),
                'PostalCode': address_details.get('zipCode', ''),
                'LocationId': address_details.get('locationKey', ''),
                'Team': webhook_data.get('team', []),
                'LineItems': webhook_data.get('lineItems', []),
                'Tags': [tag.get('name', '') for tag in webhook_data.get('tags', []) if isinstance(tag, dict)],
                'JobNotes': '\n'.join([note.get('note', '') for note in webhook_data.get('notes', []) if isinstance(note, dict)]),
                'gate_code': '',  # Not in webhook payload
                'pricing': '',  # Not in webhook payload
                'frequency': '',  # Not in webhook payload
                'alternating': '',  # Not in webhook payload
                'type_of_service': '',  # Not in webhook payload
            }
            
            # Extract custom fields (gate_code, pricing, etc.)
            for cf in webhook_data.get('customFields', []):
                if isinstance(cf, dict):
                    field_name = (cf.get('fieldName', '') or '').lower().strip()
                    value = cf.get('value', '')
                    if 'gate' in field_name:
                        workiz_job['gate_code'] = value
                    elif 'pricing' in field_name or 'price' in field_name:
                        workiz_job['pricing'] = value
                    elif 'frequency' in field_name or 'freq' in field_name:
                        workiz_job['frequency'] = value
                    elif 'alternating' in field_name:
                        workiz_job['alternating'] = value
                    elif 'type' in field_name and 'service' in field_name:
                        workiz_job['type_of_service'] = value
            
            return (job_uuid, workiz_job)
    
    # Fallback to Zapier polling format (flat structure)
    job_uuid = input_data.get('job_uuid') or input_data.get('UUID')
    
    if job_uuid:
        print("[*] Detected Zapier polling format (may be delayed)")
        return (job_uuid, None)
    
    return (None, None)


def _odoo_search_read(model, domain, fields, limit=1):
    try:
        payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "search_read", [domain], {"fields": fields, "limit": limit}]}}
        r = requests.post(ODOO_URL, json=payload, timeout=10)
        return r.json().get("result", [])
    except Exception:
        return []


def _odoo_find_user_id_by_name(tech_name):
    if not tech_name or not str(tech_name).strip():
        return None
    name = str(tech_name).strip()
    for domain in [[["name", "=", name]], [["name", "ilike", name]]]:
        users = _odoo_search_read("res.users", domain, ["id"], limit=1)
        if users:
            return users[0]["id"]
    return None


def sync_tasks_from_so_and_job(so_id, workiz_job, job_datetime_utc):
    """Sync tasks: assignee (tech), planned date/start/end, tags, customer, contact number."""
    lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], ["id"], limit=500)
    line_ids = [x["id"] for x in lines]
    if not line_ids:
        return
    try:
        r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "search", [[["sale_line_id", "in", line_ids]]]]}}, timeout=10)
        task_ids = r.json().get("result", [])
    except Exception:
        return
    if not task_ids:
        return
    task_vals = {}
    team_raw = workiz_job.get("Team") or workiz_job.get("team") or []
    if isinstance(team_raw, list) and team_raw and ODOO_TASK_ASSIGNEE_FIELD:
        first_name = None
        for m in team_raw:
            if isinstance(m, dict):
                first_name = m.get("Name") or m.get("name")
                if first_name:
                    break
        if first_name:
            user_id = _odoo_find_user_id_by_name(str(first_name).strip())
            if user_id is not None:
                task_vals[ODOO_TASK_ASSIGNEE_FIELD] = [(6, 0, [user_id])] if ODOO_TASK_ASSIGNEE_FIELD == "user_ids" else user_id
    # Planned start/end: Odoo FSM requires planned_date_begin < date_end. Do not set date_deadline from start date (becomes midnight and fails constraint); set it from end date when we have date_end.
    order_date_str = (job_datetime_utc or "").strip()
    if order_date_str:
        date_part = order_date_str.split()[0] if " " in order_date_str else order_date_str
        if ODOO_TASK_START_DATETIME_FIELD:
            task_vals[ODOO_TASK_START_DATETIME_FIELD] = order_date_str
        if ODOO_TASK_PLANNED_DATE_FIELD and not ODOO_TASK_START_DATETIME_FIELD:
            task_vals[ODOO_TASK_PLANNED_DATE_FIELD] = date_part
    if WORKIZ_JOB_END_DATETIME_FIELD and workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD) and ODOO_TASK_END_DATETIME_FIELD:
        end_str = str(workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD)).strip()
        if end_str:
            task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_str if " " in end_str else (end_str + " 17:00:00")
    elif ODOO_TASK_END_DATETIME_FIELD and order_date_str and task_vals.get(ODOO_TASK_START_DATETIME_FIELD):
        try:
            dt = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
            end_dt = dt + timedelta(hours=1)
            task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    if task_vals.get(ODOO_TASK_START_DATETIME_FIELD) and not task_vals.get(ODOO_TASK_END_DATETIME_FIELD) and ODOO_TASK_END_DATETIME_FIELD:
        try:
            dt = datetime.strptime(str(task_vals[ODOO_TASK_START_DATETIME_FIELD])[:19], "%Y-%m-%d %H:%M:%S")
            task_vals[ODOO_TASK_END_DATETIME_FIELD] = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    # Enforce planned_date_begin < date_end (Odoo constraint)
    start_val = task_vals.get(ODOO_TASK_START_DATETIME_FIELD)
    end_val = task_vals.get(ODOO_TASK_END_DATETIME_FIELD)
    if start_val and end_val and ODOO_TASK_END_DATETIME_FIELD:
        try:
            start_dt = datetime.strptime(str(start_val)[:19], "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(str(end_val)[:19], "%Y-%m-%d %H:%M:%S")
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(hours=1)
                task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                end_val = task_vals[ODOO_TASK_END_DATETIME_FIELD]
        except Exception:
            pass
    if task_vals.get(ODOO_TASK_END_DATETIME_FIELD) and ODOO_TASK_PLANNED_DATE_FIELD:
        end_val = task_vals[ODOO_TASK_END_DATETIME_FIELD]
        if end_val:
            task_vals[ODOO_TASK_PLANNED_DATE_FIELD] = (str(end_val).split()[0] if " " in str(end_val) else str(end_val))
    so_list = _odoo_search_read("sale.order", [["id", "=", so_id]], ["partner_id", "partner_shipping_id", "tag_ids"], limit=1)
    if so_list:
        so = so_list[0]
        partner_id = so.get("partner_id")
        if partner_id is not None and ODOO_TASK_PARTNER_FIELD:
            pid = partner_id[0] if isinstance(partner_id, (list, tuple)) else partner_id
            if pid:
                task_vals[ODOO_TASK_PARTNER_FIELD] = pid
        if ODOO_TASK_PROPERTY_PARTNER_FIELD:
            shipping = so.get("partner_shipping_id")
            if shipping is not None:
                sid = shipping[0] if isinstance(shipping, (list, tuple)) else shipping
                if sid:
                    task_vals[ODOO_TASK_PROPERTY_PARTNER_FIELD] = sid
        tag_ids = so.get("tag_ids") or []
        if tag_ids and ODOO_TASK_TAG_IDS_FIELD:
            ids = [t for t in tag_ids if isinstance(t, int)] or [t[0] for t in tag_ids if isinstance(t, (list, tuple)) and t]
            if ids:
                task_vals[ODOO_TASK_TAG_IDS_FIELD] = [(6, 0, ids)]
    pid = task_vals.get(ODOO_TASK_PARTNER_FIELD)
    if (pid is None or not pid) and so_list and so_list[0].get("partner_id"):
        p = so_list[0].get("partner_id")
        pid = p[0] if isinstance(p, (list, tuple)) else p
    # Task name = "Customer Name - City" (customer = Contact; city from Property).
    if pid:
        prop = _odoo_search_read("res.partner", [["id", "=", pid]], ["name", "parent_id", "city"], limit=1)
        if prop:
            prop = prop[0]
            city = (prop.get("city") or "").strip()
            contact_id = prop.get("parent_id")
            if contact_id is not None:
                contact_id = contact_id[0] if isinstance(contact_id, (list, tuple)) else contact_id
            customer_name = (prop.get("name") or "").strip()
            if contact_id:
                contact = _odoo_search_read("res.partner", [["id", "=", contact_id]], ["name"], limit=1)
                if contact:
                    customer_name = (contact[0].get("name") or customer_name).strip()
            if customer_name or city:
                task_name = f"{customer_name} - {city}".strip(" - ").strip() if city else customer_name
                if task_name:
                    task_vals["name"] = task_name
    # Phone: SO partner is Property; phone lives on Contact. Get Contact via Property.parent_id.
    if pid and ODOO_TASK_PHONE_FIELD:
        partners = _odoo_search_read("res.partner", [["id", "=", pid]], ["phone", "parent_id"], limit=1)
        if partners:
            phone = (partners[0].get("phone") or "").strip()
            if not phone and partners[0].get("parent_id"):
                contact_id_phone = partners[0]["parent_id"][0] if isinstance(partners[0]["parent_id"], (list, tuple)) else partners[0]["parent_id"]
                contact_partners = _odoo_search_read("res.partner", [["id", "=", contact_id_phone]], ["phone"], limit=1)
                if contact_partners:
                    phone = (contact_partners[0].get("phone") or "").strip()
            if phone:
                task_vals[ODOO_TASK_PHONE_FIELD] = phone
    if not task_vals:
        return
    try:
        requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "write", [task_ids, task_vals]]}}, timeout=10)
        print(f"[OK] Synced {len(task_ids)} task(s): assignee, planned date, tags, customer, contact number")
    except Exception:
        pass


def format_serial_id(serial_id):
    """Format Workiz SerialId as 6-digit string with leading zeros."""
    try:
        return str(int(serial_id)).zfill(6)
    except:
        return str(serial_id)

def convert_pacific_to_utc(pacific_datetime_str):
    """
    Convert Pacific time string to UTC (DST-aware so 10:00 Pacific shows as 10:00 in Odoo).
    Args:
        pacific_datetime_str (str): Pacific time (e.g., "2026-03-12 08:30:00")
    Returns:
        str: UTC time formatted as "YYYY-MM-DD HH:MM:SS"
    """
    dt_naive = datetime.strptime(pacific_datetime_str, '%Y-%m-%d %H:%M:%S')
    try:
        from zoneinfo import ZoneInfo
        pacific = ZoneInfo('America/Los_Angeles')
        dt_pacific = dt_naive.replace(tzinfo=pacific)
        dt_utc = dt_pacific.astimezone(ZoneInfo('UTC'))
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        offset_hours = 8 if dt_naive.month in (11, 12, 1, 2) or (dt_naive.month == 3 and dt_naive.day < 10) else 7
        dt_utc = dt_naive + timedelta(hours=offset_hours)
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')


# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

def get_job_details(job_uuid):
    """Fetch complete Workiz job data by UUID."""
    url = f"{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            response_json = response.json()
            # Workiz API returns data nested in 'data' key as a list
            data_list = response_json.get('data', [])
            if data_list and len(data_list) > 0:
                job_data = data_list[0]
                print(f"[OK] Workiz job data fetched successfully")
                return job_data
            else:
                print(f"[ERROR] No job data in Workiz response")
                return None
        else:
            print(f"[ERROR] Workiz API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception fetching Workiz job: {e}")
        return None


# ==============================================================================
# ODOO API FUNCTIONS
# ==============================================================================

def search_contact_by_client_id(client_id):
    """
    Search for Contact (Client) in Odoo by Workiz ClientId (stored in 'ref' field).
    This is the ONLY way to search - ClientId is the single source of truth.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "search_read",
                [[
                    ["x_studio_x_studio_record_category", "=", "Contact"],
                    ["ref", "=", str(client_id)]
                ]],
                {
                    "fields": ["id", "name", "email", "phone", "street", "ref"],
                    "limit": 1
                }
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            contact = result["result"][0]
            print(f"[OK] Contact found: {contact['name']} (ID: {contact['id']}, ClientId: {contact['ref']})")
            return {
                'contact_id': contact['id'],
                'name': contact['name'],
                'email': contact.get('email'),
                'phone': contact.get('phone'),
                'ref': contact.get('ref')
            }
        
        print(f"[INFO] Contact not found for ClientId: {client_id}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to search contact: {e}")
        return None


def search_property_for_contact(service_address, contact_id):
    """Search for Property linked to a specific Contact."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "search_read",
                [[
                    ["x_studio_x_studio_record_category", "=", "Property"],
                    ["street", "=", service_address.strip()],
                    ["parent_id", "=", contact_id]
                ]],
                {"fields": ["id", "name", "street"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            property_record = result["result"][0]
            print(f"[OK] Property found: {property_record['street']} (ID: {property_record['id']})")
            return {
                'property_id': property_record['id'],
                'street': property_record['street']
            }
        
        print(f"[INFO] Property not found for address: {service_address}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to search property: {e}")
        return None


def search_sales_order_by_uuid(workiz_uuid):
    """Search for Sales Order by Workiz UUID. Returns SO dict or None. Idempotency: avoid duplicate SO when Phase 4 created one first."""
    if not (workiz_uuid or str(workiz_uuid).strip()):
        return None
    u = str(workiz_uuid).strip()
    so_list = _odoo_search_read("sale.order", [["x_studio_x_studio_workiz_uuid", "=", u]], ["id", "name", "partner_id", "partner_shipping_id", "state"], limit=1)
    if so_list:
        return so_list[0]
    return None


def create_contact(customer_name, client_id, workiz_job):
    """Create new Contact in Odoo with all relevant fields from Workiz."""
    # Extract fields from Workiz job
    first_name = workiz_job.get('FirstName', '')
    last_name = workiz_job.get('LastName', '')
    phone = workiz_job.get('Phone', '')
    email = workiz_job.get('Email', '')
    street = workiz_job.get('Address', '')
    city = workiz_job.get('City', '')
    zip_code = workiz_job.get('PostalCode', '')
    
    contact_data = {
        "name": customer_name.strip(),
        "ref": str(client_id),  # Workiz ClientId - CRITICAL for Mirror V31.11
        "x_studio_x_studio_record_category": "Contact",
        "customer_rank": 1,
    }
    
    # Add optional fields if present
    if first_name:
        contact_data["x_studio_x_studio_first_name"] = first_name
    if last_name:
        contact_data["x_studio_x_studio_last_name"] = last_name
    if phone:
        contact_data["phone"] = phone
    if email:
        contact_data["email"] = email
    if street:
        contact_data["street"] = street
    if city:
        contact_data["city"] = city
    if zip_code:
        contact_data["zip"] = zip_code
    
    # State ID = 13 (California US) - verified from Bev's correctly migrated data
    contact_data["state_id"] = 13
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "create",
                [contact_data]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            contact_id = result["result"]
            print(f"[OK] Contact created: {customer_name} (ID: {contact_id}, ClientId: {client_id})")
            return contact_id
        
        print(f"[ERROR] Failed to create contact: {result}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception creating contact: {e}")
        return None


def create_property(contact_id, service_address, workiz_job, location_id=None):
    """Create new Property linked to Contact in Odoo. Name = 'Contact Name, Address' for SO list display."""
    # Extract full address details from Workiz
    city = workiz_job.get('City', '')
    zip_code = workiz_job.get('PostalCode', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    # SO Customer column shows partner name; use "Contact Name, Address"
    first_name = (workiz_job.get('FirstName') or '').strip()
    last_name = (workiz_job.get('LastName') or '').strip()
    contact_name = f"{first_name} {last_name}".strip()
    address = service_address.strip()
    property_display_name = f"{contact_name}, {address}".strip(", ").strip() if contact_name else address
    
    property_data = {
        "name": property_display_name,
        "street": address,
        "parent_id": contact_id,
        "x_studio_x_studio_record_category": "Property",
        "type": "other"
    }
    
    # Add full address details
    if city:
        property_data["city"] = city
    if zip_code:
        property_data["zip"] = zip_code
    
    # State = California (US) - state_id = 13 (verified from Bev's data)
    property_data["state_id"] = 13
    
    # Store Workiz Location ID if provided
    if location_id:
        property_data["x_studio_x_studio_location_id"] = str(location_id)
    
    # Add service details
    if frequency:
        property_data["x_studio_x_frequency"] = frequency
    if type_of_service:
        property_data["x_studio_x_type_of_service"] = type_of_service
    
    # Alternating - convert 1/0 to Yes/No
    if alternating is not None and alternating != '':
        property_data["x_studio_x_alternating"] = "Yes" if str(alternating) == "1" else "No"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "create",
                [property_data]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            property_id = result["result"]
            location_msg = f", LocationId: {location_id}" if location_id else ""
            print(f"[OK] Property created: {service_address} (ID: {property_id}{location_msg})")
            return property_id
        
        print(f"[ERROR] Failed to create property: {result}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Exception creating property: {e}")
        return None


def search_product_by_workiz_code(workiz_code):
    """Search for Odoo product by x_studio_x_studio_workiz_product_number (Workiz product code). Return product ID or None."""
    if workiz_code is None or str(workiz_code).strip() == '':
        return None
    code = str(workiz_code).strip()
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "product.product",
                "search_read",
                [[[ODOO_PRODUCT_WORKIZ_CODE_FIELD, "=", code]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]["id"]
        return None
    except Exception:
        return None


def search_product_by_name(product_name):
    """Search for Odoo product by name and return product ID."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "product.product",
                "search_read",
                [[["name", "=", product_name]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]["id"]
        return None
    except Exception:
        return None


def get_contact_tag_names(contact_id):
    """Get tag names from contact's category_id field."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "read",
                [[contact_id]],
                {"fields": ["category_id"]}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            category_data = result["result"][0].get("category_id", [])
            tag_names = [tag[1] for tag in category_data if len(tag) > 1]
            return tag_names
        return []
    except:
        return []


def get_sales_tag_ids(tag_names):
    """Get Odoo sales order tag IDs (crm.tag) for given tag names."""
    if not tag_names:
        return []
    
    if isinstance(tag_names, str):
        tags_list = [t.strip() for t in tag_names.split(',') if t.strip()]
    elif isinstance(tag_names, list):
        tags_list = [str(t).strip() for t in tag_names if t]
    else:
        return []
    
    tag_ids = []
    
    for tag_name in tags_list:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "crm.tag",
                    "search_read",
                    [[["name", "=", tag_name]]],
                    {"fields": ["id"], "limit": 1}
                ]
            }
        }
        
        try:
            response = requests.post(ODOO_URL, json=payload, timeout=10)
            result = response.json()
            
            if result.get("result") and len(result["result"]) > 0:
                tag_id = result["result"][0]["id"]
                tag_ids.append(tag_id)
        except:
            pass
    
    return tag_ids


def create_sales_order(contact_id, property_id, workiz_job_data, booking_datetime, order_name=""):
    """Create Odoo sales order with complete Workiz job details."""
    
    # Extract Workiz data
    workiz_uuid = workiz_job_data.get('UUID', '')
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', '') or workiz_job_data.get('Status', '')
    job_source = workiz_job_data.get('JobSource', '')  # Lead source from Workiz
    
    tags = workiz_job_data.get('Tags') or workiz_job_data.get('JobTags', '')
    gate_code_raw = workiz_job_data.get('GateCode') or workiz_job_data.get('gate_code') or workiz_job_data.get('Gate', '')
    pricing_raw = workiz_job_data.get('Pricing') or workiz_job_data.get('pricing') or workiz_job_data.get('PricingNote', '')
    job_notes = workiz_job_data.get('JobNotes') or workiz_job_data.get('Notes', '')
    info_to_remember = workiz_job_data.get('information_to_remember') or workiz_job_data.get('InformationToRemember', '')
    comments = workiz_job_data.get('Comments') or workiz_job_data.get('Comment', '')
    job_type = workiz_job_data.get('JobType') or workiz_job_data.get('Type', '')
    line_items_raw = workiz_job_data.get('LineItems', [])
    team_raw = workiz_job_data.get('Team') or workiz_job_data.get('team', '')
    
    # Filter placeholder text - convert to string first to handle integers
    gate_code = gate_code_raw if gate_code_raw and str(gate_code_raw).lower() not in ['gate code', 'gate', ''] else ''
    pricing = pricing_raw if pricing_raw and str(pricing_raw).lower() not in ['pricing', 'price', 'pricing note', ''] else ''
    
    # Process Team field - extract names from list of dicts
    team_names = ""
    if team_raw:
        if isinstance(team_raw, list):
            names = []
            for member in team_raw:
                if isinstance(member, dict):
                    name = member.get('Name') or member.get('name', '')
                    if name:
                        names.append(str(name).strip())
                elif member:
                    names.append(str(member).strip())
            team_names = ", ".join(names)
        elif isinstance(team_raw, str):
            team_names = team_raw.strip()
    
    # Parse line items
    if isinstance(line_items_raw, str):
        try:
            line_items = ast.literal_eval(line_items_raw)
        except:
            line_items = []
    else:
        line_items = line_items_raw if isinstance(line_items_raw, list) else []
    
    # Convert Workiz line items to Odoo format: match by Workiz product code (x_studio_x_studio_workiz_product_number) first, then by name
    odoo_order_lines = []
    for item in line_items:
        if isinstance(item, dict):
            item_name = item.get('Name', 'Service')
            qty = float(item.get('Quantity', 1))
            price = float(item.get('Price', 0))
            # Workiz LineItems per Workiz_API_Test_Results.md: ModelNum, Id
            workiz_code = item.get('ModelNum') or item.get('Id')
            product_id = None
            if workiz_code is not None and str(workiz_code).strip() != '':
                product_id = search_product_by_workiz_code(workiz_code)
            if product_id is None:
                product_id = search_product_by_name(item_name)
            if product_id is None and item_name != 'Service':
                product_id = search_product_by_name('Service')
            if product_id:
                line_data = {
                    'product_id': product_id,
                    'product_uom_qty': qty,
                    'price_unit': price
                }
                odoo_order_lines.append([0, 0, line_data])
    
    # Format notes snapshot - organize with Calendly notes first, then original notes
    notes_parts = []
    
    if job_notes and job_notes.strip():
        # Check if notes contain Calendly booking and delimiter
        if '[Calendly Booking]' in job_notes and '|||ORIGINAL_NOTES|||' in job_notes:
            # Split Calendly notes from original notes
            parts = job_notes.split('|||ORIGINAL_NOTES|||')
            calendly_part = parts[0].replace('[Calendly Booking]', '').strip()
            original_part = parts[1].strip() if len(parts) > 1 else ''
            
            # Clean newlines from each part
            calendly_clean = ' '.join(calendly_part.split())
            original_clean = ' '.join(original_part.split()) if original_part else ''
            
            # Add Calendly note FIRST
            notes_parts.append(f"[Calendly Booking] {calendly_clean}")
            
            # Add original notes second (if any)
            if original_clean:
                notes_parts.append(f"[Job Notes] {original_clean}")
        else:
            # No Calendly delimiter, treat as regular notes
            clean_notes = ' '.join(job_notes.strip().split())
            if clean_notes.startswith('[Calendly Booking]'):
                # Has Calendly tag but no delimiter (old format)
                notes_parts.append(clean_notes)
            else:
                notes_parts.append(f"[Job Notes] {clean_notes}")
    
    if comments and comments.strip():
        clean_comments = ' '.join(comments.strip().split())
        notes_parts.append(f"[Comments] {clean_comments}")
    
    notes_snapshot = " ".join(notes_parts)
    
    # DEBUG: Print extracted Workiz data
    print(f"\n[DEBUG] Workiz data extracted:")
    print(f"   UUID: {workiz_uuid}")
    print(f"   SubStatus: {workiz_substatus}")
    print(f"   Job Source: {job_source}")
    print(f"   Job Type: {job_type}")
    print(f"   Team: {team_names}")
    print(f"   Gate Code: {gate_code}")
    print(f"   Pricing: {pricing}")
    print(f"   Line Items: {len(line_items)} items")
    print(f"   Notes Snapshot: {notes_snapshot[:50] if notes_snapshot else 'None'}...")
    
    # Get tags from both Contact and Workiz
    contact_tag_names = get_contact_tag_names(contact_id)
    
    workiz_tag_names = []
    if tags:
        if isinstance(tags, list):
            workiz_tag_names = [str(t).strip() for t in tags if t]
        elif isinstance(tags, str):
            workiz_tag_names = [t.strip() for t in tags.split(',') if t.strip()]
    
    all_tag_names = list(set(contact_tag_names + workiz_tag_names))
    tag_ids = get_sales_tag_ids(all_tag_names) if all_tag_names else []
    
    print(f"   Tags: {len(all_tag_names)} total ({', '.join(all_tag_names[:3])}...)" if all_tag_names else "   Tags: None")
    
    # Build order data - set date_order BEFORE creating SO (so Odoo doesn't default to current time)
    # Property as brain: customer and billing on SO = Property. Contact remains linked via Property.parent_id.
    order_data = {
        "partner_id": property_id,
        "partner_invoice_id": property_id,
        "partner_shipping_id": property_id,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_lead_source": job_source
    }
    
    # Set date_order from booking_datetime BEFORE creating SO (so Odoo doesn't default to current time)
    if booking_datetime:
        order_data['date_order'] = booking_datetime
        print(f"   Order Date: {booking_datetime}")
    
    # Add tags if any
    if tag_ids:
        order_data["tag_ids"] = [(6, 0, tag_ids)]
    
    # Add Job Type
    if job_type:
        order_data["x_studio_x_studio_x_studio_job_type"] = job_type
    
    # Add Team/Tech
    if team_names:
        order_data["x_studio_x_studio_workiz_tech"] = team_names
    
    # Add gate/pricing snapshots
    if gate_code:
        order_data["x_studio_x_gate_snapshot"] = gate_code
    
    if pricing:
        order_data["x_studio_x_studio_pricing_snapshot"] = pricing
    
    # Add notes
    if notes_snapshot:
        order_data["x_studio_x_studio_notes_snapshot1"] = notes_snapshot
    
    # Add line items
    if odoo_order_lines and len(odoo_order_lines) > 0:
        order_data["order_line"] = odoo_order_lines
        # Products that create tasks require a project on the quotation; set default so create succeeds
        if DEFAULT_PROJECT_ID:
            order_data[ODOO_SO_PROJECT_FIELD] = DEFAULT_PROJECT_ID
    
    # Add order name
    if order_name:
        order_data["name"] = order_name
        print(f"   Order Name: {order_name}")
    
    # Create sales order
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "create", [order_data]]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            sales_order_id = result["result"]
            print(f"[OK] Sales order created: ID {sales_order_id}")
            return {'success': True, 'sales_order_id': sales_order_id, 'booking_datetime': booking_datetime}
        else:
            error = result.get("error", {})
            return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': f"Error: {error.get('message', 'Unknown')}"}
    except Exception as e:
        return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': f"Exception: {str(e)}"}


def confirm_sales_order(sales_order_id):
    """Confirm sales order (Quotation -> Sales Order)."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "sale.order",
                "action_confirm",
                [[sales_order_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not None:
            return {'success': True}
        else:
            error = result.get("error", {})
            return {'success': False, 'message': f"Error: {error.get('message', 'Unknown')}"}
    except Exception as e:
        return {'success': False, 'message': f"Exception: {str(e)}"}


def update_sales_order_date(sales_order_id, date_order):
    """
    Update sales order date_order field (Job/Schedule Date).
    IMPORTANT: Must be called AFTER confirming the sales order (Odoo overwrites during confirm).
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "sale.order",
                "write",
                [[sales_order_id], {"date_order": date_order}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            return {'success': True}
        else:
            return {'success': False, 'message': result.get('error', {}).get('message', 'Unknown error')}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def update_property_fields(property_id, gate_code=None, pricing=None, last_visit_date=None, job_notes=None, comments=None, frequency=None, alternating=None, type_of_service=None):
    """Update property's gate code, pricing, last visit date, notes, and service details."""
    
    update_data = {}
    
    # Gate code and pricing
    if gate_code:
        update_data["x_studio_x_gate_code"] = gate_code
    if pricing:
        update_data["x_studio_x_pricing"] = pricing
    
    # Last property visit date
    if last_visit_date:
        update_data["x_studio_x_studio_last_property_visit"] = last_visit_date
    
    # Service frequency and type
    if frequency:
        update_data["x_studio_x_frequency"] = frequency
    if type_of_service:
        update_data["x_studio_x_type_of_service"] = type_of_service
    
    # Alternating - convert 1/0 to Yes/No
    if alternating is not None:
        if str(alternating) == "1":
            update_data["x_studio_x_alternating"] = "Yes"
        else:
            update_data["x_studio_x_alternating"] = "No"
    
    # Combine JobNotes and Comments into the comment field (overwrites)
    combined_notes = ""
    if job_notes:
        combined_notes = f"[Job Note] {job_notes}"
    if comments:
        if combined_notes:
            combined_notes += f"\n\n[Comment] {comments}"
        else:
            combined_notes = f"[Comment] {comments}"
    
    if combined_notes:
        update_data["comment"] = combined_notes
    
    if not update_data:
        print("[*] No property updates needed (all fields empty)")
        return {'success': True, 'message': 'No property updates needed'}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "res.partner",
                "write",
                [[property_id], update_data]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Property updated successfully")
            return {'success': True}
        else:
            return {'success': False, 'message': 'Property update failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


# ==============================================================================
# PATH EXECUTION FUNCTIONS
# ==============================================================================

def execute_path_a(contact_id, property_id, workiz_job, skip_confirm=False):
    """
    PATH A: Contact exists + Property exists. skip_confirm=True = quotation only (no confirm, no task).
    """
    print("\n" + "="*70)
    print("EXECUTING PATH A: Existing Contact + Existing Property")
    print("="*70)
    
    # Step 1: Prepare data for sales order
    # Get booking datetime from Workiz (in Pacific time) and convert to UTC
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        # Workiz JobDateTime is in Pacific time: "2026-04-03 08:30:00"
        # Convert to UTC for Odoo
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format order name
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 2: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        return {'success': False, 'error': 'Failed to create sales order'}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 3: Confirm sales order only when scheduled (Next appointment / Send confirmation text / Scheduled); otherwise quotation only
    if not skip_confirm:
        confirm_result = confirm_sales_order(sales_order_id)
        if not confirm_result:
            print("[WARNING] Could not confirm sales order")
    else:
        print("[*] Quotation only (no confirm → no task).")
    
    # Step 4: date_order is now set during SO creation (no longer need to update separately)
    # update_result = update_sales_order_date(sales_order_id, booking_datetime)
    # if not update_result:
    #     print("[WARNING] Could not update date_order")
    # Step 4b: Sync tasks only when SO was confirmed
    if not skip_confirm:
        sync_tasks_from_so_and_job(sales_order_id, workiz_job, booking_datetime)
    
    # Step 5: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH A COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'A',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


def execute_path_b(contact_id, service_address, workiz_job, skip_confirm=False):
    """
    PATH B: Contact exists + Property DOES NOT exist. skip_confirm=True = quotation only (no task).
    """
    print("\n" + "="*70)
    print("EXECUTING PATH B: Existing Contact + New Property")
    print("="*70)
    
    # Step 1: Create property with Workiz LocationId and full address
    location_id = workiz_job.get('LocationId')
    property_id = create_property(contact_id, service_address, workiz_job, location_id)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    # Step 2: Prepare data for sales order
    # Convert Pacific time from Workiz to UTC for Odoo
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 5: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        return {'success': False, 'error': 'Failed to create sales order'}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 6: Confirm sales order only when scheduled; otherwise quotation only
    if not skip_confirm:
        confirm_result = confirm_sales_order(sales_order_id)
        if not confirm_result:
            print("[WARNING] Could not confirm sales order")
    else:
        print("[*] Quotation only (no confirm → no task).")
    
    # Step 7: date_order is now set during SO creation (no longer need to update separately)
    # update_result = update_sales_order_date(sales_order_id, booking_datetime)
    # if not update_result:
    #     print("[WARNING] Could not update date_order")
    if not skip_confirm:
        sync_tasks_from_so_and_job(sales_order_id, workiz_job, booking_datetime)
    
    # Step 8: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH B COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'B',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


def execute_path_c(customer_name, service_address, workiz_job, client_id, skip_confirm=False):
    """
    PATH C: Contact DOES NOT exist (and property doesn't exist). skip_confirm=True = quotation only (no task).
    """
    print("\n" + "="*70)
    print("EXECUTING PATH C: New Contact + New Property")
    print("="*70)
    
    # Step 1: Create contact with Workiz ClientId and all fields
    contact_id = create_contact(customer_name, client_id, workiz_job)
    if not contact_id:
        return {'success': False, 'error': 'Failed to create contact'}
    
    # Step 2: Create property with Workiz LocationId and full address
    location_id = workiz_job.get('LocationId')
    property_id = create_property(contact_id, service_address, workiz_job, location_id)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    # Step 3: Prepare data for sales order
    # Convert Pacific time from Workiz to UTC for Odoo
    job_datetime = workiz_job.get('JobDateTime', '')
    if job_datetime:
        booking_datetime = convert_pacific_to_utc(job_datetime)
        print(f"[*] Time conversion: Pacific {job_datetime} -> UTC {booking_datetime}")
    else:
        booking_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id(serial_id) if serial_id else ""
    
    # Step 6: Create sales order using atomic function
    so_result = create_sales_order(
        contact_id=contact_id,
        property_id=property_id,
        workiz_job_data=workiz_job,
        booking_datetime=booking_datetime,
        order_name=order_name
    )
    
    if not so_result or not so_result.get('success'):
        return {'success': False, 'error': 'Failed to create sales order'}
    
    sales_order_id = so_result['sales_order_id']
    
    # Step 7: Confirm sales order only when scheduled; otherwise quotation only
    if not skip_confirm:
        confirm_result = confirm_sales_order(sales_order_id)
        if not confirm_result:
            print("[WARNING] Could not confirm sales order")
    else:
        print("[*] Quotation only (no confirm → no task).")
    
    # Step 8: date_order is now set during SO creation (no longer need to update separately)
    # update_result = update_sales_order_date(sales_order_id, booking_datetime)
    # if not update_result:
    #     print("[WARNING] Could not update date_order")
    if not skip_confirm:
        sync_tasks_from_so_and_job(sales_order_id, workiz_job, booking_datetime)
    
    # Step 9: Update property fields (note: Workiz uses lowercase field names)
    gate_code = workiz_job.get('gate_code', '')  # Fixed: lowercase 'gate_code' not 'GateCode'
    pricing = workiz_job.get('pricing', '')  # Fixed: lowercase 'pricing' not 'Pricing'
    
    # Extract notes and comments
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH C COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'C',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': sales_order_id
    }


# ==============================================================================
# MAIN ROUTER
# ==============================================================================

def main(input_data):
    """
    Master router: Determines path and executes appropriate workflow.
    
    Expected input_data formats:
    1. Workiz webhook (real-time): {'data': {'uuid': '...', 'clientInfo': {...}, ...}}
    2. Zapier polling (legacy): {'job_uuid': 'ABC123'}
    3. Phase 4 webhook call: {'job_uuid': 'ABC123'}
    """
    print("\n" + "="*70)
    print("WORKIZ -> ODOO MASTER ROUTER (PHASE 3)")
    print("="*70)
    
    # Extract job UUID and data from input (supports both webhook and polling formats)
    job_uuid, workiz_job = extract_job_from_input(input_data)
    
    if not job_uuid:
        return {'success': False, 'error': 'No job_uuid provided'}
    
    # If webhook didn't provide full data, fetch from Workiz API
    if not workiz_job:
        print(f"\n[*] Fetching Workiz job details: {job_uuid}")
        workiz_job = get_job_details(job_uuid)
        if not workiz_job:
            return {'success': False, 'error': 'Failed to fetch Workiz job'}
    else:
        print(f"\n[*] Using Workiz webhook data (no API call needed)")
    
    # Extract key fields
    customer_name = workiz_job.get('FirstName', '') + ' ' + workiz_job.get('LastName', '')
    customer_name = customer_name.strip()
    service_address = workiz_job.get('Address', '').strip()
    phone = workiz_job.get('Phone', '')
    email = workiz_job.get('Email', '')
    client_id = workiz_job.get('ClientId')  # Workiz ClientId - THE KEY FIELD
    
    print(f"[*] Customer: {customer_name}")
    print(f"[*] ClientId: {client_id}")
    print(f"[*] Address: {service_address}")
    
    if not client_id:
        return {'success': False, 'error': 'Missing ClientId from Workiz job'}
    
    if not service_address:
        return {'success': False, 'error': 'Missing service address'}
    
    # Idempotency: if an SO already exists for this job UUID (e.g. Phase 4 created it first), return it and do not create a duplicate.
    existing_so = search_sales_order_by_uuid(job_uuid)
    if existing_so:
        so_id = existing_so['id']
        print(f"\n[*] Sales Order already exists for this job UUID: {existing_so.get('name')} (ID: {so_id}). Skipping create (idempotent).")
        pid = existing_so.get('partner_id')
        property_id = pid[0] if isinstance(pid, (list, tuple)) else pid
        contact_id = None
        if property_id:
            partners = _odoo_search_read("res.partner", [["id", "=", property_id]], ["parent_id"], limit=1)
            if partners and partners[0].get("parent_id"):
                contact_id = partners[0]["parent_id"][0] if isinstance(partners[0]["parent_id"], (list, tuple)) else partners[0]["parent_id"]
            else:
                contact_id = property_id
        return {
            'success': True,
            'sales_order_id': so_id,
            'path': 'A',
            'contact_id': contact_id or property_id,
            'property_id': property_id,
            'already_existed': True,
        }
    
    # Only confirm SO (create task) when Status or SubStatus is one of: Next appointment, Send confirmation text, Scheduled. Otherwise quotation only.
    status = workiz_job.get('Status', '') or ''
    substatus = workiz_job.get('SubStatus', '') or ''
    status_lower = status.strip().lower()
    substatus_lower = substatus.strip().lower()
    TASK_TRIGGER_VALUES = ('next appointment', 'send confirmation text', 'scheduled')
    skip_confirm = not (status_lower in TASK_TRIGGER_VALUES or substatus_lower in TASK_TRIGGER_VALUES)
    if skip_confirm:
        print("[*] Status/SubStatus is not 'Next appointment' / 'Send confirmation text' / 'Scheduled': SO will be created as quotation (no task).")
    
    # Step 2: Search for Contact by ClientId (ONLY way to search)
    print(f"\n[*] Searching for Contact by ClientId: {client_id}")
    contact_result = search_contact_by_client_id(client_id)
    
    if contact_result:
        # Contact exists - check for property
        contact_id = contact_result['contact_id']
        
        print(f"\n[*] Searching for Property: {service_address}")
        property_result = search_property_for_contact(service_address, contact_id)
        
        if property_result:
            # PATH A: Both exist
            property_id = property_result['property_id']
            return execute_path_a(contact_id, property_id, workiz_job, skip_confirm=skip_confirm)
        else:
            # PATH B: Contact exists, property doesn't
            return execute_path_b(contact_id, service_address, workiz_job, skip_confirm=skip_confirm)
    else:
        # PATH C: Contact doesn't exist (property won't exist either)
        return execute_path_c(customer_name, service_address, workiz_job, client_id, skip_confirm=skip_confirm)


# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {
        'job_uuid': '90OX52'  # Path C test: Leonard Karp (NEW customer)
    }
    
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(result)
    print("="*70)
else:
    # For Zapier deployment
    output = main(input_data)