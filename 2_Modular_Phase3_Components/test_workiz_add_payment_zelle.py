"""
Test Workiz addPayment with type "zelle" (and optionally mark job Done).
Use a TEST job UUID only — do not use a real customer job.

Create a test job in Workiz UI (or use a job you can afford to test on), copy its UUID,
then run:
  TEST_JOB_UUID=YOUR_UUID python test_workiz_add_payment_zelle.py
or set TEST_JOB_UUID in the script below.

Tests whether the API accepts payment type "zelle" (doc says only cash/credit/check).
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from functions.workiz.add_payment import add_payment
from functions.workiz.mark_job_done import mark_job_done

# Use a test job UUID — set via env or replace here. Do NOT use a real job.
TEST_JOB_UUID = os.environ.get("TEST_JOB_UUID", "").strip() or "REPLACE_WITH_TEST_JOB_UUID"


def main():
    if not TEST_JOB_UUID or TEST_JOB_UUID == "REPLACE_WITH_TEST_JOB_UUID":
        print("Set TEST_JOB_UUID (env or in script) to a test job UUID. Do not use a real job.")
        return

    from datetime import datetime
    date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    amount = 0.01  # Minimal amount for test

    print("=" * 60)
    print("Test: Workiz addPayment with type 'zelle'")
    print("=" * 60)
    print(f"Job UUID: {TEST_JOB_UUID}")
    print(f"Amount: ${amount}, Date: {date_str}, Type: zelle")
    print()

    result = add_payment(TEST_JOB_UUID, amount, "zelle", date_str, reference="TEST-ZELLE-PHASE6")
    if result.get("success"):
        print("[OK] addPayment with type 'zelle' succeeded. Workiz API accepts 'zelle'.")
    else:
        print("[FAIL]", result.get("message", ""), result.get("body", ""))

    # Optionally mark job Done (uncomment if you want to test full flow on test job)
    # out = mark_job_done(TEST_JOB_UUID)
    # print("[mark_done]", "OK" if out.get("success") else out.get("message"))

    print("=" * 60)


if __name__ == "__main__":
    main()
