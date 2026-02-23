"""
Mark a Workiz job as Done (atomic function).

Done is status only — no SubStatus in Workiz for Done.
Uses POST /job/update/ with minimal payload: auth_secret, UUID, Status.
"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET


def mark_job_done(job_uuid):
    """
    Set job status to Done in Workiz. No SubStatus (Done is status only).

    Args:
        job_uuid (str): Workiz job UUID

    Returns:
        dict: {'success': bool, 'message': str}
    """
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "Status": "Done",
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code in (200, 201, 204):
            return {"success": True}
        return {"success": False, "message": f"HTTP {response.status_code}", "body": response.text[:500]}
    except Exception as e:
        return {"success": False, "message": str(e)}
