"""
Check Invoice Currency and Fix
================================
Verify invoice has currency_id set, and if not, set it to USD.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get USD Currency ID
# ==============================================================================

def get_usd_currency_id():
    """Get USD currency ID."""
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
                "res.currency",
                "search_read",
                [[["name", "=", "USD"]]],
                {
                    "fields": ["id", "name"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        currency_id = result[0]["id"]
        print(f"[OK] USD currency ID: {currency_id}")
        return currency_id
    else:
        print("[!] USD currency not found")
        return None

# ==============================================================================
# Check Invoice Currency
# ==============================================================================

def check_invoice_currency(invoice_id=None):
    """Check if invoice has currency_id set."""
    print("\n[*] Checking invoice currency...")
    
    # If invoice_id provided, check that specific invoice
    # Otherwise check all draft invoices
    domain = [["move_type", "=", "out_invoice"], ["state", "=", "draft"]]
    if invoice_id:
        domain = [["id", "=", invoice_id]]
    
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
                [domain],
                {
                    "fields": ["id", "name", "currency_id", "amount_total"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Found {len(result)} invoice(s):")
        for inv in result:
            currency = inv.get('currency_id', [])
            currency_id = currency[0] if isinstance(currency, list) and len(currency) > 0 else None
            currency_name = currency[1] if isinstance(currency, list) and len(currency) > 1 else 'N/A'
            
            if currency_id:
                print(f"   • {inv['name']}: Currency ID {currency_id} ({currency_name}) - OK")
            else:
                print(f"   • {inv['name']}: NO CURRENCY SET - NEEDS FIX")
        
        return result
    else:
        print("[!] No invoices found")
        return []

# ==============================================================================
# Fix Invoice Currency
# ==============================================================================

def fix_invoice_currency(invoice_id, currency_id):
    """Set currency_id on invoice."""
    print(f"\n[*] Setting currency_id on invoice {invoice_id}...")
    
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
                "write",
                [[invoice_id], {
                    "currency_id": currency_id
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Currency set on invoice")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to set currency: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CHECK & FIX: Invoice Currency")
    print("="*70)
    
    # Get USD currency
    usd_id = get_usd_currency_id()
    
    if usd_id:
        # Check invoices
        invoices = check_invoice_currency()
        
        # Fix any invoices without currency
        fixed = 0
        for inv in invoices:
            currency = inv.get('currency_id', [])
            currency_id = currency[0] if isinstance(currency, list) and len(currency) > 0 else None
            
            if not currency_id:
                if fix_invoice_currency(inv['id'], usd_id):
                    fixed += 1
        
        if fixed > 0:
            print(f"\n[OK] Fixed {fixed} invoice(s) - set currency to USD")
        else:
            print("\n[OK] All invoices have currency set")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. If invoice was missing currency, it's now set to USD")
    print("2. Try creating payment again - currency should now be inherited")
    print("3. If error persists, the Pay action may need to explicitly")
    print("   pass currency in context")
    print("="*70)

