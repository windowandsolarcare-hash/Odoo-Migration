"""
Check Accounting Module Installation
======================================
Verify if accounting module is installed - this could be the root cause!
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Accounting Module
# ==============================================================================

def check_accounting_module():
    """Check if accounting module is installed."""
    print("\n[*] Checking if accounting module is installed...")
    
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
                "ir.module.module",
                "search_read",
                [[["name", "=", "account"]]],
                {
                    "fields": ["id", "name", "state", "summary"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        module = result[0]
        state = module.get("state", "unknown")
        print(f"\n[OK] Accounting module found:")
        print(f"   Name: {module.get('name', 'N/A')}")
        print(f"   State: {state}")
        print(f"   Summary: {module.get('summary', 'N/A')}")
        
        if state == "installed":
            print(f"\n[OK] Accounting module IS installed")
            return True
        elif state == "uninstalled":
            print(f"\n[!] Accounting module is NOT installed - THIS IS THE PROBLEM!")
            return False
        else:
            print(f"\n[!] Accounting module state: {state}")
            return False
    else:
        print("[!] Accounting module not found")
        return False

# ==============================================================================
# Check Account Accountant Module
# ==============================================================================

def check_account_accountant_module():
    """Check if account_accountant module is installed."""
    print("\n[*] Checking if account_accountant module is installed...")
    
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
                "ir.module.module",
                "search_read",
                [[["name", "=", "account_accountant"]]],
                {
                    "fields": ["id", "name", "state", "summary"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        module = result[0]
        state = module.get("state", "unknown")
        print(f"\n[OK] Account Accountant module:")
        print(f"   State: {state}")
        
        if state == "installed":
            print(f"   -> IS installed")
        else:
            print(f"   -> NOT installed")
        
        return state == "installed"
    else:
        print("[!] Account Accountant module not found")
        return False

# ==============================================================================
# Check What Payment-Related Modules Are Installed
# ==============================================================================

def check_payment_modules():
    """Check what payment-related modules are installed."""
    print("\n[*] Checking payment-related modules...")
    
    modules_to_check = [
        "account",
        "account_accountant", 
        "account_payment",
        "account_batch_payment"
    ]
    
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
                "ir.module.module",
                "search_read",
                [[["name", "in", modules_to_check]]],
                {
                    "fields": ["id", "name", "state"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Payment-related modules:")
        for module in result:
            state = module.get("state", "unknown")
            status = "✓" if state == "installed" else "✗"
            print(f"   {status} {module.get('name', 'N/A')}: {state}")
    else:
        print("[!] No modules found")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Accounting Module Installation")
    print("="*70)
    
    # Check accounting
    accounting_installed = check_accounting_module()
    
    # Check account_accountant
    accountant_installed = check_account_accountant_module()
    
    # Check all payment modules
    check_payment_modules()
    
    print("\n" + "="*70)
    print("DIAGNOSIS:")
    print("="*70)
    
    if not accounting_installed:
        print("\n[!] ROOT CAUSE IDENTIFIED:")
        print("    Accounting module is NOT installed!")
        print("\n    This explains:")
        print("    - Payment wizard issues")
        print("    - Currency field problems")
        print("    - Missing required fields")
        print("    - Payment creation failures")
        print("\n    SOLUTION:")
        print("    Install the Accounting module:")
        print("    1. Go to: Apps (or Settings > Apps)")
        print("    2. Search for 'Accounting'")
        print("    3. Click 'Install'")
        print("    4. Wait for installation to complete")
        print("    5. Try payment creation again")
    elif not accountant_installed:
        print("\n[!] Account Accountant module not installed")
        print("    This provides the full accounting features")
        print("    Install it for better payment handling")
    else:
        print("\n[OK] Accounting modules are installed")
        print("    The issue is elsewhere - likely wizard configuration")
    
    print("="*70)

