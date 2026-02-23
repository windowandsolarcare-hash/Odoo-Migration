"""
Fix historical SOs: set date_order and tag_ids from Workiz for any SO whose
order date (in Pacific) is outside business hours (7 AM - 6 PM).

- Batch: find all SOs with Workiz UUID where date_order (Pacific) is outside 7-6.
- One-by-one: GET job from Workiz, get JobDateTime + Tags, write date_order (UTC) and tag_ids to Odoo.
- Logs one line per job to terminal and to a log file: UUID, SO name, time (Pacific), tags, status.

Run from this folder:
  python fix_order_date_and_tags_from_workiz.py         # run for real
  python fix_order_date_and_tags_from_workiz.py --dry-run   # only list candidates, no Workiz/Odoo writes

Token note: Terminal and log file output do NOT use Cursor/LLM tokens; only chat uses tokens.
"""

import sys
import argparse
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import (
    ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
    WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET,
)
from functions.workiz.get_job_details import get_job_details
from functions.odoo.get_sales_tag_ids import get_sales_tag_ids
from functions.utils.convert_pacific_to_utc import convert_pacific_to_utc

# Business hours in Pacific: 7:00 AM (7) to 6:00 PM (18). Outside = before 7 or 6 PM and after.
BUSINESS_HOURS_START = 7   # 7 AM
BUSINESS_HOURS_END = 18    # 6 PM
WORKIZ_UUID_FIELD = "x_studio_x_studio_workiz_uuid"
LOG_DIR = os.path.dirname(__file__)


def _utc_str_to_pacific_hour(utc_datetime_str):
    """Return (hour_in_pacific, date_order as datetime) for business-hours check. DST-aware."""
    if not utc_datetime_str:
        return None, None
    try:
        from zoneinfo import ZoneInfo
        s = str(utc_datetime_str).strip()
        # Odoo date_order is naive "YYYY-MM-DD HH:MM:SS" (UTC)
        if "T" in s or "+" in s or "Z" in s:
            s = s.replace("Z", "+00:00")
            dt_utc = datetime.fromisoformat(s)
        else:
            dt_utc = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
        pacific = dt_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        return pacific.hour, pacific
    except Exception:
        return None, None


def _is_outside_business_hours(utc_datetime_str):
    """True if date_order (UTC) in Pacific is before 7 AM or at/after 6 PM."""
    hour, _ = _utc_str_to_pacific_hour(utc_datetime_str)
    if hour is None:
        return False
    return hour < BUSINESS_HOURS_START or hour >= BUSINESS_HOURS_END


def _utc_to_pacific_display(utc_datetime_str):
    """Format Odoo date_order (stored UTC) as Pacific for log - matches what user sees in Odoo (e.g. 12:00 AM)."""
    _, pacific_dt = _utc_str_to_pacific_hour(utc_datetime_str)
    if pacific_dt is None:
        return str(utc_datetime_str) if utc_datetime_str else "N/A"
    # e.g. "2025-11-14 12:00 AM" so it matches Odoo UI
    return pacific_dt.strftime("%Y-%m-%d %I:%M %p").replace(" 0", " ").strip()


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(
        ODOO_URL,
        json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    parser = argparse.ArgumentParser(description="Fix SO date_order and tags from Workiz (outside 7AM-6PM Pacific).")
    parser.add_argument("--dry-run", action="store_true", help="Only list candidates; do not fetch Workiz or write Odoo.")
    args = parser.parse_args()
    dry_run = getattr(args, "dry_run", False)

    log_fname = os.path.join(LOG_DIR, f"fix_order_date_and_tags_{datetime.now().strftime('%Y%m%d_%H%M')}.log")
    log_file = open(log_fname, "w", encoding="utf-8")

    def log(line):
        print(line)
        log_file.write(line + "\n")
        log_file.flush()

    log(f"# Fix order date and tags from Workiz - started {datetime.now().isoformat()}")
    log(f"# Business hours: {BUSINESS_HOURS_START}:00 - {BUSINESS_HOURS_END}:00 Pacific. Outside = candidate.")
    log("")

    # 1) Batch: get all SOs with Workiz UUID
    domain = [[WORKIZ_UUID_FIELD, "!=", False], [WORKIZ_UUID_FIELD, "!=", ""]]
    fields = ["id", "name", "date_order", WORKIZ_UUID_FIELD]
    all_sos = []
    offset = 0
    batch = 500
    while True:
        chunk = odoo_rpc(
            "sale.order",
            "search_read",
            [domain],
            {"fields": fields, "limit": batch, "offset": offset, "order": "id asc"},
        )
        if not chunk:
            break
        all_sos.extend(chunk)
        offset += len(chunk)
        if len(chunk) < batch:
            break
    log(f"# SOs with Workiz UUID: {len(all_sos)}")

    # 2) Filter: outside business hours (Pacific)
    candidates = []
    for so in all_sos:
        uuid_val = (so.get(WORKIZ_UUID_FIELD) or "").strip()
        if not uuid_val:
            continue
        date_order = so.get("date_order")
        if _is_outside_business_hours(date_order):
            candidates.append({
                "id": so["id"],
                "name": so["name"],
                "date_order": date_order,
                "uuid": uuid_val,
            })
    log(f"# Candidates (outside 7AM-6PM Pacific): {len(candidates)}")
    if dry_run:
        log("# DRY RUN: listing candidates only (no Workiz fetch, no Odoo write).")
        log("# current_time = as shown in Odoo (Pacific)")
        for c in candidates[:20]:
            current_pacific = _utc_to_pacific_display(c["date_order"])
            log(f"  would_process  SO={c['name']}  UUID={c['uuid']}  current_time={current_pacific}")
        if len(candidates) > 20:
            log(f"  ... and {len(candidates) - 20} more.")
        log(f"# Log file: {log_fname}")
        log_file.close()
        return
    log("")

    updated = 0
    skipped = 0
    errors = 0

    for i, c in enumerate(candidates, 1):
        so_id = c["id"]
        so_name = c["name"]
        uuid_val = c["uuid"]

        job = get_job_details(uuid_val, quiet=True)
        if not job:
            errors += 1
            current_pacific = _utc_to_pacific_display(c["date_order"])
            log(f"UUID={uuid_val}  SO={so_name}  current_time={current_pacific}  new_time=N/A  tags=N/A  status=error_no_job")
            time.sleep(0.3)
            continue

        job_datetime_str = (job.get("JobDateTime") or "").strip()
        tags_raw = job.get("Tags") or job.get("JobTags") or []
        if isinstance(tags_raw, str):
            tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
        elif isinstance(tags_raw, list):
            tags_list = [str(t).strip() for t in tags_raw if t]
        else:
            tags_list = []
        tag_names = ",".join(tags_list) if tags_list else ""

        if not job_datetime_str:
            skipped += 1
            current_pacific = _utc_to_pacific_display(c["date_order"])
            log(f"UUID={uuid_val}  SO={so_name}  current_time={current_pacific}  new_time=N/A  tags={tag_names}  status=skip_no_time")
            continue

        # JobDateTime from Workiz is Pacific
        new_date_utc = convert_pacific_to_utc(job_datetime_str)
        tag_ids = get_sales_tag_ids(tags_list) if tags_list else []

        updates = {"date_order": new_date_utc}
        if tag_ids:
            updates["tag_ids"] = [(6, 0, tag_ids)]

        try:
            odoo_rpc("sale.order", "write", [[so_id], updates])
            updated += 1
            current_pacific = _utc_to_pacific_display(c["date_order"])
            log(f"UUID={uuid_val}  SO={so_name}  current_time={current_pacific}  new_time={job_datetime_str}  tags={tag_names}  status=updated")
        except Exception as e:
            errors += 1
            current_pacific = _utc_to_pacific_display(c["date_order"])
            log(f"UUID={uuid_val}  SO={so_name}  current_time={current_pacific}  new_time={job_datetime_str}  tags={tag_names}  status=error_write {e}")

        time.sleep(0.25)

    log("")
    log(f"# Done. updated={updated}  skipped={skipped}  errors={errors}")
    log(f"# Log file: {log_fname}")
    log_file.close()


if __name__ == "__main__":
    main()
