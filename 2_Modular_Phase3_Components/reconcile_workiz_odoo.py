"""
Workiz vs Odoo reconciliation (mirror check).

1) SALES ORDER vs JOB (one-for-one by Workiz UUID)
   - Fetches Odoo SOs that have x_studio_x_studio_workiz_uuid.
   - Fetches Workiz jobs via job/all over a date range (no "list all jobs" API).
   - Reports: matched UUIDs, SOs in Odoo with UUID not seen in Workiz window, jobs in Workiz (in date window) not in Odoo.
   - Note: Workiz has no "list all jobs" API; we use job/all over a date range, so counts are for that window.

2) CONTACTS + PROPERTIES (optional, --contacts)
   - From Workiz jobs: unique (ClientId, Address).
   - From Odoo: Contacts (record_category=Contact, ref=ClientId) and Properties (record_category=Property, street).
   - Reports: counts and sample mismatches (Workiz client+address with no Odoo property; Odoo-only partners).

Uses config.py for Workiz. Use --test for Odoo test DB.
Run: python reconcile_workiz_odoo.py
     python reconcile_workiz_odoo.py --test
     python reconcile_workiz_odoo.py --contacts
"""
import sys
import os
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import requests

# Workiz from main config only
from config import WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY
from config import ODOO_URL as PROD_URL, ODOO_DB as PROD_DB, ODOO_USER_ID as PROD_UID, ODOO_API_KEY as PROD_KEY

WORKIZ_UUID_FIELD = "x_studio_x_studio_workiz_uuid"
CATEGORY_FIELD = "x_studio_x_studio_record_category"

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
    }, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def workiz_job_all(start_date, records=500, only_open=False):
    """GET /job/all/ - returns list of jobs or []."""
    url = (
        f"{WORKIZ_BASE_URL.rstrip('/')}/job/all/"
        f"?auth_secret={WORKIZ_AUTH_SECRET}&start_date={start_date}&records={records}&only_open={str(only_open).lower()}"
    )
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
        if isinstance(data, list):
            return data
        jobs = data.get("data", data) if isinstance(data, dict) else []
        return jobs if isinstance(jobs, list) else []
    except Exception as e:
        print(f"[WARN] job/all {start_date}: {e}")
        return []


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Reconcile Workiz jobs vs Odoo SOs (and optionally contacts/properties).")
    parser.add_argument("--test", action="store_true", help="Use Odoo TEST database.")
    parser.add_argument("--contacts", action="store_true", help="Also compare contacts/properties from job data.")
    parser.add_argument("--months", type=int, default=24, help="How many months back to fetch Workiz jobs (default 24).")
    args = parser.parse_args()

    if args.test:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        print("[TEST] Odoo DB:", ODOO_DB)
    else:
        print("[LIVE] Odoo DB:", ODOO_DB)

    # ----- 1) Odoo: SOs with Workiz UUID -----
    sos = odoo_rpc("sale.order", "search_read", [[[WORKIZ_UUID_FIELD, "!=", False]]], {
        "fields": ["id", "name", WORKIZ_UUID_FIELD],
        "limit": 50000,
    })
    odoo_uuid_to_so = {}
    for so in sos:
        u = (so.get(WORKIZ_UUID_FIELD) or "").strip()
        if u:
            odoo_uuid_to_so[u] = so.get("name")
    odoo_uuids = set(odoo_uuid_to_so.keys())
    total_sos = len(odoo_rpc("sale.order", "search_count", [[]]))
    print(f"\n--- Odoo ---")
    print(f"  Total SOs: {total_sos}")
    print(f"  SOs with Workiz UUID: {len(odoo_uuids)}")

    # ----- 2) Workiz: jobs over date range (chunk by month) -----
    workiz_uuids = set()
    workiz_client_address = set()  # (client_id, address_normalized)
    months_back = max(1, args.months)
    total_jobs_fetched = 0
    for month_offset in range(0, months_back, 2):  # every 2 months
        start_date = (datetime.utcnow() - timedelta(days=month_offset * 31)).strftime("%Y-%m-%d")
        jobs = workiz_job_all(start_date, records=500, only_open=False)
        total_jobs_fetched += len(jobs)
        for j in jobs:
            if not isinstance(j, dict):
                continue
            u = (j.get("UUID") or j.get("uuid") or "").strip()
            if u:
                workiz_uuids.add(u)
            if args.contacts:
                addr = (j.get("Address") or "").strip()
                cid = j.get("ClientId") or j.get("ClientID")
                if cid is not None and addr:
                    workiz_client_address.add((str(cid), addr.lower().strip()))

    print(f"\n--- Workiz (job/all over ~{months_back} months) ---")
    print(f"  Jobs fetched (raw): {total_jobs_fetched}")
    print(f"  Unique job UUIDs: {len(workiz_uuids)}")

    # ----- 3) SO vs Job comparison -----
    matched = odoo_uuids & workiz_uuids
    only_odoo = odoo_uuids - workiz_uuids
    only_workiz = workiz_uuids - odoo_uuids
    print(f"\n--- SO vs Job (by Workiz UUID) ---")
    print(f"  Matched (in both): {len(matched)}")
    print(f"  Only in Odoo (UUID not in Workiz window): {len(only_odoo)}")
    if only_odoo and len(only_odoo) <= 20:
        for u in sorted(only_odoo)[:20]:
            print(f"    - {u}  SO: {odoo_uuid_to_so.get(u)}")
    elif only_odoo:
        print(f"    (first 10) {list(sorted(only_odoo))[:10]}")
    print(f"  Only in Workiz (no SO in Odoo for this window): {len(only_workiz)}")
    if only_workiz and len(only_workiz) <= 15:
        for u in sorted(only_workiz)[:15]:
            print(f"    - {u}")
    elif only_workiz:
        print(f"    (first 10) {list(sorted(only_workiz))[:10]}")

    # ----- 4) Optional: contacts/properties -----
    if args.contacts and workiz_client_address:
        contacts = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Contact"]]], {
            "fields": ["id", "name", "ref", "street"],
            "limit": 50000,
        })
        properties = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Property"]]], {
            "fields": ["id", "name", "street", "parent_id"],
            "limit": 50000,
        })
        # Odoo: ref = ClientId for contacts; street for properties
        odoo_client_ids = {str(p.get("ref") or "").strip() for p in contacts if (p.get("ref") or "").strip()}
        odoo_streets = {((p.get("street") or "").lower().strip()) for p in properties}
        workiz_clients = {cid for cid, _ in workiz_client_address}
        workiz_addresses = {addr for _, addr in workiz_client_address}
        print(f"\n--- Contacts / Properties (from job data) ---")
        print(f"  Workiz unique (ClientId, Address) from jobs: {len(workiz_client_address)}")
        print(f"  Odoo Contacts (with ref): {len(contacts)}")
        print(f"  Odoo Properties: {len(properties)}")
        clients_in_odoo = workiz_clients & odoo_client_ids
        addresses_in_odoo = workiz_addresses & odoo_streets
        print(f"  Workiz ClientIds that exist in Odoo (ref): {len(clients_in_odoo)}")
        print(f"  Workiz addresses that exist as Odoo Property street: {len(addresses_in_odoo)}")
        missing_addr = workiz_addresses - odoo_streets
        if missing_addr and len(missing_addr) <= 15:
            print(f"  Sample Workiz addresses with no Odoo Property street: {list(missing_addr)[:15]}")
        elif missing_addr:
            print(f"  Workiz addresses with no Odoo Property match: {len(missing_addr)} (sample: {list(missing_addr)[:5]})")

    print("\nDone.")


if __name__ == "__main__":
    main()
