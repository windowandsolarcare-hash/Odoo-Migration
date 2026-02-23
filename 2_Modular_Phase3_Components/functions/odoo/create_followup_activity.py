"""
Create follow-up activity in Odoo for On Demand customers
"""
import sys
sys.path.append('../..')
import requests
from datetime import datetime, timedelta
from config import *


def create_followup_activity(workiz_job, contact_id, days_until_followup=180):
    """
    Create Odoo activity for future follow-up (On Demand / On Request / Unknown).
    
    Args:
        workiz_job (dict): Completed Workiz job data
        contact_id (int): Contact ID in Odoo
        days_until_followup (int): Days from now until activity due (default 180 = 6 months)
        
    Returns:
        dict: {'success': bool, 'activity_id': int or None}
    """
    now = datetime.now()
    today = now.date()
    days_out = max(1, int(days_until_followup))
    followup_date = now + timedelta(days=days_out)
    days_to_sunday = 6 - followup_date.weekday()
    followup_date = followup_date + timedelta(days=days_to_sunday)
    if followup_date.date() <= today:
        followup_date = now + timedelta(days=days_out)
    due_date_str = followup_date.strftime('%Y-%m-%d')
    
    # Get customer info
    customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
    service_address = workiz_job.get('Address', '')
    last_service_date = workiz_job.get('JobDateTime', '')
    
    # Build list of services performed
    line_items = workiz_job.get('LineItems', [])
    services_performed = []
    for item in line_items:
        item_name = item.get('Name', '')
        if 'tip' not in item_name.lower():
            services_performed.append(item_name)
    
    services_text = ', '.join(services_performed) if services_performed else 'Service'
    
    # Build activity description (include due date so it matches the activity's date_deadline)
    description = f"""Follow-up with customer about next service visit.

Follow-up in {days_out} days (due {due_date_str}).
Last Service Date: {last_service_date}
Services Performed: {services_text}
Property: {service_address}

Action Required:
- Call or text customer to check on property condition
- Ask if they'd like to schedule next visit
- Update service frequency if needed

Workiz Job: {workiz_job.get('UUID', 'N/A')}"""
    
    # Create activity
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "mail.activity", "create",
                [{
                    "res_model": "res.partner",
                    "res_id": contact_id,
                    "activity_type_id": 2,  # TODO: Verify correct activity type ID in Odoo
                    "summary": f"Follow-up: {customer_name}",
                    "note": description,
                    "date_deadline": due_date_str,
                    "user_id": ODOO_USER_ID
                }]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        activity_id = result.get("result")
        
        if activity_id:
            print(f"[OK] Follow-up activity created: ID {activity_id}")
            print(f"[*] Customer: {customer_name}")
            print(f"[*] Due date: {followup_date.strftime('%Y-%m-%d')} (Sunday)")
            
            return {
                'success': True,
                'activity_id': activity_id,
                'due_date': followup_date.strftime('%Y-%m-%d')
            }
        else:
            error_msg = result.get("error", {}).get("data", {}).get("message", "Unknown error")
            print(f"[ERROR] Failed to create activity: {error_msg}")
            
            return {
                'success': False,
                'activity_id': None,
                'error': error_msg
            }
    
    except Exception as e:
        print(f"[ERROR] Exception creating activity: {e}")
        return {
            'success': False,
            'activity_id': None,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test (would need real contact_id and job data)
    print("This function requires live Odoo connection to test")
    print("See phase5b_router.py for integration testing")
