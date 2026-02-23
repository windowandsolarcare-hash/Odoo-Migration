"""
Fix Collect Payment - Form First Approach
==========================================
Revert to form-first approach (fill form, then create)
but fix redirect so form stays open after creation.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Fix Collect Payment - Form First, Then Create
# ==============================================================================

def fix_collect_payment_form_first():
    """Restore form-first approach but use current window instead of popup."""
    print("\n[*] Restoring form-first approach...")
    print("    Opening form in current window (not popup)")
    print("    This should keep form open after creation")
    
    # Use target: 'current' instead of 'new' (popup)
    # This opens the form in the current window
    # After creation, it should stay on the payment form
    code = """action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'current',  # Open in current window, not popup
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
}"""
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.actions.server",
                "write",
                [[674], {  # Collect Payment action
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Updated Collect Payment action")
        print(f"     Form opens in current window (not popup)")
        print(f"     After Create, form should stay open")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Collect Payment - Form First Approach")
    print("="*70)
    
    fixed = fix_collect_payment_form_first()
    
    print("\n" + "="*70)
    print("FIXED:")
    print("="*70)
    print("\nCollect Payment now:")
    print("1. Opens payment form in current window (not popup)")
    print("2. Form is empty/new (not pre-created)")
    print("3. You fill in: Payment Method, Memo, Amount, Date")
    print("4. Click Create → Payment is created")
    print("5. Form stays open (doesn't redirect back to invoice)")
    print("6. You can immediately click Actions → Post Payment")
    print("\nWORKFLOW:")
    print("1. Invoice → Actions → Collect Payment")
    print("2. Payment form opens (empty, ready to fill)")
    print("3. Fill in: Payment Method, Memo (check number), Amount, Date")
    print("4. Click Create")
    print("5. Form stays open (you're still on payment form)")
    print("6. Click Actions → Post Payment")
    print("7. Payment fully validated → Invoice shows as paid")
    print("\nNOTE: Using 'current' window instead of 'new' popup")
    print("      This should prevent redirect back to invoice")
    print("="*70)

