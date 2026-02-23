"""
Extract failed UUIDs from Phase 6B log and retry with 2s delay.
Usage: python retry_failed_144.py <path_to_log_txt>
Or run from same dir and pass the agent-tools log path.
"""
import re
import sys
import time
import os

sys.path.insert(0, os.path.dirname(__file__))
from phase4_status_update_router import main as phase4_main

LOG = r"C:\Users\dj\.cursor\projects\c-Users-dj-Documents-Business-A-Window-and-Solar-Care-Migration-to-Odoo\agent-tools\b8e8d631-9899-495e-b4bc-272c63d576d1.txt"

def extract_failed_uuids(log_path):
    current = None
    failed = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(r"Job UUID:\s*(\w+)", line)
            if m:
                current = m.group(1)
            if "Phase 4 failed: Failed to fetch Workiz job" in line and current:
                failed.append(current)
                current = None
    return failed

def main():
    log_path = sys.argv[1] if len(sys.argv) > 1 else LOG
    if not os.path.isfile(log_path):
        print("Log file not found:", log_path)
        return
    uuids = extract_failed_uuids(log_path)
    print(f"Found {len(uuids)} failed UUIDs to retry (2s delay)")
    success = 0
    failed = 0
    for i, u in enumerate(uuids, 1):
        print(f"\n[{i}/{len(uuids)}] {u}")
        r = phase4_main({"job_uuid": u})
        if r.get("success"):
            success += 1
        else:
            failed += 1
            print("  [!]", r.get("error", r))
        if i < len(uuids):
            time.sleep(2)
    print("\n" + "="*60)
    print(f"Retry done: Success {success} | Failed {failed}")

if __name__ == "__main__":
    main()
