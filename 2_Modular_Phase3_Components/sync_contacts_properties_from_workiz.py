"""
Sync Contacts and Properties from Workiz snapshot to Odoo (live or test).
  - Add missing Contacts (Workiz ClientIds with no Odoo contact): ref=ClientId, name from Workiz.
  - Fix Contact name mismatches: set Odoo name = Workiz name (e.g. "&" vs space).
  - Add missing Properties (Workiz addresses with no Odoo property): link to Contact by ClientId.

Uses same Workiz CSV and matching logic as compare_workiz_odoo_contacts_properties.py.
Default = TEST. Use --production for LIVE. Use --dry-run to preview only.

  cd "2_Modular_Phase3_Components"
  python sync_contacts_properties_from_workiz.py --dry-run           # preview (test DB)
  python sync_contacts_properties_from_workiz.py --production        # apply on LIVE
  python sync_contacts_properties_from_workiz.py --production --dry-run  # preview on LIVE
  python sync_contacts_properties_from_workiz.py                      # apply on TEST
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
CATEGORY_FIELD = "x_studio_x_studio_record_category"
STATE_ID_CA = 13

# Default TEST; set to PROD in main() when --production is passed.
ODOO_URL = TEST_URL
ODOO_DB = TEST_DB
ODOO_USER_ID = TEST_UID
ODOO_API_KEY = TEST_KEY


def norm(s):
    return (s or "").strip().lower()


def norm_street(s):
    return norm(s).replace(",", " ")


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


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Add missing contacts/properties and fix name mismatches from Workiz snapshot.")
    parser.add_argument("--csv", default=DEFAULT_WORKIZ_CSV, help="Workiz snapshot CSV (merged).")
    parser.add_argument("--test", action="store_true", help="Use Odoo TEST database.")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be done; do not write.")
    parser.add_argument("--production", action="store_true", help="Use LIVE Odoo (default is test).")
    args = parser.parse_args()

    if getattr(args, "production", False):
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = PROD_URL, PROD_DB, PROD_UID, PROD_KEY
        print("[LIVE] Odoo DB:", ODOO_DB)
    else:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        print("[TEST] Odoo DB:", ODOO_DB)
    if args.dry_run:
        print("[DRY RUN] No changes will be written.")

    if not os.path.isfile(args.csv):
        print(f"[!] Workiz CSV not found: {args.csv}")
        return

    # ---- Load Workiz ----
    workiz_contacts = {}   # ClientId -> (first_name, last_name, address, city, state, zip)
    workiz_properties = {} # (norm_street, norm_city, norm_zip) -> (addr, city, state, zip_, ClientId)
    with open(args.csv, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            cid = (row.get("ClientId") or "").strip()
            addr = (row.get("Address") or "").strip()
            city = (row.get("City") or "").strip()
            state = (row.get("State") or "").strip()
            zip_ = (row.get("PostalCode") or "").strip()
            fn = (row.get("FirstName") or "").strip()
            ln = (row.get("LastName") or "").strip()
            if cid and cid not in workiz_contacts:
                workiz_contacts[cid] = (fn, ln, addr, city, state, zip_)
            if addr:
                key = (norm_street(addr), norm(city), norm(zip_))
                if key not in workiz_properties:
                    workiz_properties[key] = (addr, city, state, zip_, cid)

    # ---- Load Odoo ----
    contacts = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Contact"]]], {
        "fields": ["id", "name", "ref"],
        "limit": 50000,
    })
    properties = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Property"]]], {
        "fields": ["id", "street", "city", "zip"],
        "limit": 50000,
    })

    odoo_contact_by_ref = {str(p.get("ref") or "").strip(): p for p in contacts if (p.get("ref") or "").strip()}
    odoo_property_by_key = {}
    for p in properties:
        street = (p.get("street") or "").strip()
        city = (p.get("city") or "").strip()
        zip_ = (p.get("zip") or "").strip()
        key = (norm_street(street), norm(city), norm(zip_))
        odoo_property_by_key[key] = p

    workiz_cids = set(workiz_contacts.keys())
    odoo_refs = set(odoo_contact_by_ref.keys())
    only_workiz_contacts = sorted(workiz_cids - odoo_refs, key=lambda x: (workiz_contacts[x][1], workiz_contacts[x][0]))
    name_mismatch = []
    for cid in workiz_cids & odoo_refs:
        fn, ln, *_ = workiz_contacts[cid]
        workiz_name = f"{fn} {ln}".strip() or "(no name)"
        odoo_name = (odoo_contact_by_ref[cid].get("name") or "").strip()
        if norm(workiz_name) != norm(odoo_name):
            name_mismatch.append((cid, workiz_name, odoo_contact_by_ref[cid]["id"]))

    workiz_keys = set(workiz_properties.keys())
    odoo_keys = set(odoo_property_by_key.keys())
    only_workiz_props = sorted(workiz_keys - odoo_keys, key=lambda k: workiz_properties[k][0])

    print(f"\nWorkiz: {len(workiz_cids)} ClientIds, {len(workiz_keys)} addresses. Odoo: {len(odoo_refs)} Contacts, {len(odoo_keys)} Properties.")
    print(f"  -> Add {len(only_workiz_contacts)} contacts, fix {len(name_mismatch)} names, add {len(only_workiz_props)} properties.\n")

    if args.dry_run:
        if only_workiz_contacts:
            print("--- Would CREATE contacts ---")
            for cid in only_workiz_contacts:
                fn, ln, addr, city, state, zip_ = workiz_contacts[cid]
                name = f"{fn} {ln}".strip()
                print(f"  ClientId={cid}  name={name!r}  address={addr}, {city} {zip_}")
        if name_mismatch:
            print("\n--- Would UPDATE contact names (Odoo <- Workiz) ---")
            for cid, w_name, odoo_id in name_mismatch[:30]:
                print(f"  ClientId={cid}  id={odoo_id}  -> name={w_name!r}")
            if len(name_mismatch) > 30:
                print(f"  ... and {len(name_mismatch) - 30} more.")
        if only_workiz_props:
            print("\n--- Would CREATE properties ---")
            for key in only_workiz_props:
                addr, city, state, zip_, cid = workiz_properties[key]
                print(f"  {addr}, {city} {zip_}  ClientId={cid}")
        print("\n[DRY RUN] Run without --dry-run to apply.")
        return

    # ---- 1) Create missing contacts ----
    created_ref_to_id = {}  # ref (ClientId) -> new Odoo id
    for cid in only_workiz_contacts:
        fn, ln, addr, city, state, zip_ = workiz_contacts[cid]
        name = f"{fn} {ln}".strip()
        if not name:
            name = f"Client {cid}"
        vals = {
            "name": name,
            "ref": str(cid),
            CATEGORY_FIELD: "Contact",
            "state_id": STATE_ID_CA,
        }
        if fn:
            vals["x_studio_x_studio_first_name"] = fn
        if ln:
            vals["x_studio_x_studio_last_name"] = ln
        if addr:
            vals["street"] = addr
        if city:
            vals["city"] = city
        if zip_:
            vals["zip"] = zip_
        try:
            new_id = odoo_rpc("res.partner", "create", [vals])
            created_ref_to_id[cid] = new_id
            print(f"  Created Contact ref={cid} id={new_id}  name={name!r}")
        except Exception as e:
            print(f"  [ERROR] Contact ref={cid}  {e}")

    # Build ref -> id (existing + newly created)
    ref_to_contact_id = {}
    for ref, p in odoo_contact_by_ref.items():
        ref_to_contact_id[ref] = p["id"]
    for ref, id_ in created_ref_to_id.items():
        ref_to_contact_id[ref] = id_

    # ---- 2) Fix name mismatches ----
    for cid, workiz_name, odoo_id in name_mismatch:
        try:
            odoo_rpc("res.partner", "write", [[odoo_id], {"name": workiz_name}])
            print(f"  Updated Contact id={odoo_id} ref={cid}  name={workiz_name!r}")
        except Exception as e:
            print(f"  [ERROR] Contact id={odoo_id} ref={cid}  {e}")

    # ---- 3) Create missing properties ----
    for key in only_workiz_props:
        addr, city, state, zip_, cid = workiz_properties[key]
        contact_id = ref_to_contact_id.get(cid)
        if not contact_id:
            print(f"  [SKIP] Property {addr}  ClientId={cid} has no Odoo contact.")
            continue
        vals = {
            "name": addr,
            "street": addr,
            "city": city or False,
            "zip": zip_ or False,
            "parent_id": contact_id,
            CATEGORY_FIELD: "Property",
            "state_id": STATE_ID_CA,
        }
        try:
            new_id = odoo_rpc("res.partner", "create", [vals])
            print(f"  Created Property id={new_id}  {addr}, {city} {zip_}  parent={contact_id} (ClientId={cid})")
        except Exception as e:
            print(f"  [ERROR] Property {addr}  {e}")

    print("\n[OK] Sync done.")


if __name__ == "__main__":
    main()
