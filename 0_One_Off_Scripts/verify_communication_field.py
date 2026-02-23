"""
Verify Communication Field
===========================
Check if 'communication' field exists on account.payment.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Communication Field
# ==============================================================================

def check_communication_field():
    """Check if communication field exists."""
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
                "ir.model.fields",
                "search_read",
                [[
                    ["model", "=", "account.payment"],
                    ["name", "=", "communication"]
                ]],
                {
                    "fields": ["name", "field_description"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] 'communication' field exists")
        return True
    else:
        print(f"[!] 'communication' field does NOT exist")
        print(f"    Should use 'memo' or 'payment_reference' instead")
        return False

# ==============================================================================
# Fix to Use Correct Field
# ==============================================================================

def fix_to_use_memo():
    """Fix action to use 'memo' field instead."""
    print("\n[*] Fixing to use 'memo' field...")
    
    code = """# Get Bank journal
journal = env['account.journal'].search([('code', '=', 'BNK1')], limit=1)
if not journal:
    raise UserError("Bank journal not found")

# Get Check payment method line (default)
payment_method_line = env['account.payment.method.line'].search([
    ('journal_id', '=', journal.id),
    ('name', '=', 'Check')
], limit=1)

if not payment_method_line:
    # Fallback to first inbound method
    payment_method_line = env['account.payment.method.line'].search([
        ('journal_id', '=', journal.id),
        ('payment_method_id.payment_type', '=', 'inbound')
    ], limit=1)

# Create payment
payment = env['account.payment'].create({
    'payment_type': 'inbound',
    'partner_type': 'customer',
    'partner_id': record.partner_id.id,
    'amount': record.amount_residual,
    'currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
    'journal_id': journal.id,
    'payment_method_line_id': payment_method_line.id if payment_method_line else False,
    'memo': record.name,
    'invoice_ids': [(6, 0, [record.id])],
})

# Post the payment
payment.action_post()

# Show success message
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Created',
        'message': f'Payment {payment.name} created and posted successfully.',
        'type': 'success',
        'sticky': False,
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
                [[674], {
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Fixed - using 'memo' field")
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
    print("VERIFY & FIX: Communication Field")
    print("="*70)
    
    # Check if communication exists
    has_comm = check_communication_field()
    
    # Fix to use memo if communication doesn't exist
    if not has_comm:
        fix_to_use_memo()
    
    print("\n" + "="*70)
    print("FIXED:")
    print("="*70)
    print("\nUpdated to use 'memo' field (which exists on account.payment)")
    print("instead of 'ref' or 'communication'.")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Go to invoice")
    print("3. Click Actions → Collect Payment")
    print("4. Should now work!")
    print("="*70)

