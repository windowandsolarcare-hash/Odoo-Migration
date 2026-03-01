"""
fetch_recent_jobs.py
====================
Fetch the 5 most recent jobs from Workiz and print their statuses.

Auth pattern (per project conventions):
  - API key embedded in the base URL
  - auth_secret passed as a query parameter on GET requests

Usage:
  python fetch_recent_jobs.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import requests

# ---------------------------------------------------------------------------
# Credentials — injected via environment variables (set in Cursor Secrets).
# Fall back to the known values from config.py for local runs in this repo.
# ---------------------------------------------------------------------------
WORKIZ_API_TOKEN = os.environ.get(
    "Workiz API Key",
    "api_1hu6lroiy5zxomcpptuwsg8heju97iwg",
)
WORKIZ_AUTH_SECRET = os.environ.get(
    "Workiz Secret Code",
    "sec_334084295850678330105471548",
)
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

TOP_N = 5


def fetch_recent_jobs(n: int = TOP_N):
    """
    Return the n most-recent Workiz jobs (across all statuses).

    The /job/all/ endpoint returns jobs sorted by JobDateTime descending.
    We pass only_open=false so Done/Canceled jobs are included, giving a
    true "most recent" picture regardless of status.

    A wide start_date (2 years back) ensures we always capture n results
    even during slow periods.
    """
    start_date = (datetime.now(timezone.utc) - timedelta(days=730)).strftime("%Y-%m-%d")
    url = (
        f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/"
        f"?auth_secret={WORKIZ_AUTH_SECRET}"
        f"&start_date={start_date}"
        f"&records={n}"
        f"&only_open=false"
    )

    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException as exc:
        print(f"[ERROR] Network error contacting Workiz API: {exc}", file=sys.stderr)
        return []

    if response.status_code != 200:
        print(
            f"[ERROR] Workiz API returned HTTP {response.status_code}: {response.text}",
            file=sys.stderr,
        )
        return []

    payload = response.json()

    # The API can return a bare list or {"data": [...], "flag": true, ...}
    if isinstance(payload, list):
        jobs = payload
    elif isinstance(payload, dict):
        jobs = payload.get("data", [])
    else:
        jobs = []

    return jobs[:n]


def main():
    print(f"Fetching {TOP_N} most recent Workiz jobs...\n")
    jobs = fetch_recent_jobs(TOP_N)

    if not jobs:
        print("No jobs returned. Check your credentials or date range.")
        sys.exit(1)

    print(f"{'#':<4} {'UUID':<12} {'Date/Time':<22} {'Status':<20} {'SubStatus':<30} {'Customer'}")
    print("-" * 110)

    for idx, job in enumerate(jobs, start=1):
        uuid       = job.get("UUID", "N/A")
        dt         = job.get("JobDateTime", "N/A")
        status     = job.get("Status", "N/A")
        substatus  = job.get("SubStatus", "") or ""
        first      = job.get("FirstName", "")
        last       = job.get("LastName", "")
        customer   = f"{first} {last}".strip() or "N/A"

        print(f"{idx:<4} {uuid:<12} {dt:<22} {status:<20} {substatus:<30} {customer}")

    print(f"\nTotal jobs displayed: {len(jobs)}")


if __name__ == "__main__":
    main()
