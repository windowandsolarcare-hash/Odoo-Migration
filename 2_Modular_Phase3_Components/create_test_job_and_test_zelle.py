"""
Create a test job in Workiz, then test addPayment with type "zelle".
Uses job/all to get the new job's UUID after create (create returns 204, no UUID).

Run from 2_Modular_Phase3_Components: python create_test_job_and_test_zelle.py
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))

import requests
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from functions.workiz.add_payment import add_payment

# Unique note so we can find the test job in job/all
TEST_JOB_NOTES = "PHASE6-TEST-ZELLE-DELETE-ME"


def job_all(start_date=None, records=20, only_open=True):
    """GET /job/all/ - returns list of jobs (sorted by JobDateTime desc)."""
    if start_date is None:
        start_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/?auth_secret={WORKIZ_AUTH_SECRET}&start_date={start_date}&records={records}&only_open={str(only_open).lower()}"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return None, r.text
    data = r.json()
    # Response can be array or { data: [...] }
    if isinstance(data, list):
        return data, None
    return data.get("data", data) if isinstance(data, dict) else [], None


def create_test_job(client_id, first_name, last_name, address, city, state, postal_code, phone, job_type, service_area, job_datetime):
    """POST /job/create/ with minimal required fields. Returns success; UUID from job/all."""
    url = f"{WORKIZ_BASE_URL.rstrip('/')}/job/create/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": int(client_id),
        "FirstName": first_name,
        "LastName": last_name,
        "Address": address,
        "City": city,
        "State": state,
        "PostalCode": str(postal_code),
        "Phone": str(phone),
        "JobDateTime": job_datetime,
        "JobType": job_type,
        "ServiceArea": service_area,
        "JobNotes": TEST_JOB_NOTES,
    }
    r = requests.post(url, json=payload, timeout=15)
    if r.status_code in (200, 201, 204):
        return True, r.text
    return False, r.text


def main():
    print("=" * 60)
    print("Phase 6: Create test job, then test addPayment type 'zelle'")
    print("=" * 60)

    # 1) Get recent jobs to use one client for the test job
    jobs, err = job_all(records=10, only_open=True)
    if err or not jobs:
        print("[!] Could not fetch jobs from job/all:", err or "empty list")
        return

    # Use first job's client/data so create has valid ClientId and JobType/ServiceArea
    template = jobs[0] if isinstance(jobs[0], dict) else jobs[0]
    client_id = template.get("ClientId")
    if not client_id:
        print("[!] No ClientId in job/all response")
        return

    first = template.get("FirstName", "Phase6")
    last = template.get("LastName", "Test")
    address = template.get("Address", "123 Test St")
    city = template.get("City", "Palm Springs")
    state = template.get("State", "CA")
    postal = template.get("PostalCode", "92262")
    phone = template.get("Phone", "7605550000")
    job_type = template.get("JobType", "Windows Inside & Outside Plus Screens")
    service_area = template.get("ServiceArea", "metro1") or "metro1"
    job_datetime = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

    print(f"[1] Using ClientId {client_id} to create test job...")

    ok, create_resp = create_test_job(client_id, first, last, address, city, state, postal, phone, job_type, service_area, job_datetime)
    if not ok:
        print("[!] Create failed:", create_resp[:500])
        return

    print("[2] Create returned success. Fetching job/all to get new job UUID...")

    # 2) Get jobs again; find the one we just created (by JobNotes or most recent for this client)
    jobs2, err2 = job_all(records=15, only_open=True)
    if err2 or not jobs2:
        print("[!] job/all after create failed or empty:", err2 or "empty")
        return

    # Find job with our test note
    test_job = None
    for j in jobs2:
        j = j if isinstance(j, dict) else j
        if (j.get("JobNotes") or "").strip() == TEST_JOB_NOTES:
            test_job = j
            break
    if not test_job:
        # Fallback: same client, created very recently (first in list by JobDateTime desc)
        for j in jobs2:
            j = j if isinstance(j, dict) else j
            if j.get("ClientId") == client_id:
                test_job = j
                break

    if not test_job:
        print("[!] Could not find new test job in job/all")
        return

    job_uuid = test_job.get("UUID")
    if not job_uuid:
        print("[!] No UUID in job:", list(test_job.keys())[:10])
        return

    print(f"[3] Test job UUID: {job_uuid}")

    # 3) Add payment with type "zelle"
    date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    result = add_payment(job_uuid, 0.01, "zelle", date_str, reference="PHASE6-ZELLE-TEST")

    print()
    if result.get("success"):
        print("[OK] addPayment with type 'zelle' succeeded. Workiz API accepts 'zelle'.")
    else:
        print("[FAIL] addPayment failed:", result.get("message", ""), result.get("body", ""))

    print("=" * 60)


if __name__ == "__main__":
    main()
