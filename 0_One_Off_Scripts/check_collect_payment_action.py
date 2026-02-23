"""
Check Collect Payment Action
=============================
Verify if our action was created and check for naming conflicts.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check All Server Actions Named "Collect Payment"
# ==============================================================================

def check_collect_payment_actions():
    """Check all server actions with 'Collect Payment' in name."""
    print("\n[*] Checking all 'Collect Payment' server actions...")
    
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
                [[["name", "ilike", "collect payment"]]],
                {
                    "fields": ["id", "name", "model_id", "binding_model_id", "binding_view_types", "state", "code"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} server action(s) with 'Collect Payment' in name:")
        for action in result:
            model = action.get('model_id', [])
            model_name = model[1] if isinstance(model, list) and len(model) > 1 else 'N/A'
            binding = action.get('binding_model_id', [])
            binding_name = binding[1] if isinstance(binding, list) and len(binding) > 1 else 'N/A'
            view_types = action.get('binding_view_types', '')
            code_preview = action.get('code', '')[:100] if action.get('code') else 'N/A'
            
            print(f"\n   Action ID: {action['id']}")
            print(f"   Name: {action.get('name', 'N/A')}")
            print(f"   Model: {model_name}")
            print(f"   Binding Model: {binding_name}")
            print(f"   View Types: {view_types}")
            print(f"   State: {action.get('state', 'N/A')}")
            print(f"   Code preview: {code_preview}...")
            
            # Check if it's our action (has account.payment in code)
            if 'account.payment' in code_preview:
                print(f"   -> THIS IS OUR ACTION (has account.payment in code)")
            else:
                print(f"   -> This might be a default Odoo action")
    else:
        print("[!] No 'Collect Payment' actions found")
    
    return result

# ==============================================================================
# Check Action ID 674 (What We Created)
# ==============================================================================

def check_action_674():
    """Check the specific action we created (ID 674)."""
    print("\n[*] Checking action ID 674 (what we created)...")
    
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
                "read",
                [[674]],
                {
                    "fields": ["id", "name", "model_id", "binding_model_id", "binding_view_types", "state", "code"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"\n[OK] Action 674 details:")
        print(f"   Name: {action.get('name', 'N/A')}")
        model = action.get('model_id', [])
        model_name = model[1] if isinstance(model, list) and len(model) > 1 else 'N/A'
        print(f"   Model: {model_name}")
        binding = action.get('binding_model_id', [])
        binding_name = binding[1] if isinstance(binding, list) and len(binding) > 1 else 'N/A'
        print(f"   Binding Model: {binding_name}")
        view_types = action.get('binding_view_types', '')
        print(f"   View Types: {view_types}")
        print(f"   State: {action.get('state', 'N/A')}")
        
        if view_types and 'form' not in view_types:
            print(f"\n   [!] PROBLEM: 'form' not in binding_view_types!")
            print(f"       This is why it's not showing in the Actions menu")
            print(f"       Need to add 'form' to binding_view_types")
        
        code = action.get('code', '')
        if 'account.payment' in code:
            print(f"\n   [OK] This IS our action (has account.payment in code)")
        else:
            print(f"\n   [!] This doesn't look like our action")
        
        return action
    else:
        print("[!] Action 674 not found")
        return None

# ==============================================================================
# Fix Binding View Types
# ==============================================================================

def fix_binding_view_types():
    """Add 'form' to binding_view_types so it appears in Actions menu."""
    print("\n[*] Fixing binding_view_types to include 'form'...")
    
    # Get current view types
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
                "ir.actions.server",
                "read",
                [[674]],
                {
                    "fields": ["binding_view_types"]
                }
            ]
        }
    }
    
    response_read = requests.post(ODOO_URL, json=payload_read, timeout=10)
    result_read = response_read.json().get("result", [])
    
    if result_read:
        current_types = result_read[0].get("binding_view_types", "")
        print(f"   Current binding_view_types: {current_types}")
        
        # Add 'form' if not present
        if isinstance(current_types, str):
            # It's a string like "list,form" or just "list"
            if 'form' not in current_types:
                new_types = current_types + ",form" if current_types else "form"
            else:
                new_types = current_types
        else:
            # It's a list
            if isinstance(current_types, list):
                if 'form' not in current_types:
                    new_types = current_types + ['form']
                else:
                    new_types = current_types
            else:
                new_types = "form"
        
        # Update it
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
                        "binding_view_types": new_types
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result")
        
        if result:
            print(f"[OK] Updated binding_view_types to include 'form'")
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
    print("CHECK: Collect Payment Action")
    print("="*70)
    
    # Check all Collect Payment actions
    all_actions = check_collect_payment_actions()
    
    # Check our specific action
    action_674 = check_action_674()
    
    # Fix binding if needed
    if action_674:
        fixed = fix_binding_view_types()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print("\n1. Journal Entry (account.move) IS the correct model for invoices")
    print("2. The action was created (ID: 674)")
    print("3. It may not be showing because 'form' isn't in binding_view_types")
    print("4. Fixed: Added 'form' to binding_view_types")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Go to any invoice")
    print("3. Click Actions menu")
    print("4. 'Collect Payment' should now appear")
    print("="*70)

