"""
Refresh a Sales Order from Workiz (including line items).

Use this so Odoo has the latest Workiz data before you create an invoice — e.g. if
someone added "shower glass doors" at the job in Workiz, this updates the SO lines
in Odoo to match.

Usage:
  python refresh_so_from_workiz.py <so_id>              # Refresh one SO (e.g. 15832)
  python refresh_so_from_workiz.py --scheduled         # Refresh all SOs with Workiz UUID that are not yet fully invoiced (for cron every 4h)
  python refresh_so_from_workiz.py --scheduled --limit 50 --delay 2.5
  python refresh_so_from_workiz.py --scheduled --dry-run

Options:
  --scheduled   Find SOs to refresh (has Workiz UUID, not fully invoiced); use for schedule.
  --limit N     When using --scheduled, process at most N SOs (default 200).
  --delay SEC   Seconds between Workiz API calls (default 2.5; increase if 429).
  --dry-run     Only list SOs that would be refreshed; do not write to Odoo.
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.workiz.get_job_details import get_job_details
from functions.odoo.update_sales_order import update_sales_order
from functions.odoo.search_product_by_name import search_product_by_name
from functions.odoo.post_chatter_message import post_chatter_message

# Odoo product field for Workiz product code (per Phase_3_4_5_Reference_Summary.md)
ODOO_PRODUCT_WORKIZ_CODE_FIELD = "x_studio_x_studio_workiz_product_number"


def odoo_call(model, method, args, kwargs=None):
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
        raise RuntimeError(data["error"])
    return data.get("result")


def format_team_names(team_raw):
    if not team_raw:
        return ""
    if isinstance(team_raw, list):
        names = []
        for member in team_raw:
            if isinstance(member, dict):
                name = member.get("Name") or member.get("name", "")
                if name:
                    names.append(str(name).strip())
            elif member:
                names.append(str(member).strip())
        return ", ".join(names)
    return str(team_raw).strip() if isinstance(team_raw, str) else ""


def search_product_by_workiz_code(workiz_code):
    """Find Odoo product where x_studio_x_studio_workiz_product_number = workiz_code. Workiz API: ModelNum, Id (Workiz_API_Test_Results.md)."""
    if workiz_code is None or str(workiz_code).strip() == "":
        return None
    code = str(workiz_code).strip()
    r = requests.post(
        ODOO_URL,
        json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "product.product",
                    "search_read",
                    [[[ODOO_PRODUCT_WORKIZ_CODE_FIELD, "=", code]]],
                    {"fields": ["id"], "limit": 1},
                ],
            },
        },
        timeout=10,
    )
    res = r.json().get("result", [])
    return res[0]["id"] if res else None


def build_order_line_commands(workiz_line_items):
    """Build Odoo order_line from Workiz LineItems. Match by Workiz product code (ModelNum/Id) then name then Service."""
    if not workiz_line_items or not isinstance(workiz_line_items, list):
        return [(5, 0, 0)]
    lines = [(5, 0, 0)]
    for item in workiz_line_items:
        if not isinstance(item, dict):
            continue
        item_name = item.get("Name", "Service")
        qty = float(item.get("Quantity", 1))
        price = float(item.get("Price", 0))
        workiz_code = item.get("ModelNum") or item.get("Id")
        product_id = search_product_by_workiz_code(workiz_code) if workiz_code is not None and str(workiz_code).strip() != "" else None
        if product_id is None:
            product_id = search_product_by_name(item_name)
        if product_id is None and item_name != "Service":
            product_id = search_product_by_name("Service")
        if product_id:
            lines.append((0, 0, {"product_id": product_id, "product_uom_qty": qty, "price_unit": price}))
    return lines


def refresh_one_so(so_id, dry_run=False):
    """
    Fetch Workiz job by SO's UUID and update SO (status, notes, date, job type, and line items).
    Returns dict with success, error, message.
    """
    sos = odoo_call(
        "sale.order",
        "read",
        [[so_id]],
        {"fields": ["id", "name", "x_studio_x_studio_workiz_uuid", "state"]},
    )
    if not sos:
        return {"success": False, "error": "SO not found", "so_id": so_id}
    so = sos[0]
    uuid_val = (so.get("x_studio_x_studio_workiz_uuid") or "").strip()
    if not uuid_val:
        return {"success": False, "error": "SO has no Workiz UUID", "so_id": so_id}

    if dry_run:
        return {"success": True, "dry_run": True, "so_id": so_id, "name": so.get("name"), "uuid": uuid_val}

    job = get_job_details(uuid_val)
    if not job:
        return {"success": False, "error": "Could not fetch Workiz job", "so_id": so_id}

    workiz_substatus = job.get("SubStatus", "") or job.get("Status", "")
    job_type = job.get("JobType", "")
    job_source = job.get("JobSource", "")
    gate_code = job.get("gate_code", "")
    pricing = job.get("pricing", "")
    job_notes = job.get("JobNotes", "") or ""
    comments = job.get("Comments", "") or ""
    job_datetime_str = job.get("JobDateTime", "")
    team = job.get("Team", [])

    team_names = format_team_names(team)
    notes_snapshot = ""
    if job_notes:
        notes_snapshot += f"[Job Notes]\n{job_notes}\n\n"
    if comments:
        notes_snapshot += f"[Comments]\n{comments}"
    notes_snapshot = notes_snapshot.strip()

    job_datetime_utc = None
    if job_datetime_str:
        try:
            dt_pacific = datetime.strptime(job_datetime_str, "%Y-%m-%d %H:%M:%S")
            job_datetime_utc = dt_pacific + timedelta(hours=8)
        except Exception:
            pass

    updates = {
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_workiz_tech": team_names,
        "x_studio_x_gate_snapshot": gate_code,
        "x_studio_x_studio_pricing_snapshot": pricing,
        "x_studio_x_studio_notes_snapshot1": notes_snapshot,
    }
    if job_datetime_utc:
        updates["date_order"] = job_datetime_utc.strftime("%Y-%m-%d %H:%M:%S")
    if job_type:
        updates["x_studio_x_studio_x_studio_job_type"] = job_type
    if job_source:
        updates["x_studio_x_studio_lead_source"] = job_source

    line_items = job.get("LineItems", [])
    if isinstance(line_items, str):
        try:
            import ast
            line_items = ast.literal_eval(line_items)
        except Exception:
            line_items = []
    if not isinstance(line_items, list):
        line_items = []
    updates["order_line"] = build_order_line_commands(line_items)

    success = update_sales_order(so_id, updates)
    if not success:
        return {"success": False, "error": "Odoo write failed", "so_id": so_id}
    post_chatter_message(so_id, f"Refreshed from Workiz (status: {workiz_substatus}; {len(line_items)} line items)")
    return {"success": True, "so_id": so_id, "name": so.get("name"), "line_items": len(line_items)}


def main():
    ap = argparse.ArgumentParser(description="Refresh Sales Order(s) from Workiz (including line items)")
    ap.add_argument("so_id", nargs="?", type=int, default=None, help="Single SO ID to refresh")
    ap.add_argument("--scheduled", action="store_true", help="Find and refresh SOs not yet fully invoiced")
    ap.add_argument("--limit", type=int, default=200, help="Max SOs when using --scheduled")
    ap.add_argument("--delay", type=float, default=2.5, help="Seconds between Workiz API calls when --scheduled")
    ap.add_argument("--dry-run", action="store_true", help="Only list; do not write to Odoo")
    args = ap.parse_args()

    if args.so_id is not None and not args.scheduled:
        # Single SO
        result = refresh_one_so(args.so_id, dry_run=args.dry_run)
        if result.get("success"):
            if result.get("dry_run"):
                print(f"[DRY RUN] Would refresh SO {result.get('so_id')} ({result.get('name')}) UUID {result.get('uuid')}")
            else:
                print(f"[OK] Refreshed SO {result.get('so_id')} ({result.get('name')}) — {result.get('line_items', 0)} line items")
        else:
            print(f"[ERROR] {result.get('error')} (SO {result.get('so_id')})")
            sys.exit(1)
        return

    if not args.scheduled:
        print("Usage: python refresh_so_from_workiz.py <so_id>   OR   python refresh_so_from_workiz.py --scheduled")
        sys.exit(1)

    # Scheduled: find SOs with Workiz UUID that are not fully invoiced (no posted invoice or invoice in draft)
    # We consider "not fully invoiced" = sale order has invoice_status != 'invoiced' (or we search for SOs without a posted invoice linked)
    domain = [
        ["x_studio_x_studio_workiz_uuid", "!=", False],
        ["state", "in", ["sale", "done"]],  # confirmed SOs
    ]
    sos = odoo_call(
        "sale.order",
        "search_read",
        [domain],
        {"fields": ["id", "name", "x_studio_x_studio_workiz_uuid", "invoice_status"], "limit": args.limit, "order": "write_date desc"},
    )
    # Filter: only SOs that are not yet fully invoiced (invoice_status can be 'no', 'to invoice', 'invoiced')
    to_refresh = [so for so in sos if so.get("invoice_status") != "invoiced"]
    if not to_refresh:
        print("No SOs to refresh (all with Workiz UUID are already invoiced or none found).")
        return

    print(f"Found {len(to_refresh)} SO(s) to refresh from Workiz (not yet fully invoiced).")
    if args.dry_run:
        for so in to_refresh[:20]:
            print(f"  Would refresh: SO {so['id']} ({so.get('name')})")
        if len(to_refresh) > 20:
            print(f"  ... and {len(to_refresh) - 20} more")
        return

    ok = 0
    fail = 0
    for so in to_refresh:
        so_id = so["id"]
        time.sleep(args.delay)
        result = refresh_one_so(so_id, dry_run=False)
        if result.get("success"):
            ok += 1
            print(f"  [OK] {so.get('name')} — {result.get('line_items', 0)} line items")
        else:
            fail += 1
            print(f"  [SKIP] {so.get('name')}: {result.get('error')}")
    print(f"Done. Refreshed: {ok}. Skipped/failed: {fail}")


if __name__ == "__main__":
    main()
