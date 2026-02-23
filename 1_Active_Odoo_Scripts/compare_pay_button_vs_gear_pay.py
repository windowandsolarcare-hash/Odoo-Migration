"""
Compare: Top "Pay" button vs Gear menu "Pay" (Server Action)
============================================================
Lists both so we can see why the button works and the gear Pay asks for
different fields and gives "missing field required".

Run: python 1_Active_Odoo_Scripts/compare_pay_button_vs_gear_pay.py
"""

import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "Phase 6 Handoff", "backups")


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


def get_imd(model, res_id):
    imd = jsonrpc("ir.model.data", "search_read", [[["model", "=", model], ["res_id", "=", res_id]]], {"fields": ["module", "name"], "limit": 1})
    if imd:
        return imd[0].get("module", ""), imd[0].get("name", "")
    return "", ""


def main():
    print("=" * 70)
    print("Compare: Pay BUTTON (top bar) vs Pay in GEAR (Server Action)")
    print("=" * 70)

    models = jsonrpc("ir.model", "search_read", [[["model", "=", "account.move"]]], {"fields": ["id"], "limit": 1})
    if not models:
        print("[!] account.move not found")
        return
    model_id = models[0]["id"]
    os.makedirs(os.path.abspath(BACKUP_DIR), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # ---- 1) SERVER ACTIONS bound to account.move (these show in the GEAR menu) ----
    print("\n--- 1) GEAR MENU: Server Actions on Invoices (account.move) ---\n")
    servers = jsonrpc(
        "ir.actions.server",
        "search_read",
        [[["binding_model_id", "=", model_id]]],
        {"fields": ["id", "name", "state", "code", "binding_view_types"]},
    )
    for a in servers:
        mod, name = get_imd("ir.actions.server", a["id"])
        ext_id = f"{mod}.{name}" if mod and name else "(none)"
        print(f"  ID {a['id']}: {a.get('name')}")
        print(f"      Module: {mod or '(custom)'}  External ID: {ext_id}")
        print(f"      State: {a.get('state')}  Binding: {a.get('binding_view_types')}")
        code = (a.get("code") or "")[:500]
        print(f"      Code preview: {code}...")
        print()
        # Save full to backup
        fname = os.path.join(BACKUP_DIR, f"gear_pay_server_{a['id']}_{ts}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump({"type": "ir.actions.server", "id": a["id"], "name": a.get("name"), "module": mod, "external_id": ext_id, "state": a.get("state"), "code": a.get("code"), "binding_view_types": a.get("binding_view_types")}, f, indent=2)
        print(f"      Saved: {fname}\n")

    # ---- 2) WINDOW ACTIONS that open payment register wizard (likely the BUTTON) ----
    print("\n--- 2) LIKELY THE TOP BUTTON: Window Actions (payment register wizard) ---\n")
    windows = jsonrpc(
        "ir.actions.act_window",
        "search_read",
        [[["res_model", "=", "account.payment.register"]]],
        {"fields": ["id", "name", "res_model", "target", "context", "binding_model_id", "binding_view_types"]},
    )
    for a in windows:
        mod, name = get_imd("ir.actions.act_window", a["id"])
        ext_id = f"{mod}.{name}" if mod and name else "(none)"
        binding = a.get("binding_model_id")
        bid = binding[0] if isinstance(binding, (list, tuple)) else binding
        bound_to_invoice = "yes" if bid == model_id else "no"
        print(f"  ID {a['id']}: {a.get('name')}")
        print(f"      res_model: {a.get('res_model')}  (this is the PAY WIZARD)")
        print(f"      Module: {mod or '(custom)'}  External ID: {ext_id}")
        print(f"      Bound to Invoices: {bound_to_invoice}  Binding: {a.get('binding_view_types')}")
        print(f"      target: {a.get('target')}  context: {a.get('context')}")
        print()
        fname = os.path.join(BACKUP_DIR, f"button_pay_window_{a['id']}_{ts}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump({"type": "ir.actions.act_window", "id": a["id"], "name": a.get("name"), "res_model": a.get("res_model"), "module": mod, "external_id": ext_id, "target": a.get("target"), "context": a.get("context"), "binding_model_id": a.get("binding_model_id"), "binding_view_types": a.get("binding_view_types")}, f, indent=2)
        print(f"      Saved: {fname}\n")

    # ---- 3) Any other Window actions named Pay / Register bound to account.move ----
    print("\n--- 3) Other Window Actions (name Pay/Register) for account.move ---\n")
    try:
        others = jsonrpc(
            "ir.actions.act_window",
            "search_read",
            [[["name", "ilike", "Pay"]]],
            {"fields": ["id", "name", "res_model", "binding_model_id"]},
        )
    except Exception:
        others = []
    for a in others:
        binding = a.get("binding_model_id")
        bid = binding[0] if isinstance(binding, (list, tuple)) else binding
        if bid != model_id:
            continue
        print(f"  ID {a['id']}: {a.get('name')}  res_model: {a.get('res_model')}")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
- The TOP BAR 'Pay' button almost certainly opens the WIZARD: account.payment.register
  (Journal, Method, Amount, Date, Memo → Submit → Paid). That's in section 2.

- The GEAR menu 'Pay' is a SERVER ACTION (section 1). If it runs Python code that
  opens a different form (e.g. account.payment) or misses required fields, you get
  'missing field required'. Fix: either remove the gear Pay and use only the button,
  or change the Server Action to open the SAME wizard (account.payment.register)
  with the same context so it behaves like the button.
""")


if __name__ == "__main__":
    main()
