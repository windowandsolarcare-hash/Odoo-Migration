"""Create new Contact in Odoo with all relevant fields from Workiz"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def create_contact(customer_name, client_id, workiz_job):
    """
    Create new Contact in Odoo with all relevant fields from Workiz.
    
    Args:
        customer_name (str): Customer name (FirstName + LastName)
        client_id (int): Workiz ClientId (REQUIRED - stored in 'ref' field)
        workiz_job (dict): Full Workiz job data
    
    Returns:
        int: New contact ID or None if failed
    """
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
