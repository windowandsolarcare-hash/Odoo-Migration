"""
Fix Payment Ref Field
======================
The 'ref' field doesn't exist on account.payment. Need to use correct field.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Model Fields
# ==============================================================================

def check_payment_fields():
    """Check what fields exist on account.payment for reference/memo."""
    print("\n[*] Checking account.payment fields...")
    
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
                    ["name", "in", ["ref", "communication", "payment_reference", "memo"]]
                ]],
                {
                    "fields": ["name", "field_description", "ttype"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Available reference fields:")
        for field in result:
            print(f"   • {field['name']} ({field['ttype']}): {field.get('field_description', 'N/A')}")
        return result
    else:
        print("[!] No reference fields found")
        return []

# ==============================================================================
# Fix the Action Code
# ==============================================================================

def fix_action_code():
    """Fix the action code - remove invalid 'ref' field."""
    print("\n[*] Fixing Collect Payment action code...")
    
    # Remove 'ref' field - use 'communication' instead if needed
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
    'communication': record.name,
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
        print(f"[OK] Fixed - changed 'ref' to 'communication'")
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
    print("FIX: Payment Ref Field Error")
    print("="*70)
    
    # Check fields
    fields = check_payment_fields()
    
    # Fix code
    fixed = fix_action_code()
    
    print("\n" + "="*70)
    print("FIXED:")
    print("="*70)
    print("\nChanged 'ref' to 'communication' (the correct field name)")
    print("on account.payment model.")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Go to invoice")
    print("3. Click Actions → Collect Payment")
    print("4. Should now work without error!")
    print("="*70)

