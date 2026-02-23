"""
Add "Create Invoice" Server Action to Sales Order Form View
===========================================================
This script finds the standard "Create Invoice" server action and adds it to the sale.order form view.
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# STEP 1: Find the "Create Invoice" server action
# ==============================================================================

def find_create_invoice_action():
    """Find the standard 'Create Invoice' server action."""
    print("\n[*] Searching for 'Create Invoice' server action...")
    
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
                    ["name", "ilike", "create invoice"],
                    ["model_id.model", "=", "sale.order"]
                ]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} matching actions:")
        for action in result:
            print(f"   • ID: {action['id']}, Name: {action['name']}")
            print(f"     Binding: {action.get('binding_model_id', 'None')}, View Types: {action.get('binding_view_types', 'None')}")
        return result
    else:
        print("[!] No matching actions found")
        return []

# ==============================================================================
# STEP 2: Get current form view
# ==============================================================================

def get_form_view():
    """Get the current sale.order form view."""
    print("\n[*] Getting sale.order form view...")
    
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
                    "fields": ["id", "name", "arch_db", "inherit_id"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        print(f"[OK] Found form view: {view['name']} (ID: {view['id']})")
        return view
    else:
        print("[!] Form view not found")
        return None

# ==============================================================================
# STEP 3: Research Payment Methods
# ==============================================================================

def get_payment_methods():
    """Get all payment methods to map to Workiz types (cash, credit, check)."""
    print("\n[*] Getting payment methods...")
    
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
                "account.payment.method",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name", "code", "payment_type"],
                    "limit": 50
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} payment methods:")
        for method in result:
            print(f"   • ID: {method['id']}, Name: {method['name']}, Code: {method.get('code', 'N/A')}, Type: {method.get('payment_type', 'N/A')}")
        return result
    else:
        print("[!] No payment methods found")
        return []

# ==============================================================================
# STEP 4: Get Bank Journal
# ==============================================================================

def get_bank_journal():
    """Get the Bank journal (for payment journal selection)."""
    print("\n[*] Getting Bank journal...")
    
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
                "account.journal",
                "search_read",
                [[
                    ["type", "=", "bank"]
                ]],
                {
                    "fields": ["id", "name", "type", "code"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} bank journal(s):")
        for journal in result:
            print(f"   • ID: {journal['id']}, Name: {journal['name']}, Code: {journal.get('code', 'N/A')}")
        return result
    else:
        print("[!] No bank journal found")
        return []

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESEARCH: Create Invoice Action & Payment Methods")
    print("="*70)
    
    # Step 1: Find Create Invoice action
    actions = find_create_invoice_action()
    
    # Step 2: Get form view (for reference)
    form_view = get_form_view()
    
    # Step 3: Get payment methods
    payment_methods = get_payment_methods()
    
    # Step 4: Get bank journal
    bank_journals = get_bank_journal()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print("\nNext Steps:")
    print("1. Identify the correct 'Create Invoice' action ID")
    print("2. Create view inheritance to add action to form view")
    print("3. Map payment methods to Workiz types (cash, credit, check)")
    print("4. Identify trigger point for Phase 6 (after payment posted?)")
    print("="*70)

