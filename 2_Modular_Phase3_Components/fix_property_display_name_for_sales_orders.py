"""
Fix SO Customer column: remove duplicate contact name (Name, Name, Address -> Name, Address).

Updates ONLY when the Property name has the same name twice (e.g. "Adam Ruelas, Adam Ruelas, 18166 Andrea Court").
With --fix-display-double: set Property name to address only so list shows "Name, Address".

If the fix reverts after you refresh (correct then wrong again), something is overwriting the partner name:
- Zapier: a Zap triggered by "Odoo record updated" that syncs or runs Phase 4 can write back.
- Odoo: Studio computed field or Automation on res.partner that sets name from parent + street.
Use --repeat N to re-apply the fix every N seconds (e.g. 60) until you find and fix the cause.

Default = TEST. Use --production for live.
  python fix_property_display_name_for_sales_orders.py [--dry-run] [--production] [--fix-display-double]
  python fix_property_display_name_for_sales_orders.py --production --fix-display-double --repeat 60
"""
import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

import requests

from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY
from config import ODOO_URL as PROD_URL, ODOO_DB as PROD_DB, ODOO_USER_ID as PROD_UID, ODOO_API_KEY as PROD_KEY

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
    parser = argparse.ArgumentParser(description="Set Property name to 'Contact Name, Address' for SO display.")
    parser.add_argument("--dry-run", action="store_true", help="Only list changes; do not write.")
    parser.add_argument("--production", action="store_true", help="Run against LIVE Odoo (default: test).")
    parser.add_argument("--list-names", action="store_true", help="Print all SO partner names (debug); no updates.")
    parser.add_argument("--fix-display-double", action="store_true",
        help="Set Property name to address only when name contains a comma (fixes UI showing 'Name, Name, Address').")
    parser.add_argument("--repeat", type=int, default=0, metavar="SECONDS",
        help="Re-run the fix every N seconds (e.g. 60). Use if something keeps overwriting the name.")
    args = parser.parse_args()
    dry_run = getattr(args, "dry_run", False)
    use_production = getattr(args, "production", False)
    list_names = getattr(args, "list_names", False)
    fix_display_double = getattr(args, "fix_display_double", False)
    repeat_seconds = getattr(args, "repeat", 0) or 0

    if use_production:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = PROD_URL, PROD_DB, PROD_UID, PROD_KEY
        print("[LIVE] Using production Odoo:", ODOO_DB)
    else:
        print("[TEST] Using test Odoo:", ODOO_DB)

    # All SOs: partner_id, partner_shipping_id (need both for "Contact + Property" display fix)
    sos = odoo_rpc("sale.order", "search_read", [[]], {"fields": ["name", "partner_id", "partner_shipping_id"], "limit": 50000})
    partner_ids = set()
    for so in sos:
        for key in ("partner_id", "partner_shipping_id"):
            pid = so.get(key)
            if pid is None:
                continue
            pid = pid[0] if isinstance(pid, (list, tuple)) else pid
            if pid:
                partner_ids.add(pid)

    if not partner_ids:
        print("No SO partners found.")
        return

    # Read all partners: id, name, street, parent_id
    partners = odoo_rpc("res.partner", "read", [list(partner_ids)], {"fields": ["id", "name", "street", "parent_id"]})
    partner_by_id = {p["id"]: p for p in partners}
    # Only those with parent_id (Property with Contact)
    with_parent = [p for p in partners if p.get("parent_id")]
    parent_ids = set()
    for p in with_parent:
        par = p["parent_id"]
        parent_ids.add(par[0] if isinstance(par, (list, tuple)) else par)

    if not parent_ids:
        print("No SO partners with parent_id (Property with Contact). Nothing to fix.")
        return

    # Read Contact names
    contacts = odoo_rpc("res.partner", "read", [list(parent_ids)], {"fields": ["id", "name"]})
    contact_name_by_id = {c["id"]: (c.get("name") or "").strip() for c in contacts}

    if list_names:
        # Debug: print names with 2+ commas (possible "Name, Name, Address") and first-two-parts-equal
        print("Partner names with 2+ commas where first two parts are identical (possible double name):")
        for p in with_parent:
            current_name = (p.get("name") or "").strip()
            parts = [x.strip() for x in current_name.split(",")]
            if len(parts) >= 2 and parts[0] and parts[0] == parts[1]:
                parent_id = p.get("parent_id")
                parent_id = parent_id[0] if isinstance(parent_id, (list, tuple)) else parent_id
                contact_name = (contact_name_by_id.get(parent_id) or "").strip()
                print(f"  ID {p['id']}: \"{current_name}\" (contact='{contact_name}')")
        print("\nAll partner names containing a comma (first 50):")
        for p in with_parent[:50]:
            print(f"  ID {p['id']}: \"{(p.get('name') or '').strip()}\"")
        return

    to_update_dict = {}  # id -> {id, current, new} so we don't double-update
    for p in with_parent:
        pid = p["id"]
        current_name = (p.get("name") or "").strip()
        street = (p.get("street") or "").strip() or current_name
        parent_id = p.get("parent_id")
        parent_id = parent_id[0] if isinstance(parent_id, (list, tuple)) else parent_id
        contact_name = (contact_name_by_id.get(parent_id) or "").strip()
        if not contact_name:
            continue
        new_name = f"{contact_name}, {street}".strip(", ").strip()
        if not new_name or new_name == current_name:
            continue
        # Fix when first two comma-separated parts are identical ("Name, Name, Address" in DB).
        parts = [x.strip() for x in current_name.split(",")]
        first_two_same = len(parts) >= 2 and parts[0] and parts[0] == parts[1]
        if not first_two_same:
            continue
        to_update_dict[pid] = {"id": pid, "current": current_name, "new": new_name}

    # Second pass: Odoo list may show "Contact name, Property name". When SO partner = Contact and shipping = Property
    # with name "Name, Address", display is "Name, Name, Address". Fix by setting that Property name to address only.
    # Only touch Properties that are partner_shipping_id on SOs where partner_id is a Contact (no parent).
    so_partner_is_contact = set()
    for so in sos:
        pid = so.get("partner_id")
        if pid is None:
            continue
        pid = pid[0] if isinstance(pid, (list, tuple)) else pid
        p = partner_by_id.get(pid)
        if p and not p.get("parent_id"):
            so_partner_is_contact.add(pid)
    shipping_ids_when_customer_is_contact = set()
    for so in sos:
        if so.get("partner_id") is None:
            continue
        pid = so["partner_id"][0] if isinstance(so["partner_id"], (list, tuple)) else so["partner_id"]
        if pid not in so_partner_is_contact:
            continue
        sid = so.get("partner_shipping_id")
        if sid is None:
            continue
        sid = sid[0] if isinstance(sid, (list, tuple)) else sid
        shipping_ids_when_customer_is_contact.add(sid)
    for p in with_parent:
        pid = p["id"]
        if pid not in shipping_ids_when_customer_is_contact:
            continue
        current_name = (p.get("name") or "").strip()
        street = (p.get("street") or "").strip() or current_name
        if not street or current_name == street:
            continue
        parent_id = p.get("parent_id")
        parent_id = parent_id[0] if isinstance(parent_id, (list, tuple)) else parent_id
        contact_name = (contact_name_by_id.get(parent_id) or "").strip()
        if not contact_name:
            continue
        # Property name is "Name, Address" and this Property is shipping on SOs where customer = Contact -> display double.
        if not current_name.startswith(contact_name + ",") and not current_name.startswith(contact_name + ", "):
            continue
        new_name = street
        if new_name == current_name:
            continue
        to_update_dict[pid] = {"id": pid, "current": current_name, "new": new_name}

    # Third pass (--fix-display-double): When Odoo Customer column shows "parent.name, partner.name", any Property
    # with name "Name, Address" displays as "Name, Name, Address". Set such names to address only.
    if fix_display_double:
        for p in with_parent:
            pid = p["id"]
            current_name = (p.get("name") or "").strip()
            street = (p.get("street") or "").strip() or current_name
            if not street or current_name == street:
                continue
            if "," not in current_name:
                continue
            to_update_dict[pid] = {"id": pid, "current": current_name, "new": street}

    to_update = list(to_update_dict.values())
    print(f"SO partners (unique): {len(partner_ids)}")
    print(f"Partners with parent_id (Property + Contact): {len(with_parent)}")
    print(f"Properties to update (remove double name -> 'Contact Name, Address'): {len(to_update)}")

    if dry_run:
        for u in to_update[:30]:
            print(f"  ID {u['id']}: \"{u['current']}\" -> \"{u['new']}\"")
        if len(to_update) > 30:
            print(f"  ... and {len(to_update) - 30} more.")
        print("\n[DRY RUN] No changes made. Run without --dry-run to apply.")
        return

    updated = 0
    for u in to_update:
        try:
            odoo_rpc("res.partner", "write", [[u["id"]], {"name": u["new"]}])
            updated += 1
            if updated <= 15 or updated % 200 == 0:
                c, n = u['current'][:50], u['new'][:50]
                if len(u['current']) > 50: c += "..."
                if len(u['new']) > 50: n += "..."
                print(f"  Updated partner ID {u['id']}: \"{c}\" -> \"{n}\"")
        except Exception as e:
            print(f"  [ERROR] Partner ID {u['id']}: {e}")
    print(f"\n[OK] Updated {updated} Property names (double name removed). SO Customer column = 'Contact Name, Address'.")
    return repeat_seconds


if __name__ == "__main__":
    while True:
        repeat = main()
        if not repeat or repeat <= 0:
            break
        print(f"[*] Re-running in {repeat}s (--repeat). Ctrl+C to stop.")
        time.sleep(repeat)
