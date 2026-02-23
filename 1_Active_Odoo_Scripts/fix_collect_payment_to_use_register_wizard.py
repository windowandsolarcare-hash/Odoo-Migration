"""
Fix "Collect Payment" (ID 674) to use same workflow as top Pay button
=====================================================================
Replaces the code that opens account.payment form (which caused "missing
field required") with the standard Pay logic: open the payment register
wizard (account.payment.register). Same workflow as the top Pay button.

1. Backs up current 674 code to Phase 6 Handoff/backups/
2. Updates 674 to call action_force_register_payment() like Pay (350)

Run: python 1_Active_Odoo_Scripts/fix_collect_payment_to_use_register_wizard.py
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

# Standard Pay (350) code - opens payment register wizard, same as top button
CODE_SAME_AS_PAY_BUTTON = """
if records:
    action = records.action_force_register_payment()
"""


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
    print("Fix Collect Payment (674) = same workflow as top Pay button")
    print("=" * 60)

    action_id = 674
    os.makedirs(os.path.abspath(BACKUP_DIR), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # 1) Read current code
    current = jsonrpc("ir.actions.server", "read", [[action_id]], {"fields": ["id", "name", "code"]})
    if not current:
        print(f"[!] Server Action {action_id} not found")
        return
    current = current[0]
    old_code = current.get("code", "")

    # 2) Back up to file
    backup_path = os.path.join(BACKUP_DIR, f"collect_payment_674_before_wizard_fix_{ts}.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump({"id": action_id, "name": current.get("name"), "code_before": old_code, "fixed_at": ts}, f, indent=2)
    print(f"\n[1] Backed up current code to: {backup_path}")

    # 3) Update to same logic as Pay (350) - opens payment register wizard
    jsonrpc("ir.actions.server", "write", [[action_id], {"code": CODE_SAME_AS_PAY_BUTTON}])
    print(f"[2] Updated Server Action '{current.get('name')}' (ID {action_id}) to use payment register wizard (same as top Pay button).")

    # 4) Verify
    updated = jsonrpc("ir.actions.server", "read", [[action_id]], {"fields": ["name", "code"]})[0]
    print(f"\n[3] New code:\n{updated.get('code')}")
    print("=" * 60)
    print("\nDone. From the gear, 'Collect Payment' will now open the same payment")
    print("register wizard as the top Pay button (Journal, Method, Amount, Date, Memo).")
    print("=" * 60)


if __name__ == "__main__":
    main()
