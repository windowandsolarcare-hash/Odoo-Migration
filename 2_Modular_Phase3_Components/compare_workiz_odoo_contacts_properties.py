"""
Compare Workiz snapshot CSV to Odoo: CONTACTS and PROPERTIES only (read-only).
No changes to Odoo. Produces a report of what we would change if needed.

- Contacts: Workiz ClientId vs Odoo res.partner (record_category=Contact, ref=ClientId).
  Report: Workiz ClientIds with no Odoo contact; Odoo contacts not in Workiz; name mismatches.
- Properties: Workiz Address/City/PostalCode vs Odoo res.partner (record_category=Property).
  Report: Workiz addresses with no Odoo property; Odoo properties not in Workiz; address mismatches.

Uses merged Workiz snapshot CSV. Odoo: --test for test DB.
  python compare_workiz_odoo_contacts_properties.py --csv "path/to/workiz_full_snapshot_merged.csv"
  python compare_workiz_odoo_contacts_properties.py --test
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
    }, timeout=120)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def norm(s):
    return (s or "").strip().lower()


def norm_street(s):
    return norm(s).replace(",", " ")


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Compare Workiz snapshot to Odoo contacts & properties (read-only report).")
    parser.add_argument("--csv", default=DEFAULT_WORKIZ_CSV, help="Workiz snapshot CSV (merged).")
    parser.add_argument("--test", action="store_true", help="Use Odoo TEST database.")
    parser.add_argument("--output", default=None, help="Report output path. Default: 2_Migration_Archive/compare_contacts_properties_YYYYMMDD.txt")
    args = parser.parse_args()

    if args.test:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        print("[TEST] Odoo DB:", ODOO_DB)
    else:
        print("[LIVE] Odoo DB:", ODOO_DB)

    if not os.path.isfile(args.csv):
        print(f"[!] Workiz CSV not found: {args.csv}")
        return

    # ---- Load Workiz snapshot ----
    workiz_contacts = {}   # ClientId -> (first_name, last_name, sample_address)
    workiz_properties = {} # (norm_street, norm_city, norm_zip) -> (Address, City, State, PostalCode, ClientId)
    with open(args.csv, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            cid = (row.get("ClientId") or "").strip()
            addr = (row.get("Address") or "").strip()
            city = (row.get("City") or "").strip()
            state = (row.get("State") or "").strip()
            zip_ = (row.get("PostalCode") or "").strip()
            fn = (row.get("FirstName") or "").strip()
            ln = (row.get("LastName") or "").strip()
            if cid:
                if cid not in workiz_contacts:
                    workiz_contacts[cid] = (fn, ln, addr)
            if addr:
                key = (norm_street(addr), norm(city), norm(zip_))
                if key not in workiz_properties:
                    workiz_properties[key] = (addr, city, state, zip_, cid)

    print(f"[*] Workiz snapshot: {len(workiz_contacts)} unique ClientIds (contacts), {len(workiz_properties)} unique addresses (properties)")

    # ---- Load Odoo ----
    contacts = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Contact"]]], {
        "fields": ["id", "name", "ref", "street", "city", "zip"],
        "limit": 50000,
    })
    properties = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Property"]]], {
        "fields": ["id", "name", "street", "city", "zip", "parent_id"],
        "limit": 50000,
    })

    odoo_contact_by_ref = {}  # ref (ClientId) -> partner
    for p in contacts:
        ref = (p.get("ref") or "").strip()
        if ref:
            odoo_contact_by_ref[ref] = p

    odoo_property_by_key = {}  # (norm_street, norm_city, norm_zip) -> partner
    for p in properties:
        street = (p.get("street") or "").strip()
        city = (p.get("city") or "").strip()
        zip_ = (p.get("zip") or "").strip()
        key = (norm_street(street), norm(city), norm(zip_))
        odoo_property_by_key[key] = p

    print(f"[*] Odoo: {len(contacts)} Contacts (with ref), {len(properties)} Properties")

    # ---- Compare CONTACTS ----
    workiz_cids = set(workiz_contacts.keys())
    odoo_refs = set(odoo_contact_by_ref.keys())
    only_workiz_contacts = workiz_cids - odoo_refs
    only_odoo_contacts = odoo_refs - workiz_cids
    name_mismatch = []
    for cid in workiz_cids & odoo_refs:
        fn, ln, _ = workiz_contacts[cid]
        workiz_name = f"{fn} {ln}".strip() or "(no name)"
        odoo_name = (odoo_contact_by_ref[cid].get("name") or "").strip()
        if norm(workiz_name) != norm(odoo_name):
            name_mismatch.append((cid, workiz_name, odoo_name))

    # ---- Compare PROPERTIES ----
    workiz_keys = set(workiz_properties.keys())
    odoo_keys = set(odoo_property_by_key.keys())
    only_workiz_props = workiz_keys - odoo_keys
    only_odoo_props = odoo_keys - workiz_keys

    # ---- Write report ----
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out_path = args.output or os.path.join(DEFAULT_REPORT_DIR, f"compare_contacts_properties_{ts}.txt")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    lines = []
    lines.append("=" * 60)
    lines.append("Workiz vs Odoo: CONTACTS and PROPERTIES (read-only, no changes made)")
    lines.append(f"Workiz CSV: {args.csv}")
    lines.append(f"Odoo DB: {ODOO_DB}")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("=" * 60)

    lines.append("\n--- CONTACTS ---")
    lines.append(f"Workiz unique ClientIds: {len(workiz_cids)}")
    lines.append(f"Odoo Contacts (with ref): {len(odoo_refs)}")
    lines.append(f"Workiz ClientIds with NO Odoo contact (would add/fix): {len(only_workiz_contacts)}")
    if only_workiz_contacts:
        for cid in sorted(only_workiz_contacts, key=lambda x: (workiz_contacts[x][1], workiz_contacts[x][0])):
            fn, ln, addr = workiz_contacts[cid]
            lines.append(f"  ClientId={cid}  Workiz: {fn} {ln}  address: {addr[:50]}")
    lines.append(f"Odoo contacts (ref) with NO Workiz ClientId (extra in Odoo): {len(only_odoo_contacts)}")
    if only_odoo_contacts:
        for ref in sorted(only_odoo_contacts)[:100]:
            p = odoo_contact_by_ref[ref]
            lines.append(f"  ref={ref}  Odoo name={p.get('name')}  id={p.get('id')}")
        if len(only_odoo_contacts) > 100:
            lines.append(f"  ... and {len(only_odoo_contacts) - 100} more.")
    lines.append(f"Contact name MISMATCH (same ClientId, different name): {len(name_mismatch)}")
    if name_mismatch:
        for cid, w_name, o_name in name_mismatch[:50]:
            lines.append(f"  ClientId={cid}  Workiz: '{w_name}'  Odoo: '{o_name}'")
        if len(name_mismatch) > 50:
            lines.append(f"  ... and {len(name_mismatch) - 50} more.")

    lines.append("\n--- PROPERTIES ---")
    lines.append(f"Workiz unique addresses: {len(workiz_keys)}")
    lines.append(f"Odoo Properties: {len(odoo_keys)}")
    lines.append(f"Workiz addresses with NO Odoo property (would add/fix): {len(only_workiz_props)}")
    if only_workiz_props:
        for key in sorted(only_workiz_props, key=lambda k: workiz_properties[k][0])[:80]:
            addr, city, state, zip_, cid = workiz_properties[key]
            lines.append(f"  Address: {addr}, {city}, {state} {zip_}  ClientId={cid}")
        if len(only_workiz_props) > 80:
            lines.append(f"  ... and {len(only_workiz_props) - 80} more.")
    lines.append(f"Odoo properties with NO Workiz address (extra in Odoo): {len(only_odoo_props)}")
    if only_odoo_props:
        for key in sorted(only_odoo_props, key=lambda k: odoo_property_by_key[k].get("street") or "")[:80]:
            p = odoo_property_by_key[key]
            lines.append(f"  Odoo id={p.get('id')}  street={p.get('street')}  city={p.get('city')}  zip={p.get('zip')}")
        if len(only_odoo_props) > 80:
            lines.append(f"  ... and {len(only_odoo_props) - 80} more.")

    lines.append("\n--- SUMMARY (what you would change if needed) ---")
    lines.append(f"  Contacts: {len(only_workiz_contacts)} missing in Odoo, {len(only_odoo_contacts)} only in Odoo, {len(name_mismatch)} name mismatches.")
    lines.append(f"  Properties: {len(only_workiz_props)} missing in Odoo, {len(only_odoo_props)} only in Odoo.")
    lines.append("")

    report_text = "\n".join(lines)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)
    print(f"\n[OK] Report written to {out_path}")


if __name__ == "__main__":
    main()
