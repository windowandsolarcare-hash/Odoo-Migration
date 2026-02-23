"""
Compare Workiz snapshot CSV to Odoo: SALES ORDERS (mirror check by Workiz UUID).
Read-only. No changes to Odoo.

- Workiz: each row in the CSV = one job (UUID). We collect unique UUIDs from the snapshot.
- Odoo: sale.order records with x_studio_x_studio_workiz_uuid set.
- Report: matched UUIDs; jobs in Workiz snapshot with no Odoo SO; SOs in Odoo with UUID not in snapshot.

Uses same Workiz snapshot CSV as compare_workiz_odoo_contacts_properties.py.
Default = LIVE. Use --test for test DB.

  python compare_workiz_odoo_sales_orders.py
  python compare_workiz_odoo_sales_orders.py --test
  python compare_workiz_odoo_sales_orders.py --csv "path/to/workiz_full_snapshot_merged.csv" --output report.txt
"""
import sys
import os
import csv
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import requests

from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY
from config import ODOO_URL as PROD_URL, ODOO_DB as PROD_DB, ODOO_USER_ID as PROD_UID, ODOO_API_KEY as PROD_KEY

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_WORKIZ_CSV = os.path.join(PROJECT_ROOT, "2_Migration_Archive", "workiz_full_snapshot_20260218_merged.csv")
DEFAULT_REPORT_DIR = os.path.join(PROJECT_ROOT, "2_Migration_Archive")
WORKIZ_UUID_FIELD = "x_studio_x_studio_workiz_uuid"

ODOO_URL = PROD_URL
ODOO_DB = PROD_DB
ODOO_USER_ID = PROD_UID
ODOO_API_KEY = PROD_KEY


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0", "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params},
    }, timeout=120)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Compare Workiz snapshot to Odoo sales orders by UUID (mirror check).")
    parser.add_argument("--csv", default=DEFAULT_WORKIZ_CSV, help="Workiz snapshot CSV (merged).")
    parser.add_argument("--test", action="store_true", help="Use Odoo TEST database.")
    parser.add_argument("--output", default=None, help="Report output path. Default: 2_Migration_Archive/compare_sales_orders_YYYYMMDD_HHMM.txt")
    args = parser.parse_args()

    if args.test:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        print("[TEST] Odoo DB:", ODOO_DB)
    else:
        print("[LIVE] Odoo DB:", ODOO_DB)

    if not os.path.isfile(args.csv):
        print(f"[!] Workiz CSV not found: {args.csv}")
        return

    # ---- Load Workiz: unique job UUIDs from snapshot ----
    workiz_uuids = set()
    workiz_uuid_to_row = {}  # first row per UUID for reporting (ClientId, Address, JobDateTime, etc.)
    with open(args.csv, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            u = (row.get("UUID") or "").strip()
            if u:
                workiz_uuids.add(u)
                if u not in workiz_uuid_to_row:
                    workiz_uuid_to_row[u] = {
                        "ClientId": (row.get("ClientId") or "").strip(),
                        "Address": (row.get("Address") or "").strip(),
                        "City": (row.get("City") or "").strip(),
                        "PostalCode": (row.get("PostalCode") or "").strip(),
                        "JobDateTime": (row.get("JobDateTime") or "").strip(),
                        "Status": (row.get("Status") or "").strip(),
                        "FirstName": (row.get("FirstName") or "").strip(),
                        "LastName": (row.get("LastName") or "").strip(),
                    }

    print(f"[*] Workiz snapshot: {len(workiz_uuids)} unique job UUIDs (from CSV)")

    # ---- Load Odoo: SOs with Workiz UUID ----
    sos = odoo_rpc("sale.order", "search_read", [[[WORKIZ_UUID_FIELD, "!=", False]]], {
        "fields": ["id", "name", WORKIZ_UUID_FIELD, "state", "date_order", "partner_id", "partner_shipping_id"],
        "limit": 50000,
    })
    odoo_uuid_to_so = {}
    for so in sos:
        u = (so.get(WORKIZ_UUID_FIELD) or "").strip()
        if u:
            odoo_uuid_to_so[u] = so
    odoo_uuids = set(odoo_uuid_to_so.keys())
    total_sos = odoo_rpc("sale.order", "search_count", [[]])
    so_with_uuid_count = len(odoo_uuids)

    print(f"[*] Odoo: total SOs={total_sos}, SOs with Workiz UUID={so_with_uuid_count}")

    # ---- Compare ----
    matched = workiz_uuids & odoo_uuids
    only_in_workiz = sorted(workiz_uuids - odoo_uuids)   # jobs in Workiz snapshot with no Odoo SO
    only_in_odoo = sorted(odoo_uuids - workiz_uuids)    # SOs in Odoo whose UUID not in this snapshot

    # ---- Write report ----
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out_path = args.output or os.path.join(DEFAULT_REPORT_DIR, f"compare_sales_orders_{ts}.txt")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    lines = []
    lines.append("=" * 60)
    lines.append("Workiz vs Odoo: SALES ORDERS (mirror check by Workiz UUID)")
    lines.append(f"Workiz CSV: {args.csv}")
    lines.append(f"Odoo DB: {ODOO_DB}")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("=" * 60)

    lines.append("\n--- COUNTS ---")
    lines.append(f"Workiz snapshot: {len(workiz_uuids)} unique job UUIDs")
    lines.append(f"Odoo total SOs: {total_sos}")
    lines.append(f"Odoo SOs with Workiz UUID: {so_with_uuid_count}")
    lines.append(f"Matched (in both): {len(matched)}")
    lines.append(f"Only in Workiz (job in snapshot, no Odoo SO): {len(only_in_workiz)}")
    lines.append(f"Only in Odoo (SO has UUID not in this snapshot): {len(only_in_odoo)}")

    lines.append("\n--- ONLY IN WORKIZ (no Odoo SO for this UUID) ---")
    if only_in_workiz:
        for u in only_in_workiz[:100]:
            row = workiz_uuid_to_row.get(u, {})
            addr = row.get("Address", "") or "(no address)"
            client = row.get("ClientId", "")
            dt = row.get("JobDateTime", "")
            lines.append(f"  UUID={u}  ClientId={client}  {addr[:45]}  {dt}")
        if len(only_in_workiz) > 100:
            lines.append(f"  ... and {len(only_in_workiz) - 100} more.")
    else:
        lines.append("  (none)")

    lines.append("\n--- ONLY IN ODOO (UUID not in Workiz snapshot) ---")
    if only_in_odoo:
        for u in only_in_odoo[:100]:
            so = odoo_uuid_to_so.get(u, {})
            name = so.get("name", "")
            lines.append(f"  UUID={u}  Odoo SO: {name}")
        if len(only_in_odoo) > 100:
            lines.append(f"  ... and {len(only_in_odoo) - 100} more.")
    else:
        lines.append("  (none)")

    lines.append("\n--- SUMMARY ---")
    if len(matched) == len(workiz_uuids) and len(only_in_workiz) == 0:
        lines.append("  Mirror: every Workiz job in the snapshot has an Odoo SO.")
    else:
        lines.append(f"  To mirror Workiz snapshot: create or link SOs for {len(only_in_workiz)} job UUIDs missing in Odoo.")
    if only_in_odoo:
        lines.append(f"  {len(only_in_odoo)} Odoo SOs have UUIDs not in this snapshot (older/newer data or different export).")
    lines.append("")

    report_text = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)
    print(f"\n[OK] Report written to {out_path}")


if __name__ == "__main__":
    main()
