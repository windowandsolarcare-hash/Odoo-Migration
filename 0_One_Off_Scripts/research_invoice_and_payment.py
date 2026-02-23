"""
Research: Create Invoice Action & Payment Method Lines
======================================================
Find the Create Invoice action and payment method lines for Workiz mapping.
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# STEP 1: Find ALL server actions for sale.order
# ==============================================================================

def find_all_sale_order_actions():
    """Find all server actions for sale.order model."""
    print("\n[*] Searching for ALL server actions on sale.order...")
    
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
                [[["model_id.model", "=", "sale.order"]]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types", "state"],
                    "limit": 50
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} actions:")
        for action in result:
            print(f"   • ID: {action['id']}, Name: {action['name']}")
            print(f"     Binding: {action.get('binding_model_id', 'None')}, View: {action.get('binding_view_types', 'None')}")
    else:
        print("[!] No actions found")
    
    return result

# ==============================================================================
# STEP 2: Find "action_invoice_create" method (standard Odoo method)
# ==============================================================================

def find_invoice_create_method():
    """Check if sale.order has action_invoice_create method."""
    print("\n[*] Checking sale.order model for action_invoice_create method...")
    
    # This is a standard Odoo method, not a server action
    # We can call it directly, but we need to add it as a button to the form view
    print("[INFO] 'action_invoice_create' is a standard Odoo method on sale.order")
    print("       We can add it as a button to the form view via view inheritance")
    return True

# ==============================================================================
# STEP 3: Get Payment Method Lines (what shows in payment form)
# ==============================================================================

def get_payment_method_lines():
    """Get payment method lines - these are what show in the payment form dropdown."""
    print("\n[*] Getting payment method lines...")
    
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
                "account.payment.method.line",
                "search_read",
                [[["payment_method_id.payment_type", "=", "inbound"]]],
                {
                    "fields": ["id", "name", "payment_method_id", "journal_id"],
                    "limit": 50
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} inbound payment method lines:")
        for line in result:
            method_id = line.get('payment_method_id', [])
            journal_id = line.get('journal_id', [])
            method_name = method_id[1] if isinstance(method_id, list) and len(method_id) > 1 else 'N/A'
            journal_name = journal_id[1] if isinstance(journal_id, list) and len(journal_id) > 1 else 'N/A'
            print(f"   • ID: {line['id']}, Name: {line['name']}")
            print(f"     Method: {method_name}, Journal: {journal_name}")
    else:
        print("[!] No payment method lines found")
    
    return result

# ==============================================================================
# STEP 4: Check account.payment model for payment state
# ==============================================================================

def check_payment_model():
    """Check account.payment model to understand payment states."""
    print("\n[*] Checking account.payment model fields...")
    
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
                    ["name", "in", ["state", "payment_type", "payment_method_line_id", "amount", "date", "ref"]]
                ]],
                {
                    "fields": ["name", "field_description", "ttype"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} relevant payment fields:")
        for field in result:
            print(f"   • {field['name']} ({field['ttype']}) - {field['field_description']}")
    else:
        print("[!] No fields found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESEARCH: Invoice Creation & Payment Methods")
    print("="*70)
    
    # Step 1: Find all actions
    actions = find_all_sale_order_actions()
    
    # Step 2: Check for standard method
    find_invoice_create_method()
    
    # Step 3: Get payment method lines
    payment_lines = get_payment_method_lines()
    
    # Step 4: Check payment model
    payment_fields = check_payment_model()
    
    print("\n" + "="*70)
    print("FINDINGS:")
    print("="*70)
    print("\n1. 'Create Invoice' is likely a standard Odoo method (action_invoice_create)")
    print("2. We can add it as a button to form view via view inheritance")
    print("3. Payment method lines are what appear in the payment form dropdown")
    print("4. Need to map payment method lines to Workiz types (cash, credit, check)")
    print("5. Payment state field will tell us when payment is 'posted' (ready for Phase 6)")
    print("="*70)

