"""
Check why "Create Invoice" appears in list view but not form view
================================================================
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# STEP 1: Find "Create Invoice" in server actions
# ==============================================================================

def find_create_invoice_action():
    """Search for Create Invoice server action."""
    print("\n[*] Searching for 'Create Invoice' server action...")
    
    # Search by name
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
                    ["name", "ilike", "invoice"],
                    ["model_id.model", "=", "sale.order"]
                ]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types", "state", "code"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} invoice-related actions:")
        for action in result:
            print(f"\n   • ID: {action['id']}, Name: {action['name']}")
            print(f"     Binding Model: {action.get('binding_model_id', 'None')}")
            print(f"     View Types: {action.get('binding_view_types', 'None')}")
            print(f"     State: {action.get('state', 'N/A')}")
            if action.get('code'):
                code_preview = action['code'][:100] if len(action.get('code', '')) > 100 else action.get('code', '')
                print(f"     Code preview: {code_preview}...")
    else:
        print("[!] No invoice-related actions found")
    
    return result

# ==============================================================================
# STEP 2: Check if it's a button in the view XML
# ==============================================================================

def check_view_for_invoice_button():
    """Check the list view XML for Create Invoice button."""
    print("\n[*] Checking list view for Create Invoice button...")
    
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
                "ir.ui.view",
                "search_read",
                [[
                    ["model", "=", "sale.order"],
                    ["type", "=", "tree"],
                    ["mode", "=", "primary"]
                ]],
                {
                    "fields": ["id", "name", "arch_db"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        arch = view.get('arch_db', '')
        
        # Check for action_invoice_create
        if 'action_invoice_create' in arch or 'create.*invoice' in arch.lower():
            print("[OK] Found 'action_invoice_create' reference in list view XML")
            # Extract the button definition
            import re
            button_match = re.search(r'<button[^>]*action_invoice_create[^>]*>', arch, re.IGNORECASE)
            if button_match:
                print(f"     Button found: {button_match.group()[:200]}")
        else:
            print("[!] No direct button found in list view XML")
            print("     It might be added via server action or menu")
    
    return result

# ==============================================================================
# STEP 3: Check form view for comparison
# ==============================================================================

def check_form_view():
    """Check form view to see what's there."""
    print("\n[*] Checking form view...")
    
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
                "ir.ui.view",
                "search_read",
                [[
                    ["model", "=", "sale.order"],
                    ["type", "=", "form"],
                    ["mode", "=", "primary"]
                ]],
                {
                    "fields": ["id", "name", "arch_db"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        arch = view.get('arch_db', '')
        
        if 'action_invoice_create' in arch:
            print("[OK] 'action_invoice_create' IS in form view XML")
        else:
            print("[!] 'action_invoice_create' is NOT in form view XML")
            print("     This explains why it doesn't appear in form view")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Why Create Invoice in List but Not Form")
    print("="*70)
    
    # Step 1: Check server actions
    actions = find_create_invoice_action()
    
    # Step 2: Check list view
    list_view = check_view_for_invoice_button()
    
    # Step 3: Check form view
    form_view = check_form_view()
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    print("If 'action_invoice_create' is in list view but not form view,")
    print("we can add it via view inheritance (add button to form view XML)")
    print("="*70)

