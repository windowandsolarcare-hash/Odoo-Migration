"""
Compare SO 004149 address: Odoo (Property = partner_shipping_id) vs Workiz job.
Run from this folder: python compare_so_004149_address.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.workiz.get_job_details import get_job_details


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0", "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params},
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    so_name = "004149"
    # Find SO by name
    sos = odoo_rpc("sale.order", "search_read", [[["name", "=", so_name]]], {
        "fields": ["id", "name", "partner_id", "partner_shipping_id", "x_studio_x_studio_workiz_uuid"],
        "limit": 1,
    })
    if not sos:
        print(f"SO {so_name} not found in Odoo.")
        return
    so = sos[0]
    so_id = so["id"]
    uuid_val = (so.get("x_studio_x_studio_workiz_uuid") or "").strip()
    if not uuid_val:
        print(f"SO {so_name} has no Workiz UUID; cannot fetch Workiz job.")
        return

    # Property = partner_shipping_id (can be [id, display_name] or id)
    shipping = so.get("partner_shipping_id")
    if not shipping:
        print(f"SO {so_name} has no partner_shipping_id (Property).")
        property_id = None
    else:
        property_id = shipping[0] if isinstance(shipping, (list, tuple)) else shipping
    odoo_addr = {}
    if property_id:
        partners = odoo_rpc("res.partner", "search_read", [[["id", "=", property_id]]], {
            "fields": ["id", "name", "street", "street2", "city", "zip", "state_id"],
            "limit": 1,
        })
        if partners:
            p = partners[0]
            odoo_addr = {
                "name": p.get("name") or "",
                "street": p.get("street") or "",
                "street2": p.get("street2") or "",
                "city": p.get("city") or "",
                "zip": p.get("zip") or "",
                "state_id": p.get("state_id"),  # can be [id, name]
            }

    # Workiz job
    job = get_job_details(uuid_val, quiet=True)
    workiz_addr = {}
    if job:
        workiz_addr = {
            "Address": (job.get("Address") or "").strip(),
            "City": (job.get("City") or "").strip(),
            "PostalCode": (job.get("PostalCode") or "").strip(),
            "State": (job.get("State") or "").strip(),
        }

    # Report
    print("=" * 60)
    print(f"SO {so_name} (id {so_id})  Workiz UUID: {uuid_val}")
    print("=" * 60)
    print("\n--- Workiz (source of truth for job address) ---")
    print(f"  Address:    {workiz_addr.get('Address') or '(empty)'}")
    print(f"  City:       {workiz_addr.get('City') or '(empty)'}")
    print(f"  State:      {workiz_addr.get('State') or '(empty)'}")
    print(f"  PostalCode: {workiz_addr.get('PostalCode') or '(empty)'}")
    print("\n--- Odoo Property (partner_shipping_id) ---")
    if not odoo_addr:
        print("  (no property or could not load)")
    else:
        print(f"  name:   {odoo_addr.get('name') or '(empty)'}")
        print(f"  street: {odoo_addr.get('street') or '(empty)'}")
        print(f"  street2: {odoo_addr.get('street2') or '(empty)'}")
        print(f"  city:   {odoo_addr.get('city') or '(empty)'}")
        print(f"  zip:    {odoo_addr.get('zip') or '(empty)'}")
        state = odoo_addr.get("state_id")
        if isinstance(state, (list, tuple)) and len(state) >= 2:
            print(f"  state:  {state[1]}")
        else:
            print(f"  state:  {state}")
    print()

    # Why wrong?
    w_street = (workiz_addr.get("Address") or "").strip()
    o_street = (odoo_addr.get("street") or "").strip()
    if w_street and o_street and w_street != o_street:
        print("--- WHY ODOO CAN BE WRONG ---")
        print("Odoo Property was likely created or linked at SO creation (Phase 3) using")
        print("the Workiz job address at that time. If in Workiz the job's address was")
        print("later changed (or the SO was linked to a different Property by address")
        print("match), Odoo does not auto-update the Property's street/city/zip.")
        print("Phase 4 updates many SO fields but does not overwrite Property address")
        print("from Workiz on every sync (to avoid overwriting manual edits).")
        print("FIX: Update the Property in Odoo to match Workiz, or add a sync step that")
        print("writes Workiz Address/City/PostalCode to the linked Property when they differ.")


if __name__ == "__main__":
    main()
