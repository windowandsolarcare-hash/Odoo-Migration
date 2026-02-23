"""
Phase 6 Automation: Find paid invoices (from SO with Workiz UUID) and sync each to Workiz.

Run on a schedule (e.g. every 5–10 min via Task Scheduler / cron) so that when you
mark an invoice paid in Odoo, it is picked up and Phase 6 runs (add payment in Workiz,
mark job Done). No Odoo config changes required; processed invoice IDs are stored
locally so we do not double-sync.

Usage:
  python phase6_auto_sync_paid_invoices.py              # Check last 7 days of paid invoices
  python phase6_auto_sync_paid_invoices.py --days 1     # Only last 1 day (faster)
  python phase6_auto_sync_paid_invoices.py --dry-run     # List what would be synced, no writes
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from phase6_payment_sync_to_workiz import run as phase6_run

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase6_processed_invoices.json")


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


def load_processed():
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_processed(ids_set):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(ids_set), f, indent=0)


def main():
    ap = argparse.ArgumentParser(description="Auto-sync paid Odoo invoices to Workiz (Phase 6)")
    ap.add_argument("--days", type=int, default=7, help="Consider invoices paid in the last N days (default 7)")
    ap.add_argument("--dry-run", action="store_true", help="Only list invoices that would be synced; do not call Workiz")
    args = ap.parse_args()

    processed = load_processed()
    since = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    # Search paid customer invoices with an origin (SO)
    domain = [
        ["move_type", "=", "out_invoice"],
        ["payment_state", "=", "paid"],
        ["invoice_origin", "!=", False],
        ["date", ">=", since],
    ]
    invs = odoo_call(
        "account.move",
        "search_read",
        [domain],
        {"fields": ["id", "name", "invoice_origin", "date", "amount_total"], "order": "date desc"},
    )

    to_process = [inv for inv in invs if inv["id"] not in processed]
    if not to_process:
        print("No new paid invoices to sync.")
        return

    print(f"Found {len(to_process)} paid invoice(s) not yet synced (since {since}).")
    if args.dry_run:
        for inv in to_process:
            print(f"  Would sync: id={inv['id']} {inv.get('name')} origin={inv.get('invoice_origin')} amount={inv.get('amount_total')}")
        return

    for inv in to_process:
        inv_id = inv["id"]
        print(f"Syncing invoice id={inv_id} ({inv.get('name')})...")
        result = phase6_run(inv_id)
        if result.get("success"):
            processed.add(inv_id)
            save_processed(processed)
            print(f"  OK: {result.get('job_uuid')} amount={result.get('amount')}")
        else:
            # Do not add to processed so we retry next run (or skip if no SO/Workiz UUID)
            print(f"  Skip/fail: {result.get('error')}")


if __name__ == "__main__":
    main()
