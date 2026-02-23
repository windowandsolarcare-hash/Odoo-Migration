"""
Automate Payment Posting
=========================
Modify Collect Payment action to automatically post/validate the payment
after creation, so user doesn't have to do it manually.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Update Action to Create and Post Payment Automatically
# ==============================================================================

def automate_payment_posting():
    """Update action to create payment and post it automatically."""
    print("\n[*] Updating Collect Payment action to auto-post payment...")
    
    # Instead of opening a form, we'll create the payment directly
    # and post it, then show a success message or redirect
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
    'ref': record.name,
    'invoice_ids': [(6, 0, [record.id])],
})

# Post the payment
payment.action_post()

# Show success message and refresh invoice
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
        print(f"[OK] Updated action to auto-create and post payment")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# Alternative: Keep Form but Auto-Post After Creation
# ==============================================================================

def create_wizard_approach():
    """Alternative: Create a wizard that collects info then auto-posts."""
    print("\n[*] This would require a custom wizard model...")
    print("    For now, the direct creation approach is simpler")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("AUTOMATE: Payment Posting")
    print("="*70)
    print("\nThis will change 'Collect Payment' to:")
    print("1. Create payment automatically (no form)")
    print("2. Post/validate it automatically")
    print("3. Show success message")
    print("\nNOTE: This skips the form - payment is created with defaults:")
    print("  - Payment Method: Check (or first available)")
    print("  - Amount: Invoice amount due")
    print("  - Date: Today")
    print("\nIf you need to enter check number or change payment method,")
    print("we'd need a custom wizard instead.")
    print("="*70)
    
    automated = automate_payment_posting()
    
    if automated:
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print("\nThe 'Collect Payment' action now:")
        print("1. Creates payment automatically")
        print("2. Posts/validates it automatically")
        print("3. Shows success notification")
        print("\nNEXT STEPS:")
        print("1. Refresh browser (Ctrl+F5)")
        print("2. Go to invoice")
        print("3. Click Actions → Collect Payment")
        print("4. Payment is created and posted automatically!")
        print("5. Invoice should show as paid")
        print("\nNOTE: This uses default payment method (Check).")
        print("If you need to select Cash/Credit or enter check number,")
        print("we can create a custom wizard for that.")
        print("="*70)

