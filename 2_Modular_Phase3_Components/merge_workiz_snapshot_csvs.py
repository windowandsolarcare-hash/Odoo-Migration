"""
Merge two Workiz snapshot CSVs into one (dedupe by UUID).
Use this after a resume run: e.g. you have workiz_full_snapshot_20260218.csv (missing closed 19-22),
then after quota reset you run export_workiz_full_snapshot.py --resume-closed-interval 19 --output workiz_resume.csv,
then run this to merge: new rows (by UUID) from the second file are added to the first.

  python merge_workiz_snapshot_csvs.py base.csv new.csv
  python merge_workiz_snapshot_csvs.py base.csv new.csv --output merged.csv
"""
import sys
import os
import csv
import argparse

SNAPSHOT_COLUMNS = [
    "UUID", "ClientId", "Address", "City", "State", "PostalCode",
    "FirstName", "LastName", "JobDateTime", "Status",
    "frequency", "type_of_service", "JobType", "SubStatus",
]


def main():
    parser = argparse.ArgumentParser(description="Merge two Workiz snapshot CSVs by UUID.")
    parser.add_argument("base", help="Existing snapshot CSV (primary).")
    parser.add_argument("new", help="New/resume snapshot CSV (add missing UUIDs).")
    parser.add_argument("--output", "-o", default=None, help="Output merged CSV. Default: overwrite base with merged.")
    args = parser.parse_args()
    base_path = args.base
    new_path = args.new
    out_path = args.output or base_path

    if not os.path.isfile(base_path):
        print(f"[!] Base file not found: {base_path}")
        return
    if not os.path.isfile(new_path):
        print(f"[!] New file not found: {new_path}")
        return

    seen = set()
    rows = []
    with open(base_path, "r", encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        for row in r:
            uid = (row.get("UUID") or "").strip()
            if uid and uid not in seen:
                seen.add(uid)
                rows.append(row)
    base_count = len(rows)
    added = 0
    with open(new_path, "r", encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        for row in r:
            uid = (row.get("UUID") or "").strip()
            if uid and uid not in seen:
                seen.add(uid)
                rows.append(row)
                added += 1
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SNAPSHOT_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] Base: {base_count} rows. Added from new: {added}. Total: {len(rows)}. Wrote {out_path}")


if __name__ == "__main__":
    main()
