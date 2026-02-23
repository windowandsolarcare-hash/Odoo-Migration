"""
Apply minimal "Collect Payment" Server Action (Phase 6)
======================================================
Creates or updates the Collect Payment action on Invoices (account.move) with
the minimal code that opens the payment form only. Safe to run multiple times.

Usage: python apply_collect_payment_action_minimal.py

See: Phase 6 Handoff/Collect_Payment_Action_Minimal.md
     Phase 6 Handoff/Payment_Entry_What_to_Revert_and_Use.md
"""

import requests
import sys

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Minimal code: opens account.payment form with context. No import, no creating payment in code.
COLLECT_PAYMENT_CODE = """action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'default_payment_type': 'inbound',
        'default_partner_type': 'customer',
        'default_partner_id': record.partner_id.id,
        'default_amount': record.amount_residual,
        'default_currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
        'default_journal_id': env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
        'default_invoice_ids': [(6, 0, [record.id])],
    }
}"""


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
    print("=" * 60)
    print("Apply minimal Collect Payment Server Action")
    print("=" * 60)

    # Get account.move model id
    models = jsonrpc("ir.model", "search_read", [[["model", "=", "account.move"]]], {"fields": ["id"], "limit": 1})
    if not models:
        print("[!] account.move model not found")
        return
    model_id = models[0]["id"]

    # Find existing "Collect Payment" action bound to account.move
    action_ids = jsonrpc(
        "ir.actions.server",
        "search",
        [[["name", "=", "Collect Payment"], ["model_id", "=", model_id]]],
    )

    if action_ids:
        action_id = action_ids[0]
        print(f"[*] Updating existing Collect Payment action (ID: {action_id})")
        jsonrpc("ir.actions.server", "write", [[action_id], {"code": COLLECT_PAYMENT_CODE, "active": True}])
        # Ensure it appears on form view
        jsonrpc("ir.actions.server", "write", [[action_id], {"binding_view_types": "form"}])
        print("[OK] Action updated with minimal code (form only, no payment creation in code).")
    else:
        print("[*] Creating new Collect Payment action")
        action_id = jsonrpc(
            "ir.actions.server",
            "create",
            [
                {
                    "name": "Collect Payment",
                    "model_id": model_id,
                    "binding_model_id": model_id,
                    "binding_view_types": "form",
                    "state": "code",
                    "code": COLLECT_PAYMENT_CODE,
                }
            ],
        )
        print(f"[OK] Action created (ID: {action_id}).")

    print()
    print("Next: Open an invoice in Odoo → Action → Collect Payment.")
    print("Form will open with journal/amount pre-filled; enter method, date, ref (check #).")
    print("=" * 60)


if __name__ == "__main__":
    main()
