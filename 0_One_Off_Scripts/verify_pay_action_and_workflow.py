"""
Verify Pay Action and Payment Workflow
======================================
1. Find the "Pay" action on account.move (invoice)
2. Understand payment states (draft vs posted)
3. Determine best trigger point for Phase 6
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# STEP 1: Find "Pay" action on account.move (invoice)
# ==============================================================================

def find_pay_action():
    """Find the Pay action for invoices."""
    print("\n[*] Searching for 'Pay' action on account.move...")
    
    # Search server actions
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
                "search_read",
                [[
                    ["name", "ilike", "pay"],
                    ["model_id.model", "=", "account.move"]
                ]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types", "state"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} 'Pay' actions:")
        for action in result:
            print(f"   • ID: {action['id']}, Name: {action['name']}")
            print(f"     Binding: {action.get('binding_model_id', 'None')}, View: {action.get('binding_view_types', 'None')}")
    else:
        print("[!] No 'Pay' server actions found")
    
    # Also check window actions
    payload2 = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.actions.act_window",
                "search_read",
                [[
                    ["name", "ilike", "pay"],
                    ["res_model", "=", "account.payment"]
                ]],
                {
                    "fields": ["id", "name", "res_model", "binding_model_id", "binding_view_types"],
                    "limit": 10
                }
            ]
        }
    }
    
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get("result", [])
    
    if result2:
        print(f"\n[OK] Found {len(result2)} 'Pay' window actions:")
        for action in result2:
            print(f"   • ID: {action['id']}, Name: {action['name']}, Model: {action.get('res_model', 'N/A')}")
            print(f"     Binding: {action.get('binding_model_id', 'None')}, View: {action.get('binding_view_types', 'None')}")
    
    return result + result2

# ==============================================================================
# STEP 2: Check account.payment model states
# ==============================================================================

def check_payment_states():
    """Check what states a payment can have."""
    print("\n[*] Checking account.payment model states...")
    
    # Get the model to see state field
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
                    ["name", "=", "state"]
                ]],
                {
                    "fields": ["name", "field_description", "selection"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        field = result[0]
        selection = field.get('selection', '')
        print(f"[OK] Payment states:")
        if selection:
            # selection is a string like "[('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')]"
            print(f"   Selection field: {selection[:200]}")
        else:
            print("   (Selection not in field definition - check Odoo docs)")
        print("\n   Standard Odoo payment states:")
        print("   - draft: Payment created but not posted")
        print("   - posted: Payment is posted (confirmed, affects accounts)")
        print("   - cancel: Payment cancelled")
    
    return result

# ==============================================================================
# STEP 3: Check if there's an action_post method
# ==============================================================================

def check_payment_methods():
    """Check what methods exist on account.payment."""
    print("\n[*] Checking account.payment model methods...")
    
    # We can't directly list methods via API, but we know standard Odoo has:
    print("[INFO] Standard Odoo payment methods:")
    print("   - action_post(): Posts the payment (draft -> paid)")
    print("   - action_draft(): Unposts the payment (paid -> draft)")
    print("   - action_cancel(): Cancels the payment")
    print("\n   When payment is 'paid', it affects the accounts.")
    print("   This is when the invoice balance is actually reduced.")
    
    return True

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("VERIFY: Pay Action and Payment Workflow")
    print("="*70)
    
    pay_actions = find_pay_action()
    payment_states = check_payment_states()
    payment_methods = check_payment_methods()
    
    print("\n" + "="*70)
    print("PAYMENT WORKFLOW:")
    print("="*70)
    print("\nStandard Odoo Invoice Payment Flow:")
    print("1. Click 'Pay' action on invoice")
    print("2. Payment form opens (Journal, Payment Method, Amount, Date)")
    print("3. Click 'Create Payment' -> Payment created in 'draft' state")
    print("4. Payment must be 'posted' (paid state) to affect accounts and reduce invoice balance")
    print("\nQUESTION: When should Phase 6 trigger?")
    print("  A) After payment created (draft state)")
    print("  B) After payment posted (paid state) - RECOMMENDED")
    print("\nRecommendation: After PAID state")
    print("  - Payment is confirmed and affects accounts")
    print("  - Invoice balance is actually reduced")
    print("  - More reliable (no risk of cancelling draft payment)")
    print("="*70)

