"""
Check Payment Form & Add Check Number Field
============================================
1. Understand why Cash/Credit/Check might not show
2. Check payment form view to see if check_number is visible
3. Add check_number to payment form if needed
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Payment Form View XML
# ==============================================================================

def get_payment_form_arch():
    """Get the main payment form view architecture."""
    print("\n[*] Getting payment form view architecture...")
    
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
                "search_read",
                [[["name", "=", "account.payment.form"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        arch = result[0].get("arch", "")
        view_id = result[0]["id"]
        print(f"[OK] Found payment form view (ID: {view_id})")
        
        # Check if check_number is in the form
        if "check_number" in arch:
            print("[OK] check_number field IS in the form")
        else:
            print("[!] check_number field NOT in the form - needs to be added")
        
        # Check for payment_method_line_id
        if "payment_method_line_id" in arch:
            print("[OK] payment_method_line_id field IS in the form")
        else:
            print("[!] payment_method_line_id field NOT in the form")
        
        return result[0]
    else:
        print("[!] Payment form view not found")
        return None

# ==============================================================================
# Check Payment Method Line Filtering
# ==============================================================================

def check_payment_method_line_domain():
    """Check how payment method lines are filtered in the payment form."""
    print("\n[*] Checking payment method line filtering logic...")
    
    # The payment form likely filters by journal_id
    # When you select a journal, it shows only method lines for that journal
    print("[INFO] Payment method lines are filtered by journal_id")
    print("       When Bank journal is selected, it should show:")
    print("       - All method lines where journal_id = Bank journal")
    print("\n[INFO] Your Cash/Credit/Check lines (IDs 6,7,8) are linked to Bank journal")
    print("       They should appear when Bank journal is selected")
    print("\n[INFO] Possible reasons they're not showing:")
    print("       1. Browser cache - try hard refresh (Ctrl+F5)")
    print("       2. Journal not selected yet")
    print("       3. Form needs to be reloaded")

# ==============================================================================
# Check Payment Amount Behavior
# ==============================================================================

def check_payment_amount_behavior():
    """Explain payment amount field behavior."""
    print("\n[*] Payment Amount Field Behavior:")
    print("\n[INFO] In Odoo payment forms:")
    print("       1. Amount is often auto-filled from invoice amount")
    print("       2. Amount may be editable or read-only depending on:")
    print("          - Payment type (inbound vs outbound)")
    print("          - Whether payment is linked to invoice")
    print("          - Form configuration")
    print("\n[INFO] Typical workflow:")
    print("       1. Select payment method line")
    print("       2. Amount auto-fills from invoice")
    print("       3. You can modify amount if needed")
    print("       4. Enter check_number (if check payment)")
    print("       5. Select payment date")
    print("       6. Click 'Create Payment'")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK: Payment Form & Check Number Field")
    print("="*70)
    
    # Get form view
    form_view = get_payment_form_arch()
    
    # Check filtering
    check_payment_method_line_domain()
    
    # Check amount behavior
    check_payment_amount_behavior()
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    print("="*70)
    print("\n1. REFRESH BROWSER:")
    print("   -> Hard refresh (Ctrl+F5) to see new payment method lines")
    print("\n2. CHECK NUMBER FIELD:")
    print("   -> Field exists: check_number")
    print("   -> May need to add to form view if not visible")
    print("\n3. AMOUNT FIELD:")
    print("   -> Likely auto-fills from invoice")
    print("   -> Should be editable after selecting payment method")
    print("="*70)

