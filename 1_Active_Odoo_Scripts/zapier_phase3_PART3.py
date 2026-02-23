# ==============================================================================
# ZAPIER PHASE 3 - PART 3 of 4
# ==============================================================================
# Create Sales Order Function
# Paste this after PART 2, then paste PART 4 after this
# ==============================================================================

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
    
    # Format notes snapshot - remove all newlines
    notes_parts = []
    
    if job_notes and job_notes.strip():
        clean_notes = ' '.join(job_notes.strip().split())
        notes_parts.append(f"[Job Notes] {clean_notes}")
    
    if comments and comments.strip():
        clean_comments = ' '.join(comments.strip().split())
        notes_parts.append(f"[Comments] {clean_comments}")
    
    notes_snapshot = " ".join(notes_parts)
    
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
