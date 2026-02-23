"""
Create next maintenance job in Workiz
"""
import sys
sys.path.append('../..')
import requests
from config import *


def create_next_maintenance_job(completed_job_data, scheduled_datetime, line_items_text):
    """
    Create new maintenance job in Workiz for next service.
    
    NOTE: LineItems cannot be added via API - they must be added manually.
    We store the pricing reference in a custom field instead.
    
    Args:
        completed_job_data (dict): Data from completed Workiz job
        scheduled_datetime (str): Next service date/time (format: 'YYYY-MM-DD HH:MM:SS')
        line_items_text (str): Formatted line items for custom field reference
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    # Format the line items reference with context
    line_items_reference = f"""AUTO-SCHEDULED - Next {completed_job_data.get('frequency', '3 Months')} service

Previous Job UUID: {completed_job_data.get('UUID')}

LINE ITEMS TO ADD:
{line_items_text}"""
    
    # Build new job payload
    new_job_data = {
        'auth_secret': WORKIZ_AUTH_SECRET,
        
        # Required fields
        'ClientId': completed_job_data.get('ClientId'),
        'FirstName': completed_job_data.get('FirstName'),
        'LastName': completed_job_data.get('LastName'),
        'Address': completed_job_data.get('Address'),
        'City': completed_job_data.get('City'),
        'State': completed_job_data.get('State', 'CA'),
        'PostalCode': completed_job_data.get('PostalCode'),
        'Phone': completed_job_data.get('Phone'),
        'JobDateTime': scheduled_datetime,
        'JobType': completed_job_data.get('JobType'),
        
        # Custom fields (Workiz expects strings for these)
        'frequency': str(completed_job_data.get('frequency') or ''),
        'alternating': str(completed_job_data.get('alternating') or ''),
        'type_of_service': str(completed_job_data.get('type_of_service') or 'Maintenance'),
        'gate_code': str(completed_job_data.get('gate_code') or ''),
        'pricing': str(completed_job_data.get('pricing') or ''),
        
        # LINE ITEMS REFERENCE (with context) - adjust field name to match your Workiz custom field
        'next_job_line_items': line_items_reference,
        
        # Job notes - preserve from previous job
        'JobNotes': str(completed_job_data.get('JobNotes') or '')
    }
    
    # Add optional fields only if they have valid values
    email = completed_job_data.get('Email', '')
    if email:
        new_job_data['Email'] = email
    
    second_phone = completed_job_data.get('SecondPhone', '')
    if second_phone:
        new_job_data['SecondPhone'] = second_phone
    
    unit = completed_job_data.get('Unit', '')
    if unit:
        new_job_data['Unit'] = unit
    
    job_source = completed_job_data.get('JobSource', '')
    if job_source:
        new_job_data['JobSource'] = job_source
    
    create_url = f'{WORKIZ_BASE_URL}/job/create/'
    
    print(f"[*] Creating job for {new_job_data['FirstName']} {new_job_data['LastName']}")
    
    # NOTE: Team and Tags are NOT included in create payload per Workiz API:
    # - Team: Must be assigned via /job/assign/ endpoint after creation
    # - Tags: Can only be updated via /job/update/ endpoint after creation
    
    try:
        response = requests.post(create_url, json=new_job_data, timeout=10)
        
        # Workiz can return either:
        # - HTTP 204 (No Content) on success
        # - HTTP 200 with JSON {"flag": true, "msg": "Created Job"}
        if response.status_code == 204:
            print("[OK] Job created successfully (HTTP 204)")
            return {'success': True, 'message': 'Job created'}
        
        elif response.status_code == 200:
            try:
                result = response.json()
                
                # Check if it's a success response
                if result.get('flag') == True or 'created' in result.get('msg', '').lower():
                    print(f"[OK] Job created successfully (HTTP 200): {result.get('msg')}")
                    return {'success': True, 'message': result.get('msg', 'Job created')}
                else:
                    # It's an error response
                    return {'success': False, 'message': result.get('msg'), 'details': result.get('details')}
            except:
                return {'success': False, 'message': f"HTTP 200 but invalid JSON"}
        
        else:
            # Other status codes
            try:
                error_result = response.json()
                return {'success': False, 'message': error_result.get('msg'), 'details': error_result.get('details')}
            except:
                return {'success': False, 'message': f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


if __name__ == "__main__":
    # Test with sample data
    test_job = {
        'UUID': 'TEST123',
        'ClientId': '31677',
        'FirstName': 'Test',
        'LastName': 'Customer',
        'Address': '123 Test St',
        'City': 'Palm Springs',
        'State': 'CA',
        'PostalCode': '92262',
        'Phone': '7605551234',
        'JobType': 'Windows Inside & Outside Plus Screens',
        'frequency': '3 Months',
        'type_of_service': 'Maintenance',
        'gate_code': '1234',
        'pricing': '150/85'
    }
    
    test_datetime = '2026-05-15 10:00:00'
    test_line_items = "Windows In & Out: $150\nSolar Panels: $45"
    
    result = create_next_maintenance_job(test_job, test_datetime, test_line_items)
    print("\nResult:")
    print(result)
