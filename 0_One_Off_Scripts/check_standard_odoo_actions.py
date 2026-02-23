"""
Check standard Odoo actions and menu items
===========================================
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check if "Create Invoice" is a standard action in ir.actions.act_window
# ==============================================================================

def check_window_actions():
    """Check window actions (standard Odoo actions)."""
    print("\n[*] Checking window actions for 'Create Invoice'...")
    
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
                "ir.actions.act_window",
                "search_read",
                [[["name", "ilike", "invoice"]]],
                {
                    "fields": ["id", "name", "res_model", "binding_model_id", "binding_view_types"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} window actions:")
        for action in result:
            print(f"   • ID: {action['id']}, Name: {action['name']}, Model: {action.get('res_model', 'N/A')}")
    else:
        print("[!] No window actions found")
    
    return result

# ==============================================================================
# Check ALL server actions on sale.order (broader search)
# ==============================================================================

def check_all_sale_order_actions():
    """Check ALL server actions bound to sale.order."""
    print("\n[*] Checking ALL server actions on sale.order...")
    
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
                    ["binding_model_id.model", "=", "sale.order"]
                ]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types"],
                    "limit": 50
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} server actions bound to sale.order:")
        for action in result:
            view_types = action.get('binding_view_types', '')
            if 'list' in view_types or 'form' in view_types:
                print(f"   • ID: {action['id']}, Name: {action['name']}")
                print(f"     View Types: {view_types}")
    
    return result

# ==============================================================================
# Check if it's in the standard Odoo menu
# ==============================================================================

def check_menu_items():
    """Check menu items for Create Invoice."""
    print("\n[*] Checking menu items...")
    
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
                "ir.ui.menu",
                "search_read",
                [[["name", "ilike", "invoice"]]],
                {
                    "fields": ["id", "name", "action"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} menu items:")
        for menu in result:
            print(f"   • ID: {menu['id']}, Name: {menu['name']}")
    else:
        print("[!] No menu items found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Where Create Invoice Comes From")
    print("="*70)
    
    window_actions = check_window_actions()
    server_actions = check_all_sale_order_actions()
    menu_items = check_menu_items()
    
    print("\n" + "="*70)
    print("EXPLANATION:")
    print("="*70)
    print("'Create Invoice' in list view is likely a standard Odoo action")
    print("that appears when you select records. It's not a server action,")
    print("it's a built-in method call.")
    print("\nTo add it to form view, we can:")
    print("1. Create a server action that calls action_invoice_create")
    print("2. Bind it to form view")
    print("OR")
    print("3. Add a button directly to form view XML via view inheritance")
    print("="*70)

