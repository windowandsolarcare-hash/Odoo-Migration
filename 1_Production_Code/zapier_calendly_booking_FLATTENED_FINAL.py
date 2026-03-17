"""
==============================================================================
ZAPIER CALENDLY BOOKING HANDLER - FLATTENED FOR "CODE BY ZAPIER"
==============================================================================
Complete Calendly → Workiz → Odoo integration in a single file.
No imports required - ready for Zapier deployment.

FLOW:
1. Phase 3A: Lookup Odoo contact by address
2. Phase 3B: Find opportunity with Workiz UUID
3. Phase 3C: Update Workiz job (date/time, status, job type)
4. Phase 3D: Mark opportunity as Won
5. Phase 3E: Create & confirm sales order with all fields
6. Phase 3F: Update contact email

INPUT (from Calendly webhook via Zapier - Custom Questions):
- event_start_time: "2026-03-12T15:30:00.000000Z"
- invitee_email: "customer@example.com"
- invitee_name: "John Doe"
- service_address: "123 Main St, City, CA 12345" (Question 1)
- service_type_required: "Windows Inside & Outside Plus Screens" (Question 2)
- additional_notes: "Please call before arriving" (Question 3)

OUTPUT:
- success: True/False
- sales_order_id: Odoo SO ID
- message: Success or error message
==============================================================================
"""

import requests
from datetime import datetime, timezone, timedelta

# ==============================================================================
# CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# ==============================================================================
# PHASE 3A: PROPERTY & CONTACT LOOKUP
# ==============================================================================

def search_property_and_contact_by_address(street_address):
    """
    Find Odoo Property by address, then get Contact from parent_id.
    Follows Mirror V31.11 hierarchy: Client -> Property -> Job
    
    Returns:
        dict with 'property_id', 'contact_id', 'property_name', 'contact_name', 'street'
        OR None if not found
    """
    # Step 1: Find Property by address
    property_payload = {
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
                    ["street", "=", street_address],
                    ["x_studio_x_studio_record_category", "=", "Property"]
                ]],
                {"fields": ["id", "name", "street", "city", "parent_id"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=property_payload, timeout=10)
        result = response.json()
        
        if not result.get("result") or len(result["result"]) == 0:
            print(f"[ERROR] No Property found for address: {street_address}")
            return None
        
        property_record = result["result"][0]
        property_id = property_record['id']
        property_name = property_record['name']
        
        # Step 2: Get parent_id (Contact/Client ID)
        parent_id = property_record.get('parent_id')
        
        if not parent_id:
            print(f"[ERROR] Property {property_id} has no parent_id (Contact)")
            return None
        
        # parent_id is returned as [id, name] tuple
        contact_id = parent_id[0] if isinstance(parent_id, list) else parent_id
        contact_name = parent_id[1] if isinstance(parent_id, list) and len(parent_id) > 1 else "Unknown"
        
        print(f"[OK] Property found: {property_name} (ID: {property_id})")
        print(f"[OK] Contact found: {contact_name} (ID: {contact_id})")
        
        return {
            'property_id': property_id,
            'contact_id': contact_id,
            'property_name': property_name,
            'contact_name': contact_name,
            'street': property_record['street']
        }
        
    except Exception as e:
        print(f"[ERROR] Exception in property/contact lookup: {e}")
        return None

# ==============================================================================
# PHASE 3B: OPPORTUNITY LOOKUP
# ==============================================================================

def find_opportunity_with_workiz_uuid(contact_id):
    """Find opportunity linked to contact with Workiz UUID populated."""
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
                "crm.lead",
                "search_read",
                [[
                    ["partner_id", "=", contact_id],
                    ["x_workiz_graveyard_uuid", "!=", False]
                ]],
                {"fields": ["id", "name", "x_workiz_graveyard_uuid"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            opp = result["result"][0]
            print(f"[OK] Opportunity found: {opp['name']} (ID: {opp['id']})")
            print(f"   Graveyard UUID: {opp['x_workiz_graveyard_uuid']}")
            return {'success': True, 'opportunity': opp}
        else:
            return {'success': False, 'message': 'No opportunity with Workiz UUID found'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ==============================================================================
# PHASE 3C: WORKIZ JOB UPDATE
# ==============================================================================

def update_workiz_job(job_uuid, booking_time_utc, job_type, job_notes=""):
    """Update Workiz job with new date/time, status, job type, and notes (prepended to existing)."""
    
    # Convert UTC to Pacific time (UTC-8 for PST, UTC-7 for PDT)
    # Parse UTC datetime
    dt_utc = datetime.fromisoformat(booking_time_utc.replace('Z', '+00:00'))
    
    # Convert to Pacific (using UTC-7 for PDT, which is most of the year)
    # For accurate DST handling, we check the month
    pacific_offset = timedelta(hours=-8) if dt_utc.month in [11, 12, 1, 2, 3] and dt_utc.day < 10 else timedelta(hours=-7)
    dt_pacific = dt_utc + pacific_offset
    pacific_datetime = dt_pacific.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[*] Time conversion:")
    print(f"   UTC:     {booking_time_utc}")
    print(f"   Pacific: {pacific_datetime}")
    
    # Fetch current job to get existing notes (so we don't overwrite them)
    combined_notes = ""
    if job_notes:
        current_job = get_workiz_job_details(job_uuid)
        existing_notes = current_job.get('JobNotes', '') if current_job else ''
        
        # Prepend new Calendly notes to existing notes with clear delimiter
        if existing_notes and existing_notes.strip():
            combined_notes = f"[Calendly Booking] {job_notes} |||ORIGINAL_NOTES||| {existing_notes}"
            print(f"[*] Prepending Calendly notes to existing JobNotes")
        else:
            combined_notes = f"[Calendly Booking] {job_notes}"
            print(f"[*] Adding Calendly notes as new JobNotes")
    
    # Update Workiz job
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "JobDateTime": pacific_datetime,
        "JobType": job_type,
        "Status": "Pending",
        "SubStatus": "Send Confirmation - Text"
    }
    
    # Add combined notes if provided (skip if None, which means notes already have Calendly booking)
    if combined_notes:
        payload["JobNotes"] = combined_notes
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Workiz job updated successfully!")
            return {'success': True}
        else:
            return {'success': False, 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ==============================================================================
# PHASE 3D: MARK OPPORTUNITY WON
# ==============================================================================

def mark_opportunity_won(opportunity_id):
    """Mark Odoo opportunity as Won."""
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
                "crm.lead",
                "action_set_won",
                [[opportunity_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not None:
            print(f"[OK] Opportunity {opportunity_id} marked as Won!")
            return {'success': True}
        else:
            return {'success': False, 'message': 'action_set_won failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

# ==============================================================================
# PHASE 3E: CREATE SALES ORDER (ALL HELPER FUNCTIONS)
# ==============================================================================

def get_workiz_job_details(job_uuid):
    """Fetch complete Workiz job data."""
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
            print(f"[ERROR] Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception fetching Workiz job: {e}")
        return None


def search_odoo_product_by_name(product_name):
    """Search for Odoo product by name, return product ID."""
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
    except:
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


def get_property_for_contact(service_address):
    """Find property record by address."""
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
                    ["street", "=", service_address],
                    ["x_studio_x_studio_record_category", "=", "Property"]
                ]],
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
    except:
        return None


def format_serial_id_for_odoo(serial_id):
    """Format Workiz SerialId as 6-digit string (e.g., 4111 -> 004111)."""
    try:
        return str(int(serial_id)).zfill(6)
    except:
        return str(serial_id)


def create_sales_order(contact_id, property_id, workiz_job_data, booking_datetime, order_name=""):
    """Create Odoo sales order with complete Workiz job details."""
    
    # Extract Workiz data
    workiz_uuid = workiz_job_data.get('UUID', '')
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', '')
    
    tags = workiz_job_data.get('Tags') or workiz_job_data.get('JobTags', '')
    gate_code_raw = workiz_job_data.get('GateCode') or workiz_job_data.get('gate_code') or workiz_job_data.get('Gate', '')
    pricing_raw = workiz_job_data.get('Pricing') or workiz_job_data.get('pricing') or workiz_job_data.get('PricingNote', '')
    job_notes = workiz_job_data.get('JobNotes') or workiz_job_data.get('Notes', '')
    info_to_remember = workiz_job_data.get('information_to_remember') or workiz_job_data.get('InformationToRemember', '')
    comments = workiz_job_data.get('Comments') or workiz_job_data.get('Comment', '')
    job_type = workiz_job_data.get('JobType') or workiz_job_data.get('Type', '')
    line_items_raw = workiz_job_data.get('LineItems', [])
    team_raw = workiz_job_data.get('Team') or workiz_job_data.get('team', '')
    
    # Filter placeholder text
    gate_code = gate_code_raw if gate_code_raw and gate_code_raw.lower() not in ['gate code', 'gate', ''] else ''
    pricing = pricing_raw if pricing_raw and pricing_raw.lower() not in ['pricing', 'price', 'pricing note', ''] else ''
    
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
            import ast
            line_items = ast.literal_eval(line_items_raw)
        except:
            line_items = []
    else:
        line_items = line_items_raw if isinstance(line_items_raw, list) else []
    
    # Convert Workiz line items to Odoo format with product lookup
    odoo_order_lines = []
    for item in line_items:
        if isinstance(item, dict):
            item_name = item.get('Name', 'Service')
            qty = float(item.get('Quantity', 1))
            price = float(item.get('Price', 0))
            
            product_id = search_odoo_product_by_name(item_name)
            
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
    
    # Build order data (WITHOUT date_order - will set AFTER confirmation)
    order_data = {
        "partner_id": contact_id,
        "partner_shipping_id": property_id,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_lead_source": "Calendly"
    }
    
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
    """Update sales order date_order field (Job/Schedule Date)."""
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


def update_property_fields(property_id, gate_code, pricing):
    """Update property's gate code and pricing fields."""
    if not gate_code and not pricing:
        return {'success': True, 'message': 'No property updates needed'}
    
    update_data = {}
    if gate_code:
        update_data["x_studio_x_gate_code"] = gate_code
    if pricing:
        update_data["x_studio_x_pricing"] = pricing
    
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


def process_phase3e(contact_id, property_id, opportunity, booking_info, won_result):
    """Phase 3E: Create sales order with full Workiz data + confirm + update property."""
    
    print("\n" + "="*70)
    print("PHASE 3E: CREATE SALES ORDER")
    print("="*70)
    
    if not won_result.get('success'):
        return {'success': False, 'sales_order_id': None, 'message': 'Opportunity not Won'}
    
    # Get Workiz job details
    workiz_job = get_workiz_job_details(opportunity['x_workiz_graveyard_uuid'])
    if not workiz_job:
        return {'success': False, 'sales_order_id': None, 'message': 'Could not fetch Workiz job'}
    
    # Get SerialId for order name
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id_for_odoo(serial_id) if serial_id else None
    
    # Extract gate code and pricing for property update
    gate_code = workiz_job.get('GateCode') or workiz_job.get('gate_code') or workiz_job.get('Gate') or workiz_job.get('information_to_remember', '')
    pricing = workiz_job.get('Pricing') or workiz_job.get('pricing') or workiz_job.get('PricingNote') or workiz_job.get('price_note', '')
    
    # Get JobDateTime from Workiz (Pacific time) and convert to UTC
    job_datetime_pacific = workiz_job.get('JobDateTime', '')
    
    if job_datetime_pacific:
        # Parse Pacific time (format: "2026-03-12 08:30:00")
        dt_naive = datetime.strptime(job_datetime_pacific, '%Y-%m-%d %H:%M:%S')
        
        # Convert Pacific to UTC (add 8 hours for PST or 7 hours for PDT)
        # Check if date is in PST (roughly Nov-March) or PDT (March-Nov)
        pacific_offset = timedelta(hours=8) if dt_naive.month in [11, 12, 1, 2] or (dt_naive.month == 3 and dt_naive.day < 10) else timedelta(hours=7)
        dt_utc = dt_naive + pacific_offset
        
        booking_datetime_for_odoo = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    else:
        booking_datetime_for_odoo = booking_info['booking_time'].replace('T', ' ').replace('Z', '').split('.')[0]
    
    # Create sales order
    so_result = create_sales_order(contact_id, property_id, workiz_job, booking_datetime_for_odoo, order_name)
    
    if not so_result['success']:
        return so_result
    
    print(f"[*] Note: Job/Schedule Date will be set AFTER confirmation to prevent Odoo from overriding it")
    
    # Confirm sales order (Quotation -> Sales Order)
    print(f"\n[*] Confirming sales order (Quotation -> Sales Order)...")
    confirm_result = confirm_sales_order(so_result['sales_order_id'])
    
    if confirm_result['success']:
        print(f"[OK] Sales order confirmed (now in Sales Order status)")
        
        # NOW update date_order to the correct JobDateTime (after confirmation)
        print(f"\n[*] Updating Job/Schedule Date (date_order) to: {booking_datetime_for_odoo}")
        update_date_result = update_sales_order_date(so_result['sales_order_id'], booking_datetime_for_odoo)
        
        if update_date_result['success']:
            print(f"[OK] Job/Schedule Date updated to: {booking_datetime_for_odoo}")
        else:
            print(f"[WARNING] Could not update date_order: {update_date_result.get('message', 'Unknown error')}")
    else:
        print(f"[WARNING] Could not confirm sales order: {confirm_result['message']}")
    
    # Update property with gate code and pricing
    update_property_fields(property_id, gate_code, pricing)
    
    return so_result

# ==============================================================================
# PHASE 3F: UPDATE CONTACT EMAIL
# ==============================================================================

def update_contact_email(contact_id, new_email):
    """Update Odoo contact email address."""
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
                [[contact_id], {"email": new_email}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Contact email updated!")
            return {'success': True}
        else:
            return {'success': False, 'message': 'Email update failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def process_phase3f(contact_id, booking_info):
    """Phase 3F: Update contact email from Calendly."""
    print("\n" + "="*70)
    print("PHASE 3F: UPDATE CONTACT EMAIL")
    print("="*70)
    
    new_email = booking_info.get('email', '')
    
    if not new_email:
        return {'success': False, 'message': 'No email provided'}
    
    return update_contact_email(contact_id, new_email)

# ==============================================================================
# MAIN ORCHESTRATOR - THIS IS WHAT ZAPIER WILL CALL
# ==============================================================================

def main(input_data):
    """
    Main function for Zapier "Code by Zapier" action.
    
    INPUT (input_data from Zapier):
    {
        "event_start_time": "2026-03-12T15:30:00.000000Z",
        "invitee_email": "customer@example.com",
        "invitee_name": "John Doe",
        "service_address": "123 Main St, City, CA 12345" (Question 1),
        "service_type_required": "Windows Inside & Outside Plus Screens" (Question 2),
        "additional_notes": "Please call before arriving" (Question 3)
    }
    
    OUTPUT (for Zapier):
    {
        "success": True/False,
        "sales_order_id": 12345,
        "message": "Success or error message"
    }
    """
    
    print("\n" + "="*70)
    print("PHASE 3 - CALENDLY TO ODOO INTEGRATION")
    print("="*70)
    
    # Parse booking data from Calendly custom questions
    booking_info = {
        'booking_time': input_data.get('event_start_time'),
        'service_type': input_data.get('service_type_required'),
        'additional_notes': input_data.get('additional_notes', ''),
        'email': input_data.get('invitee_email'),
        'name': input_data.get('invitee_name')
    }
    
    # Extract address from Question 1
    service_address = input_data.get('service_address', '')
    address_parts = service_address.split(',')
    street = address_parts[0].strip() if address_parts else ''
    
    if not street:
        return {'success': False, 'message': 'No service address provided'}
    
    # -------------------------------------------------------------------------
    # PHASE 3A: PROPERTY & CONTACT LOOKUP
    # -------------------------------------------------------------------------
    
    lookup_result = search_property_and_contact_by_address(street)
    
    if not lookup_result:
        return {'success': False, 'failed_at': 'Phase 3A', 'message': f'Property/Contact not found for address: {street}'}
    
    property_id = lookup_result['property_id']
    contact_id = lookup_result['contact_id']
    
    # -------------------------------------------------------------------------
    # PHASE 3B: OPPORTUNITY LOOKUP
    # -------------------------------------------------------------------------
    
    opportunity_result = find_opportunity_with_workiz_uuid(contact_id)
    
    if not opportunity_result['success']:
        return {'success': False, 'failed_at': 'Phase 3B', 'message': opportunity_result['message']}
    
    opportunity = opportunity_result['opportunity']
    
    # -------------------------------------------------------------------------
    # PHASE 3C: WORKIZ JOB UPDATE
    # -------------------------------------------------------------------------
    
    workiz_result = update_workiz_job(
        opportunity['x_workiz_graveyard_uuid'],
        booking_info['booking_time'],
        booking_info['service_type'],
        booking_info['additional_notes']
    )
    
    if not workiz_result['success']:
        return {'success': False, 'failed_at': 'Phase 3C', 'message': workiz_result['message']}
    
    # -------------------------------------------------------------------------
    # PHASE 3D: MARK OPPORTUNITY WON
    # -------------------------------------------------------------------------
    
    won_result = mark_opportunity_won(opportunity['id'])
    
    if not won_result['success']:
        return {'success': False, 'failed_at': 'Phase 3D', 'message': won_result['message']}
    
    # -------------------------------------------------------------------------
    # PHASE 3E: CREATE SALES ORDER
    # -------------------------------------------------------------------------
    
    so_result = process_phase3e(contact_id, property_id, opportunity, booking_info, won_result)
    
    if not so_result['success']:
        return {'success': False, 'failed_at': 'Phase 3E', 'message': so_result['message']}
    
    sales_order_id = so_result['sales_order_id']
    
    # -------------------------------------------------------------------------
    # PHASE 3F: UPDATE CONTACT EMAIL
    # -------------------------------------------------------------------------
    
    email_result = process_phase3f(contact_id, booking_info)
    
    if not email_result['success']:
        return {'success': False, 'failed_at': 'Phase 3F', 'message': email_result['message']}
    
    # -------------------------------------------------------------------------
    # SUCCESS
    # -------------------------------------------------------------------------
    
    print("\n" + "="*70)
    print("[OK] PHASE 3 - CALENDLY BOOKING COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'contact_id': contact_id,
        'property_id': property_id,
        'opportunity_id': opportunity['id'],
        'sales_order_id': sales_order_id,
        'message': 'Calendly booking integration completed successfully'
    }


# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================
output = main(input_data)
