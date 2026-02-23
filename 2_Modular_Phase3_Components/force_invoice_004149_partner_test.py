"""
Force the invoice for SO 004149 to use the same partner_id (Property) as the SO.
Use when the migration script ran but the invoice still shows the wrong address,
or when the UI won't let you change it (Posted invoices lock the Customer field).

Uses TEST config only. Run: python force_invoice_004149_partner_test.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import requests
from config_test import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


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
    # 1) Get SO 004149's partner_id (the Property with correct address)
    sos = odoo_rpc("sale.order", "search_read", [[["name", "ilike", "004149"]]], {
        "fields": ["id", "name", "partner_id"],
        "limit": 5,
    })
    so = None
    for s in sos:
        if "004149" in (s.get("name") or ""):
            so = s
            break
    if not so:
        print("SO 004149 not found.")
        return
    so_partner = so.get("partner_id")
    so_partner_id = so_partner[0] if isinstance(so_partner, (list, tuple)) else so_partner
    print(f"SO {so.get('name')} partner_id (Property) = {so_partner_id}")

    # 2) Find invoice(s) with origin 004149
    invoices = odoo_rpc("account.move", "search_read", [
        [["move_type", "=", "out_invoice"], ["invoice_origin", "ilike", "004149"]]
    ], {"fields": ["id", "name", "invoice_origin", "partner_id", "state"], "limit": 20})
    if not invoices:
        # try by name
        invoices = odoo_rpc("account.move", "search_read", [
            [["move_type", "=", "out_invoice"], ["name", "ilike", "00011"]]
        ], {"fields": ["id", "name", "invoice_origin", "partner_id", "state"], "limit": 20})

    if not invoices:
        print("No invoice found for order 004149.")
        return

    for inv in invoices:
        inv_pid = inv.get("partner_id")
        inv_pid = inv_pid[0] if isinstance(inv_pid, (list, tuple)) else inv_pid
        print(f"\nInvoice {inv.get('name')} (id={inv['id']}) state={inv.get('state')} current partner_id={inv_pid}")
        if inv_pid == so_partner_id:
            print("  -> Already correct. No change.")
            continue
        try:
            odoo_rpc("account.move", "write", [[inv["id"]], {"partner_id": so_partner_id}])
            print(f"  -> Updated partner_id to {so_partner_id}. Refresh the invoice in the browser.")
        except Exception as e:
            print(f"  -> ERROR: {e}")
            if "posted" in str(e).lower() or "lock" in str(e).lower():
                print("     (Odoo may block changing partner on a Posted invoice. You may need a developer module to allow it.)")


if __name__ == "__main__":
    main()
