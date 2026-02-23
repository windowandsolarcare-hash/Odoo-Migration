"""
Fix Currency in Payment Creation
==================================
The Pay action should pass currency from invoice, but it's not working.
We need to check the Pay action and potentially fix it.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Pay Action Full Details
# ==============================================================================

def get_pay_action_details():
    """Get full details of the Pay action."""
    print("\n[*] Getting Pay action details...")
    
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
                [[350]],  # Pay action ID
                {
                    "fields": ["id", "name", "model_id", "state", "code", "binding_model_id", "binding_view_types"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        action = result[0]
        print(f"\n[OK] Pay action (ID: 350):")
        print(f"   Name: {action.get('name', 'N/A')}")
        print(f"   State: {action.get('state', 'N/A')}")
        if action.get('code'):
            print(f"\n   Code:")
            print(f"   {action['code']}")
    else:
        print("[!] Pay action not found")
    
    return result[0] if result else None

# ==============================================================================
# Check Company Currency
# ==============================================================================

def get_company_currency():
    """Get the company's default currency."""
    print("\n[*] Getting company currency...")
    
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
                "res.company",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name", "currency_id"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        company = result[0]
        currency = company.get('currency_id', [])
        currency_id = currency[0] if isinstance(currency, list) and len(currency) > 0 else None
        currency_name = currency[1] if isinstance(currency, list) and len(currency) > 1 else 'N/A'
        print(f"[OK] Company currency: ID {currency_id} ({currency_name})")
        return currency_id
    else:
        print("[!] Company not found")
        return None

# ==============================================================================
# Check Journal Currency
# ==============================================================================

def get_bank_journal_currency():
    """Get the Bank journal's currency."""
    print("\n[*] Getting Bank journal currency...")
    
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
                [[["code", "=", "BNK1"]]],
                {
                    "fields": ["id", "name", "currency_id"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        journal = result[0]
        currency = journal.get('currency_id', [])
        currency_id = currency[0] if isinstance(currency, list) and len(currency) > 0 else None
        currency_name = currency[1] if isinstance(currency, list) and len(currency) > 1 else 'N/A'
        if currency_id:
            print(f"[OK] Bank journal currency: ID {currency_id} ({currency_name})")
        else:
            print("[OK] Bank journal has no specific currency (uses company default)")
        return currency_id
    else:
        print("[!] Bank journal not found")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Currency Error in Payment Creation")
    print("="*70)
    
    # Get Pay action
    pay_action = get_pay_action_details()
    
    # Get currencies
    company_currency = get_company_currency()
    journal_currency = get_bank_journal_currency()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nThe Pay action calls 'action_force_register_payment()' which should")
    print("automatically set currency from the invoice. However, the error")
    print("suggests the currency isn't being passed to the journal entry.")
    print("\nPOSSIBLE FIXES:")
    print("1. Ensure invoice has currency_id set (it should)")
    print("2. Check if Bank journal needs currency_id set")
    print("3. The payment form might need currency_id as a hidden field")
    print("   that defaults from invoice context")
    print("\nRECOMMENDATION:")
    print("The issue is likely that when the payment wizard opens, the")
    print("currency isn't being defaulted. We may need to add currency_id")
    print("as a hidden field in the payment form that defaults from context.")
    print("="*70)

