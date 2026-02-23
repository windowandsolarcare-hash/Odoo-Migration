"""
Phase 6B: Sync all open Workiz jobs to Odoo (create or update SO per job).

- Uses Workiz GET /job/all/?only_open=true (excludes Done and Canceled).
- Pagination: offset 0, 1, 2, 3, 4... (per Workiz support; each page = 100 records).
- For each job UUID, runs Phase 4 in-process (one Workiz call per job). No Personal Time
  filtering — bring all over; you can sort/delete Personal Time in Odoo.
- Delay between jobs to avoid Workiz 429; retry once after 5s on fetch/429 errors.

Run from 2_Modular_Phase3_Components:
  python phase6b_sync_open_jobs_to_odoo.py 2020-01-01       # full backfill
  python phase6b_sync_open_jobs_to_odoo.py 2020-01-01 50    # first 50 (test)

Optional env:
  PHASE6B_START_DATE=2020-01-01  (yyyy-MM-dd)
  PHASE6B_DRY_RUN=1              (only list UUIDs, do not call Phase 4)
  PHASE6B_LIMIT=50               (process only first N jobs)
  PHASE6B_DELAY_SECONDS=1.2     (delay between jobs; default 1.2 to avoid rate limit)
"""

import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from functions.workiz.list_open_jobs import list_open_jobs
from phase4_status_update_router import main as phase4_main

RECORDS_PER_PAGE = 100


def main(start_date=None, dry_run=False, limit=None, delay_seconds=1.2):
    """
    List all open jobs (paginated: offset 0, 1, 2, 3...), then for each UUID run Phase 4 in-process.

    Args:
        start_date (str|None): yyyy-MM-dd. If None, use 1 year ago.
        dry_run (bool): If True, only list UUIDs and counts; do not call Phase 4.
        limit (int|None): If set, process only first N jobs (for testing). None = all.
        delay_seconds (float): Sleep between each job to avoid Workiz 429 (default 1.2).

    Returns:
        dict: total_jobs, processed, success, failed, errors (list of {uuid, error})
    """
    if start_date is None:
        start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    print("\n" + "="*70)
    print("PHASE 6B: SYNC OPEN WORKIZ JOBS TO ODOO")
    print("="*70)
    print(f"Start date: {start_date}  (only_open=true, offset 0,1,2,3...)")
    if limit:
        print(f"Limit: first {limit} jobs only (test run)")
    if dry_run:
        print("[DRY RUN] Will not call Phase 4")
    print(f"Delay between jobs: {delay_seconds}s (set PHASE6B_DELAY_SECONDS to change)")
    print("(Phase 4 runs in this process — no Zapier calls)")
    print()

    all_uuids = []
    offset = 0  # Page index: 0, 1, 2, 3, 4... (each page = 100 records, per Workiz support)
    while True:
        jobs, err = list_open_jobs(start_date=start_date, records=RECORDS_PER_PAGE, offset=offset)
        if err:
            print(f"[ERROR] list_open_jobs offset={offset}: {err}")
            return {
                "total_jobs": len(all_uuids),
                "processed": 0,
                "success": 0,
                "failed": 0,
                "errors": [{"offset": offset, "error": err}],
            }
        if not jobs:
            break
        for j in jobs:
            j = j if isinstance(j, dict) else j
            u = j.get("UUID")
            if u:
                all_uuids.append(u)
        print(f"  Fetched offset {offset}: {len(jobs)} jobs (total UUIDs so far: {len(all_uuids)})")
        if len(jobs) < RECORDS_PER_PAGE:
            break
        offset += 1  # Next page (0, 1, 2, 3... per Workiz API)

    if limit and limit > 0:
        all_uuids = all_uuids[:limit]
        print(f"\n[*] Limited to first {limit} jobs (test)")
    total = len(all_uuids)
    print(f"\n[*] Total open jobs to sync: {total}")
    if total == 0:
        return {"total_jobs": 0, "processed": 0, "success": 0, "failed": 0, "errors": []}

    if dry_run:
        for i, u in enumerate(all_uuids[:20], 1):
            print(f"  {i}. {u}")
        if total > 20:
            print(f"  ... and {total - 20} more")
        return {"total_jobs": total, "dry_run": True, "uuids": all_uuids}

    success = 0
    failed = 0
    errors = []
    for i, job_uuid in enumerate(all_uuids, 1):
        print(f"\n[{i}/{total}] Job UUID: {job_uuid}")
        result = phase4_main({"job_uuid": job_uuid})
        if not result.get("success"):
            err = result.get("error", "unknown")
            err_lower = str(err).lower()
            if ("fetch" in err_lower or "429" in err_lower) and delay_seconds < 2:
                print(f"  [retry after 5s]")
                time.sleep(5)
                result = phase4_main({"job_uuid": job_uuid})
        if result.get("success"):
            success += 1
        else:
            failed += 1
            errors.append({"uuid": job_uuid, "error": result.get("error", "unknown")})
            print(f"  [!] Phase 4 failed: {result.get('error', result)}")
        if i < total:
            time.sleep(delay_seconds)

    print("\n" + "="*70)
    print("PHASE 6B COMPLETE")
    print("="*70)
    print(f"Total open jobs: {total}  |  Success: {success}  |  Failed: {failed}")
    if errors:
        print("Errors:")
        for e in errors[:10]:
            print(f"  {e['uuid']}: {e['error']}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    return {
        "total_jobs": total,
        "processed": success + failed,
        "success": success,
        "failed": failed,
        "errors": errors,
    }


if __name__ == "__main__":
    start = os.environ.get("PHASE6B_START_DATE")
    lim = os.environ.get("PHASE6B_LIMIT")
    if len(sys.argv) >= 2:
        start = start or sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            lim = int(sys.argv[2])
        except ValueError:
            lim = None
    if lim is not None and isinstance(lim, str):
        try:
            lim = int(lim)
        except ValueError:
            lim = None
    dry = os.environ.get("PHASE6B_DRY_RUN", "").strip() in ("1", "true", "yes")
    try:
        d = float(os.environ.get("PHASE6B_DELAY_SECONDS", "1.2"))
    except (ValueError, TypeError):
        d = 1.2
    main(start_date=start, dry_run=dry, limit=lim, delay_seconds=d)
