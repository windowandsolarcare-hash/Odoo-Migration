"""
List Invoice-Related Server Actions: Custom vs Standard
========================================================
Shows which actions on Invoices (account.move) are from Odoo (have a module
External ID) vs created by us / custom (no module or __export__).
Run from repo root: python 1_Active_Odoo_Scripts/list_invoice_actions_custom_vs_standard.py

See: Phase 6 Handoff/Odoo_Custom_vs_Standard_Actions.md
"""

import requests
import sys

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"


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


def main():
    print("=" * 70)
    print("Invoice-related Server Actions: Custom vs Standard")
    print("=" * 70)

    # Get account.move model id
    models = jsonrpc("ir.model", "search_read", [[["model", "=", "account.move"]]], {"fields": ["id"], "limit": 1})
    if not models:
        print("[!] account.move model not found")
        return
    model_id = models[0]["id"]

    # All server actions bound to account.move (form or list)
    actions = jsonrpc(
        "ir.actions.server",
        "search_read",
        [[["binding_model_id", "=", model_id]]],
        {"fields": ["id", "name", "state", "code", "active", "binding_view_types"], "order": "id"},
    )

    if not actions:
        print("\nNo Server Actions bound to Invoices (account.move).")
        print("Standard 'Register Payment' may be a Window Action, not a Server Action.")
        # Try to list window actions on account.move too
        wactions = jsonrpc(
            "ir.actions.act_window",
            "search_read",
            [[["res_model", "=", "account.move"]]],
            {"fields": ["id", "name", "res_model"], "limit": 20},
        )
        if wactions:
            print("\nWindow actions for account.move (may include standard Pay/Register):")
            for a in wactions:
                print(f"  ID {a['id']}: {a.get('name', '')}")
        print("=" * 70)
        return

    # Get External IDs (ir.model.data) for these action IDs
    action_ids = [a["id"] for a in actions]
    imd = jsonrpc(
        "ir.model.data",
        "search_read",
        [[["model", "=", "ir.actions.server"], ["res_id", "in", action_ids]]],
        {"fields": ["module", "name", "res_id"]},
    )
    # map res_id -> (module, full external_id)
    by_res_id = {}
    for row in imd:
        res_id = row["res_id"]
        mod = row.get("module", "")
        name = row.get("name", "")
        ext_id = f"{mod}.{name}" if mod and name else ""
        # Prefer non-export module if multiple
        if res_id not in by_res_id or (by_res_id[res_id][0] == "__export__" and mod != "__export__"):
            by_res_id[res_id] = (mod, ext_id)

    print(f"\nFound {len(actions)} Server Action(s) bound to Invoices:\n")
    print(f"{'ID':<6} {'Name':<35} {'Module':<12} {'Custom?':<8} Code preview")
    print("-" * 70)

    for a in actions:
        aid = a["id"]
        name = (a.get("name") or "")[:34]
        mod, ext_id = by_res_id.get(aid, ("", ""))
        is_custom = "Yes" if (not mod or mod == "__export__") else "No"
        code = (a.get("code") or "")[:80].replace("\n", " ")
        print(f"{aid:<6} {name:<35} {(mod or '—'):<12} {is_custom:<8} {code}...")

    print("-" * 70)
    print("\nCustom = created by us or in UI (no standard module / __export__).")
    print("Standard = has module like 'account' or 'sale' (Odoo built-in).")
    print("=" * 70)


if __name__ == "__main__":
    main()
