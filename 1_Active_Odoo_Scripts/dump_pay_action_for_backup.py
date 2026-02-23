"""
Dump current "Pay" action for backup / comparison
=================================================
Finds the "Pay" (or "Register Payment") action on Invoices (account.move)
and writes its full definition to Phase 6 Handoff/backups/ so you can see
what it looks like now vs standard Odoo. Run whenever you want a snapshot.

Usage: python 1_Active_Odoo_Scripts/dump_pay_action_for_backup.py

See: Phase 6 Handoff/Odoo_Custom_vs_Standard_Actions.md
"""

import json
import os
import requests
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Backup dir relative to repo root (script may be run from repo root or from 1_Active_Odoo_Scripts)
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "Phase 6 Handoff", "backups")


def jsonrpc(model, method, args, kwargs=None):
    params_args = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params_args.append(kwargs)
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params_args},
    }
    r = requests.post(ODOO_URL, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def get_imd(model, res_id):
    """Get ir.model.data for a record (module, name = external id)."""
    imd = jsonrpc(
        "ir.model.data",
        "search_read",
        [[["model", "=", model], ["res_id", "=", res_id]]],
        {"fields": ["module", "name"], "limit": 1},
    )
    if imd:
        return imd[0].get("module", ""), imd[0].get("name", "")
    return "", ""


def main():
    print("=" * 60)
    print("Dump 'Pay' action for backup")
    print("=" * 60)

    # Resolve backup dir (absolute)
    backup_dir = os.path.abspath(BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # account.move model id
    models = jsonrpc("ir.model", "search_read", [[["model", "=", "account.move"]]], {"fields": ["id"], "limit": 1})
    if not models:
        print("[!] account.move model not found")
        return
    model_id = models[0]["id"]

    dumped = []

    # 1) Server actions named "Pay" bound to account.move
    servers = jsonrpc(
        "ir.actions.server",
        "search_read",
        [[["name", "=", "Pay"], ["binding_model_id", "=", model_id]]],
        {"fields": ["id", "name", "model_id", "state", "code", "binding_view_types", "active"]},
    )
    for a in servers:
        mod, name = get_imd("ir.actions.server", a["id"])
        ext_id = f"{mod}.{name}" if mod and name else "(none)"
        out = {
            "type": "ir.actions.server",
            "id": a["id"],
            "name": a.get("name"),
            "external_id": ext_id,
            "module": mod,
            "state": a.get("state"),
            "binding_view_types": a.get("binding_view_types"),
            "active": a.get("active"),
            "code": a.get("code"),
        }
        fname = os.path.join(backup_dir, f"pay_action_server_{a['id']}_{ts}.txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write("# Pay action (Server Action) - backup\n")
            f.write(f"# ID: {a['id']}  External ID: {ext_id}  Module: {mod}\n")
            f.write(f"# Dumped: {ts}\n\n")
            f.write(json.dumps(out, indent=2))
        print(f"[OK] Wrote server action Pay (ID {a['id']}) -> {fname}")
        dumped.append(fname)

    # 2) Window actions that might be "Pay" / "Register Payment" for invoices
    # (standard Pay is often act_window opening account.payment.register)
    for name_filter in ["Pay", "Register Payment", "Register payment"]:
        windows = jsonrpc(
            "ir.actions.act_window",
            "search_read",
            [[["name", "ilike", name_filter]]],
            {"fields": ["id", "name", "res_model", "target", "context", "binding_model_id", "binding_view_types"]},
        )
        for a in windows:
            # Only care if bound to account.move or opens payment register
            binding = a.get("binding_model_id")
            bid = binding[0] if isinstance(binding, (list, tuple)) else binding
            if bid != model_id and a.get("res_model") != "account.payment.register":
                continue
            mod, name = get_imd("ir.actions.act_window", a["id"])
            ext_id = f"{mod}.{name}" if mod and name else "(none)"
            out = {
                "type": "ir.actions.act_window",
                "id": a["id"],
                "name": a.get("name"),
                "external_id": ext_id,
                "module": mod,
                "res_model": a.get("res_model"),
                "target": a.get("target"),
                "context": a.get("context"),
                "binding_model_id": a.get("binding_model_id"),
                "binding_view_types": a.get("binding_view_types"),
            }
            safe_name = (a.get("name") or "unnamed").replace(" ", "_")[:30]
            fname = os.path.join(backup_dir, f"pay_action_window_{a['id']}_{safe_name}_{ts}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write("# Pay/Register Payment action (Window Action) - backup\n")
                f.write(f"# ID: {a['id']}  External ID: {ext_id}  Module: {mod}\n")
                f.write(f"# Dumped: {ts}\n\n")
                f.write(json.dumps(out, indent=2))
            print(f"[OK] Wrote window action (ID {a['id']}) -> {fname}")
            dumped.append(fname)

    if not dumped:
        print("\n[INFO] No 'Pay' or 'Register Payment' action found bound to Invoices.")
        print("       Standard Pay may be defined elsewhere (e.g. button action on form).")
    else:
        print(f"\n[OK] Backed up {len(dumped)} action(s) to {backup_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
