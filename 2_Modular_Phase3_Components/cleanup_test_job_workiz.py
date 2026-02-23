"""
Cancel a Phase 6 test job in Workiz (set Status to Canceled).
Uses job/update with JobDateTime and JobType from current job so update succeeds.

Usage: Set TEST_JOB_UUID in the script or env, then run:
  python cleanup_test_job_workiz.py
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

import requests
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from functions.workiz.get_job_details import get_job_details

TEST_JOB_UUID = os.environ.get("TEST_JOB_UUID", "").strip() or "REPLACE_WITH_JOB_UUID"


def main():
    if not TEST_JOB_UUID or TEST_JOB_UUID == "REPLACE_WITH_JOB_UUID":
        print("Set TEST_JOB_UUID (env or in script) to the job UUID to cancel.")
        return

    print("=" * 60)
    print("Cleanup: Cancel test job in Workiz")
    print("=" * 60)

    job = get_job_details(TEST_JOB_UUID)
    if not job:
        print("[!] Could not fetch job (may already be gone)")
        return

    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": TEST_JOB_UUID,
        "Status": "Canceled",
        "JobDateTime": job.get("JobDateTime") or "2026-02-12T00:00:00.000Z",
        "JobType": job.get("JobType") or "Windows Inside & Outside Plus Screens",
    }

    r = requests.post(url, json=payload, timeout=15)
    if r.status_code in (200, 201, 204):
        print(f"[OK] Job {TEST_JOB_UUID} set to Canceled.")
    else:
        print(f"[!] Update returned {r.status_code}:", r.text[:300])
        payload["Status"] = "Cancelled"
        r2 = requests.post(url, json=payload, timeout=15)
        if r2.status_code in (200, 201, 204):
            print(f"[OK] Job {TEST_JOB_UUID} set to Cancelled.")
        else:
            print(f"[!] Cancelled also failed: {r2.status_code}", r2.text[:300])
    print("=" * 60)


if __name__ == "__main__":
    main()
