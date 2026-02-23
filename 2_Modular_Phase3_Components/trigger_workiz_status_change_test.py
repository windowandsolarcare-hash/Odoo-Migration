"""
One-off: Change Workiz job KB9IH3 (Brenda Williams) to In Progress, then back to Canceled.
This should fire the Zap "Job Status Changed" twice; Phase 4 will run and (on first change)
create the SO in Odoo since the job currently has no SO.

Usage: python trigger_workiz_status_change_test.py
"""
import sys
import time
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from functions.workiz.get_job_details import get_job_details

JOB_UUID = "KB9IH3"  # Brenda Williams - from 39 list #9


def job_update(uuid, status, job_datetime=None, job_type=None, substatus=None):
    """POST job/update with required fields. Only add SubStatus if provided (Workiz validates values)."""
    job = get_job_details(uuid, quiet=True)
    if not job:
        print(f"[!] Could not fetch job {uuid}")
        return False
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": uuid,
        "Status": status,
        "JobDateTime": job.get("JobDateTime") or job_datetime or "2026-02-12T00:00:00.000Z",
        "JobType": job.get("JobType") or job_type or "Windows Inside & Outside Plus Screens",
    }
    # Only include SubStatus if provided (Workiz has a fixed list; "In Progress" as SubStatus was rejected)
    if substatus is not None:
        payload["SubStatus"] = substatus
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code in (200, 201, 204):
        print(f"[OK] Job {uuid} set to Status={status}")
        return True
    print(f"[!] job/update returned {r.status_code}: {r.text[:400]}")
    return False


def main():
    print("=" * 60)
    print("Trigger Zap test: KB9IH3 (Brenda Williams)")
    print("  1) Set status to In Progress (Zap should run -> Phase 4 -> create SO)")
    print("  2) Set status back to Canceled")
    print("=" * 60)

    # 1) In Progress (no SubStatus - Workiz may reject unknown SubStatus)
    if not job_update(JOB_UUID, "In Progress"):
        print("[!] First update failed; aborting.")
        return
    print("[*] Waiting 15s for Zap to run...")
    time.sleep(15)

    # 2) Back to Canceled
    if not job_update(JOB_UUID, "Canceled"):
        print("[!] Second update failed (job may still be In Progress in Workiz).")
    print("=" * 60)
    print("Done. Check Zapier task history and Odoo for new SO linked to job KB9IH3.")


if __name__ == "__main__":
    main()
