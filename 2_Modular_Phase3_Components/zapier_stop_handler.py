"""
STOP COMPLIANCE HANDLER
Author: DJ Sanders
Date: 2026-03-16

Triggered by: Workiz webhook (via Zapier) when job status = "STOP - Do not Call or Text"
Purpose: Blacklist phone number + Update contact to "Do not Contact"

Input from Zapier:
- client_id: Workiz client serial ID
- phone: Primary phone number
"""

import requests
import json

# Odoo credentials
ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

def odoo_call(model, method, domain=None, fields=None, values=None):
    """Generic Odoo JSON-RPC call"""
    args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method]
    
    if domain is not None:
        args.append(domain)
    if fields is not None:
        args.append({"fields": fields})
    if values is not None:
        args.append(values)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": args
        },
        "id": 1
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=30)
    result = response.json()
    
    if "error" in result:
        raise Exception(f"Odoo API Error: {result['error']}")
    
    return result.get("result")

def format_e164(phone):
    """Format phone to E.164"""
    digits = ''.join(filter(str.isdigit, str(phone)))
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+{digits}"
    else:
        return phone

def blacklist_phone(phone):
    """Add phone to Odoo phone blacklist"""
    e164_phone = format_e164(phone)
    
    # Check if already blacklisted
    existing = odoo_call(
        "phone.blacklist", 
        "search_read",
        [[["number", "=", e164_phone]]],
        ["id"]
    )
    
    if not existing:
        # Create blacklist record - values must be passed as a list
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    "phone.blacklist", "create",
                    [{"number": e164_phone}]
                ]
            },
            "id": 1
        }
        response = requests.post(ODOO_URL, json=payload, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Odoo API Error: {result['error']}")
        
        return f"Blacklisted {e164_phone}"
    else:
        return f"{e164_phone} already blacklisted"

def update_contact_status(client_id):
    """Find contact by client_id and update to 'Do not Contact'"""
    # Search by ref field (client serial ID)
    contacts = odoo_call(
        "res.partner",
        "search_read",
        [[["ref", "=", str(client_id)]]],
        ["id", "name"]
    )
    
    if contacts:
        contact = contacts[0]
        contact_id = contact["id"]
        contact_name = contact["name"]
        
        # Update Active/Lead field - write requires [ids], values
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    "res.partner", "write",
                    [[contact_id], {"x_studio_activelead": "do_not_contact"}]
                ]
            },
            "id": 1
        }
        response = requests.post(ODOO_URL, json=payload, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Odoo API Error: {result['error']}")
        
        return f"Updated {contact_name} to 'Do not Contact'"
    else:
        return f"Contact not found (client_id={client_id})"

# Main execution
client_id = input_data.get("client_id", "")
phone = input_data.get("phone", "")

if not client_id or not phone:
    output = {
        "status": "error",
        "message": f"Missing data: client_id={client_id}, phone={phone}"
    }
else:
    try:
        # 1. Blacklist phone
        blacklist_result = blacklist_phone(phone)
        
        # 2. Update contact status
        contact_result = update_contact_status(client_id)
        
        output = {
            "status": "success",
            "blacklist": blacklist_result,
            "contact": contact_result,
            "client_id": client_id,
            "phone": phone
        }
    except Exception as e:
        output = {
            "status": "error",
            "message": str(e),
            "client_id": client_id,
            "phone": phone
        }
