"""
PHASE 4: Workiz Job Status Update Router
==========================================
Triggered by: Workiz job status change (any status)
Purpose: Update existing Sales Order OR create new one if missing

Flow:
1. Get Workiz job details
2. Search for existing SO by UUID
3. If SO exists: Update fields
4. If SO missing: Call Phase 3 to create it
5. When status = "Done": do NOT write payment fields (payment originates in Odoo via Phase 6A)
"""
import sys
sys.path.append('.')

# Import Phase 3 router (REUSE!)
from tier3_workiz_master_router import main as phase3_create_so

# Import Workiz functions
from functions.workiz.get_job_details import get_job_details
from functions.workiz.extract_tip_from_line_items import extract_tip_from_line_items

# Import Odoo functions
from functions.odoo.search_sales_order_by_uuid import search_sales_order_by_uuid
from functions.odoo.update_sales_order import update_sales_order
from functions.odoo.update_property_fields import update_property_fields
from functions.odoo.post_chatter_message import post_chatter_message
from functions.odoo.get_property_city import get_property_city

from datetime import datetime, timedelta


# ============================================================================
# INLINE UTILITY FUNCTIONS (to avoid import dependencies)
# ============================================================================

def format_team_names(team_raw):
    """Extract team member names from Workiz team data."""
    if not team_raw:
        return ""
    
    if isinstance(team_raw, list):
        names = []
        for member in team_raw:
            if isinstance(member, dict):
                name = member.get('Name') or member.get('name', '')
                if name:
                    names.append(str(name).strip())
            elif member:
                names.append(str(member).strip())
        return ", ".join(names)
    elif isinstance(team_raw, str):
        return team_raw.strip()
    return ""


def convert_to_utc(dt_pacific):
    """Convert Pacific time to UTC for Odoo."""
    # Pacific is UTC-8 (standard) or UTC-7 (daylight)
    # For simplicity, use UTC-8
    utc_offset = timedelta(hours=8)
    return dt_pacific + utc_offset


# ============================================================================
# MAIN UPDATE FUNCTIONS
# ============================================================================

def update_existing_sales_order(so_id, workiz_job):
    """
    Update an existing Sales Order with latest Workiz data.
    
    Args:
        so_id (int): Sales Order ID in Odoo
        workiz_job (dict): Full Workiz job data
        
    Returns:
        dict: Update result
    """
    print(f"\n[*] Updating existing Sales Order ID: {so_id}")
    
    # Extract Workiz data
    workiz_uuid = workiz_job.get('UUID', '')
    workiz_substatus = workiz_job.get('SubStatus', '') or workiz_job.get('Status', '')
    job_source = workiz_job.get('JobSource', '')
    job_type = workiz_job.get('JobType', '')
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    job_datetime_str = workiz_job.get('JobDateTime', '')
    team = workiz_job.get('Team', [])
    tags = workiz_job.get('Tags', [])
    line_items = workiz_job.get('LineItems', [])
    status = workiz_job.get('Status', '')
    
    # Format team names
    team_names = format_team_names(team)
    
    # Convert job date/time to UTC for Odoo
    job_datetime_utc = None
    if job_datetime_str:
        dt_pacific = datetime.strptime(job_datetime_str, '%Y-%m-%d %H:%M:%S')
        job_datetime_utc = convert_to_utc(dt_pacific)
    
    # Combine notes
    notes_snapshot = ""
    if job_notes:
        notes_snapshot += f"[Job Notes]\n{job_notes}\n\n"
    if comments:
        notes_snapshot += f"[Comments]\n{comments}"
    notes_snapshot = notes_snapshot.strip()
    
    # Build update payload (always update these fields)
    updates = {
        'x_studio_x_studio_workiz_status': workiz_substatus,
        'x_studio_x_studio_workiz_tech': team_names,
        'x_studio_x_gate_snapshot': gate_code,
        'x_studio_x_studio_pricing_snapshot': pricing,
        'x_studio_x_studio_notes_snapshot1': notes_snapshot,
    }
    
    # Update date_order if available
    if job_datetime_utc:
        updates['date_order'] = job_datetime_utc.strftime('%Y-%m-%d %H:%M:%S')
    
    # Update job type if available
    if job_type:
        updates['x_studio_x_studio_x_studio_job_type'] = job_type
    
    # Update lead source if available
    if job_source:
        updates['x_studio_x_studio_lead_source'] = job_source
    
    # Update tags (if available and changed)
    if tags:
        # Note: Tag update would require searching for existing contact tags
        # and combining - skipping for now unless critical
        pass
    
    # When status is Done, do NOT write payment fields to Odoo (payment originates in Odoo via Phase 6A).
    
    # Update the Sales Order
    success = update_sales_order(so_id, updates)
    
    if not success:
        print("[ERROR] Failed to update Sales Order")
        return {'success': False, 'error': 'SO update failed'}
    
    print("[OK] Sales Order updated successfully")
    
    # Post status change to chatter
    last_status_update = workiz_job.get('LastStatusUpdate', '')
    
    # Build single-line message with semicolons
    message_parts = [f"Status updated to: {workiz_substatus}"]
    
    if last_status_update:
        # Append date to the status line
        message_parts[0] = f"Status updated to: {workiz_substatus} on {last_status_update}"
    
    # Do not append payment status/tip when Done; payment data originates in Odoo (Phase 6A).
    
    chatter_message = "; ".join(message_parts)
    post_chatter_message(so_id, chatter_message)
    print("[OK] Posted status update to chatter")
    
    return {'success': True, 'so_id': so_id, 'updated': True}


def update_property_from_job(property_id, workiz_job, is_done=False):
    """
    Update property fields from Workiz job data.
    
    Args:
        property_id (int): Property ID in Odoo
        workiz_job (dict): Workiz job data
        is_done (bool): Whether job status is "Done"
    """
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service', '')
    
    # If job is done, update last property visit
    last_visit_date = None
    if is_done:
        job_datetime_str = workiz_job.get('JobDateTime', '')
        if job_datetime_str:
            last_visit_date = job_datetime_str.split(' ')[0]  # Extract date only
            print(f"[*] Updating Last Property Visit to: {last_visit_date}")
    
    update_property_fields(
        property_id, 
        gate_code, 
        pricing, 
        last_visit_date,  # Only set if job is done
        job_notes, 
        comments, 
        frequency, 
        alternating, 
        type_of_service
    )
    print(f"[OK] Property {property_id} updated")


def main(input_data):
    """
    Phase 4 Main Router: Handle Workiz job status updates.
    
    Expected input_data from Zapier:
    {
        'job_uuid': 'ABC123'  # From Workiz status change trigger
    }
    """
    print("\n" + "="*70)
    print("PHASE 4: WORKIZ JOB STATUS UPDATE")
    print("="*70)
    
    # Extract job UUID
    job_uuid = input_data.get('job_uuid')
    if not job_uuid:
        return {'success': False, 'error': 'No job_uuid provided'}
    
    # Step 1: Get Workiz job details
    print(f"\n[*] Fetching Workiz job: {job_uuid}")
    workiz_job = get_job_details(job_uuid)
    if not workiz_job:
        return {'success': False, 'error': 'Failed to fetch Workiz job'}
    
    status = workiz_job.get('Status', '')
    substatus = workiz_job.get('SubStatus', '')
    print(f"[*] Job Status: {status}")
    if substatus:
        print(f"[*] Job SubStatus: {substatus}")
    
    # Step 2: Search for existing Sales Order
    print(f"\n[*] Searching for existing Sales Order with UUID: {job_uuid}")
    existing_so = search_sales_order_by_uuid(job_uuid)
    
    if existing_so:
        # SO exists - update it
        so_id = existing_so['id']
        print(f"[OK] Found existing SO: {existing_so['name']} (ID: {so_id})")
        
        # Update the Sales Order
        result = update_existing_sales_order(so_id, workiz_job)
        
        # Update property fields
        property_id = existing_so.get('partner_shipping_id')
        if property_id:
            if isinstance(property_id, list):
                property_id = property_id[0]  # Extract ID from [ID, "Name"] format
            update_property_from_job(property_id, workiz_job, is_done=(status.lower() == 'done'))
        
        # PHASE 5: Auto-schedule next job (if status is Done)
        if status.lower() == 'done':
            type_of_service = workiz_job.get('type_of_service', '').lower()
            
            tos = (type_of_service or '').lower()
            if 'maintenance' in tos or 'on demand' in tos or 'on-demand' in tos or 'on request' in tos or 'unknown' in tos or not tos.strip():
                print("\n[*] Triggering Phase 5: Auto-scheduler")
                
                # Import Phase 5 router
                from phase5_auto_scheduler import main as phase5_auto_scheduler
                
                # Get customer city from Odoo property
                contact_id = existing_so.get('partner_id')
                if isinstance(contact_id, list):
                    contact_id = contact_id[0]
                
                # Fetch city from property for route-based scheduling
                customer_city = get_property_city(property_id)
                
                phase5_input = {
                    'workiz_job': workiz_job,
                    'property_id': property_id,
                    'contact_id': contact_id,
                    'customer_city': customer_city
                }
                
                phase5_result = phase5_auto_scheduler(phase5_input)
                print(f"[*] Phase 5 result: {phase5_result.get('path', 'unknown')}")
        
        print("="*70)
        print("[OK] PHASE 4 COMPLETE - SALES ORDER UPDATED")
        print("="*70)
        return result
    
    else:
        # SO doesn't exist - call Phase 3 to create it
        print("[!] Sales Order not found - calling Phase 3 to create it")
        print("="*70)
        
        # Call Phase 3 router (imports the entire creation flow)
        phase3_result = phase3_create_so(input_data)
        
        if not phase3_result.get('success'):
            return phase3_result
        
        # Phase 3 created the SO. When status is Done, do NOT push payment from Workiz (payment originates in Odoo via 6A).
        so_id = phase3_result.get('sales_order_id')
        
        # PHASE 5: Auto-schedule next job (if status is Done)
        if so_id and status.lower() == 'done':
            type_of_service = workiz_job.get('type_of_service', '').lower()
            
            tos = (type_of_service or '').lower()
            if 'maintenance' in tos or 'on demand' in tos or 'on-demand' in tos or 'on request' in tos or 'unknown' in tos or not tos.strip():
                print("\n[*] Triggering Phase 5: Auto-scheduler")
                
                # Import Phase 5 router
                from phase5_auto_scheduler import main as phase5_auto_scheduler
                
                # Get property and contact IDs from Phase 3 result
                property_id = phase3_result.get('property_id')
                contact_id = phase3_result.get('contact_id')
                
                # Fetch city from property for route-based scheduling
                customer_city = get_property_city(property_id) if property_id else ''
                
                phase5_input = {
                    'workiz_job': workiz_job,
                    'property_id': property_id,
                    'contact_id': contact_id,
                    'customer_city': customer_city
                }
                
                phase5_result = phase5_auto_scheduler(phase5_input)
                print(f"[*] Phase 5 result: {phase5_result.get('path', 'unknown')}")
        
        print("="*70)
        print("[OK] PHASE 4 COMPLETE - SALES ORDER CREATED & UPDATED")
        print("="*70)
        return phase3_result


# ============================================================================
# ZAPIER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {
        'job_uuid': 'IC3ZC9'  # Blair Becker - test chatter formatting
    }
    
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(result)
    print("="*70)
# When imported (e.g. by Phase 6B), do not run main — Zapier uses flattened script.
