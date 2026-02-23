"""
Restore Collect Payment (674) to open account.payment form (pre-wizard version)
==============================================================================
Reverts 674 to the code that opens the payment form with context defaults,
so you can use Collect Payment from the gear again. Pay (350) is left as-is
(may still error on draft from gear - use top Pay on confirmed invoices).

Run once: python 1_Active_Odoo_Scripts/restore_collect_payment_674_to_form.py
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# Original Collect Payment: open account.payment form with defaults (from backup)
CODE_OPEN_PAYMENT_FORM = """
record = records[0]
action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'current',
    'context': {
        'default_payment_type': 'inbound',
        'default_partner_type': 'customer',
        'default_partner_id': record.partner_id.id,
        'default_amount': record.amount_residual,
        'default_currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
        'default_journal_id': env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
        'default_memo': record.name,
        'default_invoice_ids': [(6, 0, [record.id])],
    }
}
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
    print("Restore Collect Payment (674) to open payment form")
    print("=" * 60)
    jsonrpc("ir.actions.server", "write", [[674], {"code": CODE_OPEN_PAYMENT_FORM}])
    print("[OK] Collect Payment (674) restored to open account.payment form.")
    print("     Pay (350) unchanged; use top Pay on confirmed invoices if gear Pay errors.")
    print("=" * 60)


if __name__ == "__main__":
    main()
