"""
Rename Existing Payment Method Lines
=====================================
Rename the payment method lines that the wizard already shows:
- "Checks" (ID: 4) → "Check"
- "Manual Payment" (ID: 1) → "Cash"
- "Manual Payment" (ID: 3) → "Credit"
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Rename Payment Method Lines
# ==============================================================================

def rename_payment_method_lines():
    """Rename existing payment method lines to Cash, Credit, Check."""
    print("\n[*] Renaming existing payment method lines...")
    
    # Rename "Checks" (ID: 4) to "Check"
    print("\n[*] Renaming 'Checks' (ID: 4) to 'Check'...")
    payload1 = {
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
                "write",
                [[4], {
                    "name": "Check"
                }]
            ]
        }
    }
    
    response1 = requests.post(ODOO_URL, json=payload1, timeout=10)
    result1 = response1.json().get("result")
    
    if result1:
        print(f"[OK] Renamed 'Checks' to 'Check'")
    else:
        error1 = response1.json().get("error", {})
        print(f"[!] Failed: {error1}")
    
    # Rename "Manual Payment" (ID: 1) to "Cash"
    print("\n[*] Renaming 'Manual Payment' (ID: 1) to 'Cash'...")
    payload2 = {
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
                "write",
                [[1], {
                    "name": "Cash"
                }]
            ]
        }
    }
    
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get("result")
    
    if result2:
        print(f"[OK] Renamed 'Manual Payment' (ID: 1) to 'Cash'")
    else:
        error2 = response2.json().get("error", {})
        print(f"[!] Failed: {error2}")
    
    # Rename "Manual Payment" (ID: 3) to "Credit"
    print("\n[*] Renaming 'Manual Payment' (ID: 3) to 'Credit'...")
    payload3 = {
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
                "write",
                [[3], {
                    "name": "Credit"
                }]
            ]
        }
    }
    
    response3 = requests.post(ODOO_URL, json=payload3, timeout=10)
    result3 = response3.json().get("result")
    
    if result3:
        print(f"[OK] Renamed 'Manual Payment' (ID: 3) to 'Credit'")
    else:
        error3 = response3.json().get("error", {})
        print(f"[!] Failed: {error3}")
    
    return result1 and result2 and result3

# ==============================================================================
# Verify Renames
# ==============================================================================

def verify_renames():
    """Verify the renames worked."""
    print("\n[*] Verifying renames...")
    
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
                "read",
                [[1, 3, 4]],
                {
                    "fields": ["id", "name", "journal_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Renamed payment method lines:")
        for line in result:
            print(f"   • ID: {line['id']}, Name: '{line['name']}'")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RENAME: Existing Payment Method Lines")
    print("="*70)
    print("\nStrategy: Rename the payment method lines that the wizard")
    print("already recognizes instead of creating new ones.")
    print("\nRenaming:")
    print("  • 'Checks' (ID: 4) → 'Check'")
    print("  • 'Manual Payment' (ID: 1) → 'Cash'")
    print("  • 'Manual Payment' (ID: 3) → 'Credit'")
    print("="*70)
    
    # Rename
    success = rename_payment_method_lines()
    
    # Verify
    if success:
        verify_renames()
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Click Pay on invoice")
    print("3. Select Bank journal")
    print("4. Payment Method should now show: Cash, Credit, Check")
    print("\nThese are the same lines the wizard was already showing,")
    print("just renamed to match Workiz requirements.")
    print("="*70)

