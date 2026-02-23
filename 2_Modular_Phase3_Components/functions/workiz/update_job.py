"""Update Workiz job with new date/time, status, type, and optional notes"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET


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
