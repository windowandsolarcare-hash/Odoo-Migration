# ==============================================================================
# PHASE 3 MASTER - COMPLETE END-TO-END TEST
# ==============================================================================
# Purpose: Run all 6 phases (3A-3F) in sequence for complete integration test
# Created: 2026-02-05
# ==============================================================================

from phase3a_contact_lookup import search_contact_by_address
from phase3b_opportunity_lookup import process_phase3b
from phase3c_workiz_update import process_phase3c
from phase3d_mark_won import mark_opportunity_won
from phase3e_sales_order_COMPLETE import process_phase3e
from phase3f_update_contact import process_phase3f

# ==============================================================================
# TEST DATA - BEV HARTIN (Calendly Webhook Simulation)
# ==============================================================================

calendly_booking = {
    "event_start_time": "2026-03-12T15:30:00.000000Z",  # UTC
    "event_type_name": "Windows Inside & Outside Plus Screens",
    "invitee_email": "bev.hartin.updated@example.com",
    "invitee_first_name": "Bev",
    "invitee_last_name": "Hartin",
    "location": "29 Toscana Way E, Rancho Mirage, CA 92270"
}

# ==============================================================================
# MASTER ORCHESTRATOR
# ==============================================================================

def run_phase3_full_test():
    """
    Execute all 6 phases of the Calendly → Workiz → Odoo flow.
    
    Flow:
    1. Phase 3A: Lookup contact by address
    2. Phase 3B: Lookup opportunity with Workiz UUID
    3. Phase 3C: Update Workiz job (datetime, status, substatus)
    4. Phase 3D: Mark opportunity as Won
    5. Phase 3E: Create sales order with line items
    6. Phase 3F: Update contact email
    """
    
    print("\n" + "="*70)
    print("PHASE 3 - MASTER END-TO-END TEST")
    print("="*70)
    print("\nTest Booking: Bev Hartin")
    print(f"Date/Time: {calendly_booking['event_start_time']}")
    print(f"Service: {calendly_booking['event_type_name']}")
    print(f"Address: {calendly_booking['location']}")
    print("="*70)
    
    # Parse booking data
    booking_info = {
        'booking_time': calendly_booking['event_start_time'],
        'service_type': calendly_booking['event_type_name'],
        'email': calendly_booking['invitee_email'],
        'first_name': calendly_booking['invitee_first_name'],
        'last_name': calendly_booking['invitee_last_name']
    }
    
    # Extract address
    address_parts = calendly_booking['location'].split(',')
    street = address_parts[0].strip()
    
    # -------------------------------------------------------------------------
    # PHASE 3A: CONTACT LOOKUP
    # -------------------------------------------------------------------------
    
    contact = search_contact_by_address(street)
    
    if not contact:
        print(f"\n[FAILED] Phase 3A failed: Contact not found for address '{street}'")
        return {'success': False, 'failed_at': 'Phase 3A'}
    
    # -------------------------------------------------------------------------
    # PHASE 3B: OPPORTUNITY LOOKUP
    # -------------------------------------------------------------------------
    
    opportunity_result = process_phase3b(contact)
    
    if not opportunity_result['success']:
        print(f"\n[FAILED] Phase 3B failed: {opportunity_result['message']}")
        return {'success': False, 'failed_at': 'Phase 3B'}
    
    opportunity = opportunity_result['opportunity']
    
    # -------------------------------------------------------------------------
    # PHASE 3C: WORKIZ JOB UPDATE
    # -------------------------------------------------------------------------
    
    workiz_result = process_phase3c(opportunity, booking_info)
    
    if not workiz_result['success']:
        print(f"\n[FAILED] Phase 3C failed: {workiz_result['message']}")
        return {'success': False, 'failed_at': 'Phase 3C'}
    
    # -------------------------------------------------------------------------
    # PHASE 3D: MARK OPPORTUNITY WON
    # -------------------------------------------------------------------------
    
    won_result = mark_opportunity_won(opportunity['id'])
    
    if not won_result['success']:
        print(f"\n[FAILED] Phase 3D failed: {won_result['message']}")
        return {'success': False, 'failed_at': 'Phase 3D'}
    
    # -------------------------------------------------------------------------
    # PHASE 3E: CREATE SALES ORDER
    # -------------------------------------------------------------------------
    
    so_result = process_phase3e(contact, opportunity, booking_info, won_result)
    
    if not so_result['success']:
        print(f"\n[FAILED] Phase 3E failed: {so_result['message']}")
        return {'success': False, 'failed_at': 'Phase 3E'}
    
    sales_order_id = so_result['sales_order_id']
    
    # -------------------------------------------------------------------------
    # PHASE 3F: UPDATE CONTACT EMAIL
    # -------------------------------------------------------------------------
    
    email_result = process_phase3f(contact, booking_info)
    
    if not email_result['success']:
        print(f"\n[FAILED] Phase 3F failed: {email_result['message']}")
        return {'success': False, 'failed_at': 'Phase 3F'}
    
    # -------------------------------------------------------------------------
    # SUCCESS SUMMARY
    # -------------------------------------------------------------------------
    
    print("\n" + "="*70)
    print("[OK] PHASE 3 COMPLETE - ALL PHASES SUCCESSFUL")
    print("="*70)
    print(f"\n[OK] Phase 3A: Contact found (ID: {contact['id']})")
    print(f"[OK] Phase 3B: Opportunity found (ID: {opportunity['id']})")
    print(f"[OK] Phase 3C: Workiz job updated (UUID: {opportunity['x_workiz_graveyard_uuid']})")
    print(f"[OK] Phase 3D: Opportunity marked Won")
    print(f"[OK] Phase 3E: Sales order created (ID: {sales_order_id})")
    print(f"[OK] Phase 3F: Contact email updated ({booking_info['email']})")
    print("\n" + "="*70)
    
    return {
        'success': True,
        'contact_id': contact['id'],
        'opportunity_id': opportunity['id'],
        'sales_order_id': sales_order_id
    }


# ==============================================================================
# RUN TEST
# ==============================================================================

if __name__ == "__main__":
    result = run_phase3_full_test()
    
    if result['success']:
        print("\n[SUCCESS] END-TO-END TEST PASSED!")
    else:
        print(f"\n[ERROR] TEST FAILED AT: {result.get('failed_at', 'Unknown')}")
