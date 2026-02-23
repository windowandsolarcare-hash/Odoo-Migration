"""
Fix SO 004149 (and its invoice): set the Property address to 941 Ocea Cir
so the SO and invoice display the correct service address instead of e.g. 47446 Rabat Dr.

Updates the partner record that is the SO's customer (partner_id = Property) with the correct street.
Uses TEST by default; use --production for live.

Run: python fix_so_004149_address_941_ocea_cir.py
     python fix_so_004149_address_941_ocea_cir.py --production
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
import requests

from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY
from config import ODOO_URL as PROD_URL, ODOO_DB as PROD_DB, ODOO_USER_ID as PROD_UID, ODOO_API_KEY as PROD_KEY

# Address to set (service address for this job)
TARGET_STREET = "941 Ocea Cir"
TARGET_CITY = ""   # optional: set if you want to update city (e.g. "Palm Springs")
TARGET_ZIP = ""    # optional: set if you want to update zip

ODOO_URL = TEST_URL
ODOO_DB = TEST_DB
ODOO_USER_ID = TEST_UID
ODOO_API_KEY = TEST_KEY


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0", "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params},
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Set SO 004149 Property address to 941 Ocea Cir.")
    parser.add_argument("--production", action="store_true", help="Run on LIVE Odoo.")
    args = parser.parse_args()
    if args.production:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = PROD_URL, PROD_DB, PROD_UID, PROD_KEY
        print("[LIVE]", ODOO_DB)
    else:
        print("[TEST]", ODOO_DB)

    # Find SO by name (004149 or S004149)
    sos = odoo_rpc("sale.order", "search_read", [[["name", "ilike", "004149"]]], {
        "fields": ["id", "name", "partner_id", "partner_shipping_id"],
        "limit": 5,
    })
    so = None
    for s in sos:
        if "004149" in (s.get("name") or ""):
            so = s
            break
    if not so:
        print("SO 004149 not found.")
        return

    pid = so.get("partner_id")
    pid = pid[0] if isinstance(pid, (list, tuple)) else pid
    shipping_id = so.get("partner_shipping_id")
    shipping_id = shipping_id[0] if isinstance(shipping_id, (list, tuple)) else shipping_id
    # Fix the delivery/Property address (partner_shipping_id). After migration, partner_id = same,
    # so the document shows this address. Prefer shipping so we don't overwrite Contact's address.
    partner_id_to_fix = shipping_id or pid
    if not partner_id_to_fix:
        print("SO has no partner_id or partner_shipping_id.")
        return

    partners = odoo_rpc("res.partner", "search_read", [[["id", "=", partner_id_to_fix]]], {
        "fields": ["id", "name", "street", "street2", "city", "zip"],
    })
    if not partners:
        print("Partner not found.")
        return
    partner = partners[0]
    print(f"SO {so.get('name')} (id {so['id']})")
    print(f"  Customer/delivery partner: id={partner_id_to_fix}  name={partner.get('name')}")
    print(f"  Current street: {partner.get('street') or '(empty)'}")
    print(f"  -> Setting street to: {TARGET_STREET}")

    updates = {"street": TARGET_STREET}
    if TARGET_CITY:
        updates["city"] = TARGET_CITY
    if TARGET_ZIP:
        updates["zip"] = TARGET_ZIP

    odoo_rpc("res.partner", "write", [[partner_id_to_fix], updates])
    print(f"[OK] Updated partner id={partner_id_to_fix} address to {TARGET_STREET}.")
    print("     SO and any invoice using this partner will now show 941 Ocea Cir.")


if __name__ == "__main__":
    main()
