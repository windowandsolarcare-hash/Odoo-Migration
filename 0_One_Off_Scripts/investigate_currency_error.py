"""
Investigate Currency Error in Payment Creation
===============================================
The payment form is missing currency_id when creating payment from invoice.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment Form Context
# ==============================================================================

def check_payment_fields():
    """Check what fields are required on account.payment."""
    print("\n[*] Checking account.payment required fields...")
    
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
                "fields_get",
                [],
                {"attributes": ["required", "type", "string"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    fields = response.json().get("result", {})
    
    required_fields = []
    for field_name, field_info in fields.items():
        if field_info.get("required", False):
            field_type = field_info.get("type", "unknown")
            field_string = field_info.get("string", field_name)
            required_fields.append((field_name, field_type, field_string))
    
    print(f"\n[OK] Required fields on account.payment:")
    for field_name, field_type, field_string in required_fields:
        print(f"   • {field_name} ({field_type}): {field_string}")
    
    # Check specifically for currency_id
    if "currency_id" in fields:
        currency_info = fields["currency_id"]
        print(f"\n[OK] currency_id field exists:")
        print(f"   Type: {currency_info.get('type', 'unknown')}")
        print(f"   Required: {currency_info.get('required', False)}")
        print(f"   String: {currency_info.get('string', 'N/A')}")
    
    return fields

# ==============================================================================
# Check Invoice Currency
# ==============================================================================

def check_invoice_currency():
    """Check how invoices store currency."""
    print("\n[*] Checking invoice currency field...")
    
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
                [[["move_type", "=", "out_invoice"]], ["state", "=", "draft"]],
                {
                    "fields": ["id", "name", "currency_id", "amount_total"],
                    "limit": 3
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} draft invoices:")
        for inv in result:
            currency = inv.get('currency_id', [])
            currency_name = currency[1] if isinstance(currency, list) and len(currency) > 1 else 'N/A'
            currency_id = currency[0] if isinstance(currency, list) and len(currency) > 0 else None
            print(f"   • {inv['name']}: Currency ID {currency_id} ({currency_name}), Total: ${inv.get('amount_total', 0)}")
    else:
        print("[!] No draft invoices found")
    
    return result

# ==============================================================================
# Check Pay Action Context
# ==============================================================================

def check_pay_action_context():
    """Check what context the Pay action passes."""
    print("\n[*] Checking Pay action context...")
    
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
                "search_read",
                [[["name", "ilike", "pay"], ["model_id.model", "=", "account.move"]]],
                {
                    "fields": ["id", "name", "binding_model_id", "binding_view_types", "state", "code"],
                    "limit": 5
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} Pay actions:")
        for action in result:
            print(f"   • ID: {action['id']}, Name: {action['name']}")
            if action.get('code'):
                code_preview = action['code'][:200] if len(action['code']) > 200 else action['code']
                print(f"     Code preview: {code_preview}...")
    else:
        print("[!] No Pay actions found")
    
    return result

# ==============================================================================
# Check Payment Form View for Currency Field
# ==============================================================================

def check_payment_form_currency():
    """Check if currency_id is in payment form view."""
    print("\n[*] Checking if currency_id is in payment form...")
    
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
        if "currency_id" in arch:
            print("[OK] currency_id field IS in the form")
        else:
            print("[!] currency_id field NOT in the form - this is the problem!")
            print("    The payment form needs currency_id to be set from invoice context")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Currency Error in Payment Creation")
    print("="*70)
    
    # Check payment fields
    payment_fields = check_payment_fields()
    
    # Check invoice currency
    invoices = check_invoice_currency()
    
    # Check Pay action
    pay_actions = check_pay_action_context()
    
    # Check form view
    form_view = check_payment_form_currency()
    
    print("\n" + "="*70)
    print("PROBLEM:")
    print("="*70)
    print("\nThe payment form is missing currency_id when created from invoice.")
    print("Odoo should automatically inherit currency from the invoice, but")
    print("it's not being passed in the context or defaulted properly.")
    print("\nSOLUTION:")
    print("We need to ensure currency_id is set when creating payment from invoice.")
    print("This is typically done via:")
    print("1. Context from Pay action (default_currency_id)")
    print("2. Default value from journal")
    print("3. Explicitly setting it in the form")
    print("="*70)

