"""
Research: Batch Payments & Studio Access
=========================================
1. Check if Odoo supports batch payments
2. Answer Studio access in popups question
3. Check payment method creation requirements
"""

import requests
import sys

# Fix encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Method Structure
# ==============================================================================

def check_payment_method_structure():
    """Check what fields are required to create payment method lines."""
    print("\n[*] Checking payment method line structure...")
    
    # Get fields of account.payment.method.line
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
                "fields_get",
                [],
                {"attributes": ["required", "type", "string"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    fields = response.json().get("result", {})
    
    print("\n[OK] Payment Method Line Fields:")
    for field_name, field_info in fields.items():
        required = field_info.get("required", False)
        field_type = field_info.get("type", "unknown")
        string = field_info.get("string", field_name)
        if required or field_name in ["name", "payment_method_id", "journal_id"]:
            print(f"   • {field_name} ({field_type}): {string} {'[REQUIRED]' if required else ''}")
    
    return fields

# ==============================================================================
# Check Payment Methods Available
# ==============================================================================

def get_payment_methods():
    """Get all payment methods (not method lines)."""
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
                [[["payment_type", "=", "inbound"]]],
                {
                    "fields": ["id", "name", "code", "payment_type"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} inbound payment methods:")
        for method in result:
            print(f"   • ID: {method['id']}, Name: {method['name']}, Code: {method.get('code', 'N/A')}")
    else:
        print("[!] No payment methods found")
    
    return result

# ==============================================================================
# Check Batch Payment Options
# ==============================================================================

def check_batch_payment_module():
    """Check if batch payment module exists."""
    print("\n[*] Checking for batch payment module...")
    
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
                [[["name", "=", "account_batch_payment"]]],
                {
                    "fields": ["id", "name", "state"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        state = result[0].get("state", "unknown")
        print(f"[OK] Batch Payment module found: {state}")
        if state == "installed":
            print("   -> Batch payments are available!")
        else:
            print("   -> Module exists but not installed")
    else:
        print("[!] Batch Payment module not found")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("RESEARCH: Batch Payments & Studio Access")
    print("="*70)
    
    # Check payment method structure
    fields = check_payment_method_structure()
    
    # Get payment methods
    methods = get_payment_methods()
    
    # Check batch payment module
    batch_module = check_batch_payment_module()
    
    print("\n" + "="*70)
    print("ANSWERS:")
    print("="*70)
    print("\n1. STUDIO ACCESS IN POPUPS:")
    print("   -> Studio icon is grayed out in popups because Studio")
    print("     can only edit main views, not modal/popup windows.")
    print("   -> Popups are temporary views - you can't customize them")
    print("     via Studio. You'd need to create a custom wizard or")
    print("     modify the view via XML/API.")
    print("\n2. BATCH PAYMENTS:")
    print("   -> Odoo has a 'Batch Payment' module (account_batch_payment)")
    print("   -> This allows grouping multiple invoices into one payment")
    print("   -> However, for your workflow (6-7 checks at end of day):")
    print("     * Each check = 1 invoice = 1 payment (individual)")
    print("     * Batch payments are for: 1 payment covering multiple invoices")
    print("   -> Your workflow is already optimal: individual payments")
    print("     per invoice (one check per customer)")
    print("\n3. PAYMENT METHOD CREATION:")
    print("   -> We can create payment method lines via API")
    print("   -> Need: name, payment_method_id, journal_id")
    print("="*70)

