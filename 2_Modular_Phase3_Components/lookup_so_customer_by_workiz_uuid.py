"""
Look up a Sales Order by Odoo SO name (e.g. 002104), cross-reference with Workiz via UUID,
and report Odoo vs Workiz customer name so you can decide how to fix.

Usage:
  python lookup_so_customer_by_workiz_uuid.py 002104
  python lookup_so_customer_by_workiz_uuid.py 002104 --test   # use test Odoo DB

Linking: SO has x_studio_x_studio_workiz_uuid → Workiz job UUID. SO partner_id = Property;
Contact = Property.parent_id. Workiz job has ClientId, FirstName, LastName. Odoo Contact has ref=ClientId, name.
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
import requests

from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, WORKIZ_BASE_URL, WORKIZ_AUTH_SECRET
from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY

ODOO_SO_NAME_FIELD = "name"
WORKIZ_UUID_FIELD = "x_studio_x_studio_workiz_uuid"
CATEGORY_FIELD = "x_studio_x_studio_record_category"


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
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


def get_workiz_job(job_uuid):
    """Fetch job from Workiz by UUID."""
    url = f"{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    try:
        resp = requests.get(url, timeout=10)
        result = resp.json()
        if result.get("flag") and result.get("data"):
            return result["data"][0]
    except Exception as e:
        print(f"[!] Workiz API error: {e}")
    return None


def main():
    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    parser = argparse.ArgumentParser(description="Look up SO by name and cross-reference Odoo customer with Workiz via UUID.")
    parser.add_argument("so_name", help="Odoo Sales Order name (e.g. 002104)")
    parser.add_argument("--test", action="store_true", help="Use Odoo TEST database.")
    args = parser.parse_args()

    so_name = (args.so_name or "").strip()
    if not so_name:
        print("Usage: python lookup_so_customer_by_workiz_uuid.py <SO_NAME>   e.g. 002104")
        return

    if args.test:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        print(f"[TEST] Odoo DB: {ODOO_DB}\n")
    else:
        print(f"[LIVE] Odoo DB: {ODOO_DB}\n")

    # ---- 1) Odoo: find SO by name ----
    sos = odoo_rpc("sale.order", "search_read", [[[ODOO_SO_NAME_FIELD, "=", so_name]]], {
        "fields": ["id", "name", "partner_id", "partner_shipping_id", WORKIZ_UUID_FIELD, "state"],
        "limit": 1,
    })
    if not sos:
        print(f"No Sales Order found with name = '{so_name}' in Odoo.")
        return
    so = sos[0]
    so_id = so["id"]
    workiz_uuid = (so.get(WORKIZ_UUID_FIELD) or "").strip()
    partner_id = so.get("partner_id")
    shipping_id = so.get("partner_shipping_id")
    pid = partner_id[0] if isinstance(partner_id, (list, tuple)) else partner_id
    sid = shipping_id[0] if isinstance(shipping_id, (list, tuple)) else shipping_id

    print(f"Sales Order: {so['name']}  (id={so_id}, state={so.get('state')})")
    print(f"Workiz UUID: {workiz_uuid or '(not set)'}")
    print(f"SO partner_id (Property): {pid}")
    print(f"SO partner_shipping_id:    {sid}")
    print()

    # ---- 2) Odoo: get Property and Contact (customer) ----
    odoo_contact_id = None
    odoo_contact_name = None
    odoo_contact_ref = None
    property_name = None
    if pid:
        partners = odoo_rpc("res.partner", "search_read", [[["id", "=", pid]]], {"fields": ["id", "name", "parent_id", "ref", "city", "street"], "limit": 1})
        if partners:
            prop = partners[0]
            property_name = prop.get("name")
            parent_id = prop.get("parent_id")
            contact_id = parent_id[0] if isinstance(parent_id, (list, tuple)) else parent_id
            if contact_id:
                contacts = odoo_rpc("res.partner", "search_read", [[["id", "=", contact_id]]], {"fields": ["id", "name", "ref"], "limit": 1})
                if contacts:
                    c = contacts[0]
                    odoo_contact_id = c["id"]
                    odoo_contact_name = (c.get("name") or "").strip()
                    odoo_contact_ref = (c.get("ref") or "").strip()

    print("--- Odoo (customer = Contact, parent of Property) ---")
    print(f"  Property: {property_name or '(n/a)'}  (id={pid})")
    print(f"  Contact:  {odoo_contact_name or '(n/a)'}  (id={odoo_contact_id}, ref/ClientId={odoo_contact_ref or '(none)'})")
    print()

    # ---- 3) Workiz: fetch job by UUID ----
    workiz_name = None
    workiz_client_id = None
    if workiz_uuid:
        job = get_workiz_job(workiz_uuid)
        if job:
            fn = (job.get("FirstName") or "").strip()
            ln = (job.get("LastName") or "").strip()
            workiz_name = f"{fn} {ln}".strip()
            workiz_client_id = str(job.get("ClientId") or "").strip() or None
            print("--- Workiz (job by UUID) ---")
            print(f"  Customer: {workiz_name or '(n/a)'}")
            print(f"  ClientId: {workiz_client_id or '(none)'}")
        else:
            print("--- Workiz ---")
            print("  (Could not fetch job by UUID; API error or job not found.)")
    else:
        print("--- Workiz ---")
        print("  (No Workiz UUID on SO; cannot cross-reference.)")
    print()

    # ---- 4) Recommendation ----
    print("--- How to handle ---")
    if not workiz_uuid:
        print("  SO has no Workiz UUID. Set x_studio_x_studio_workiz_uuid to the job UUID from Workiz if this SO is the mirror of a Workiz job.")
        return
    if not workiz_name and not workiz_client_id:
        print("  Workiz job not found or API failed. Check UUID in Workiz; if correct, fix Odoo contact name manually or re-run when API is available.")
        return

    # Compare names and ClientId
    name_ok = (odoo_contact_name or "").strip() == (workiz_name or "").strip()
    ref_ok = (odoo_contact_ref or "").strip() == (workiz_client_id or "").strip()

    if name_ok and ref_ok:
        print("  Odoo contact name and ref match Workiz. No change needed.")
        return
    if not ref_ok and workiz_client_id:
        print(f"  ClientId mismatch: Odoo ref={odoo_contact_ref!r}, Workiz ClientId={workiz_client_id!r}.")
        print("  This SO may be linked to the wrong contact. Fix ref on the Odoo Contact to match Workiz ClientId, or link the SO to the correct Property/Contact.")
        return
    if not name_ok:
        print(f"  Name mismatch: Odoo contact = {odoo_contact_name!r}, Workiz = {workiz_name!r}.")
        print("  Option A: Update Odoo contact name to match Workiz (source of truth):")
        print(f"    - In Odoo: Contacts → find ref={odoo_contact_ref} → set name to {workiz_name!r}")
        print("  Option B: Run sync from Workiz snapshot to fix names in bulk:")
        print("    python sync_contacts_properties_from_workiz.py --production --dry-run   # preview")
        print("    python sync_contacts_properties_from_workiz.py --production               # apply (updates Odoo name = Workiz name for same ClientId)")
    return


if __name__ == "__main__":
    main()
