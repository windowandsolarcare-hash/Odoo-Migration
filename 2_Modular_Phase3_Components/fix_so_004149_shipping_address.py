"""
Fix SO 004149: set partner_shipping_id to the Property that matches Workiz (941 Oceo Cir S, Palm Springs).
Currently the SO may be showing Contact (Palm Desert = bill-to) as the delivery address;
it should show the Property address that matches Workiz.
Run from this folder: python fix_so_004149_shipping_address.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
from functions.workiz.get_job_details import get_job_details

WORKIZ_UUID_FIELD = "x_studio_x_studio_workiz_uuid"
CATEGORY_FIELD = "x_studio_x_studio_record_category"


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
    sos = odoo_rpc("sale.order", "search_read", [[["name", "=", so_name]]], {
        "fields": ["id", "name", "partner_id", "partner_shipping_id", WORKIZ_UUID_FIELD],
        "limit": 1,
    })
    if not sos:
        print(f"SO {so_name} not found.")
        return
    so = sos[0]
    so_id = so["id"]
    contact_id = so.get("partner_id")
    contact_id = contact_id[0] if isinstance(contact_id, (list, tuple)) else contact_id
    shipping_id = so.get("partner_shipping_id")
    shipping_id = shipping_id[0] if isinstance(shipping_id, (list, tuple)) else shipping_id
    uuid_val = (so.get(WORKIZ_UUID_FIELD) or "").strip()
    if not uuid_val:
        print("SO has no Workiz UUID.")
        return

    # Load both partners
    partner_ids = list({contact_id, shipping_id})
    partners = odoo_rpc("res.partner", "search_read", [[["id", "in", partner_ids]]], {
        "fields": ["id", "name", "street", "city", "zip", CATEGORY_FIELD],
        "limit": 10,
    })
    by_id = {p["id"]: p for p in partners}
    contact = by_id.get(contact_id, {})
    shipping = by_id.get(shipping_id, {})

    # Workiz = property address
    job = get_job_details(uuid_val, quiet=True)
    if not job:
        print("Could not load Workiz job.")
        return
    w_street = (job.get("Address") or "").strip()
    w_city = (job.get("City") or "").strip()
    w_zip = (job.get("PostalCode") or "").strip()

    print("=" * 60)
    print(f"SO {so_name} (id {so_id})")
    print("=" * 60)
    print("\n--- Contact (Bill To / partner_id) ---")
    print(f"  id={contact_id}  name={contact.get('name')}  street={contact.get('street')}  city={contact.get('city')}  category={contact.get(CATEGORY_FIELD)}")
    print("\n--- Current Delivery (partner_shipping_id) ---")
    print(f"  id={shipping_id}  name={shipping.get('name')}  street={shipping.get('street')}  city={shipping.get('city')}  category={shipping.get(CATEGORY_FIELD)}")
    print("\n--- Workiz (property address for this job) ---")
    print(f"  Address={w_street}  City={w_city}  Zip={w_zip}")

    # If shipping already matches Workiz, nothing to do
    if shipping.get("street", "").strip() == w_street and (shipping.get("city") or "").strip() == w_city:
        print("\n[OK] Delivery address already matches Workiz. No change.")
        return

    # Find a Property (record_category=Property) with this street+city, optionally linked to same contact
    # Search by street and category Property
    props = odoo_rpc("res.partner", "search_read", [
        [
            [CATEGORY_FIELD, "=", "Property"],
            ["street", "=", w_street],
        ]
    ], {"fields": ["id", "name", "street", "city", "zip", "parent_id"], "limit": 10})
    if not props:
        # Try ilike in case of extra spaces
        props = odoo_rpc("res.partner", "search_read", [
            [
                [CATEGORY_FIELD, "=", "Property"],
                ["street", "ilike", w_street],
            ]
        ], {"fields": ["id", "name", "street", "city", "zip"], "limit": 10})

    correct_property_id = None
    for p in props:
        if (p.get("street") or "").strip() == w_street and (p.get("city") or "").strip() == w_city:
            correct_property_id = p["id"]
            print(f"\n[*] Found Property id={correct_property_id}  {p.get('street')}, {p.get('city')}")
            break
    if not correct_property_id and props:
        correct_property_id = props[0]["id"]
        print(f"\n[*] Using Property id={correct_property_id}  {props[0].get('street')}, {props[0].get('city')}")

    if not correct_property_id:
        print("\n[!] No Property in Odoo with Workiz address. Create the Property or fix address and re-run.")
        return

    if correct_property_id == shipping_id:
        print("\n[OK] SO already has correct Property as delivery. No change.")
        return

    # Update SO: set partner_shipping_id to the correct Property
    odoo_rpc("sale.order", "write", [[so_id], {"partner_shipping_id": correct_property_id}])
    print(f"\n[OK] Updated SO {so_name}: partner_shipping_id = {correct_property_id} (Property: {w_street}, {w_city})")
    print("     Delivery address on the SO will now show the property address, not the contact (Palm Desert).")


if __name__ == "__main__":
    main()
