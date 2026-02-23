"""
1) With --skip-property: copy property -> SO for every SO (use when property is source of truth for all).
2) Without --skip-property: backfill ~492 properties from Workiz, and write that job's freq/type to the
   ONE SO we used (same UUID) so that SO is a true mirror of that Workiz job. Part 2 is NOT run after
   backfill, so we never overwrite other SOs with a different job's data (one address can have multiple jobs).

Prerequisite: In Odoo, create on sale.order (Selection type, Workiz options):
  - x_studio_x_studio_frequency_so       -> 3 Months, 4 Months, 6 Months, 12 Months, Unknown
  - x_studio_x_studio_type_of_service_so -> Maintenance, On Request, Unknown

USAGE (these are command-line flags; add them when you run the script):

  Full run (backfill properties from Workiz, then copy to all SOs):
    python sync_frequency_type_to_all_sales_orders.py

  SO sync only (no Workiz API; only copy property -> SO for every Sales Order):
    python sync_frequency_type_to_all_sales_orders.py --skip-property

  Test without writing:
    python sync_frequency_type_to_all_sales_orders.py --skip-property --dry-run --limit 50

  Flags:  --skip-property  = skip Workiz; only copy property data to SOs
          --dry-run       = do not write to Odoo
          --limit N       = process only N SOs (for testing)
          --delay 2.5     = seconds between Workiz calls (when not using --skip-property); use higher if you see 429s
"""
import sys
import os
import argparse
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

CATEGORY_FIELD = "x_studio_x_studio_record_category"
PROP_FREQ = "x_studio_x_frequency"
PROP_TOS = "x_studio_x_type_of_service"
SO_FREQ = "x_studio_x_studio_frequency_so"
SO_TOS = "x_studio_x_studio_type_of_service_so"


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
    r = requests.post(ODOO_URL, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        msg = data["error"].get("data", {}).get("message", str(data["error"]))
        raise RuntimeError(msg)
    return data.get("result", [])


def odoo_write(model, id_or_ids, vals):
    ids = [id_or_ids] if isinstance(id_or_ids, int) else id_or_ids
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "write", [ids, vals]],
        },
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        msg = data["error"].get("data", {}).get("message", str(data["error"]))
        raise RuntimeError(msg)
    return data.get("result")


def main():
    ap = argparse.ArgumentParser(description="Backfill properties from Workiz (optional), then sync freq/type to all SOs from property")
    ap.add_argument("--skip-property", action="store_true", help="Skip Workiz property backfill; only sync property -> SO")
    ap.add_argument("--dry-run", action="store_true", help="No Odoo or Workiz writes")
    ap.add_argument("--limit", type=int, default=None, help="Max SOs to sync (for testing)")
    ap.add_argument("--delay", type=float, default=2.5, help="Seconds between Workiz API calls (increase if you see 429 rate limits)")
    args = ap.parse_args()

    print("=" * 70)
    print("Sync Frequency & Type of Service: Property -> All Sales Orders")
    print("=" * 70)

    # --- Part 1: Optional backfill of properties missing freq/type from Workiz ---
    # When we backfill, we also write that job's freq/tos to the ONE SO we used (same UUID) so that
    # SO stays a true mirror of that Workiz job. We do NOT then copy property -> all SOs (Part 2),
    # so we don't overwrite other SOs with a different job's data.
    if not args.skip_property and not args.dry_run:
        try:
            from functions.odoo.get_selection_values import get_selection_values
            allowed_freq = get_selection_values("sale.order", SO_FREQ)
            allowed_tos = get_selection_values("sale.order", SO_TOS)
        except Exception:
            allowed_freq = allowed_tos = []
        domain_missing = [
            [CATEGORY_FIELD, "=", "Property"],
            "|",
            [PROP_FREQ, "in", [False, ""]],
            [PROP_TOS, "in", [False, ""]],
        ]
        properties = odoo_search_read("res.partner", domain_missing, ["id", "name", "street"], limit=0)
        from functions.workiz.get_job_details import get_job_details
        from functions.odoo.update_property_fields import update_property_fields
        updated_props = 0
        updated_sos = 0
        for i, p in enumerate(properties):
            orders = odoo_search_read(
                "sale.order",
                [["partner_shipping_id", "=", p["id"]]],
                ["id", "x_studio_x_studio_workiz_uuid"],
                limit=1,
                order="date_order desc",
            )
            if not orders or not orders[0].get("x_studio_x_studio_workiz_uuid"):
                continue
            so_id = orders[0]["id"]
            uuid_val = orders[0]["x_studio_x_studio_workiz_uuid"].strip()
            time.sleep(args.delay)
            job = get_job_details(uuid_val)
            if not job:
                continue
            freq = (job.get("frequency") or "").strip()
            tos = (job.get("type_of_service") or "").strip()
            if not freq and not tos:
                continue
            res = update_property_fields(p["id"], frequency=freq or None, type_of_service=tos or None)
            if res.get("success"):
                updated_props += 1
            # Mirror that job's data onto the SO we used (same UUID) so SO = that job
            if allowed_freq and freq and freq not in allowed_freq:
                freq = ""
            if allowed_tos and tos and tos not in allowed_tos:
                tos = ""
            try:
                odoo_write("sale.order", so_id, {SO_FREQ: freq, SO_TOS: tos})
                updated_sos += 1
            except Exception:
                pass
        print(f"[OK] Property backfill from Workiz: {updated_props} properties updated")
        print(f"[OK] Mirrored that job's freq/type onto {updated_sos} SOs (one SO per property, same UUID)")
        print("[*] Skipping Part 2 (copy property -> all SOs) so other SOs are not overwritten.")
        return
    elif not args.skip_property and args.dry_run:
        domain_missing = [
            [CATEGORY_FIELD, "=", "Property"],
            "|",
            [PROP_FREQ, "in", [False, ""]],
            [PROP_TOS, "in", [False, ""]],
        ]
        n = len(odoo_search_read("res.partner", domain_missing, ["id"], limit=0))
        print(f"[DRY RUN] Would try to backfill {n} properties from Workiz (skipped)")

    # --- Part 2: Copy property freq/tos to every SO ---
    print("\n[*] Loading all Sales Orders (id, partner_shipping_id)...")
    so_list = odoo_search_read(
        "sale.order",
        [],
        ["id", "name", "partner_shipping_id"],
        limit=args.limit,
    )
    print(f"[*] Found {len(so_list)} Sales Orders")
    if not so_list:
        print("Nothing to do.")
        return

    # Unique property IDs (partner_shipping_id can be [id, name] or id)
    property_ids = set()
    for so in so_list:
        pid = so.get("partner_shipping_id")
        if pid is None:
            continue
        if isinstance(pid, (list, tuple)):
            pid = pid[0] if pid else None
        if pid:
            property_ids.add(pid)

    # If SO fields are Selection, only write values that are in the allowed list
    try:
        from functions.odoo.get_selection_values import get_selection_values
        allowed_freq = get_selection_values("sale.order", SO_FREQ)
        allowed_tos = get_selection_values("sale.order", SO_TOS)
    except Exception:
        allowed_freq = allowed_tos = []

    print(f"[*] Loading {len(property_ids)} properties (frequency, type_of_service)...")
    prop_data = {}
    if property_ids:
        # search_read in batches (Odoo limit 1000 or so)
        batch = 500
        ids_list = list(property_ids)
        for i in range(0, len(ids_list), batch):
            chunk = ids_list[i : i + batch]
            recs = odoo_search_read(
                "res.partner",
                [["id", "in", chunk]],
                ["id", PROP_FREQ, PROP_TOS],
                limit=0,
            )
            for r in recs:
                prop_data[r["id"]] = (
                    (r.get(PROP_FREQ) or ""),
                    (r.get(PROP_TOS) or ""),
                )

    written = 0
    skipped = 0
    errors = 0
    for so in so_list:
        so_id = so["id"]
        pid = so.get("partner_shipping_id")
        if pid is None:
            skipped += 1
            continue
        if isinstance(pid, (list, tuple)):
            pid = pid[0] if pid else None
        if not pid:
            skipped += 1
            continue
        freq, tos = prop_data.get(pid, ("", ""))
        freq = (freq or "").strip()
        tos = (tos or "").strip()
        # If SO fields are Selection, only include values that are allowed
        if allowed_freq and freq and freq not in allowed_freq:
            freq = ""
        if allowed_tos and tos and tos not in allowed_tos:
            tos = ""
        if args.dry_run:
            if written < 5:
                print(f"  Would set SO {so_id} ({so.get('name')}) <- freq={freq!r} tos={tos!r} (property {pid})")
            written += 1
            continue
        try:
            vals = {SO_FREQ: freq, SO_TOS: tos}
            odoo_write("sale.order", so_id, vals)
            written += 1
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"[!] SO {so_id}: {e}")

    if args.dry_run:
        print(f"[DRY RUN] Would write freq/tos to {written} SOs (skipped {skipped})")
    else:
        print(f"[OK] Wrote freq/type to {written} Sales Orders. Skipped (no property): {skipped}. Errors: {errors}")
    print("=" * 70)


if __name__ == "__main__":
    main()
