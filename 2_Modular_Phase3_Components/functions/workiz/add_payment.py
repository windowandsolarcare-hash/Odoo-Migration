"""
Add a payment to a Workiz job (atomic function).

API: POST /job/addPayment/{UUID}/
Body: addPaymentBody — auth_secret*, amount*, type*, date*, reference (optional)
type: 'cash' | 'credit' | 'check' (API doc); UI may support more (e.g. zelle, venmo).
"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET


def add_payment(job_uuid, amount, payment_type, date_str, reference=None):
    """
    Add a payment to a Workiz job.

    Args:
        job_uuid (str): Workiz job UUID
        amount (float): Payment amount
        payment_type (str): 'cash' | 'credit' | 'check' (or try 'zelle', 'venmo', etc. if API accepts)
        date_str (str): When payment was made — ISO date-time e.g. '2016-08-29T09:12:33.001Z' (API: date-time)
        reference (str, optional): Confirmation number or reference

    Returns:
        dict: {'success': bool, 'message': str}
    """
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/addPayment/{job_uuid}/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "uuid": str(job_uuid).strip(),
        "amount": round(float(amount), 2),
        "type": payment_type.lower().strip(),
        "date": date_str,
    }
    if reference:
        payload["reference"] = str(reference)[:255]

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code in (200, 201, 204):
            return {"success": True}
        return {"success": False, "message": f"HTTP {response.status_code}", "body": response.text[:500]}
    except Exception as e:
        return {"success": False, "message": str(e)}
