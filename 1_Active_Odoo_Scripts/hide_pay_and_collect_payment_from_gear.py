"""
Hide Pay and Collect Payment from the invoice gear menu only
============================================================
Unbinds server actions 350 (Pay) and 674 (Collect Payment) by clearing
binding_model_id so they no longer appear in the gear dropdown on invoices.

Does NOT touch:
- The top "Pay" button on the invoice (that is a view button, not these actions).
- Any other part of Odoo.

Reversible: set binding_model_id back to account.move to show in gear again.

Run once: python 1_Active_Odoo_Scripts/hide_pay_and_collect_payment_from_gear.py
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"


def jsonrpc(model, method, args, kwargs=None):
    import requests
    params_args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params_args.append(kwargs)
    payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params_args}}
    r = requests.post(ODOO_URL, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def main():
    print("=" * 60)
    print("Hide Pay (350) and Collect Payment (674) from invoice gear only")
    print("=" * 60)
    jsonrpc("ir.actions.server", "write", [[350, 674], {"binding_model_id": False}])
    print("[OK] Both options removed from the gear menu on invoices.")
    print("     Top 'Pay' button is unchanged and still works.")
    print("=" * 60)


if __name__ == "__main__":
    main()
