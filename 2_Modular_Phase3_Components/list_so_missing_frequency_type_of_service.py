"""
List Sales Orders that do NOT have frequency or type of service populated.
Run from 2_Modular_Phase3_Components: python list_so_missing_frequency_type_of_service.py

If the two SO fields (x_studio_x_studio_frequency_so, x_studio_x_studio_type_of_service_so) do not
exist on sale.order yet, this script lists all SOs with a Workiz UUID as backfill candidates.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def odoo_search_read(model, domain, fields, limit=None):
    kwargs = {"fields": fields}
    if limit:
        kwargs["limit"] = limit
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                model,
                "search_read",
                [domain],
                kwargs,
            ],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        err = data["error"]
        msg = err.get("data", {}).get("message", str(err))
        raise RuntimeError(msg)
    return data.get("result", [])


def odoo_search_count(domain):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "search_count", [domain]],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result", 0)


def main():
    # Fields we need for "missing" check (must exist on sale.order)
    freq_field = "x_studio_x_studio_frequency_so"
    tos_field = "x_studio_x_studio_type_of_service_so"
    fields_with_freq_tos = ["id", "name", "x_studio_x_studio_workiz_uuid", freq_field, tos_field]
    fields_uuid_only = ["id", "name", "x_studio_x_studio_workiz_uuid"]

    # Check if SO has the two custom fields by trying a small search_read
    fields_exist = False
    try:
        odoo_search_read("sale.order", [], fields_with_freq_tos, limit=1)
        fields_exist = True
    except Exception as e:
        err = str(e)
        if "frequency_so" in err or "type_of_service_so" in err:
            fields_exist = False
        else:
            raise

    total_count = odoo_search_count([])

    if not fields_exist:
        print("=" * 60)
        print("Sales Order fields for Frequency / Type of Service")
        print("=" * 60)
        print("The fields x_studio_x_studio_frequency_so and x_studio_x_studio_type_of_service_so")
        print("do not exist on Sales Order in Odoo yet.")
        print()
        print("Next steps:")
        print("  1. In Odoo: add the two custom fields on sale.order (see Phase_3_4_5_Reference_Summary.md).")
        print("  2. Re-run this script to list SOs that are missing frequency or type of service.")
        print()
        print("Meanwhile, listing all Sales Orders with a Workiz UUID (backfill candidates):")
        print("-" * 60)
        domain_has_uuid = [["x_studio_x_studio_workiz_uuid", "!=", False]]
        count_with_uuid = odoo_search_count(domain_has_uuid)
        print(f"Total Sales Orders in Odoo:        {total_count}")
        print(f"With Workiz UUID (can backfill):   {count_with_uuid}")
        sos_with_uuid = odoo_search_read("sale.order", domain_has_uuid, fields_uuid_only, limit=0)
        uuids_file = os.path.join(os.path.dirname(__file__), "so_missing_frequency_type_uuids.txt")
        with open(uuids_file, "w") as f:
            for so in sos_with_uuid:
                f.write(so["x_studio_x_studio_workiz_uuid"] + "\n")
        print(f"UUID list written to: {uuids_file}")
        print("=" * 60)
        return

    # Fields exist: find SOs missing frequency OR type_of_service
    domain_missing = [
        "|",
        [freq_field, "in", [False, ""]],
        [tos_field, "in", [False, ""]],
    ]
    missing_count = odoo_search_count(domain_missing)
    missing_sos = odoo_search_read("sale.order", domain_missing, fields_with_freq_tos, limit=0)
    missing_with_uuid = [so for so in missing_sos if so.get("x_studio_x_studio_workiz_uuid")]
    missing_no_uuid = [so for so in missing_sos if not so.get("x_studio_x_studio_workiz_uuid")]

    print("=" * 60)
    print("Sales Orders missing Frequency or Type of Service")
    print("=" * 60)
    print(f"Total Sales Orders in Odoo:     {total_count}")
    print(f"Missing frequency or type:      {missing_count}")
    print(f"  - With Workiz UUID (can backfill): {len(missing_with_uuid)}")
    print(f"  - Without Workiz UUID:             {len(missing_no_uuid)}")
    print()

    if missing_with_uuid:
        print("First 30 with Workiz UUID (can backfill from Workiz):")
        print("-" * 60)
        for so in missing_with_uuid[:30]:
            freq = so.get(freq_field) or "(empty)"
            tos = so.get(tos_field) or "(empty)"
            print(f"  ID {so['id']:5}  {so['name']:12}  UUID: {so.get('x_studio_x_studio_workiz_uuid') or 'N/A':8}  freq={freq}  type={tos}")
        if len(missing_with_uuid) > 30:
            print(f"  ... and {len(missing_with_uuid) - 30} more with UUID")
        print()
        uuids_file = os.path.join(os.path.dirname(__file__), "so_missing_frequency_type_uuids.txt")
        with open(uuids_file, "w") as f:
            for so in missing_with_uuid:
                f.write(so["x_studio_x_studio_workiz_uuid"] + "\n")
        print(f"Full list of {len(missing_with_uuid)} Workiz UUIDs written to: {uuids_file}")

    if missing_no_uuid:
        print("Sample without Workiz UUID (cannot backfill from Workiz):")
        for so in missing_no_uuid[:10]:
            print(f"  ID {so['id']}  {so['name']}")
        if len(missing_no_uuid) > 10:
            print(f"  ... and {len(missing_no_uuid) - 10} more")
    print("=" * 60)


if __name__ == "__main__":
    main()
