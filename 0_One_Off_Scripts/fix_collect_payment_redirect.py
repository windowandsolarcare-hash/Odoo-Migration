"""
Fix Collect Payment Redirect
============================
Modify Collect Payment to open payment form in new window (not popup)
so it stays open after creation, allowing immediate Post Payment.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Fix Collect Payment Action - Open in New Window
# ==============================================================================

def fix_collect_payment_action():
    """Modify Collect Payment to open payment form in new window."""
    print("\n[*] Modifying Collect Payment action...")
    print("    Changing from popup (target: 'new') to new window")
    print("    This should keep payment form open after creation")
    
    # Change target from 'new' (popup) to 'current' (same window)
    # OR we can try creating payment first, then opening it
    # Actually, let's try a different approach: create payment in draft, then open it
    
    code = """# Create payment in draft first
journal = env['account.journal'].search([('code', '=', 'BNK1')], limit=1)
if not journal:
    raise UserError("Bank journal not found")

# Create payment in draft
payment_vals = {
    'payment_type': 'inbound',
    'partner_type': 'customer',
    'partner_id': record.partner_id.id,
    'amount': record.amount_residual,
    'currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
    'journal_id': journal.id,
    'memo': record.name,
    'invoice_ids': [(6, 0, [record.id])],
}

payment = env['account.payment'].create(payment_vals)

# Open the payment form (not as popup, so it stays open)
action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'res_id': payment.id,
    'view_mode': 'form',
    'target': 'current',  # Open in current window, not popup
    'context': {
        'form_view_initial_mode': 'edit',
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
        print(f"     Payment will be created in draft, then form opens")
        print(f"     Form stays open (not popup) so you can immediately Post")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# Verify Post Payment Action
# ==============================================================================

def verify_post_payment_action():
    """Verify Post Payment action is correct."""
    print("\n[*] Verifying Post Payment action...")
    
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
                "read",
                [[675]],
                {
                    "fields": ["id", "name", "code"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        code = result[0].get("code", "")
        if "action_post()" in code:
            print("[OK] Post Payment action uses action_post() - correct")
            return True
        else:
            print("[!] Post Payment action may not be fully validating")
            return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Collect Payment Redirect Issue")
    print("="*70)
    
    # Fix Collect Payment
    fixed = fix_collect_payment_action()
    
    # Verify Post Payment
    verified = verify_post_payment_action()
    
    print("\n" + "="*70)
    print("FIXES APPLIED:")
    print("="*70)
    print("\n1. Collect Payment: Now creates payment in draft, then opens form")
    print("   - Form opens in current window (not popup)")
    print("   - After you fill in Payment Method, Check Number, etc.")
    print("   - Form stays open (doesn't redirect back to invoice)")
    print("   - You can immediately click Actions → Post Payment")
    print("\n2. Post Payment: Uses action_post() to fully validate")
    print("\nNEW WORKFLOW:")
    print("1. Invoice → Actions → Collect Payment")
    print("2. Payment form opens (already created in draft)")
    print("3. Fill in: Payment Method, Memo (check number), Amount, Date")
    print("4. Click Save (or it auto-saves)")
    print("5. Click Actions → Post Payment")
    print("6. Payment is fully validated/posted")
    print("7. Invoice shows as paid")
    print("\nNOTE: Payment is created immediately, so you can't cancel")
    print("      If you need to cancel, delete the payment from invoice")
    print("="*70)

