"""
Add Create & Post Button to Payment Form
==========================================
Add a button to payment form that creates and posts in one click.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Create Server Action for Create & Post
# ==============================================================================

def create_create_and_post_action():
    """Create a server action that creates and posts payment."""
    print("\n[*] Creating 'Create & Post Payment' server action...")
    
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
        
        code = """# Create payment from form values
# This runs when payment is in draft state
for payment in records:
    if payment.state == 'draft':
        # Payment already created, just post it
        payment.action_post()
    else:
        # Create new payment if needed
        payment.action_post()
        
# Show success and close form
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Posted',
        'message': f'Payment posted successfully.',
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
                        "name": "Create & Post Payment",
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
            print(f"[OK] Created 'Create & Post Payment' action (ID: {result})")
            return result
    
    return None

# ==============================================================================
# Add Button to Payment Form View
# ==============================================================================

def add_button_to_payment_form():
    """Add a 'Create & Post' button to payment form."""
    print("\n[*] Adding button to payment form...")
    
    # Get payment form view
    payload_read = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.ui.view",
                "search_read",
                [[["name", "=", "account.payment.form"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_read = requests.post(ODOO_URL, json=payload_read, timeout=10)
    view_result = response_read.json().get("result", [])
    
    if view_result:
        view_id = view_result[0]["id"]
        
        # Add button before the footer
        arch = """<?xml version="1.0"?>
<data>
    <xpath expr="//footer" position="before">
        <button name="action_create_and_post" 
                string="Create &amp; Post Payment" 
                type="object" 
                class="oe_highlight"
                attrs="{'invisible': [('state', '!=', 'draft')]}"/>
    </xpath>
</data>"""
        
        # Actually, we can't add a button that calls a method that doesn't exist
        # We'd need to add the method to the model first
        
        print("[!] Cannot add button without model method")
        print("    Would need to add method to account.payment model")
        print("    This requires a custom module")
        
        return False
    
    return False

# ==============================================================================
# Better Approach: Modify Collect Payment Action
# ==============================================================================

def modify_collect_payment_to_use_wizard():
    """Actually, let's use the payment register wizard but customize it."""
    print("\n[*] Actually, the payment register wizard already exists")
    print("    and has a form. The issue is it doesn't auto-post.")
    print("\n    BEST SOLUTION: Keep current approach but make it clearer:")
    print("    1. Collect Payment opens form")
    print("    2. Fill in → Create")
    print("    3. Click 'Post Payment' action (one more click)")
    print("\n    OR we create a custom module with wizard that auto-posts")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD: Create & Post Button")
    print("="*70)
    
    # Create action
    action_id = create_create_and_post_action()
    
    # Try to add button (will fail without model method)
    button_added = add_button_to_payment_form()
    
    modify_collect_payment_to_use_wizard()
    
    print("\n" + "="*70)
    print("CURRENT STATUS:")
    print("="*70)
    print("\n1. 'Collect Payment' opens payment form ✓")
    print("2. You fill in: Method, Check Number, Amount, Date ✓")
    print("3. Click 'Create' → Payment created in draft")
    print("4. Click 'Post Payment' action → Payment posted ✓")
    print("\nTo fully automate step 4, we'd need a custom Python module")
    print("that adds a method to account.payment model.")
    print("\nFor now, the workflow is:")
    print("  Form → Create → Post Payment action (2 clicks total)")
    print("="*70)

