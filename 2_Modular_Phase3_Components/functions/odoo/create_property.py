"""Create new Property linked to Contact in Odoo"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def create_property(contact_id, service_address, workiz_job, location_id=None):
    """
    Create new Property linked to Contact in Odoo.
    
    Args:
        contact_id (int): Parent contact ID
        service_address (str): Service address (becomes the Property name)
        workiz_job (dict): Full Workiz job data for address details
        location_id (int): Workiz Location ID (optional)
    
    Returns:
        int: New property ID or None if failed
    """
    # Extract full address details from Workiz
    city = workiz_job.get('City', '')
    zip_code = workiz_job.get('PostalCode', '')
    
    # Extract service details
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    property_data = {
        "name": service_address.strip(),  # Property NAME = Service Address
        "street": service_address.strip(),
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
