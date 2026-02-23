"""
Backfill Odoo property frequency and type_of_service from Holy Grail CSV (done jobs).
No Workiz API calls for jobs in the CSV. Optional API fallback for UUIDs not in CSV.

Steps:
  1. Get properties missing freq/type from Odoo (record_category=Property).
  2. Map each property -> one Workiz UUID via sale.order (partner_shipping_id).
  3. Load Holy Grail CSV (done jobs) into UUID -> {frequency, type_of_service}.
  4. For each property with UUID: if UUID in CSV and has data -> update Odoo property.
  5. Optional: --api-fallback with delay for UUIDs not in CSV (open jobs).

Usage:
  python backfill_property_frequency_type_from_holy_grail.py [--dry-run] [--limit N] [--csv PATH] [--api-fallback] [--delay SEC]
"""
import sys
import os
import csv
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

# Default Holy Grail path (relative to project root = parent of 2_Modular_Phase3_Components)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HOLY_GRAIL_CSV = os.path.join(
    PROJECT_ROOT,
    "2_Migration_Archive",
    "Holy Grale Data - Done Stutus",
    "Workiz_6Year_Done_History_Master.csv",
)

CATEGORY_FIELD = "x_studio_x_studio_record_category"
FREQ_FIELD = "x_studio_x_frequency"
TOS_FIELD = "x_studio_x_type_of_service"


def odoo_search_read(model, domain, fields, limit=None, order=None):
    kwargs = {"fields": fields}
    if limit is not None:
        kwargs["limit"] = limit
    if order:
        kwargs["order"] = order
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "search_read", [domain], kwargs],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        msg = data["error"].get("data", {}).get("message", str(data["error"]))
        raise RuntimeError(msg)
    return data.get("result", [])


def odoo_write_property_frequency_type(property_id, frequency=None, type_of_service=None):
    """Update only frequency and/or type_of_service on res.partner."""
    from functions.odoo.update_property_fields import update_property_fields
    return update_property_fields(
        property_id,
        gate_code=None,
        pricing=None,
        last_visit_date=None,
        job_notes=None,
        comments=None,
        frequency=frequency or None,
        alternating=None,
        type_of_service=type_of_service or None,
    )


def load_holy_grail(csv_path):
    """Load Holy Grail CSV; return dict UUID -> {'frequency': str, 'type_of_service': str}."""
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Holy Grail CSV not found: {csv_path}")
    by_uuid = {}
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uid = (row.get("UUID") or "").strip()
            if not uid:
                continue
            freq = (row.get("frequency") or "").strip()
            tos = (row.get("type_of_service") or "").strip()
            by_uuid[uid] = {"frequency": freq, "type_of_service": tos}
    return by_uuid


def main():
    ap = argparse.ArgumentParser(description="Backfill property freq/type from Holy Grail CSV")
    ap.add_argument("--dry-run", action="store_true", help="Do not write to Odoo")
    ap.add_argument("--limit", type=int, default=None, help="Max properties to process (for testing)")
    ap.add_argument("--csv", default=DEFAULT_HOLY_GRAIL_CSV, help="Path to Holy Grail CSV")
    ap.add_argument("--api-fallback", action="store_true", help="Call Workiz API for UUIDs not in CSV (with delay)")
    ap.add_argument("--delay", type=float, default=1.2, help="Seconds between API calls if --api-fallback")
    args = ap.parse_args()

    print("=" * 70)
    print("Backfill Property Frequency & Type of Service from Holy Grail")
    print("=" * 70)

    # 1) Load Holy Grail
    print(f"\n[*] Loading Holy Grail CSV: {args.csv}")
    holy = load_holy_grail(args.csv)
    print(f"[OK] Loaded {len(holy)} jobs (done jobs) by UUID")

    # 2) Properties missing freq/type
    domain_missing = [
        [CATEGORY_FIELD, "=", "Property"],
        "|",
        [FREQ_FIELD, "in", [False, ""]],
        [TOS_FIELD, "in", [False, ""]],
    ]
    properties = odoo_search_read(
        "res.partner",
        domain_missing,
        ["id", "name", "street", FREQ_FIELD, TOS_FIELD],
        limit=args.limit,
    )
    print(f"[*] Found {len(properties)} properties missing frequency or type_of_service")

    # 3) Map property_id -> one Workiz UUID (most recent SO by date_order)
    property_to_uuid = {}
    for p in properties:
        pid = p["id"]
        orders = odoo_search_read(
            "sale.order",
            [["partner_shipping_id", "=", pid]],
            ["x_studio_x_studio_workiz_uuid", "date_order"],
            limit=1,
            order="date_order desc",
        )
        if orders and orders[0].get("x_studio_x_studio_workiz_uuid"):
            property_to_uuid[pid] = orders[0]["x_studio_x_studio_workiz_uuid"].strip()

    with_uuid = len(property_to_uuid)
    print(f"[*] Of those, {with_uuid} have at least one SO with a Workiz UUID")

    # 4) Build listing and decide updates from Holy Grail (and optionally API)
    listing_path = os.path.join(os.path.dirname(__file__), "backfill_freq_type_listing.csv")
    rows = []
    to_update = []  # (property_id, name, street, frequency, type_of_service, source)

    for p in properties:
        pid = p["id"]
        name = p.get("name") or ""
        street = p.get("street") or ""
        uuid_val = property_to_uuid.get(pid)
        in_holy = uuid_val and uuid_val in holy
        freq, tos = "", ""
        source = ""
        if uuid_val and uuid_val in holy:
            job = holy[uuid_val]
            freq = job.get("frequency") or ""
            tos = job.get("type_of_service") or ""
            if freq or tos:
                source = "holy_grail"
                to_update.append((pid, name, street, freq, tos, source))
        elif args.api_fallback and uuid_val:
            source = "api"  # will fetch in step 5
        rows.append({
            "property_id": pid,
            "name": name,
            "street": street,
            "workiz_uuid": uuid_val or "",
            "in_holy_grail": "yes" if in_holy else "no",
            "frequency": freq,
            "type_of_service": tos,
            "source": source,
        })

    # Write listing CSV
    with open(listing_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["property_id", "name", "street", "workiz_uuid", "in_holy_grail", "frequency", "type_of_service", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] Listing written: {listing_path}")

    # 5) API fallback: for UUIDs not in Holy Grail, fetch from Workiz and add to to_update
    if args.api_fallback:
        from functions.workiz.get_job_details import get_job_details
        api_candidates = [p for p in properties if p["id"] in property_to_uuid and property_to_uuid[p["id"]] not in holy]
        for p in api_candidates:
            pid = p["id"]
            uuid_val = property_to_uuid[pid]
            time.sleep(args.delay)
            job = get_job_details(uuid_val)
            if job:
                freq = (job.get("frequency") or "").strip()
                tos = (job.get("type_of_service") or "").strip()
                if freq or tos:
                    to_update.append((pid, p.get("name") or "", p.get("street") or "", freq, tos, "api"))

    from_holy = [t for t in to_update if t[5] == "holy_grail"]
    from_api = [t for t in to_update if t[5] == "api"]

    print(f"\n[*] Properties to update from Holy Grail (have freq or type): {len(from_holy)}")
    if args.api_fallback:
        print(f"[*] Properties to update from API (had UUID not in Holy Grail): {len(from_api)}")

    if args.dry_run:
        print("\n[DRY RUN] No Odoo writes. Sample of would-update (first 10):")
        for t in (from_holy + from_api)[:10]:
            print(f"  Property ID {t[0]}  {t[1]}  freq={t[3]!r}  type={t[4]!r}  source={t[5]}")
        print("=" * 70)
        return

    updated = 0
    failed = 0
    for t in from_holy + from_api:
        pid, _name, _street, freq, tos, _src = t
        res = odoo_write_property_frequency_type(pid, frequency=freq or None, type_of_service=tos or None)
        if res.get("success"):
            updated += 1
        else:
            failed += 1
            print(f"[!] Failed to update property {pid}: {res.get('message', 'unknown')}")

    print(f"\n[OK] Updated {updated} properties in Odoo. Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    main()
