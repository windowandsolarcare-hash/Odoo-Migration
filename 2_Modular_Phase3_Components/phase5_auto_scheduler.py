"""
PHASE 5: Automated Job Scheduling Router
=========================================
Triggered by: Phase 4 after job marked "Done"

Two Paths:
- MAINTENANCE: Create next scheduled job in Workiz
- ON DEMAND: Create follow-up reminder in Odoo
"""
import sys
sys.path.append('.')

# Import utility functions
from functions.utils.calculate_next_service_date import calculate_next_service_date
from functions.utils.get_line_items_for_next_job import (
    get_line_items_for_next_job, 
    format_line_items_for_custom_field
)

# Import Workiz functions
from functions.workiz.get_job_details import get_job_details
from functions.workiz.create_next_maintenance_job import create_next_maintenance_job

# Import Odoo functions
from functions.odoo.create_followup_activity import create_followup_activity
from functions.odoo.search_all_sales_orders_for_property import search_all_sales_orders_for_property


# ==============================================================================
# PHASE 5A: MAINTENANCE PATH
# ==============================================================================

def schedule_next_maintenance_job(workiz_job, property_id, customer_city):
    """
    Create next maintenance job in Workiz.
    
    Args:
        workiz_job (dict): Completed Workiz job data
        property_id (int): Property ID in Odoo (for job history lookup)
        customer_city (str): Customer's city for route-based scheduling
        
    Returns:
        dict: Result of job creation
    """
    print("\n" + "="*70)
    print("PHASE 5A: MAINTENANCE AUTO-SCHEDULER")
    print("="*70)
    
    # Step 1: Calculate next service date
    frequency = workiz_job.get('frequency', '3 Months')
    print(f"\n[*] Service frequency: {frequency}")
    
    scheduled_datetime = calculate_next_service_date(frequency, customer_city)
    print(f"[OK] Next service scheduled for: {scheduled_datetime}")
    
    # Step 2: Get line items for next job (handles alternating logic)
    line_items = get_line_items_for_next_job(workiz_job, property_id)
    
    # Format line items for custom field
    line_items_text = format_line_items_for_custom_field(line_items)
    print(f"\n[*] Line items reference:\n{line_items_text}")
    
    # Step 3: Create new job in Workiz
    print(f"\n[*] Creating next maintenance job in Workiz...")
    result = create_next_maintenance_job(workiz_job, scheduled_datetime, line_items_text)
    
    if result['success']:
        print("[OK] Next maintenance job created!")
        print("    User will need to:")
        print("    1. Add line items manually in Workiz UI")
        print("    2. Set status to 'Send Next Job - Text'")
    else:
        print(f"[ERROR] Failed to create job: {result['message']}")
    
    print("="*70)
    return result


# ==============================================================================
# PHASE 5B: ON DEMAND PATH
# ==============================================================================

def create_ondemand_followup(workiz_job, contact_id, days_until_followup=180):
    """
    Create follow-up reminder activity in Odoo (no Workiz job).
    
    Args:
        workiz_job (dict): Completed Workiz job data
        contact_id (int): Contact ID in Odoo
        days_until_followup (int): 180 = 6 months default (On Demand / Unknown / On Request)
    """
    print("\n" + "="*70)
    print("PHASE 5B: FOLLOW-UP REMINDER (no Workiz job)")
    print("="*70)
    
    customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
    print(f"\n[*] Creating follow-up reminder for: {customer_name}")
    print(f"[*] Due in {days_until_followup} days (Sunday of that week)")
    
    result = create_followup_activity(workiz_job, contact_id, days_until_followup=days_until_followup)
    
    if result['success']:
        print(f"[OK] Follow-up reminder created!")
        print(f"    Activity ID: {result['activity_id']}")
        print(f"    Due: {result['due_date']} (Sunday)")
        print("    NO job created in Workiz (keeps schedule clean)")
    else:
        print(f"[ERROR] Failed to create reminder: {result.get('error')}")
    
    print("="*70)
    return result


# ==============================================================================
# MAIN ROUTER
# ==============================================================================

def main(input_data):
    """
    Phase 5 Main Router: Auto-schedule next job or create reminder.
    
    Expected to be called from Phase 4 after job marked "Done".
    
    Input data from Phase 4:
    {
        'workiz_job': {...},      # Full Workiz job data
        'property_id': 12345,     # Odoo property ID
        'contact_id': 67890,      # Odoo contact ID
        'customer_city': 'Palm Springs'
    }
    """
    print("\n" + "="*70)
    print("PHASE 5: AUTO-SCHEDULER")
    print("="*70)
    
    # Extract input
    workiz_job = input_data.get('workiz_job')
    property_id = input_data.get('property_id')
    contact_id = input_data.get('contact_id')
    customer_city = input_data.get('customer_city', '')
    
    if not workiz_job:
        return {'success': False, 'error': 'Missing workiz_job data'}
    
    # Check service type
    type_of_service = workiz_job.get('type_of_service', '').lower()
    
    print(f"\n[*] Service Type: {type_of_service}")
    
    # Route based on service type
    if 'maintenance' in type_of_service:
        # FORK 1: Maintenance - create next scheduled job
        if not property_id or not customer_city:
            return {'success': False, 'error': 'Missing property_id or customer_city for maintenance scheduling'}
        
        result = schedule_next_maintenance_job(workiz_job, property_id, customer_city)
        return {
            'success': result['success'],
            'path': '5A_maintenance',
            'result': result
        }
    
    elif 'on demand' in type_of_service or 'on-demand' in type_of_service:
        # FORK 2: On Demand - create follow-up reminder (6 months)
        if not contact_id:
            return {'success': False, 'error': 'Missing contact_id for follow-up reminder'}
        result = create_ondemand_followup(workiz_job, contact_id, days_until_followup=180)
        return {'success': result['success'], 'path': '5B_ondemand', 'result': result}
    
    elif 'on request' in type_of_service or 'unknown' in type_of_service or not type_of_service.strip():
        # FORK 3: On Request / Unknown - create follow-up reminder only, 1 year (no Workiz job)
        if not contact_id:
            return {'success': False, 'error': 'Missing contact_id for follow-up reminder'}
        print(f"[*] Type: {type_of_service or 'empty'} -> follow-up in 6 months (no new job in Workiz)")
        result = create_ondemand_followup(workiz_job, contact_id, days_until_followup=180)
        return {'success': result['success'], 'path': '5B_on_request_unknown', 'result': result}
    
    else:
        # Unrecognized - treat as follow-up in 6 months (do not create Workiz job)
        print(f"[!] Unrecognized service type '{type_of_service}' - creating 6-month follow-up only")
        if not contact_id:
            return {'success': False, 'error': 'Missing contact_id for follow-up reminder'}
        result = create_ondemand_followup(workiz_job, contact_id, days_until_followup=180)
        return {'success': result['success'], 'path': '5B_fallback', 'result': result}


# ==============================================================================
# TEST ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    print("Phase 5 Router - Test Mode")
    print("="*70)
    
    # For testing, we'd need to integrate with Phase 4's completed job data
    # This would typically be called FROM phase4_status_update_router.py
    
    print("\nTo test Phase 5:")
    print("1. Trigger Phase 4 with a 'Done' job")
    print("2. Phase 4 will detect Maintenance/On Demand")
    print("3. Phase 4 calls Phase 5 with required data")
    print("\nOr test individual paths:")
    print("- python functions/workiz/create_next_maintenance_job.py")
    print("- python functions/odoo/create_followup_activity.py")
