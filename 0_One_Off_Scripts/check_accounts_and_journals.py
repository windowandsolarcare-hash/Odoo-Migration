"""
Check Existing Journals and Accounts
====================================
Verify what journals and accounts exist for payment processing.
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# STEP 1: Get all journals
# ==============================================================================

def get_all_journals():
    """Get all journals in the system."""
    print("\n[*] Getting all journals...")
    
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
                [[]],
                {
                    "fields": ["id", "name", "type", "code", "default_account_id"],
                    "limit": 50
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} journals:")
        for journal in result:
            account = journal.get('default_account_id', [])
            account_name = account[1] if isinstance(account, list) and len(account) > 1 else 'N/A'
            print(f"   • ID: {journal['id']}, Name: {journal['name']}, Type: {journal.get('type', 'N/A')}, Code: {journal.get('code', 'N/A')}")
            print(f"     Default Account: {account_name}")
    else:
        print("[!] No journals found")
    
    return result

# ==============================================================================
# STEP 2: Get accounts (specifically Bank, AR, Revenue)
# ==============================================================================

def get_accounts():
    """Get accounts, specifically looking for Bank, AR, Revenue."""
    print("\n[*] Getting accounts (Bank, AR, Revenue)...")
    
    # Search for common account types
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
                "account.account",
                "search_read",
                [[
                    "|", "|",
                    ["name", "ilike", "bank"],
                    ["name", "ilike", "receivable"],
                    ["name", "ilike", "revenue"]
                ]],
                {
                    "fields": ["id", "name", "code", "account_type", "user_type_id"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} relevant accounts:")
        for account in result:
            account_type = account.get('account_type', 'N/A')
            user_type = account.get('user_type_id', [])
            user_type_name = user_type[1] if isinstance(user_type, list) and len(user_type) > 1 else 'N/A'
            print(f"   • ID: {account['id']}, Name: {account['name']}, Code: {account.get('code', 'N/A')}")
            print(f"     Type: {account_type}, User Type: {user_type_name}")
    else:
        print("[!] No relevant accounts found")
    
    return result

# ==============================================================================
# STEP 3: Check account types available
# ==============================================================================

def check_account_types():
    """Check what account types are available in the system."""
    print("\n[*] Checking available account types...")
    
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
                "account.account.type",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name", "type"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} account types:")
        for acc_type in result:
            print(f"   • ID: {acc_type['id']}, Name: {acc_type['name']}, Type: {acc_type.get('type', 'N/A')}")
    else:
        print("[!] No account types found")
    
    return result

# ==============================================================================
# STEP 4: Check if accounting app is installed
# ==============================================================================

def check_accounting_app():
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
                [[
                    ["name", "in", ["account", "sale", "account_accountant"]],
                    ["state", "=", "installed"]
                ]],
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
        print(f"[OK] Installed modules:")
        for module in result:
            print(f"   • {module['name']} ({module.get('state', 'N/A')})")
    else:
        print("[!] No accounting modules found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Journals and Accounts for Payment Processing")
    print("="*70)
    
    journals = get_all_journals()
    accounts = get_accounts()
    account_types = check_account_types()
    modules = check_accounting_app()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    print("\nFor basic payment processing, you need:")
    print("1. Bank Journal (with Bank account)")
    print("2. Accounts Receivable account")
    print("3. Revenue/Income account")
    print("\nCheck above to see what exists.")
    print("="*70)

