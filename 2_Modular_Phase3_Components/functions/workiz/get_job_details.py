"""Fetch complete Workiz job data by UUID"""

import time
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET

# Retry on 429: max attempts, default wait (seconds) if no Retry-After header
MAX_429_RETRIES = 3
DEFAULT_429_WAIT = 60


def get_job_details(job_uuid, quiet=False):
    """
    Fetch complete Workiz job data by UUID.
    On 429 (rate limit), waits (Retry-After or 60s) and retries up to MAX_429_RETRIES times.
    
    Args:
        job_uuid (str): Workiz job UUID
        quiet (bool): If True, do not print success/error messages (for batch scripts).
    
    Returns:
        dict: Job data or None if failed
    """
    url = f"{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    for attempt in range(MAX_429_RETRIES + 1):
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                response_json = response.json()
                # Workiz API returns data nested in 'data' key as a list
                data_list = response_json.get('data', [])
                if data_list and len(data_list) > 0:
                    job_data = data_list[0]
                    if not quiet:
                        print(f"[OK] Workiz job data fetched successfully")
                    return job_data
                else:
                    if not quiet:
                        print(f"[ERROR] No job data in Workiz response")
                    return None
            elif response.status_code == 429 and attempt < MAX_429_RETRIES:
                wait = DEFAULT_429_WAIT
                retry_after = response.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    wait = int(retry_after)
                if not quiet:
                    print(f"[429] Rate limited; waiting {wait}s then retry {attempt + 1}/{MAX_429_RETRIES}")
                time.sleep(wait)
                continue
            else:
                if not quiet:
                    print(f"[ERROR] Workiz API returned status {response.status_code}")
                return None
        except Exception as e:
            if not quiet:
                print(f"[ERROR] Exception fetching Workiz job: {e}")
            return None
    return None
