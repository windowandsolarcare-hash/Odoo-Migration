"""
Add "Create Invoice" to Sales Order Form View
=============================================
This will create a server action that opens the Create Invoice wizard,
and bind it to the form view (so it appears in the Actions menu).
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# The window action ID for "Create invoice(s)" wizard
CREATE_INVOICE_WIZARD_ACTION_ID = 478

# ==============================================================================
# STEP 1: Get the window action details
# ==============================================================================

def get_wizard_action():
    """Get details of the Create Invoice wizard action."""
    print("\n[*] Getting Create Invoice wizard action details...")
    
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
                "read",
                [[CREATE_INVOICE_WIZARD_ACTION_ID]],
                {"fields": ["id", "name", "res_model", "target", "context"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"[OK] Found wizard action:")
        print(f"   Name: {action['name']}")
        print(f"   Model: {action.get('res_model', 'N/A')}")
        print(f"   Target: {action.get('target', 'N/A')}")
        return action
    else:
        print("[ERROR] Could not find wizard action")
        return None

# ==============================================================================
# STEP 2: Get sale.order model ID
# ==============================================================================

def get_sale_order_model_id():
    """Get the sale.order model ID for binding."""
    print("\n[*] Getting sale.order model ID...")
    
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
                [[["model", "=", "sale.order"]]],
                {"fields": ["id", "model"], "limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        model_id = result[0]['id']
        print(f"[OK] sale.order model ID: {model_id}")
        return model_id
    else:
        print("[ERROR] Could not find sale.order model")
        return None

# ==============================================================================
# STEP 3: Create server action that opens the wizard
# ==============================================================================

def create_server_action(model_id):
    """Create a server action that opens the Create Invoice wizard."""
    print("\n[*] Creating server action for Create Invoice...")
    
    # The server action will use Python code to open the wizard
    # We'll use action_server_run to execute the window action
    action_data = {
        "name": "Create Invoice",
        "model_id": model_id,
        "binding_model_id": model_id,
        "binding_view_types": "form",  # Only show in form view
        "state": "code",
        "code": f"""
# Open the Create Invoice wizard
action = env.ref('sale.action_view_sale_advance_payment_inv')
result = action.read()[0]
# Set context to use current record
result['context'] = {{'active_model': 'sale.order', 'active_ids': [record.id], 'active_id': record.id}}
"""
    }
    
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
                [action_data]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result"):
        action_id = result["result"]
        print(f"[OK] Server action created: ID {action_id}")
        return action_id
    else:
        error = result.get("error", {})
        print(f"[ERROR] Failed to create server action: {error}")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("ADD CREATE INVOICE TO FORM VIEW")
    print("="*70)
    
    # Step 1: Get wizard action
    wizard_action = get_wizard_action()
    if not wizard_action:
        exit(1)
    
    # Step 2: Get model ID
    model_id = get_sale_order_model_id()
    if not model_id:
        exit(1)
    
    # Step 3: Create server action
    print("\n[!] READY TO CREATE SERVER ACTION")
    print("    This will add 'Create Invoice' to the form view Actions menu")
    print("    Proceed? (Currently just showing what would be created)")
    
    # For now, just show what we'd create - don't actually create it
    print("\n[INFO] To actually create, uncomment the create_server_action call")
    # action_id = create_server_action(model_id)

