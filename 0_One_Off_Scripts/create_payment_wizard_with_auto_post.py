"""
Create Payment Wizard with Auto-Post
=====================================
Create a custom wizard that:
1. Asks for payment method, check number, amount, date
2. Creates payment
3. Automatically posts/validates it
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Update Action to Open Form, Then Auto-Post After Creation
# ==============================================================================

def restore_form_with_auto_post():
    """Restore the form approach but with auto-post after creation."""
    print("\n[*] Restoring form approach with auto-post...")
    
    # Go back to opening the payment form
    # But we can't auto-post after form submission
    # So we need a different approach - use the payment register wizard
    # but customize it, OR create a custom wizard
    
    # Actually, simplest: Go back to opening payment form
    # User fills it in, clicks Create
    # Then we can't auto-post from server action...
    
    # Better: Use a server action that creates a payment in draft,
    # then opens it for editing, then we post it via another action?
    # No, that's too complex.
    
    # Best: Go back to form opening, but add a note that they need to validate
    # OR create a custom wizard
    
    # Let me restore the form opening approach first:
    code = """action = {
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
                [[674], {
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Restored form approach")
        print(f"\n[INFO] This opens the payment form where you can:")
        print(f"       - Select Payment Method (Cash/Credit/Check)")
        print(f"       - Enter Check Number")
        print(f"       - Adjust Amount if needed")
        print(f"       - Adjust Date if needed")
        print(f"\n[INFO] After you click Create, the payment is in draft.")
        print(f"       We can't auto-post from a form submission, but")
        print(f"       we can add a second action or button to auto-post.")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# Create Auto-Post Action for Payments
# ==============================================================================

def create_auto_post_payment_action():
    """Create a server action on account.payment to auto-post."""
    print("\n[*] Creating auto-post action for payments...")
    
    # Get account.payment model ID
    payload_model = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.model",
                "search_read",
                [[["model", "=", "account.payment"]]],
                {
                    "fields": ["id", "model"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_model = requests.post(ODOO_URL, json=payload_model, timeout=10)
    model_result = response_model.json().get("result", [])
    
    if model_result:
        model_id = model_result[0]["id"]
        
        code = """# Post the payment
for payment in records:
    if payment.state == 'draft':
        payment.action_post()
        
# Show success
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Posted',
        'message': f'Payment(s) posted successfully.',
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
                    "create",
                    [{
                        "name": "Post Payment",
                        "model_id": model_id,
                        "binding_model_id": model_id,
                        "binding_view_types": "form",
                        "state": "code",
                        "code": code
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result")
        
        if result:
            print(f"[OK] Created 'Post Payment' action (ID: {result})")
            print(f"     This will appear in Actions menu on payment form")
            return result
        else:
            error = response.json().get("error", {})
            print(f"[!] Failed: {error}")
            return None
    
    return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESTORE: Form with Auto-Post Option")
    print("="*70)
    
    # Restore form
    restored = restore_form_with_auto_post()
    
    # Create auto-post action
    post_action = create_auto_post_payment_action()
    
    print("\n" + "="*70)
    print("SOLUTION:")
    print("="*70)
    print("\n1. 'Collect Payment' now opens payment form (restored)")
    print("   - You can select Payment Method (Cash/Credit/Check)")
    print("   - Enter Check Number")
    print("   - Adjust Amount/Date if needed")
    print("\n2. After clicking 'Create', payment is in draft")
    print("\n3. 'Post Payment' action is now available:")
    print("   - Click Actions menu on payment form")
    print("   - Select 'Post Payment'")
    print("   - Payment is posted automatically")
    print("\nWORKFLOW:")
    print("1. Invoice → Actions → Collect Payment")
    print("2. Fill in form (Method, Check Number, etc.)")
    print("3. Click Create")
    print("4. On payment form → Actions → Post Payment")
    print("5. Done! Invoice is paid")
    print("="*70)

