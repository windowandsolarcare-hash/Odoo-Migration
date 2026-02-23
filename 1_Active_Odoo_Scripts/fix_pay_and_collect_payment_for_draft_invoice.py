"""
Fix Pay (350) and Collect Payment (674) for unconfirmed (draft) invoices
========================================================================
When the invoice is draft, the payment register wizard can open without
default_currency_id in context, causing "missing required field" (often
currency). This script updates BOTH server actions to pass default_currency_id
(and company fallback) so the wizard works from the gear even on unconfirmed
invoices.

1. Backs up current code for 350 and 674 to Phase 6 Handoff/backups/
2. Updates both actions to inject default_currency_id before calling
   action_force_register_payment()

Run: python 1_Active_Odoo_Scripts/fix_pay_and_collect_payment_for_draft_invoice.py
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

# Same as standard Pay but ensures wizard gets currency when invoice is draft
CODE_WITH_CURRENCY_CONTEXT = """
if records:
    rec = records[0]
    ctx = dict(env.context)
    ctx['default_currency_id'] = rec.currency_id.id if rec.currency_id else rec.company_id.currency_id.id
    action = records.with_context(ctx).action_force_register_payment()
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
    print("Fix Pay (350) and Collect Payment (674) for draft invoices")
    print("=" * 60)

    action_ids = [350, 674]
    os.makedirs(os.path.abspath(BACKUP_DIR), exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"pay_350_collect_674_before_draft_fix_{ts}.json")
    backups = []

    for action_id in action_ids:
        current = jsonrpc("ir.actions.server", "read", [[action_id]], {"fields": ["id", "name", "code"]})
        if not current:
            print(f"[!] Server Action {action_id} not found, skip")
            continue
        current = current[0]
        backups.append({"id": action_id, "name": current.get("name"), "code_before": current.get("code", "")})
        jsonrpc("ir.actions.server", "write", [[action_id], {"code": CODE_WITH_CURRENCY_CONTEXT}])
        print(f"[OK] Updated '{current.get('name')}' (ID {action_id})")

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump({"fixed_at": ts, "actions": backups}, f, indent=2)
    print(f"\n[1] Backed up previous code to: {backup_path}")
    print("\n[2] Both Pay (350) and Collect Payment (674) now pass default_currency_id")
    print("    so the payment register wizard works from the gear even when the")
    print("    invoice is unconfirmed (draft).")
    print("=" * 60)


if __name__ == "__main__":
    main()
