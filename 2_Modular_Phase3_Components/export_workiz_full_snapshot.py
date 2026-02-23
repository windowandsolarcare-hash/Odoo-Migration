"""
Build a full Workiz snapshot CSV from the API only (no Holy Grail dependency).

API: GET job/all
  start_date (yyyy-MM-dd), offset (page index = interval), records (max 100), only_open (bool).
  INTERVAL is 0, 1, 2, 3, 4, 5 ... (not 100, 200, 300).
  interval 0 → records 1–100, interval 1 → 101–200, interval 2 → 201–300, ...
  We pass interval as the offset parameter: offset=0, offset=1, offset=2, ...

We fetch ALL jobs in two passes:
  1) only_open=True  → open jobs (interval 0, 1, 2, 3, ... until no more)
  2) only_open=False → closed/done/canceled (interval 0, 1, 2, 3, ... until no more)

Delay: 1.2 seconds between each API call (after each 100 records).

On error: we log interval + only_open + error; retry; then continue. Resume with --resume-open-interval N.

Usage:
  python export_workiz_full_snapshot.py
  python export_workiz_full_snapshot.py --resume-open-interval 5   # resume from interval 5 after error
"""
import sys
import os
import csv
import argparse
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import requests
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HOLY_GRAIL_CSV = os.path.join(
    PROJECT_ROOT,
    "2_Migration_Archive",
    "Holy Grale Data - Done Stutus",
    "Workiz_6Year_Done_History_Master.csv",
)
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "2_Migration_Archive")
SNAPSHOT_COLUMNS = [
    "UUID", "ClientId", "Address", "City", "State", "PostalCode",
    "FirstName", "LastName", "JobDateTime", "Status",
    "frequency", "type_of_service", "JobType", "SubStatus",
]

RECORDS_PER_REQUEST = 100
DEFAULT_DELAY_SEC = 1.2
MAX_RETRIES = 3


def job_all_interval(start_date, interval, records=100, only_open=True):
    """
    GET /job/all/ with INTERVAL (page index) = 0, 1, 2, 3, 4, 5 ...
    interval 0 → first 100, interval 1 → next 100, interval 2 → next 100, etc.
    We pass interval as the offset query param (value is 0,1,2,3 not 0,100,200).
    Returns (list of jobs, has_more_or_none, None) or ([], None, error_message).
    """
    url = (
        f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/"
        f"?auth_secret={WORKIZ_AUTH_SECRET}&start_date={start_date}&records={records}"
        f"&only_open={str(only_open).lower()}&offset={interval}"
    )
    try:
        r = requests.get(url, timeout=90)
        if r.status_code != 200:
            return [], None, f"HTTP {r.status_code}: {r.text[:400]}"
        data = r.json()
        jobs = []
        has_more = None
        if isinstance(data, list):
            jobs = data
        elif isinstance(data, dict):
            jobs = data.get("data", data.get("jobs", []))
            if not isinstance(jobs, list):
                jobs = []
            # Response code / "more data" indicator (name may vary)
            has_more = data.get("has_more", data.get("more", data.get("next_offset") is not None))
            if has_more is None and "code" in data:
                code = data.get("code")
                has_more = code not in (0, "0", "no_more", "end", None)
        return (jobs, has_more, None)
    except Exception as e:
        return [], None, str(e)


def row_from_api_job(job, status_label):
    """Build a snapshot row from job/all API response."""
    def get(key, default=""):
        v = job.get(key) or job.get(key.replace("Id", "ID")) or default
        if v is None:
            return ""
        return str(v).strip() if not isinstance(v, str) else v.strip()
    # Prefer API Status if present (Done, Canceled, etc.)
    status = get("Status") or status_label
    return {
        "UUID": get("UUID"),
        "ClientId": get("ClientId"),
        "Address": get("Address"),
        "City": get("City"),
        "State": get("State"),
        "PostalCode": get("PostalCode"),
        "FirstName": get("FirstName"),
        "LastName": get("LastName"),
        "JobDateTime": get("JobDateTime"),
        "Status": status,
        "frequency": get("frequency"),
        "type_of_service": get("type_of_service"),
        "JobType": get("JobType"),
        "SubStatus": get("SubStatus"),
    }


def fetch_all_jobs_one_pass(
    start_date, only_open, start_interval=0, records_per_request=100, delay_sec=1.2,
    error_log_path=None,
):
    """
    Fetch all jobs for one only_open value using INTERVAL = 0, 1, 2, 3, 4, 5 ...
    On error: log interval + error, retry, then continue to next interval. Resume with --resume-*-interval N.
    """
    label = "open" if only_open else "closed"
    status_label = "Open" if only_open else "Done"
    collected = []
    seen_uuids = set()
    interval = start_interval
    last_error_interval = None
    last_error_msg = None

    def log_error(ival, msg):
        line = f"[{datetime.now(timezone.utc).isoformat()}] interval={ival} only_open={only_open} error={msg}\n"
        print(f"  [ERROR] job/all interval={ival} only_open={only_open}: {msg}")
        if error_log_path:
            try:
                with open(error_log_path, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                pass
        print(f"  [RESUME] To retry from this point: --resume-{'open' if only_open else 'closed'}-interval {ival}")

    while True:
        jobs, has_more, err = job_all_interval(
            start_date, interval, records=records_per_request, only_open=only_open
        )
        if err:
            last_error_interval = interval
            last_error_msg = err
            for attempt in range(MAX_RETRIES):
                time.sleep(delay_sec * (attempt + 1))
                jobs, has_more, err = job_all_interval(
                    start_date, interval, records=records_per_request, only_open=only_open
                )
                if not err:
                    break
                log_error(interval, f"retry {attempt + 1}/{MAX_RETRIES}: {err}")
            if err:
                log_error(interval, err)
                interval += 1
                continue
        for j in (jobs or []):
            if not isinstance(j, dict):
                continue
            u = (j.get("UUID") or j.get("uuid") or "").strip()
            if u and u not in seen_uuids:
                seen_uuids.add(u)
                collected.append(row_from_api_job(j, status_label))
        got = len(jobs) if jobs else 0
        if got < records_per_request:
            break
        if has_more is False:
            break
        interval += 1
        time.sleep(delay_sec)
    print(f"  [*] {label}: {len(collected)} unique jobs (intervals {start_interval} to {interval})")
    if last_error_msg:
        print(f"  [*] Last error was at interval={last_error_interval}; use --resume-*-interval to retry.")
    return collected


def main():
    parser = argparse.ArgumentParser(
        description="Export full Workiz snapshot from API (interval 0,1,2,3... = 100 records each)."
    )
    parser.add_argument(
        "--start-date",
        default="2019-01-01",
        help="Start date for job/all (default 2019-01-01).",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=RECORDS_PER_REQUEST,
        help=f"Records per request, max 100 (default {RECORDS_PER_REQUEST}).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SEC,
        help=f"Seconds between API requests (default {DEFAULT_DELAY_SEC}).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output CSV path. Default: 2_Migration_Archive/workiz_full_snapshot_YYYYMMDD.csv",
    )
    parser.add_argument(
        "--resume-open-interval",
        type=int,
        default=0,
        help="Resume open-job fetch from this interval (0, 1, 2, 3...). Use after an error.",
    )
    parser.add_argument(
        "--resume-closed-interval",
        type=int,
        default=0,
        help="Resume closed-job fetch from this interval (0, 1, 2, 3...). Use after an error.",
    )
    parser.add_argument(
        "--holy-grail",
        action="store_true",
        help="Optionally merge Holy Grail CSV (done jobs) into snapshot.",
    )
    parser.add_argument("--csv", default=DEFAULT_HOLY_GRAIL_CSV, help="Path to Holy Grail CSV (used only if --holy-grail).")
    args = parser.parse_args()

    start_date = args.start_date
    delay_sec = args.delay
    records_per_request = min(100, max(1, args.records))
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    error_log_path = os.path.join(DEFAULT_OUTPUT_DIR, f"export_workiz_errors_{ts}.log")
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    all_rows = []
    seen_uuids = set()

    # 1) Fetch all OPEN jobs (interval 0, 1, 2, 3, ...)
    print(f"[*] Fetching OPEN jobs from API (start_date={start_date}, interval 0,1,2,3..., {records_per_request} per request, delay={delay_sec}s)...")
    open_rows = fetch_all_jobs_one_pass(
        start_date, only_open=True, start_interval=args.resume_open_interval,
        records_per_request=records_per_request, delay_sec=delay_sec,
        error_log_path=error_log_path,
    )
    for r in open_rows:
        if r["UUID"] and r["UUID"] not in seen_uuids:
            seen_uuids.add(r["UUID"])
            all_rows.append(r)
    time.sleep(delay_sec)

    # 2) Fetch all CLOSED/DONE/CANCELED jobs (interval 0, 1, 2, 3, ...)
    print(f"[*] Fetching CLOSED/DONE/CANCELED jobs from API (same start_date, interval 0,1,2,3..., delay={delay_sec}s)...")
    closed_rows = fetch_all_jobs_one_pass(
        start_date, only_open=False, start_interval=args.resume_closed_interval,
        records_per_request=records_per_request, delay_sec=delay_sec,
        error_log_path=error_log_path,
    )
    for r in closed_rows:
        if r["UUID"] and r["UUID"] not in seen_uuids:
            seen_uuids.add(r["UUID"])
            all_rows.append(r)

    # 3) Optional: merge Holy Grail (done) so any missing-from-API rows are included
    if args.holy_grail and os.path.isfile(args.csv):
        print(f"[*] Merging Holy Grail (done jobs): {args.csv}")
        def get(row_dict, key, default=""):
            v = row_dict.get(key) or row_dict.get(key.replace("_", " ")) or default
            return (v if v is not None else "").strip() if isinstance(v, str) else (str(v).strip() if v is not None else "")
        added = 0
        with open(args.csv, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = get(row, "UUID")
                if not uid or uid in seen_uuids:
                    continue
                seen_uuids.add(uid)
                added += 1
                all_rows.append({
                    "UUID": uid,
                    "ClientId": get(row, "ClientId"),
                    "Address": get(row, "Address"),
                    "City": get(row, "City"),
                    "State": get(row, "State"),
                    "PostalCode": get(row, "PostalCode"),
                    "FirstName": get(row, "FirstName"),
                    "LastName": get(row, "LastName"),
                    "JobDateTime": get(row, "JobDateTime"),
                    "Status": "Done",
                    "frequency": get(row, "frequency"),
                    "type_of_service": get(row, "type_of_service"),
                    "JobType": get(row, "JobType"),
                    "SubStatus": get(row, "SubStatus"),
                })
        print(f"    Added from Holy Grail (not in API): {added}")

    print(f"\n[*] Total unique jobs in snapshot: {len(all_rows)}")

    if not all_rows:
        print("[!] No rows to write.")
        return

    out_path = args.output
    if not out_path:
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(DEFAULT_OUTPUT_DIR, f"workiz_full_snapshot_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SNAPSHOT_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)
    print(f"\n[OK] Wrote {len(all_rows)} rows to {out_path}")
    print("     Use this file to compare against Odoo (contacts, properties, sales orders) without API calls.")


if __name__ == "__main__":
    main()
