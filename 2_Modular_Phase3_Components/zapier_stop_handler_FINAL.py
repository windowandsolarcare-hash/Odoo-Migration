"""
WORKIZ STOP REQUEST HANDLER - ZAPIER WEBHOOK
Author: DJ Sanders
Date: 2026-03-08
GitHub: windowandsolarcare-hash/Odoo-Migration

PURPOSE:
When a customer replies "STOP" to any SMS sent via Workiz, this script:
1. Receives webhook from Workiz (trigger: incoming message contains "STOP")
2. Finds the Contact in Odoo by phone number
3. Sets is_blacklisted = True (marketing blacklist)
4. Logs the opt-out activity to their CRM Activity History

ZAPIER SETUP:
- Trigger: Workiz webhook (new message received, filter for "STOP")
- Action: Code by Zapier (Python)
- Input fields: customer_phone, message_body, workiz_job_id (optional)

USAGE IN ZAPIER:
import urllib.request
exec(urllib.request.urlopen('https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_stop_handler_FINAL.py').read().decode())
return main(input_data)
"""

import requests
import json

# Odoo credentials
ODOO_URL = "https://window-solar-care-migration-dj-sanders-main-15099858.dev.odoo.com"
ODOO_DB = "window-solar-care-migration-dj-sanders-main-15099858"
ODOO_USERNAME = "dj@asolarwindow.com"
ODOO_API_KEY = "c7c1ce77c3ac5b2a09c1d41d1891a3e35e2c3ca0"

def odoo_authenticate():
    """Authenticate with Odoo and return uid"""
    url = f"{ODOO_URL}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [ODOO_DB, ODOO_USERNAME, ODOO_API_KEY]
        },
        "id": 1
    }
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    result = response.json()
    return result.get("result")

def odoo_call(model, method, args=None, kwargs=None):
    """Execute Odoo API call"""
    uid = odoo_authenticate()
    url = f"{ODOO_URL}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, uid, ODOO_API_KEY, model, method, args or [], kwargs or {}]
        },
        "id": 2
    }
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    result = response.json()
    return result.get("result")

def main(input_data):
    """
    Main handler for STOP requests
    
    Expected input_data:
    {
        "customer_phone": "+15551234567",  # From Workiz webhook
        "message_body": "STOP",             # The actual message
        "workiz_job_id": "ABC123"           # Optional - for reference
    }
    """
    
    customer_phone = input_data.get('customer_phone', '')
    message_body = input_data.get('message_body', '')
    workiz_job_id = input_data.get('workiz_job_id', 'N/A')
    
    if not customer_phone:
        return {
            "status": "error",
            "message": "No phone number provided"
        }
    
    # Normalize phone number (remove formatting)
    phone_clean = ''.join(filter(str.isdigit, customer_phone))
    
    # Search for Contact by phone
    # Try multiple phone field formats
    contacts = odoo_call('res.partner', 'search_read', 
        args=[[
            '|', '|',
            ('phone', 'ilike', phone_clean[-10:]),  # Last 10 digits
            ('mobile', 'ilike', phone_clean[-10:]),
            ('phone', '=', customer_phone)
        ]],
        kwargs={'fields': ['name', 'phone', 'mobile', 'is_blacklisted'], 'limit': 1}
    )
    
    if not contacts:
        return {
            "status": "error",
            "message": f"Contact not found for phone: {customer_phone}",
            "phone_cleaned": phone_clean
        }
    
    contact = contacts[0]
    contact_id = contact['id']
    contact_name = contact['name']
    
    # Check if already blacklisted
    if contact.get('is_blacklisted'):
        return {
            "status": "already_blacklisted",
            "contact_id": contact_id,
            "contact_name": contact_name,
            "message": f"Contact {contact_name} was already blacklisted"
        }
    
    # Set is_blacklisted = True
    odoo_call('res.partner', 'write', args=[[contact_id], {'is_blacklisted': True}])
    
    # Log the opt-out activity
    activity_data = {
        "x_name": f"SMS Opt-Out Request",
        "x_activity_type": "opt_out",
        "x_description": f"Customer replied '{message_body}' to SMS. Blacklisted from future campaigns. Workiz Job: {workiz_job_id}",
        "x_contact_id": contact_id,
        "x_campaign_id": 1
    }
    
    odoo_call('x_crm_activity_log', 'create', args=[activity_data])
    
    return {
        "status": "success",
        "contact_id": contact_id,
        "contact_name": contact_name,
        "phone": customer_phone,
        "message": f"Contact {contact_name} blacklisted successfully",
        "workiz_job_id": workiz_job_id
    }

# For local testing
if __name__ == "__main__":
    test_data = {
        "customer_phone": "+15551234567",
        "message_body": "STOP",
        "workiz_job_id": "TEST123"
    }
    result = main(test_data)
    print(json.dumps(result, indent=2))
