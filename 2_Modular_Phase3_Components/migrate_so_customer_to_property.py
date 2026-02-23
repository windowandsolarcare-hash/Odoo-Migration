"""
Property-as-brain migration:
  1) Set SO partner_id AND partner_invoice_id = Property (from partner_shipping_id).
     (Odoo uses partner_invoice_id when creating a new invoice from the SO — so both must be Property.)
  2) Set existing Invoice partner_id = SO's partner_id (so invoices show Property too; phone stays on Contact).

Does NOT touch Contact or Property records. Property.parent_id = Contact is preserved.
DEFAULT = TEST database. LIVE = only when you pass --production on the command line.
  In main() (lines ~80-86): if use_production then ODOO_* = PROD_* (live), else ODOO_* = TEST_* (test).

Usage (run from folder 2_Modular_Phase3_Components, or use the path below):
  cd "2_Modular_Phase3_Components"
  python migrate_so_customer_to_property.py                  # apply on TEST
  python migrate_so_customer_to_property.py --production      # apply on LIVE

If you are in the project root (Migration to Odoo), run:
  python "2_Modular_Phase3_Components/migrate_so_customer_to_property.py" --production
"""
import sys
import os
import re
import argparse

sys.path.insert(0, os.path.dirname(__file__))

import requests
# Default: test. Override with --production for live.
from config_test import ODOO_URL as TEST_URL, ODOO_DB as TEST_DB, ODOO_USER_ID as TEST_UID, ODOO_API_KEY as TEST_KEY
from config import ODOO_URL as PROD_URL, ODOO_DB as PROD_DB, ODOO_USER_ID as PROD_UID, ODOO_API_KEY as PROD_KEY

# Default = TEST. Overwritten in main() to PROD_* when you pass --production (see main() lines ~80-86).
ODOO_URL = TEST_URL
ODOO_DB = TEST_DB
ODOO_USER_ID = TEST_UID
ODOO_API_KEY = TEST_KEY

CATEGORY_FIELD = "x_studio_x_studio_record_category"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "2_Migration_Archive")


def _write_log(log_lines):
    from datetime import datetime, timezone
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "migrate_property_brain_live.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    log_lines.append(f"(Log written to {path})")


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
    parser = argparse.ArgumentParser(description="Migrate SO customer from Contact to Property (partner_id = partner_shipping_id).")
    parser.add_argument("--dry-run", action="store_true", help="Only list SOs/invoices that would be updated; do not write.")
    parser.add_argument("--production", action="store_true", help="Run against LIVE Odoo (default: test).")
    args = parser.parse_args()
    dry_run = getattr(args, "dry_run", False)
    use_production = getattr(args, "production", False)
    log_lines = []
    def log(msg):
        log_lines.append(msg)
        print(msg, flush=True)
    # --- SWITCH TO LIVE ONLY WHEN --production IS PASSED ---
    if use_production:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = PROD_URL, PROD_DB, PROD_UID, PROD_KEY
        log("[LIVE] Using production Odoo: " + str(ODOO_DB))
        _write_log(log_lines)  # create log file early so we have it if script fails later
    else:
        ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY = TEST_URL, TEST_DB, TEST_UID, TEST_KEY
        log("[TEST] Using test Odoo: " + str(ODOO_DB))

    # All SOs that have partner_shipping_id (delivery address) set
    domain = [["partner_shipping_id", "!=", False]]
    fields = ["id", "name", "partner_id", "partner_shipping_id", "partner_invoice_id"]
    sos = odoo_rpc("sale.order", "search_read", [domain], {"fields": fields, "limit": 10000})
    # Update where customer or invoice address != delivery (Property)
    to_update = []
    for so in sos:
        pid = so.get("partner_id")
        sid = so.get("partner_shipping_id")
        inv_id = so.get("partner_invoice_id")
        pid = pid[0] if isinstance(pid, (list, tuple)) else pid
        sid = sid[0] if isinstance(sid, (list, tuple)) else sid
        inv_id = inv_id[0] if isinstance(inv_id, (list, tuple)) else inv_id
        if sid and (pid != sid or inv_id != sid):
            to_update.append({"id": so["id"], "name": so["name"], "current_partner_id": pid, "partner_shipping_id": sid})

    log(f"Odoo instance: {ODOO_URL} (DB: {ODOO_DB})")
    log(f"SOs with partner_shipping_id set: {len(sos)}")
    log(f"SOs where partner_id != partner_shipping_id (would set partner_id & partner_invoice_id = Property): {len(to_update)}")
    if dry_run:
        for so in to_update[:20]:
            log(f"  SO {so['name']} id={so['id']}  current partner_id={so['current_partner_id']}  -> partner_shipping_id={so['partner_shipping_id']}")
        if len(to_update) > 20:
            log(f"  ... and {len(to_update) - 20} more.")
        log("\n[DRY RUN] SO list above. Invoice list below (no writes yet).")
    else:
        updated = 0
        for so in to_update:
            try:
                # Both so new invoices from this SO use Property (Odoo uses partner_invoice_id when creating invoice)
                odoo_rpc("sale.order", "write", [[so["id"]], {
                    "partner_id": so["partner_shipping_id"],
                    "partner_invoice_id": so["partner_shipping_id"],
                }])
                updated += 1
                if updated <= 10 or updated % 500 == 0:
                    log(f"  Updated SO {so['name']} (id {so['id']}): partner_id = {so['partner_shipping_id']}")
            except Exception as e:
                log(f"  [ERROR] SO {so['name']} id={so['id']}: {e}")
        log(f"\n[OK] Updated {updated} sales orders. Customer (partner_id) and billing (partner_invoice_id) are now the Property.")

    # --- Step 2: Invoices — set partner_id = SO's partner_id (Property) so invoice matches SO ---
    # Build SO name -> partner_id from current state (all SOs, so already-migrated are correct)
    so_list = odoo_rpc("sale.order", "search_read", [[]], {"fields": ["name", "partner_id"], "limit": 50000})
    so_name_to_partner = {}
    for s in so_list:
        pid = s.get("partner_id")
        pid = pid[0] if isinstance(pid, (list, tuple)) else pid
        if s.get("name") and pid:
            so_name_to_partner[str(s["name"]).strip()] = pid
    # Invoices: move_type out_invoice, with invoice_origin = SO name
    # Include state: only draft invoices can have partner_id changed; posted moves are readonly.
    inv_domain = [["move_type", "=", "out_invoice"], ["invoice_origin", "!=", False]]
    invoices = odoo_rpc("account.move", "search_read", [inv_domain], {"fields": ["id", "name", "invoice_origin", "partner_id", "state"], "limit": 50000})
    to_inv_update = []
    skipped_posted = 0
    def _match_origin_to_so(origin_str):
        """Match invoice_origin to an SO name. Odoo can store '004149', 'S004149', 'SO 004149', or 'S004149, S004150'."""
        o = (origin_str or "").strip()
        if not o:
            return None
        if o in so_name_to_partner:
            return so_name_to_partner[o]
        # Substring: e.g. origin "004149" vs SO name "S004149"
        for key in so_name_to_partner:
            if o in key or key in o:
                return so_name_to_partner[key]
        # Normalize: take trailing digits (order number) and match SO name ending with them
        digits = re.sub(r"^.*?(\d+)$", r"\1", o)
        if digits:
            for key in so_name_to_partner:
                if key.rstrip().endswith(digits):
                    return so_name_to_partner[key]
        return None

    for inv in invoices:
        origin = (inv.get("invoice_origin") or "").strip()
        if not origin:
            continue
        so_partner_id = _match_origin_to_so(origin)
        if not so_partner_id:
            continue
        inv_pid = inv.get("partner_id")
        inv_pid = inv_pid[0] if isinstance(inv_pid, (list, tuple)) else inv_pid
        if inv_pid != so_partner_id:
            state = (inv.get("state") or "draft").strip().lower()
            if state != "draft":
                skipped_posted += 1
                continue  # Odoo: partner_id is readonly on posted/cancel moves
            to_inv_update.append({"id": inv["id"], "name": inv.get("name"), "origin": origin, "new_partner_id": so_partner_id})
    log(f"\nInvoices (out_invoice) with origin in SOs: {len(invoices)}; would set partner_id to SO's Property: {len(to_inv_update)} (skipped {skipped_posted} posted — partner_id is readonly once posted).")
    if dry_run:
        for inv in to_inv_update[:15]:
            log(f"  Invoice {inv['name']} origin={inv['origin']} -> partner_id={inv['new_partner_id']}")
        if len(to_inv_update) > 15:
            log(f"  ... and {len(to_inv_update) - 15} more.")
        log("\n[DRY RUN] No changes made. Run without --dry-run to apply.")
        if use_production:
            _write_log(log_lines)
        return
    inv_updated = 0
    for inv in to_inv_update:
        try:
            odoo_rpc("account.move", "write", [[inv["id"]], {"partner_id": inv["new_partner_id"]}])
            inv_updated += 1
            if inv_updated <= 10 or inv_updated % 500 == 0:
                log(f"  Updated invoice {inv['name']} (origin {inv['origin']}): partner_id = {inv['new_partner_id']}")
        except Exception as e:
            log(f"  [ERROR] Invoice {inv['name']} id={inv['id']}: {e}")
    log(f"\n[OK] Updated {inv_updated} invoices. Customer (partner_id) now matches SO (Property). Contact link preserved via Property.parent_id.")
    log("\nPhone on SO/Invoice and hiding 'United States' require Odoo form customization (Studio): add Contact phone from partner_id.parent_id, show as link.")
    if use_production:
        _write_log(log_lines)


if __name__ == "__main__":
    main()
