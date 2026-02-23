"""
Chase Zelle CSV -> Odoo SO matching for invoicing.

Reads Chase9008_Activity_*.CSV from the workspace root, parses Zelle payments (customer name,
amount, date), finds the Odoo Sales Order most likely associated (same customer, SO date
closest to Zelle payment date), and outputs: Customer, SO, Zelle amount, Payment date.

Usage:
  python zelle_to_odoo_so_report.py
  python zelle_to_odoo_so_report.py --csv "path/to/Chase9008_Activity_20260221.CSV"
  python zelle_to_odoo_so_report.py --output zelle_so_matches.csv

Output: printed table + optional CSV. SO = Odoo sale.order name (e.g. 004170).
"""
import sys
import os
import csv
import re
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import requests

from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(PROJECT_ROOT, "Chase9008_Activity_20260221.CSV")
CATEGORY_FIELD = "x_studio_x_studio_record_category"


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


def parse_zelle_customer(description):
    """From 'Zelle payment from Linda Diane Lusk USBtWjhrFrdJ' return 'Linda Diane Lusk'.
    Strip trailing bank ref (long alphanumeric token)."""
    if not description or "Zelle payment from " not in description:
        return ""
    name_part = description.split("Zelle payment from ", 1)[1].strip()
    if not name_part:
        return ""
    parts = name_part.split()
    # Remove trailing token if it looks like a ref: alphanumeric, length >= 6
    while parts:
        last = parts[-1]
        if re.match(r"^[A-Za-z0-9]{6,}$", last):
            parts.pop()
        else:
            break
    return " ".join(parts).strip() if parts else name_part


def parse_chase_zelle_csv(path):
    """Yield (customer_name, amount, posting_date_str, raw_description) for each Zelle CREDIT."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            details = (row.get("Details") or "").strip()
            desc = (row.get("Description") or "").strip()
            if details.upper() != "CREDIT":
                continue
            if "Zelle payment from " not in desc:
                continue
            amount_str = (row.get("Amount") or "").strip()
            try:
                amount = float(amount_str.replace(",", ""))
            except ValueError:
                continue
            posting = (row.get("Posting Date") or "").strip()
            customer = parse_zelle_customer(desc)
            yield customer, amount, posting, desc


def parse_date_mmddyyyy(s):
    """Parse MM/DD/YYYY to date for comparison."""
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except Exception:
        return None


def find_contacts_by_name_in_memory(contacts_list, name):
    """From list of {id, name}, return ids where name contains first and last word of name (case-insensitive)."""
    if not name or not name.strip():
        return [], ""
    words = [w.strip() for w in name.split() if len(w.strip()) > 1]
    if not words:
        return [], ""
    search_words = [words[0], words[-1]] if len(words) > 1 else [words[0]]
    name_lower = " ".join(search_words).lower()
    matched = []
    display_name = ""
    for c in contacts_list:
        n = (c.get("name") or "").strip()
        if not n:
            continue
        n_lower = n.lower()
        if all(w.lower() in n_lower for w in search_words):
            matched.append(c["id"])
            if not display_name:
                display_name = n
    return matched, display_name


def fetch_all_contacts_properties_sos(odoo_rpc):
    """One-time fetch: all Contacts, all Properties (parent_id), all SOs. Returns (contacts, parent_to_properties, partner_to_sos)."""
    contacts = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Contact"]]], {"fields": ["id", "name"]})
    properties = odoo_rpc("res.partner", "search_read", [[[CATEGORY_FIELD, "=", "Property"]]], {"fields": ["id", "parent_id"]})
    # parent_id can be [id, name] or False
    parent_to_props = {}
    for p in properties:
        pid = p.get("parent_id")
        if pid is None or pid is False:
            continue
        parent_id = pid[0] if isinstance(pid, (list, tuple)) else pid
        parent_to_props.setdefault(parent_id, []).append(p["id"])

    sos = odoo_rpc("sale.order", "search_read", [[]], {"fields": ["id", "name", "date_order", "partner_id"], "order": "date_order desc"})
    partner_to_sos = {}
    for so in sos:
        pid = so.get("partner_id")
        if pid is None:
            continue
        partner_id = pid[0] if isinstance(pid, (list, tuple)) else pid
        partner_to_sos.setdefault(partner_id, []).append(so)
    return contacts, parent_to_props, partner_to_sos


def pick_closest_so_by_date(sos, zelle_date):
    """Of list of SO dicts (with date_order), return the one with date_order closest to zelle_date."""
    if not sos:
        return None
    zelle_d = zelle_date if hasattr(zelle_date, "day") else parse_date_mmddyyyy(str(zelle_date))
    if not zelle_d:
        return sos[0] if sos else None
    best = None
    best_diff = None
    for so in sos:
        do = so.get("date_order")
        if not do:
            continue
        # date_order can be "2025-02-10 18:30:00" or datetime
        if isinstance(do, str):
            try:
                do = datetime.strptime(do[:10], "%Y-%m-%d").date()
            except Exception:
                continue
        else:
            do = getattr(do, "date", lambda: do)() if hasattr(do, "date") else do
        diff = abs((do - zelle_d).days)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best = so
    return best or (sos[0] if sos else None)


def main():
    parser = argparse.ArgumentParser(description="Match Chase Zelle payments to Odoo SOs by customer and closest date.")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to Chase activity CSV")
    parser.add_argument("--output", default=None, help="Output CSV path (default: print only)")
    parser.add_argument("--test", action="store_true", help="Use Odoo test DB (config_test)")
    args = parser.parse_args()

    global ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
    if args.test:
        from config_test import ODOO_URL as U, ODOO_DB as D, ODOO_USER_ID as I, ODOO_API_KEY as K
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = U, D, I, K

    if not os.path.isfile(args.csv):
        print(f"[!] CSV not found: {args.csv}")
        return

    # Collect Zelle rows
    zelle_rows = list(parse_chase_zelle_csv(args.csv))
    print(f"[*] Parsed {len(zelle_rows)} Zelle payment(s) from {args.csv}")

    # One-time fetch from Odoo (fast)
    print("[*] Fetching Contacts, Properties, and Sales Orders from Odoo...")
    contacts_list, parent_to_props, partner_to_sos = fetch_all_contacts_properties_sos(odoo_rpc)
    print(f"    Contacts: {len(contacts_list)}, Properties: {sum(len(v) for v in parent_to_props.values())}, SOs: {sum(len(v) for v in partner_to_sos.values())}\n")

    report = []
    for customer_raw, amount, posting_str, zelle_description in zelle_rows:
        zelle_date = parse_date_mmddyyyy(posting_str)
        contact_ids, customer_display = find_contacts_by_name_in_memory(contacts_list, customer_raw)
        if not customer_display:
            customer_display = customer_raw
        property_ids = []
        for cid in contact_ids:
            property_ids.extend(parent_to_props.get(cid, []))
        all_partner_ids = list(set(property_ids + contact_ids))
        sos = []
        for pid in all_partner_ids:
            sos.extend(partner_to_sos.get(pid, []))
        so = pick_closest_so_by_date(sos, zelle_date)
        so_name = so.get("name") if so else ""
        report.append({
            "customer": customer_display,
            "so": so_name,
            "zelle_amount": amount,
            "payment_date": posting_str,
            "zelle_description": zelle_description,
        })

    # Sort by payment date descending (most recent first); use parsed date for correct order
    def _sort_key(r):
        d = parse_date_mmddyyyy(r["payment_date"])
        return (d or datetime.min.date(), r["customer"])

    report.sort(key=_sort_key, reverse=True)

    # Print table (include truncated Zelle description)
    print(f"{'Customer':<36} {'SO':<10} {'Amount':>8} {'Date':<12} {'Zelle (original)'}")
    print("-" * 95)
    for r in report:
        zelle_short = (r["zelle_description"] or "")[:48]
        print(f"{r['customer'][:35]:<36} {r['so']:<10} {r['zelle_amount']:>8.2f} {r['payment_date']:<12} {zelle_short}")

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["customer", "so", "zelle_amount", "payment_date", "zelle_description"])
            w.writeheader()
            w.writerows(report)
        print(f"\n[OK] Wrote {len(report)} rows to {args.output}")

    return report


if __name__ == "__main__":
    main()
