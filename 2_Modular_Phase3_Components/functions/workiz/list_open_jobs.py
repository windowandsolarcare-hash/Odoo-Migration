"""
List open jobs from Workiz (excludes Done and Canceled).

Uses GET /job/all/ with only_open=true.
API: sorted by JobDateTime desc; default range last 14 days if start_date omitted.
"""

import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET


def list_open_jobs(start_date=None, records=100, offset=0):
    """
    Fetch a page of open jobs (excludes Done and Canceled).

    Args:
        start_date (str, optional): Start of date range (yyyy-MM-dd). If None, API uses last 14 days.
        records (int): Number of records per page (max 100).
        offset (int): Page index for pagination. Workiz uses 0, 1, 2, 3, 4... (each page = up to 100 records).

    Returns:
        tuple: (list of job dicts, error_message).
               On success: (jobs, None). Each job has at least UUID.
               On failure: ([], error_string).
    """
    url = (
        f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/"
        f"?auth_secret={WORKIZ_AUTH_SECRET}"
        f"&records={min(records, 100)}"
        f"&offset={offset}"
        f"&only_open=true"
    )
    if start_date:
        url += f"&start_date={start_date}"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}: {r.text[:500]}"
        data = r.json()
        if isinstance(data, list):
            return data, None
        jobs = data.get("data", data) if isinstance(data, dict) else []
        return jobs if isinstance(jobs, list) else [], None
    except Exception as e:
        return [], str(e)
