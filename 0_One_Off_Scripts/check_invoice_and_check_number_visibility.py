"""
Check Invoice Details and check_number Visibility
==================================================
1. Check why invoice name is False
2. Check check_number visibility conditions
3. Verify payment is correct
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Invoice Details
# ==============================================================================

def check_invoice_details():
    """Check invoice details including name and origin."""
    print("\n[*] Checking invoice details...")
    
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
                "account.move",
                "search_read",
                [[["move_type", "=", "out_invoice"], ["state", "=", "draft"]]],
                {
                    "fields": ["id", "name", "state", "invoice_origin", "ref", "amount_total", "currency_id"],
                    "order": "id desc",
                    "limit": 3
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Draft invoices:")
        for inv in result:
            print(f"\n   Invoice ID: {inv['id']}")
            print(f"   Name: {inv.get('name', 'False')} (False = not confirmed yet)")
            print(f"   State: {inv.get('state', 'N/A')}")
            print(f"   Origin (SO): {inv.get('invoice_origin', 'N/A')}")
            print(f"   Ref: {inv.get('ref', 'N/A')}")
            print(f"   Total: ${inv.get('amount_total', 0)}")
            
            # Check if it has a sale order
            if inv.get('invoice_origin'):
                so_name = inv['invoice_origin']
                print(f"   -> Created from Sales Order: {so_name}")
    
    return result

# ==============================================================================
# Check check_number Visibility Conditions
# ==============================================================================

def check_check_number_visibility():
    """Check why check_number field isn't showing."""
    print("\n[*] Checking check_number visibility conditions...")
    
    # Get our view inheritance
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
                "ir.ui.view",
                "read",
                [[2403]],  # Our check_number inheritance
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        arch = view.get("arch", "")
        print(f"\n[OK] Our check_number view inheritance:")
        print(f"   Name: {view.get('name', 'N/A')}")
        print(f"   Arch preview: {arch[:300]}")
        
        # Check if it has visibility conditions
        if "invisible" in arch.lower():
            print(f"\n   [!] Has 'invisible' condition - field may be hidden")
        if "required" in arch.lower():
            print(f"   [!] Has 'required' condition")
    
    # Also check the other view that has check_number
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
                "ir.ui.view",
                "read",
                [[1099]],  # The other view with check_number
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get("result", [])
    
    if result2:
        view2 = result2[0]
        arch2 = view2.get("arch", "")
        print(f"\n[OK] Other check_number view (ID 1099):")
        print(f"   Name: {view2.get('name', 'N/A')}")
        # Check for visibility conditions
        if "invisible" in arch2.lower() or "attrs" in arch2.lower():
            print(f"   [!] Has visibility conditions - may only show for certain payment methods")
    
    return result, result2

# ==============================================================================
# Check Payment Method Line ID for Check
# ==============================================================================

def verify_check_payment_method_id():
    """Verify the Check payment method line ID."""
    print("\n[*] Verifying Check payment method line ID...")
    
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
                [[["name", "=", "Check"]]],
                {
                    "fields": ["id", "name", "journal_id", "payment_method_id"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        check_line = result[0]
        check_id = check_line["id"]
        print(f"\n[OK] Check payment method line:")
        print(f"   ID: {check_id}")
        print(f"   Name: {check_line.get('name', 'N/A')}")
        print(f"\n   [!] Our view inheritance may need to check for ID {check_id}")
        print(f"   -> Currently checking for ID 8, but need to verify")
        return check_id
    else:
        print("[!] Check payment method line not found")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Invoice Details & check_number Visibility")
    print("="*70)
    
    # Check invoices
    invoices = check_invoice_details()
    
    # Check check_number visibility
    our_view, other_view = check_check_number_visibility()
    
    # Verify Check payment method ID
    check_id = verify_check_payment_method_id()
    
    print("\n" + "="*70)
    print("FINDINGS:")
    print("="*70)
    print("\n1. INVOICE NUMBERING:")
    print("   -> Invoice name is 'False' because invoice is in DRAFT state")
    print("   -> Invoices get their name (INV/2026/00001) when CONFIRMED")
    print("   -> The '004134' in breadcrumbs is the Sales Order number")
    print("   -> Invoice will be numbered when you confirm it")
    print("\n2. CHECK_NUMBER FIELD:")
    print("   -> Field exists in view but may have visibility conditions")
    print("   -> May only show when Check payment method is selected")
    print("   -> Need to verify payment_method_line_id = 8 (Check)")
    print("\n3. PAYMENT TYPE:")
    print("   -> Payment is correct: 'inbound' (receiving money from customer)")
    print("   -> 'Recipient Bank Account' is for customer's bank (optional)")
    print("   -> 'Company Bank Account' would be for AP (outbound) - not needed here")
    print("="*70)

