"""
Workiz API Module - Workiz API Interactions
============================================
All Workiz API calls and data extraction functions.
"""

import requests
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET


def get_job_details(job_uuid):
    """
    Fetch complete Workiz job data by UUID.
    
    Args:
        job_uuid (str): Workiz job UUID
    
    Returns:
        dict: Job data or None if failed
    """
    url = f"{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            response_json = response.json()
            # Workiz API returns data nested in 'data' key as a list
            data_list = response_json.get('data', [])
            if data_list and len(data_list) > 0:
                job_data = data_list[0]
                print(f"[OK] Workiz job data fetched successfully")
                return job_data
            else:
                print(f"[ERROR] No job data in Workiz response")
                return None
        else:
            print(f"[ERROR] Workiz API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception fetching Workiz job: {e}")
        return None


def update_job(job_uuid, job_datetime_pacific, job_type, job_notes=None, status="Pending", substatus="Send Confirmation - Text"):
    """
    Update Workiz job with new date/time, status, type, and optional notes.
    
    Args:
        job_uuid (str): Workiz job UUID
        job_datetime_pacific (str): Job date/time in Pacific format "YYYY-MM-DD HH:MM:SS"
        job_type (str): Job type
        job_notes (str, optional): Notes to prepend (if None, notes won't be updated)
        status (str): Job status (default: "Pending")
        substatus (str): Job substatus (default: "Send Confirmation - Text")
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "JobDateTime": job_datetime_pacific,
        "JobType": job_type,
        "Status": status,
        "SubStatus": substatus
    }
    
    # Add combined notes if provided
    if job_notes:
        payload["JobNotes"] = job_notes
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Workiz job updated successfully!")
            return {'success': True}
        else:
            return {'success': False, 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def prepend_calendly_notes_to_job(job_uuid, new_notes):
    """
    Fetch current JobNotes and prepend new Calendly booking notes.
    
    Args:
        job_uuid (str): Workiz job UUID
        new_notes (str): New notes from Calendly to prepend
    
    Returns:
        str: Combined notes with delimiter, or None if no update needed
    """
    if not new_notes:
        return None
    
    current_job = get_job_details(job_uuid)
    existing_notes = current_job.get('JobNotes', '') if current_job else ''
    
    # Prepend new Calendly notes to existing notes with clear delimiter
    if existing_notes and existing_notes.strip():
        combined_notes = f"[Calendly Booking] {new_notes} |||ORIGINAL_NOTES||| {existing_notes}"
        print(f"[*] Prepending Calendly notes to existing JobNotes")
    else:
        combined_notes = f"[Calendly Booking] {new_notes}"
        print(f"[*] Adding Calendly notes as new JobNotes")
    
    return combined_notes
