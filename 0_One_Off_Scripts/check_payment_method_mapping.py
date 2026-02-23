"""
Check Payment Method Mapping
============================
See what payment method names exist and how to map to Workiz.
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get payment method lines (what shows in dropdown)
# ==============================================================================

def get_payment_method_lines():
    """Get all payment method lines."""
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
                    "limit": 20
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
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Payment Method Mapping")
    print("="*70)
    
    method_lines = get_payment_method_lines()
    
    print("\n" + "="*70)
    print("MAPPING STRATEGY:")
    print("="*70)
    print("\nWorkiz requires: 'cash', 'credit', or 'check'")
    print("\nWe need to:")
    print("1. Create 3 payment method lines in Odoo: 'Cash', 'Credit', 'Check'")
    print("2. When syncing to Workiz, map the selected method name:")
    print("   - If name contains 'cash' -> 'cash'")
    print("   - If name contains 'credit' -> 'credit'")
    print("   - If name contains 'check' -> 'check'")
    print("\nOR we can store the mapping in a dictionary.")
    print("="*70)

