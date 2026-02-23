# ==============================================================================
# PHASE 3C: WORKIZ JOB UPDATE
# ==============================================================================
# Purpose: Update unscheduled Workiz graveyard job with booking date/time
# Created: 2026-02-05
# Status: Development - Ready for testing with Bev Hartin
# ==============================================================================

import requests
import json
from datetime import datetime
import pytz

# ==============================================================================
# CONFIGURATION
# ==============================================================================

WORKIZ_API_BASE = "https://api.workiz.com/api/v1"
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"

# ==============================================================================
# TIMEZONE CONVERSION
# ==============================================================================

def convert_utc_to_pacific(utc_datetime_str):
    """
    Convert UTC datetime string from Calendly to Pacific Time for Workiz.
    
    Args:
        utc_datetime_str (str): UTC datetime (e.g., "2026-02-20T22:30:00.000000Z")
        
    Returns:
        str: Pacific Time formatted for Workiz (e.g., "2026-02-20 14:30:00")
        
    TESTED: 2026-02-05
    NOTES: 
    - Calendly sends times in UTC with 'Z' suffix
    - Workiz expects Pacific Time without timezone suffix
    - Handles both PST (UTC-8) and PDT (UTC-7) automatically
    """
    
    # Parse UTC datetime
    # Handle both formats: with and without microseconds
    if '.' in utc_datetime_str:
        # Remove microseconds and Z
        utc_datetime_str = utc_datetime_str.split('.')[0] + 'Z'
    
    utc_time = datetime.strptime(utc_datetime_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
    utc_time = pytz.utc.localize(utc_time)
    
    # Convert to Pacific Time
    pacific_tz = pytz.timezone('America/Los_Angeles')
    pacific_time = utc_time.astimezone(pacific_tz)
    
    # Format for Workiz: "YYYY-MM-DD HH:MM:SS"
    workiz_format = pacific_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[*] Time conversion:")
    print(f"   UTC:     {utc_datetime_str}")
    print(f"   Pacific: {workiz_format}")
    
    return workiz_format


# ==============================================================================
# PHASE 3C FUNCTION
# ==============================================================================

def update_workiz_job(job_uuid, booking_datetime_utc, service_type, status="Pending", substatus="Send Confirmation - Text"):
    """
    Update Workiz job with booking date/time, status, and job type.
    
    Args:
        job_uuid (str): Workiz job UUID (e.g., "SG6AMX")
        booking_datetime_utc (str): UTC datetime from Calendly
        service_type (str): Service type from Calendly (for JobType mapping)
        status (str): Job status (default: "Pending")
        substatus (str): Job substatus (default: "Send Confirmation - Text")
        
    Returns:
        dict: {'success': bool, 'message': str, 'details': dict}
        
    TESTED: 2026-02-05 - Updated to include JobType
    NOTES: 
    - Updates unscheduled graveyard job to scheduled
    - Sets JobType based on Calendly service selection
    - Status "Pending" + Substatus "Send Confirmation - Text" triggers auto SMS
    - Uses Workiz API endpoint: POST /job/update/
    """
    
    # Convert UTC to Pacific Time
    pacific_datetime = convert_utc_to_pacific(booking_datetime_utc)
    
    # Use service type directly as JobType (Calendly dropdown matches Workiz exactly)
    job_type = service_type
    print(f"[#]  JobType: {job_type}")
    
    # Workiz API endpoint - token goes in URL, UUID in body
    url = f"{WORKIZ_API_BASE}/{WORKIZ_API_TOKEN}/job/update/"
    
    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request body
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "JobDateTime": pacific_datetime,
        "JobType": job_type,
        "Status": status,
        "SubStatus": substatus
    }
    
    print(f"\n[*] Updating Workiz job {job_uuid}...")
    print(f"   URL: {url}")
    print(f"   Date/Time: {pacific_datetime}")
    print(f"   JobType: {job_type}")
    print(f"   Status: {status}")
    print(f"   SubStatus: {substatus}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Workiz job updated successfully!")
            return {
                'success': True,
                'message': f"Job {job_uuid} scheduled for {pacific_datetime}",
                'details': result
            }
        else:
            print(f"[ERROR] Workiz API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return {
                'success': False,
                'message': f"Workiz API returned status {response.status_code}",
                'details': {'status_code': response.status_code, 'response': response.text}
            }
            
    except Exception as e:
        print(f"[ERROR] Error updating Workiz job: {e}")
        return {
            'success': False,
            'message': f"Error: {str(e)}",
            'details': {}
        }


def process_phase3c(opportunity, booking_info):
    """
    Phase 3C handler: Update Workiz job from Phase 3B data.
    
    Args:
        opportunity (dict): Opportunity record from Phase 3B
        booking_info (dict): Booking data from Phase 3A
        
    Returns:
        dict: {
            'success': bool,
            'opportunity': dict,
            'booking_info': dict,
            'workiz_result': dict,
            'message': str
        }
    """
    
    print("\n" + "="*70)
    print("PHASE 3C: WORKIZ JOB UPDATE")
    print("="*70)
    print(f"Graveyard UUID: {opportunity['x_workiz_graveyard_uuid']}")
    print(f"Booking Time (UTC): {booking_info['booking_time']}")
    print("="*70 + "\n")
    
    # Validate graveyard UUID
    if not opportunity.get('x_workiz_graveyard_uuid'):
        return {
            'success': False,
            'opportunity': opportunity,
            'booking_info': booking_info,
            'workiz_result': {},
            'message': 'Opportunity missing graveyard UUID'
        }
    
    # Update Workiz job
    workiz_result = update_workiz_job(
        job_uuid=opportunity['x_workiz_graveyard_uuid'],
        booking_datetime_utc=booking_info['booking_time'],
        service_type=booking_info.get('service_type', ''),
        status="Pending",
        substatus="Send Confirmation - Text"
    )
    
    return {
        'success': workiz_result['success'],
        'opportunity': opportunity,
        'booking_info': booking_info,
        'workiz_result': workiz_result,
        'message': workiz_result['message']
    }


# ==============================================================================
# INTEGRATION: PHASE 3A + 3B + 3C
# ==============================================================================

def phase3a_3b_3c_combined(calendly_data):
    """
    Combined Phase 3A + 3B + 3C: Full flow from Calendly to Workiz update.
    
    Args:
        calendly_data (dict): Calendly webhook payload
        
    Returns:
        dict: Combined results from all three phases
    """
    from phase3b_opportunity_lookup import phase3a_and_3b_combined
    
    print("\n" + "= "*35)
    print("TESTING PHASE 3A + 3B + 3C INTEGRATION")
    print("= "*35 + "\n")
    
    # Phase 3A + 3B: Find contact and opportunity
    phase3ab_result = phase3a_and_3b_combined(calendly_data)
    
    if not phase3ab_result['success']:
        print("\n[ERROR] Phase 3A/3B failed - cannot proceed to Phase 3C")
        return phase3ab_result
    
    # Phase 3C: Update Workiz job
    phase3c_result = process_phase3c(
        opportunity=phase3ab_result['opportunity'],
        booking_info=phase3ab_result['booking_info']
    )
    
    return phase3c_result


# ==============================================================================
# TEST WITH BEV HARTIN DATA
# ==============================================================================

if __name__ == "__main__":
    
    # Test 1: Timezone conversion
    print("\n" + "- "*35)
    print("TEST 1: Timezone Conversion")
    print("- "*35 + "\n")
    
    test_utc_time = "2026-02-20T22:30:00.000000Z"
    pacific_time = convert_utc_to_pacific(test_utc_time)
    print(f"\nResult: {pacific_time}")
    print("Expected: 2026-02-20 14:30:00 (if PST, 2:30 PM)")
    
    # Test 2: Direct Workiz update (Phase 3C only)
    print("\n\n" + "- "*35)
    print("TEST 2: Direct Workiz Update (Phase 3C Only)")
    print("- "*35 + "\n")
    
    test_opportunity = {
        'id': 41,
        'name': 'Reactivation Campaign - Bev Hartin - 02/02/2026',
        'x_workiz_graveyard_uuid': 'SG6AMX',
        'expected_revenue': 635.0
    }
    
    test_booking_info = {
        'name': 'Bev Hartin',
        'email': 'dansyourrealtor@gmail.com',
        'service_address': '29 Toscana Way E',
        'service_type': 'Windows Inside & Outside Plus Screens',
        'booking_time': '2026-03-12T15:30:00.000000Z',
        'timezone': 'America/Los_Angeles'
    }
    
    result = process_phase3c(test_opportunity, test_booking_info)
    
    print("\n" + "="*70)
    print("PHASE 3C RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"\n[OK] WORKIZ JOB UPDATED!")
        print(f"   Job UUID: {test_opportunity['x_workiz_graveyard_uuid']}")
        print(f"   Status: Pending")
        print(f"   SubStatus: Send Confirmation - Text")
        print(f"   Confirmation SMS should be sent to customer automatically")
    
    print("="*70 + "\n")
    
    # Test 3: Full integration (Phase 3A + 3B + 3C)
    print("\n" + "- "*35)
    print("TEST 3: Full Integration (Phase 3A + 3B + 3C)")
    print("- "*35 + "\n")
    
    test_calendly_data = {
        'Name': 'Bev Hartin',
        'Email': 'dansyourrealtor@gmail.com',
        'Service Address': '29 Toscana Way E',
        'Service Type': 'Windows Outside Only',
        'Additional Notes': '',
        'Event Type': 'Rancho Mirage Service',
        'Booking Time': '2026-02-20T22:30:00.000000Z',
        'Timezone': 'America/Los_Angeles',
        'Status': 'active'
    }
    
    full_result = phase3a_3b_3c_combined(test_calendly_data)
    
    print("\n" + "="*70)
    print("FULL INTEGRATION RESULT (3A + 3B + 3C):")
    print("="*70)
    print(f"Success: {full_result['success']}")
    print(f"Message: {full_result['message']}")
    
    if full_result['success']:
        print(f"\n[SUCCESS] COMPLETE FLOW SUCCESSFUL!")
        print(f"   Contact: {full_result['booking_info']['name']}")
        print(f"   Opportunity ID: {full_result['opportunity']['id']}")
        print(f"   Workiz Job: {full_result['opportunity']['x_workiz_graveyard_uuid']}")
        print(f"   Scheduled: {convert_utc_to_pacific(full_result['booking_info']['booking_time'])}")
        print(f"\n[NEXT] Ready for Phase 3D: Mark Opportunity as Won")
    
    print("="*70 + "\n")
