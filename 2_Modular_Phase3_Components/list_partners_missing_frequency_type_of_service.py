"""
List res.partner records (Contacts vs Properties) that do NOT have
frequency or type_of_service populated.

In Odoo both are res.partner; we split by x_studio_x_studio_record_category:
  - "Contact" = billing contact (customer)
  - "Property" = delivery address / service location (the "brain" for service data)

Our sync writes frequency/type to the PROPERTY only. Historical migration may have
populated one or both. Some records will legitimately be empty (never filled in Workiz).

Run from 2_Modular_Phase3_Components: python list_partners_missing_frequency_type_of_service.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

FREQ_FIELD = "x_studio_x_frequency"
TOS_FIELD = "x_studio_x_type_of_service"
CATEGORY_FIELD = "x_studio_x_studio_record_category"


def odoo_search_read(domain, fields, limit=None):
    kwargs = {"fields": fields}
    if limit is not None:
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
                "res.partner",
                "search_read",
                [domain],
                kwargs,
            ],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        msg = data["error"].get("data", {}).get("message", str(data["error"]))
        raise RuntimeError(msg)
    return data.get("result", [])


def odoo_search_count(domain):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "res.partner", "search_count", [domain]],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result", 0)


def analyze_group(records, label):
    """Given list of partner dicts with FREQ_FIELD and TOS_FIELD, return stats."""
    total = len(records)
    has_freq = sum(1 for r in records if r.get(FREQ_FIELD))
    has_tos = sum(1 for r in records if r.get(TOS_FIELD))
    has_both = sum(1 for r in records if r.get(FREQ_FIELD) and r.get(TOS_FIELD))
    missing_freq = sum(1 for r in records if not r.get(FREQ_FIELD))
    missing_tos = sum(1 for r in records if not r.get(TOS_FIELD))
    missing_either = sum(1 for r in records if not r.get(FREQ_FIELD) or not r.get(TOS_FIELD))
    return {
        "total": total,
        "has_freq": has_freq,
        "has_tos": has_tos,
        "has_both": has_both,
        "missing_freq": missing_freq,
        "missing_tos": missing_tos,
        "missing_either": missing_either,
    }


def main():
    fields = ["id", "name", "street", FREQ_FIELD, TOS_FIELD, "ref"]

    # ---- Contacts ----
    domain_contact = [[CATEGORY_FIELD, "=", "Contact"]]
    try:
        contacts = odoo_search_read(domain_contact, fields, limit=0)
    except Exception as e:
        if "record_category" in str(e) or "record_category" in str(e).lower():
            print("Could not filter by record category. Trying without category (all res.partner)...")
            contacts = []
        else:
            raise
    contact_count = odoo_search_count(domain_contact)

    # ---- Properties ----
    domain_property = [[CATEGORY_FIELD, "=", "Property"]]
    try:
        properties = odoo_search_read(domain_property, fields, limit=0)
    except Exception as e:
        print(f"Error fetching properties: {e}")
        properties = []
    property_count = odoo_search_count(domain_property)

    # Stats
    c = analyze_group(contacts, "Contact")
    p = analyze_group(properties, "Property")

    print("=" * 70)
    print("Frequency & Type of Service on res.partner (Contact vs Property)")
    print("=" * 70)
    print()
    print("CONTACTS (billing / customer) — x_studio_x_studio_record_category = Contact")
    print("-" * 70)
    print(f"  Total Contacts:                    {c['total']}")
    print(f"  With Frequency populated:           {c['has_freq']}")
    print(f"  With Type of Service populated:    {c['has_tos']}")
    print(f"  With BOTH populated:               {c['has_both']}")
    print(f"  Missing Frequency:                 {c['missing_freq']}")
    print(f"  Missing Type of Service:           {c['missing_tos']}")
    print(f"  Missing EITHER (freq or type):    {c['missing_either']}")
    print()
    print("PROPERTIES (delivery address / service location — 'the brain')")
    print("-" * 70)
    print(f"  Total Properties:                   {p['total']}")
    print(f"  With Frequency populated:          {p['has_freq']}")
    print(f"  With Type of Service populated:    {p['has_tos']}")
    print(f"  With BOTH populated:               {p['has_both']}")
    print(f"  Missing Frequency:                 {p['missing_freq']}")
    print(f"  Missing Type of Service:           {p['missing_tos']}")
    print(f"  Missing EITHER (freq or type):    {p['missing_either']}")
    print()
    print("Takeaway: Our sync writes frequency/type to the PROPERTY only. Historical")
    print("migration likely populated properties. Some blanks are normal (not set in Workiz).")
    print("=" * 70)

    # Sample of properties missing either
    missing_props = [r for r in properties if not r.get(FREQ_FIELD) or not r.get(TOS_FIELD)]
    if missing_props:
        print()
        print("Sample of PROPERTIES missing frequency or type of service (first 20):")
        for r in missing_props[:20]:
            print(f"  ID {r['id']:5}  {str(r.get('name') or ''):40}  freq={repr(r.get(FREQ_FIELD)):12}  type={repr(r.get(TOS_FIELD))}")
        if len(missing_props) > 20:
            print(f"  ... and {len(missing_props) - 20} more properties")

    # Sample of contacts missing either
    missing_contacts = [r for r in contacts if not r.get(FREQ_FIELD) or not r.get(TOS_FIELD)]
    if missing_contacts:
        print()
        print("Sample of CONTACTS missing frequency or type of service (first 20):")
        for r in missing_contacts[:20]:
            print(f"  ID {r['id']:5}  {str(r.get('name') or ''):40}  freq={repr(r.get(FREQ_FIELD)):12}  type={repr(r.get(TOS_FIELD))}")
        if len(missing_contacts) > 20:
            print(f"  ... and {len(missing_contacts) - 20} more contacts")


if __name__ == "__main__":
    main()
