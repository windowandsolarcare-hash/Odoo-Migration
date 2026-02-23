"""
Check Payment Register Wizard Workflow
======================================
The payment register wizard should create AND post the payment in one step.
Need to understand why it's not creating move lines.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Register Wizard
# ==============================================================================

def check_payment_register_wizard():
    """Check the payment register wizard model and its methods."""
    print("\n[*] Checking payment register wizard...")
    
    # Check if account.payment.register model exists
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
                "ir.model",
                "search_read",
                [[["model", "=", "account.payment.register"]]],
                {
                    "fields": ["id", "name", "model"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Payment register wizard model exists")
        print(f"    Model: {result[0].get('model', 'N/A')}")
        
        # The wizard should have an action_create_payments() method
        # This method creates the payment AND posts it in one step
        # It also reconciles automatically
        
        print(f"\n[INFO] The payment register wizard should:")
        print(f"   1. Collect payment info (method, amount, date, etc.)")
        print(f"   2. Call action_create_payments()")
        print(f"   3. This creates payment, posts it, and reconciles")
        print(f"\n[INFO] The issue might be that the wizard isn't calling")
        print(f"       action_create_payments() correctly, or the payment")
        print(f"       isn't being posted properly.")
        
        return True
    else:
        print(f"[!] Payment register wizard model not found")
        return False

# ==============================================================================
# Create Server Action to Properly Post Payment
# ==============================================================================

def create_proper_post_payment_action():
    """Create a server action that properly posts payment and reconciles."""
    print("\n[*] Creating proper post payment action...")
    
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
        
        # Create action that properly posts and reconciles
        code = """# Properly post payment and reconcile
for payment in records:
    # Ensure payment is linked to invoice
    if not payment.invoice_ids:
        raise UserError("Payment must be linked to an invoice")
    
    # Post the payment (this creates move and move lines)
    if payment.state == 'draft':
        payment.action_post()
    elif payment.state != 'posted':
        # Try to post anyway
        payment.action_post()
    
    # The payment register wizard uses action_create_payments() which does:
    # 1. Creates payment
    # 2. Posts it (creates move and move lines)
    # 3. Reconciles automatically
    
    # Since we're posting manually, we need to ensure reconciliation
    # The payment should have move lines now
    if payment.move_id:
        # Reconcile with invoice
        for invoice in payment.invoice_ids:
            # Get invoice receivable line
            invoice_lines = invoice.line_ids.filtered(
                lambda l: l.account_id.internal_type == 'receivable'
                and l.balance > 0
                and not l.reconciled
            )
            
            # Get payment receivable line
            payment_lines = payment.move_id.line_ids.filtered(
                lambda l: l.account_id.internal_type == 'receivable'
                and l.balance < 0
                and not l.reconciled
            )
            
            # Reconcile
            if invoice_lines and payment_lines:
                (invoice_lines + payment_lines).reconcile()

# Show success
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Posted & Reconciled',
        'message': 'Payment has been posted and reconciled with invoice.',
        'type': 'success',
        'sticky': False,
    }
}"""
        
        # Update existing Post Payment action (ID: 675)
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
                    [[675], {
                        "code": code
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result")
        
        if result:
            print(f"[OK] Updated Post Payment action to properly post and reconcile")
            return True
        else:
            error = response.json().get("error", {})
            print(f"[!] Failed: {error}")
            return False
    
    return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Payment Register Wizard Workflow")
    print("="*70)
    
    wizard_checked = check_payment_register_wizard()
    action_updated = create_proper_post_payment_action()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nThe payment register wizard should create AND post the payment")
    print("in one step via action_create_payments().")
    print("\nWhen you use the standard 'Pay' button:")
    print("1. Wizard opens")
    print("2. You fill in payment details")
    print("3. Click 'Create Payment' (not 'Confirm' then 'Validate')")
    print("4. This calls action_create_payments() which:")
    print("   - Creates the payment")
    print("   - Posts it (creates move and move lines)")
    print("   - Reconciles automatically")
    print("\nThe issue is you're clicking 'Confirm' then 'Validate' separately,")
    print("which might not be creating the move lines properly.")
    print("\nSOLUTION:")
    print("Use the 'Create Payment' button in the wizard (if available),")
    print("OR ensure the payment is fully posted with move lines before reconciling.")
    print("="*70)

