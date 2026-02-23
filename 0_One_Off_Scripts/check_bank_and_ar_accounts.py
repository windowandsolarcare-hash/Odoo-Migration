"""
Check Bank Journal Account and AR Accounts
==========================================
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Bank Journal details
# ==============================================================================

def get_bank_journal_details():
    """Get full details of Bank journal."""
    print("\n[*] Getting Bank journal details...")
    
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
                [[["type", "=", "bank"]]],
                {"fields": ["id", "name", "type", "code", "default_account_id", "payment_debit_account_id", "payment_credit_account_id"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        journal = result[0]
        print(f"[OK] Bank Journal:")
        print(f"   Name: {journal['name']}")
        print(f"   Code: {journal.get('code', 'N/A')}")
        default_acc = journal.get('default_account_id', [])
        if default_acc:
            print(f"   Default Account: {default_acc[1]} (ID: {default_acc[0]})")
        return journal
    else:
        print("[!] Bank journal not found")
        return None

# ==============================================================================
# Search for AR accounts (Accounts Receivable)
# ==============================================================================

def find_ar_accounts():
    """Find Accounts Receivable accounts."""
    print("\n[*] Searching for Accounts Receivable accounts...")
    
    # Search by name variations
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
                    "|", "|", "|",
                    ["name", "ilike", "receivable"],
                    ["name", "ilike", "customer"],
                    ["name", "ilike", "trade"],
                    ["code", "ilike", "120"]
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
        print(f"[OK] Found {len(result)} potential AR accounts:")
        for account in result:
            account_type = account.get('account_type', 'N/A')
            user_type = account.get('user_type_id', [])
            user_type_name = user_type[1] if isinstance(user_type, list) and len(user_type) > 1 else 'N/A'
            print(f"   • ID: {account['id']}, Name: {account['name']}, Code: {account.get('code', 'N/A')}")
            print(f"     Account Type: {account_type}, User Type: {user_type_name}")
    else:
        print("[!] No AR accounts found")
    
    return result

# ==============================================================================
# Get all accounts to see what exists
# ==============================================================================

def get_all_accounts():
    """Get all accounts to see what's available."""
    print("\n[*] Getting ALL accounts (first 30)...")
    
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
                [[]],
                {
                    "fields": ["id", "name", "code", "account_type"],
                    "limit": 30,
                    "order": "code"
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} accounts (showing first 30):")
        for account in result:
            print(f"   • Code: {account.get('code', 'N/A'):<10} Name: {account['name']:<40} Type: {account.get('account_type', 'N/A')}")
    else:
        print("[!] No accounts found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Bank Journal and AR Accounts")
    print("="*70)
    
    bank_journal = get_bank_journal_details()
    ar_accounts = find_ar_accounts()
    all_accounts = get_all_accounts()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nFor payment processing, Odoo typically needs:")
    print("1. Bank Journal (check above)")
    print("2. Accounts Receivable account (check above)")
    print("3. Revenue account (check 'Product Sales' above)")
    print("\nIf AR account doesn't exist, Odoo may create it automatically")
    print("or you may need to set it up in accounting configuration.")
    print("="*70)

