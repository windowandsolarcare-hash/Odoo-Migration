"""Create Odoo sales order with complete Workiz job details"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.odoo.search_product_by_name import search_product_by_name
from functions.odoo.get_contact_tag_names import get_contact_tag_names
from functions.odoo.get_sales_tag_ids import get_sales_tag_ids
from functions.odoo.get_selection_values import get_selection_values


def create_sales_order(contact_id, property_id, workiz_job_data, booking_datetime, order_name=""):
    """
    Create Odoo sales order with complete Workiz job details.
    
    Args:
        contact_id (int): Odoo contact ID
        property_id (int): Odoo property ID
        workiz_job_data (dict): Complete Workiz job data
        booking_datetime (str): Booking date/time in UTC format "YYYY-MM-DD HH:MM:SS"
        order_name (str, optional): Order name (formatted SerialId)
    
    Returns:
        dict: {'success': bool, 'sales_order_id': int, 'booking_datetime': str, 'message': str (optional)}
    """
    
    # Extract Workiz data
    workiz_uuid = workiz_job_data.get('UUID', '')
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', '') or workiz_job_data.get('Status', '')
    job_source = workiz_job_data.get('JobSource', '')  # Lead source from Workiz
    
    tags = workiz_job_data.get('Tags') or workiz_job_data.get('JobTags', '')
    gate_code_raw = workiz_job_data.get('GateCode') or workiz_job_data.get('gate_code') or workiz_job_data.get('Gate', '')
    pricing_raw = workiz_job_data.get('Pricing') or workiz_job_data.get('pricing') or workiz_job_data.get('PricingNote', '')
    job_notes = str(workiz_job_data.get('JobNotes') or workiz_job_data.get('Notes') or '')
    info_to_remember = workiz_job_data.get('information_to_remember') or workiz_job_data.get('InformationToRemember', '')
    comments = str(workiz_job_data.get('Comments') or workiz_job_data.get('Comment') or '')
    job_type = workiz_job_data.get('JobType') or workiz_job_data.get('Type', '')
    frequency = workiz_job_data.get('frequency', '') or workiz_job_data.get('Frequency', '')
    type_of_service = workiz_job_data.get('type_of_service', '') or workiz_job_data.get('TypeOfService', '')
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
            
            product_id = search_product_by_name(item_name)
            
            if product_id:
                line_data = {
                    'product_id': product_id,
                    'product_uom_qty': qty,
                    'price_unit': price
                }
                odoo_order_lines.append([0, 0, line_data])
    
    # Mirror Workiz: no default line when Workiz has no line items.
    
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
    
    # Build order data (WITHOUT date_order - will set AFTER confirmation)
    # Property as brain: customer on SO = Property (partner_id). Contact remains linked via Property.parent_id.
    order_data = {
        "partner_id": property_id,
        "partner_shipping_id": property_id,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_lead_source": job_source
    }
    
    # Add tags if any
    if tag_ids:
        order_data["tag_ids"] = [(6, 0, tag_ids)]
    
    # Add Job Type only if it is an allowed value in Odoo (selection field)
    JOB_TYPE_FIELD = "x_studio_x_studio_x_studio_job_type"
    if job_type:
        allowed = get_selection_values("sale.order", JOB_TYPE_FIELD)
        if allowed and job_type in allowed:
            order_data[JOB_TYPE_FIELD] = job_type
        elif allowed:
            print(f"[INFO] Job type '{job_type}' not in Odoo — add '{job_type}' to the Job Type field in Odoo to sync it; omitting for this create.")
    
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
    
    # Frequency and type of service on SO (Selection in Odoo = only write if value allowed)
    # Odoo Selection values: Frequency = 3 Months, 4 Months, 6 Months, 12 Months, Unknown
    #                        Type of Service = Maintenance, On Request, Unknown
    SO_FREQ_FIELD = "x_studio_x_studio_frequency_so"
    SO_TOS_FIELD = "x_studio_x_studio_type_of_service_so"
    if frequency:
        freq_val = str(frequency).strip()
        allowed_freq = get_selection_values("sale.order", SO_FREQ_FIELD)
        if not allowed_freq or freq_val in allowed_freq:
            order_data[SO_FREQ_FIELD] = freq_val
        elif allowed_freq:
            print(f"[INFO] Frequency '{freq_val}' not in Odoo selection — add it to {SO_FREQ_FIELD}; omitting.")
    if type_of_service:
        tos_val = str(type_of_service).strip()
        allowed_tos = get_selection_values("sale.order", SO_TOS_FIELD)
        if not allowed_tos or tos_val in allowed_tos:
            order_data[SO_TOS_FIELD] = tos_val
        elif allowed_tos:
            print(f"[INFO] Type of service '{tos_val}' not in Odoo selection — add it to {SO_TOS_FIELD}; omitting.")
    
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
            err = result.get("error", {})
            msg = err.get("message", "Unknown")
            data = err.get("data", {})
            if isinstance(data, dict):
                # Odoo often puts validation/traceback in data.message or data.debug
                detail = data.get("message") or data.get("debug") or data.get("name")
                if detail:
                    msg = f"{msg} | {detail}"
            elif isinstance(data, str):
                msg = f"{msg} | {data}"
            print(f"[ERROR] Odoo create failed: {msg}")
            return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': msg}
    except Exception as e:
        return {'success': False, 'sales_order_id': None, 'booking_datetime': None, 'message': f"Exception: {str(e)}"}
