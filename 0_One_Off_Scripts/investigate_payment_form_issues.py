"""
Investigate Payment Form Issues
================================
1. Check why check_number field isn't showing
2. Verify we're using correct payment type (inbound for AR)
3. Check invoice numbering
4. Verify Company Bank Account field usage
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Form View for check_number
# ==============================================================================

def check_check_number_in_form():
    """Check if check_number is actually in the form view."""
    print("\n[*] Checking payment form view for check_number...")
    
    # Get all form views for account.payment
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
                [[["model", "=", "account.payment"], ["type", "=", "form"]]],
                {
                    "fields": ["id", "name", "arch"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[OK] Found {len(result)} payment form views:")
        for view in result:
            arch = view.get("arch", "")
            if "check_number" in arch:
                print(f"   • {view['name']} (ID: {view['id']}) - HAS check_number")
                # Check if it's conditional
                if "invisible" in arch.lower() or "attrs" in arch.lower():
                    print(f"     -> Has visibility conditions")
            else:
                print(f"   • {view['name']} (ID: {view['id']}) - NO check_number")
    
    return result

# ==============================================================================
# Check Payment Type (Inbound vs Outbound)
# ==============================================================================

def check_payment_type():
    """Check payment type field and values."""
    print("\n[*] Checking payment type field...")
    
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
                "ir.model.fields",
                "search_read",
                [[["model", "=", "account.payment"], ["name", "=", "payment_type"]]],
                {
                    "fields": ["name", "field_description", "selection"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        field = result[0]
        selection = field.get("selection", "")
        print(f"[OK] payment_type field:")
        print(f"   Description: {field.get('field_description', 'N/A')}")
        print(f"   Selection: {selection[:200] if selection else 'N/A'}")
        print(f"\n   For Accounts Receivable (customer payments):")
        print(f"   -> payment_type should be 'inbound' (receiving money)")
        print(f"   -> partner_type should be 'customer'")
    
    return result

# ==============================================================================
# Check Invoice Numbering
# ==============================================================================

def check_invoice_numbering():
    """Check invoice numbering sequence."""
    print("\n[*] Checking invoice numbering...")
    
    # Get recent invoices
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
                [[["move_type", "=", "out_invoice"]]],
                {
                    "fields": ["id", "name", "state", "invoice_date", "amount_total"],
                    "order": "id desc",
                    "limit": 5
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Recent invoices:")
        for inv in result:
            print(f"   • ID: {inv['id']}, Name: {inv['name']}, State: {inv.get('state', 'N/A')}, Total: ${inv.get('amount_total', 0)}")
    
    # Check sequence
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
                "ir.sequence",
                "search_read",
                [[["code", "=", "account.move.customer.invoice"]]],
                {
                    "fields": ["id", "name", "code", "number_next"],
                    "limit": 1
                }
            ]
        }
    }
    
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get("result", [])
    
    if result2:
        seq = result2[0]
        print(f"\n[OK] Invoice sequence:")
        print(f"   Name: {seq.get('name', 'N/A')}")
        print(f"   Code: {seq.get('code', 'N/A')}")
        print(f"   Next number: {seq.get('number_next', 'N/A')}")
    
    return result, result2

# ==============================================================================
# Check Company Bank Account Field
# ==============================================================================

def check_company_bank_account_field():
    """Check what the Company Bank Account field is for."""
    print("\n[*] Checking Company Bank Account field...")
    
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
                "ir.model.fields",
                "search_read",
                [[
                    ["model", "=", "account.payment"],
                    ["name", "in", ["partner_bank_id", "destination_account_id", "company_bank_account_id"]]
                ]],
                {
                    "fields": ["name", "field_description", "ttype", "help"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Bank account related fields:")
        for field in result:
            print(f"   • {field['name']}: {field.get('field_description', 'N/A')}")
            if field.get('help'):
                print(f"     Help: {field['help'][:100]}")
    
    return result

# ==============================================================================
# Check Payment Created
# ==============================================================================

def check_recent_payment():
    """Check the most recent payment to see its details."""
    print("\n[*] Checking most recent payment...")
    
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
                "account.payment",
                "search_read",
                [[]],
                {
                    "fields": ["id", "name", "payment_type", "partner_type", "amount", "currency_id", "state", "check_number"],
                    "order": "id desc",
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        payment = result[0]
        print(f"\n[OK] Most recent payment:")
        print(f"   ID: {payment['id']}")
        print(f"   Name: {payment.get('name', 'N/A')}")
        print(f"   Payment Type: {payment.get('payment_type', 'N/A')}")
        print(f"   Partner Type: {payment.get('partner_type', 'N/A')}")
        print(f"   Amount: ${payment.get('amount', 0)}")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Check Number: {payment.get('check_number', 'N/A')}")
        
        currency = payment.get('currency_id', [])
        currency_name = currency[1] if isinstance(currency, list) and len(currency) > 1 else 'N/A'
        print(f"   Currency: {currency_name}")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Payment Form Issues")
    print("="*70)
    
    # Check check_number in form
    form_views = check_check_number_in_form()
    
    # Check payment type
    payment_type = check_payment_type()
    
    # Check invoice numbering
    invoices, sequence = check_invoice_numbering()
    
    # Check company bank account
    bank_fields = check_company_bank_account_field()
    
    # Check recent payment
    recent_payment = check_recent_payment()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\n1. CHECK_NUMBER FIELD:")
    print("   -> May be conditional (only shows for certain payment methods)")
    print("   -> May need to check visibility conditions")
    print("\n2. PAYMENT TYPE:")
    print("   -> For customer payments (AR), should be 'inbound'")
    print("   -> 'Company Bank Account' is for AP (outbound) payments")
    print("   -> For AR, we receive money, so no company bank account needed")
    print("\n3. INVOICE NUMBERING:")
    print("   -> Invoice name vs ID may be different")
    print("   -> Need to check actual invoice record")
    print("="*70)

