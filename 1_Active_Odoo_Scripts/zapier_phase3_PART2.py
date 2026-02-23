# ==============================================================================
# ZAPIER PHASE 3 - PART 2 of 3
# ==============================================================================
# Helper Functions for Phase 3E
# Paste this after PART 1, then paste PART 3 after this
# ==============================================================================

def get_workiz_job_details(job_uuid):
    """Fetch complete Workiz job data."""
    url = f"{WORKIZ_BASE_URL}/job/get/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            job_data = response.json()
            return job_data
        return None
    except:
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
