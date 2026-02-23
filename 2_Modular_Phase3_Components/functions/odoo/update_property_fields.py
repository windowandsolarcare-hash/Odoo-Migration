"""Update property's gate code and pricing fields"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def update_property_fields(property_id, gate_code=None, pricing=None, last_visit_date=None, job_notes=None, comments=None, frequency=None, alternating=None, type_of_service=None):
    """
    Update property's gate code, pricing, last visit date, notes, and service details.
    
    Args:
        property_id (int): Odoo property ID
        gate_code (str, optional): Gate code to update
        pricing (str, optional): Pricing information to update
        last_visit_date (str, optional): Last property visit date (format: YYYY-MM-DD)
        job_notes (str, optional): Job notes from Workiz
        comments (str, optional): Comments from Workiz
        frequency (str, optional): Service frequency (e.g., "4 Months")
        alternating (int/str, optional): Alternating service (1/0 or "Yes"/"No")
        type_of_service (str, optional): Type of service (e.g., "Maintenance")
    
    Returns:
        dict: {'success': bool, 'message': str (optional)}
    """
    # print(f"[DEBUG] update_property_fields called with: property_id={property_id}, gate_code='{gate_code}', pricing='{pricing}', last_visit={last_visit_date}")
    
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
