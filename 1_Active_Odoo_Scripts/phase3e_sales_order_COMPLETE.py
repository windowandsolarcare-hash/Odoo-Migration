# ==============================================================================
# PHASE 3E: CREATE SALES ORDER (COMPLETE VERSION)
# ==============================================================================
# Purpose: Create Odoo sales order with full Workiz job details
# Created: 2026-02-05
# Status: Development - All Workiz fields included
# ==============================================================================

import requests
import json
from datetime import datetime, timedelta
import pytz

# ==============================================================================
# CONFIGURATION
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_BASE = "https://api.workiz.com/api/v1"
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"

# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

def get_workiz_job_details(job_uuid):
    """Get complete job details from Workiz including all snapshot fields."""
    url = f"{WORKIZ_API_BASE}/{WORKIZ_API_TOKEN}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    print(f"[*] Fetching Workiz job details for UUID: {job_uuid}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            response_json = response.json()
            job_data = response_json.get('data', {})
            
            if isinstance(job_data, list) and len(job_data) > 0:
                job_data = job_data[0]
            
            serial_id = job_data.get('SerialId', '')
            print(f"[OK] Job found - SerialId: {serial_id}")
            
            return job_data
        else:
            print(f"[ERROR] Workiz API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Error fetching Workiz job: {e}")
        return None


def format_serial_id_for_odoo(serial_id):
    """Pad Workiz SerialId with leading zeros (e.g., 4111 → 004111)."""
    serial_str = str(serial_id)
    padded = serial_str.zfill(6)
    print(f"[#] Serial ID formatted: {serial_id} -> {padded}")
    return padded


# ==============================================================================
# ODOO API FUNCTIONS
# ==============================================================================

def search_odoo_product_by_name(product_name):
    """
    Search for Odoo product by exact name match.
    Returns product_id if found, None otherwise.
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
    """
    Get tag names from a contact's category_id field.
    Returns list of tag names.
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
            # category_id is a list of [id, name] pairs
            category_data = result["result"][0].get("category_id", [])
            # Extract just the names
            tag_names = [tag[1] for tag in category_data if len(tag) > 1]
            return tag_names
        return []
    except Exception as e:
        print(f"      Error reading contact tags: {e}")
        return []


def get_sales_tag_ids(tag_names):
    """
    Get Odoo sales order tag IDs (crm.tag) for the given tag names.
    Tags can be a string or a list. Returns list of tag IDs.
    """
    if not tag_names:
        return []
    
    # Handle both string and list inputs
    if isinstance(tag_names, str):
        # Split by comma if it's a comma-separated string
        tags_list = [t.strip() for t in tag_names.split(',') if t.strip()]
    elif isinstance(tag_names, list):
        # Already a list, just clean it up
        tags_list = [str(t).strip() for t in tag_names if t]
    else:
        return []
    
    tag_ids = []
    
    for tag_name in tags_list:
        # Search for existing tag by name in crm.tag model
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
                print(f"      '{tag_name}': ID {tag_id}")
            else:
                print(f"      '{tag_name}': Not found in sales tags (skipping)")
        except Exception as e:
            print(f"      '{tag_name}': Error - {e}")
    
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


def create_sales_order(contact_id, property_id, workiz_job_data, booking_datetime, order_name=""):
    """
    Create Odoo sales order with complete Workiz job details.
    
    Includes all snapshot fields: Tags, Gate, Pricing, Notes
    """
    
    # DEBUG: Print ALL available keys to find correct field names
    print(f"\n[DEBUG] All Workiz keys available:")
    for key in sorted(workiz_job_data.keys()):
        value = workiz_job_data.get(key)
        # Show key and first 100 chars of value
        value_preview = str(value)[:100] if value else "(empty)"
        print(f"   {key}: {value_preview}")
    
    # Extract Workiz data (trying various possible field names)
    workiz_uuid = workiz_job_data.get('UUID', '')
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', '')
    
    # Try multiple possible field names for each
    tags = workiz_job_data.get('Tags') or workiz_job_data.get('JobTags', '')
    gate_code_raw = workiz_job_data.get('GateCode') or workiz_job_data.get('gate_code') or workiz_job_data.get('Gate', '')
    pricing_raw = workiz_job_data.get('Pricing') or workiz_job_data.get('pricing') or workiz_job_data.get('PricingNote', '')
    job_notes = workiz_job_data.get('JobNotes') or workiz_job_data.get('Notes', '')
    info_to_remember = workiz_job_data.get('information_to_remember') or workiz_job_data.get('InformationToRemember', '')
    comments = workiz_job_data.get('Comments') or workiz_job_data.get('Comment', '')
    job_type = workiz_job_data.get('JobType') or workiz_job_data.get('Type', '')
    line_items_raw = workiz_job_data.get('LineItems', [])
    team_raw = workiz_job_data.get('Team') or workiz_job_data.get('team', '')
    
    # Filter out placeholder text - only use real data
    gate_code = gate_code_raw if gate_code_raw and gate_code_raw.lower() not in ['gate code', 'gate', ''] else ''
    pricing = pricing_raw if pricing_raw and pricing_raw.lower() not in ['pricing', 'price', 'pricing note', ''] else ''
    
    # Process Team field - convert list/array to comma-separated string
    team_names = ""
    if team_raw:
        if isinstance(team_raw, list):
            # It's a list of dictionaries with 'Name' keys - extract just the names
            names = []
            for member in team_raw:
                if isinstance(member, dict):
                    name = member.get('Name') or member.get('name', '')
                    if name:
                        names.append(str(name).strip())
                elif member:
                    # It's just a plain name
                    names.append(str(member).strip())
            team_names = ", ".join(names)
        elif isinstance(team_raw, str):
            # It's a string - use as-is
            team_names = team_raw.strip()
    
    print(f"   Team (raw): {team_raw}")
    print(f"   Team (formatted): '{team_names}' {'[REAL DATA]' if team_names else '[EMPTY]'}")
    
    print(f"\n[*] Workiz data extracted:")
    print(f"   SubStatus: {workiz_substatus}")
    print(f"   Job Type: {job_type}")
    print(f"   Tags: {tags}")
    print(f"   Gate Code (raw): '{gate_code_raw}'")
    print(f"   Gate Code (filtered): '{gate_code}' {'[REAL DATA]' if gate_code else '[EMPTY/PLACEHOLDER]'}")
    print(f"   Pricing (raw): '{pricing_raw}'")
    print(f"   Pricing (filtered): '{pricing}' {'[REAL DATA]' if pricing else '[EMPTY/PLACEHOLDER]'}")
    print(f"   Job Notes: {len(job_notes) if job_notes else 0} chars")
    print(f"   Info to Remember: {len(info_to_remember) if info_to_remember else 0} chars")
    print(f"   Comments: {len(comments) if comments else 0} chars")
    print(f"   Line Items: {len(line_items_raw) if isinstance(line_items_raw, list) else 'Not a list'}")
    
    # Parse line items if they're JSON string
    if isinstance(line_items_raw, str):
        try:
            import ast
            line_items = ast.literal_eval(line_items_raw)
        except:
            line_items = []
    else:
        line_items = line_items_raw if isinstance(line_items_raw, list) else []
    
    # Convert Workiz line items to Odoo format (with product lookup)
    odoo_order_lines = []
    for item in line_items:
        if isinstance(item, dict):
            item_name = item.get('Name', 'Service')
            qty = float(item.get('Quantity', 1))
            price = float(item.get('Price', 0))
            
            # Search for matching Odoo product by name
            product_id = search_odoo_product_by_name(item_name)
            
            if product_id:
                # Product found - create proper line item with product_id
                line_data = {
                    'product_id': product_id,
                    'product_uom_qty': qty,
                    'price_unit': price
                }
                odoo_order_lines.append([0, 0, line_data])
                print(f"   - {item_name}: ${price} x {qty} (Product ID: {product_id})")
            else:
                # Product not found - skip this line item
                print(f"   - [SKIP] {item_name}: Product not found in Odoo")
    
    print(f"   Odoo order lines created: {len(odoo_order_lines)}")
    
    # Format notes snapshot - only include Job Notes and Comments
    # IMPORTANT: Remove all newlines within each section and replace with spaces
    notes_parts = []
    
    if job_notes and job_notes.strip():
        # Replace all newlines with spaces to keep everything on one line
        clean_notes = ' '.join(job_notes.strip().split())
        notes_parts.append(f"[Job Notes] {clean_notes}")
    
    if comments and comments.strip():
        # Replace all newlines with spaces to keep everything on one line
        clean_comments = ' '.join(comments.strip().split())
        notes_parts.append(f"[Comments] {clean_comments}")
    
    # Join with single space separator
    notes_snapshot = " ".join(notes_parts)
    
    if notes_snapshot:
        print(f"   [+] Notes snapshot created: {len(notes_snapshot)} chars")
    else:
        print(f"   [-] No notes data available")
    
    # Get tags from both Contact and Workiz, then combine them
    print(f"\n[*] Processing tags...")
    
    # Get contact's existing tags
    print(f"   [*] Reading contact tags...")
    contact_tag_names = get_contact_tag_names(contact_id)
    if contact_tag_names:
        print(f"      Contact has {len(contact_tag_names)} tag(s): {', '.join(contact_tag_names)}")
    else:
        print(f"      Contact has no tags")
    
    # Get Workiz tags (if any)
    workiz_tag_names = []
    if tags:
        if isinstance(tags, list):
            workiz_tag_names = [str(t).strip() for t in tags if t]
        elif isinstance(tags, str):
            workiz_tag_names = [t.strip() for t in tags.split(',') if t.strip()]
        
        if workiz_tag_names:
            print(f"      Workiz has {len(workiz_tag_names)} tag(s): {', '.join(workiz_tag_names)}")
        else:
            print(f"      Workiz has no tags")
    
    # Combine and deduplicate tag names
    all_tag_names = list(set(contact_tag_names + workiz_tag_names))
    
    if all_tag_names:
        print(f"   [*] Converting {len(all_tag_names)} unique tag(s) to sales order tags...")
        tag_ids = get_sales_tag_ids(all_tag_names)
        if tag_ids:
            print(f"   [+] Will add {len(tag_ids)} tag(s) to sales order")
        else:
            print(f"   [-] No matching sales tags found")
    else:
        tag_ids = []
        print(f"   [-] No tags to add")
    
    # Build order data (WITHOUT date_order - we'll set it AFTER confirmation)
    order_data = {
        "partner_id": contact_id,
        "partner_shipping_id": property_id,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_lead_source": "Calendly"
    }
    
    # Add tags if we have any (many2many relationship format)
    if tag_ids:
        order_data["tag_ids"] = [(6, 0, tag_ids)]
    
    # Add Job Type if available
    if job_type:
        order_data["x_studio_x_studio_x_studio_job_type"] = job_type
        print(f"   [+] Adding job type: '{job_type}'")
    
    # Add Team/Tech if available
    if team_names:
        order_data["x_studio_x_studio_workiz_tech"] = team_names
        print(f"   [+] Adding team/tech: '{team_names}'")
    
    # Only add gate/pricing snapshot if we have real data (not placeholders)
    if gate_code:
        order_data["x_studio_x_gate_snapshot"] = gate_code
        print(f"   [+] Adding gate snapshot: '{gate_code}'")
    else:
        print(f"   [-] Skipping gate snapshot (no real data)")
    
    if pricing:
        order_data["x_studio_x_studio_pricing_snapshot"] = pricing
        print(f"   [+] Adding pricing snapshot: '{pricing}'")
    else:
        print(f"   [-] Skipping pricing snapshot (no real data)")
    
    # Always add notes if available
    if notes_snapshot:
        order_data["x_studio_x_studio_notes_snapshot1"] = notes_snapshot
    
    # Add line items
    if odoo_order_lines and len(odoo_order_lines) > 0:
        order_data["order_line"] = odoo_order_lines
    
    if order_name:
        order_data["name"] = order_name
    
    print(f"\n[*] Creating sales order...")
    print(f"   Order Name: {order_name or 'Auto-generated'}")
    print(f"   Contact ID: {contact_id}")
    print(f"   Property ID: {property_id}")
    print(f"   Workiz UUID: {workiz_uuid}")
    print(f"   Job/Schedule Date (will be set after confirmation): {booking_datetime}")
    print(f"   Lead Source: Calendly")
    print(f"   Workiz SubStatus: {workiz_substatus}")
    print(f"   Job Type: {job_type or 'None'}")
    print(f"   Team/Tech: {team_names or 'None'}")
    print(f"   Gate Code: {gate_code or 'None'}")
    print(f"   Pricing: {pricing or 'None'}")
    print(f"   Tags: {tags or 'None'}")
    print(f"   Line Items: {len(odoo_order_lines)}")
    
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
            return {'success': True, 'sales_order_id': sales_order_id, 'booking_datetime': booking_datetime, 'message': f"Sales order {sales_order_id} created"}
        else:
            error = result.get("error", {})
            print(f"[ERROR] Error: {error}")
            return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': f"Error: {error.get('message', 'Unknown')}"}
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': f"Exception: {str(e)}"}


def read_sales_order_status(sales_order_id):
    """Read the current status of a sales order."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "read", [[sales_order_id]], {"fields": ["state"]}]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0].get("state")
        return None
    except:
        return None


def confirm_sales_order(sales_order_id):
    """Convert Quotation to Sales Order using action_confirm."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "action_confirm", [[sales_order_id]]]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        # Debug: print what Odoo returned
        print(f"   [DEBUG] Odoo response: {result}")
        
        if result.get("result") is not None:
            print(f"[OK] Sales order confirmed (Quotation -> Sales Order)")
            return {'success': True, 'message': 'Sales order confirmed'}
        elif result.get("error"):
            error_msg = result["error"].get("data", {}).get("message", str(result["error"]))
            print(f"[ERROR] Odoo error: {error_msg}")
            return {'success': False, 'message': error_msg}
        else:
            print(f"[ERROR] Unexpected response from Odoo")
            return {'success': False, 'message': 'Unexpected response'}
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return {'success': False, 'message': str(e)}


def update_property_fields(property_id, gate_code, pricing_note):
    """
    Update property record with gate code and pricing note.
    Only updates if real data is provided (not placeholder text).
    """
    update_data = {}
    
    # Only update if we have real data (not empty, not placeholder text)
    if gate_code and gate_code.lower() not in ['gate code', 'gate', '']:
        update_data["x_studio_x_gate_code"] = gate_code
        print(f"[*] Will update property gate code: '{gate_code}'")
    else:
        print(f"[*] Skipping property gate code (no real data)")
    
    if pricing_note and pricing_note.lower() not in ['pricing', 'price', 'pricing note', '']:
        update_data["x_studio_x_pricing"] = pricing_note
        print(f"[*] Will update property pricing: '{pricing_note}'")
    else:
        print(f"[*] Skipping property pricing (no real data)")
    
    if not update_data:
        print(f"[OK] No property updates needed (no real gate/pricing data)")
        return {'success': True, 'message': 'No property updates needed'}
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "res.partner", "write", [[property_id], update_data]]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") == True:
            print(f"[OK] Property updated successfully")
            return {'success': True, 'message': 'Property updated'}
        else:
            return {'success': False, 'message': 'Property update failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


# ==============================================================================
# PHASE 3E MAIN FUNCTION
# ==============================================================================

def process_phase3e(contact, opportunity, booking_info, won_result):
    """
    Phase 3E: Create sales order with full Workiz data + confirm + update property.
    """
    
    print("\n" + "="*70)
    print("PHASE 3E: CREATE SALES ORDER")
    print("="*70)
    
    # Validate won
    if not won_result.get('success'):
        return {'success': False, 'sales_order_id': None, 'message': 'Opportunity not Won'}
    
    # Get property
    property_id = get_property_for_contact(contact['street'])
    if not property_id:
        property_id = contact['id']
    
    # Get Workiz job details
    workiz_job = get_workiz_job_details(opportunity['x_workiz_graveyard_uuid'])
    if not workiz_job:
        return {'success': False, 'sales_order_id': None, 'message': 'Could not fetch Workiz job'}
    
    # Get SerialId for order name
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id_for_odoo(serial_id) if serial_id else None
    
    # Extract gate code and pricing ONCE with multiple fallbacks
    gate_code = workiz_job.get('GateCode') or workiz_job.get('gate_code') or workiz_job.get('Gate') or workiz_job.get('information_to_remember', '')
    pricing = workiz_job.get('Pricing') or workiz_job.get('pricing') or workiz_job.get('PricingNote') or workiz_job.get('price_note', '')
    
    print(f"[*] Extracted for property update:")
    print(f"   Gate Code: '{gate_code}'")
    print(f"   Pricing: '{pricing}'")
    
    # Get JobDateTime from Workiz (this is the scheduled date/time for the job in Pacific time)
    job_datetime_pacific = workiz_job.get('JobDateTime', '')
    print(f"[*] Job DateTime from Workiz (Pacific): {job_datetime_pacific}")
    
    # Convert Pacific time to UTC for Odoo
    if job_datetime_pacific:
        # Parse the Workiz datetime (format: 2026-03-12 08:30:00)
        pacific = pytz.timezone('America/Los_Angeles')
        utc = pytz.UTC
        
        # Parse as naive datetime, then localize to Pacific
        dt_naive = datetime.strptime(job_datetime_pacific, '%Y-%m-%d %H:%M:%S')
        dt_pacific = pacific.localize(dt_naive)
        
        # Convert to UTC
        dt_utc = dt_pacific.astimezone(utc)
        
        # Format for Odoo (YYYY-MM-DD HH:MM:SS in UTC)
        booking_datetime_for_odoo = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"[*] Time conversion:")
        print(f"   Pacific: {job_datetime_pacific}")
        print(f"   UTC:     {booking_datetime_for_odoo}")
    else:
        # Fallback to Calendly booking time if JobDateTime not available (already in UTC)
        booking_datetime_for_odoo = booking_info['booking_time'].replace('T', ' ').replace('Z', '').split('.')[0]
        print(f"[*] Using Calendly booking time (UTC): {booking_datetime_for_odoo}")
    
    # Create sales order (pass the extracted values)
    so_result = create_sales_order(contact['id'], property_id, workiz_job, booking_datetime_for_odoo, order_name)
    
    if not so_result['success']:
        return so_result
    
    print(f"[*] Note: Job/Schedule Date will be set AFTER confirmation to prevent Odoo from overriding it")
    
    # Confirm sales order (Quotation -> Sales Order)
    print(f"\n[*] Confirming sales order (Quotation -> Sales Order)...")
    confirm_result = confirm_sales_order(so_result['sales_order_id'])
    
    if confirm_result['success']:
        print(f"[OK] Sales order confirmed (now in Sales Order status)")
        
        # Verify the status changed
        verify_status = read_sales_order_status(so_result['sales_order_id'])
        if verify_status:
            print(f"[VERIFY] Actual status in Odoo: {verify_status}")
        
        # NOW update date_order to the correct JobDateTime (after confirmation)
        print(f"\n[*] Updating Job/Schedule Date (date_order) to: {booking_datetime_for_odoo}")
        update_date_payload = {
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
                    [[so_result['sales_order_id']], {"date_order": booking_datetime_for_odoo}]
                ]
            }
        }
        
        try:
            date_response = requests.post(ODOO_URL, json=update_date_payload, timeout=10)
            date_result = date_response.json()
            
            if date_result.get("result"):
                print(f"[OK] Job/Schedule Date updated to: {booking_datetime_for_odoo}")
                
                # Verify the update
                verify_date_payload = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "service": "object",
                        "method": "execute_kw",
                        "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "read", [[so_result['sales_order_id']]], {"fields": ["date_order"]}]
                    }
                }
                verify_date_response = requests.post(ODOO_URL, json=verify_date_payload, timeout=10)
                verify_date_result = verify_date_response.json()
                
                if verify_date_result.get("result"):
                    final_date = verify_date_result["result"][0].get("date_order")
                    print(f"[VERIFY] Final date_order in Odoo: {final_date}")
            else:
                print(f"[WARNING] Could not update date_order: {date_result.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"[WARNING] Exception updating date_order: {e}")
    else:
        print(f"[WARNING] Could not confirm sales order: {confirm_result['message']}")
    
    # Update property with gate code and pricing (use extracted values)
    update_property_fields(property_id, gate_code, pricing)
    
    return so_result


# ==============================================================================
# TEST
# ==============================================================================

if __name__ == "__main__":
    
    test_contact = {'id': 23629, 'name': 'Bev Hartin', 'street': '29 Toscana Way E', 'city': 'Rancho Mirage'}
    test_opportunity = {'id': 41, 'x_workiz_graveyard_uuid': 'SG6AMX'}
    test_booking_info = {'booking_time': '2026-03-12T15:30:00.000000Z', 'service_type': 'Windows Inside & Outside Plus Screens'}
    test_won_result = {'success': True}
    
    result = process_phase3e(test_contact, test_opportunity, test_booking_info, test_won_result)
    
    print("\n" + "="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result.get('sales_order_id'):
        print(f"Sales Order ID: {result['sales_order_id']}")
    print("="*70)
