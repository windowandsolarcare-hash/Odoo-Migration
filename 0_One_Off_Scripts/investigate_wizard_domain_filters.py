"""
Investigate Wizard Domain Filters
==================================
Check how the payment register wizard filters payment method lines.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Get Wizard Form View XML
# ==============================================================================

def get_wizard_form_xml():
    """Get the full XML of the wizard form to see domain filters."""
    print("\n[*] Getting wizard form XML...")
    
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
                [[885]],
                {
                    "fields": ["id", "name", "arch"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        arch = result[0].get("arch", "")
        
        # Look for payment_method_line_id field
        if "payment_method_line_id" in arch:
            print("[OK] Found payment_method_line_id field in wizard")
            
            # Extract the field definition
            import re
            # Find the field tag
            pattern = r'<field[^>]*name=["\']payment_method_line_id["\'][^>]*>'
            match = re.search(pattern, arch, re.IGNORECASE)
            
            if match:
                field_tag = match.group(0)
                print(f"\n[OK] payment_method_line_id field definition:")
                print(f"   {field_tag}")
                
                # Check for domain
                if "domain" in field_tag.lower():
                    print(f"\n   [!] HAS DOMAIN FILTER - this may be excluding our methods")
                    # Extract domain
                    domain_match = re.search(r'domain=["\']([^"\']+)["\']', field_tag, re.IGNORECASE)
                    if domain_match:
                        domain = domain_match.group(1)
                        print(f"   Domain: {domain}")
                else:
                    print(f"\n   [OK] No domain filter on field itself")
                
                # Check for options
                if "options" in field_tag.lower():
                    options_match = re.search(r'options=["\']([^"\']+)["\']', field_tag, re.IGNORECASE)
                    if options_match:
                        options = options_match.group(1)
                        print(f"   Options: {options}")
        
        # Save full XML to file for inspection
        with open("0_One_Off_Scripts/wizard_form_xml.txt", "w", encoding="utf-8") as f:
            f.write(arch)
        print(f"\n[OK] Full XML saved to wizard_form_xml.txt for inspection")
        
        return arch
    else:
        print("[!] Wizard form not found")
        return None

# ==============================================================================
# Check Payment Method Line Domain Logic
# ==============================================================================

def check_payment_method_line_domain():
    """Check how payment method lines are filtered in the wizard model."""
    print("\n[*] Checking payment method line domain logic...")
    
    # Check account.payment.register model fields
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
                    ["model", "=", "account.payment.register"],
                    ["name", "in", ["payment_method_line_id", "journal_id"]]
                ]],
                {
                    "fields": ["name", "field_description", "relation", "domain"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Wizard model fields:")
        for field in result:
            print(f"   • {field['name']}: {field.get('field_description', 'N/A')}")
            if field.get('domain'):
                print(f"     Domain: {field.get('domain')}")

# ==============================================================================
# Check Payment Method Lines by Journal
# ==============================================================================

def verify_payment_method_lines():
    """Verify our payment method lines are correctly configured."""
    print("\n[*] Verifying payment method lines...")
    
    # Get Bank journal ID
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
                    "fields": ["id", "name", "code"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    journal_result = response.json().get("result", [])
    
    if journal_result:
        journal_id = journal_result[0]["id"]
        print(f"[OK] Bank journal ID: {journal_id}")
        
        # Get all payment method lines for this journal
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
                    "search_read",
                    [[["journal_id", "=", journal_id]]],
                    {
                        "fields": ["id", "name", "journal_id", "payment_method_id"],
                        "limit": 20
                    }
                ]
            }
        }
        
        response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
        result2 = response2.json().get("result", [])
        
        if result2:
            print(f"\n[OK] All payment method lines for Bank journal ({len(result2)} total):")
            for line in result2:
                method_id = line.get('payment_method_id', [])
                method_name = method_id[1] if isinstance(method_id, list) and len(method_id) > 1 else 'N/A'
                print(f"   • ID: {line['id']}, Name: '{line['name']}', Method: {method_name}")
            
            # Check our specific ones
            cash_credit_check = [line for line in result2 if line['name'] in ['Cash', 'Credit', 'Check']]
            if cash_credit_check:
                print(f"\n[OK] Our Cash/Credit/Check lines:")
                for line in cash_credit_check:
                    print(f"   • {line['name']} (ID: {line['id']}) - EXISTS and linked to Bank journal")
            else:
                print(f"\n[!] Cash/Credit/Check lines NOT found!")
        
        return result2

# ==============================================================================
# Check if Payment Method Lines Need payment_type Filter
# ==============================================================================

def check_payment_method_type():
    """Check if payment method lines need to match payment_type."""
    print("\n[*] Checking payment method type requirements...")
    
    # Check payment method lines for inbound type
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
                [[
                    ["journal_id.code", "=", "BNK1"],
                    ["payment_method_id.payment_type", "=", "inbound"]
                ]],
                {
                    "fields": ["id", "name", "payment_method_id"],
                    "limit": 20
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Payment method lines for Bank journal with inbound type ({len(result)} total):")
        for line in result:
            print(f"   • ID: {line['id']}, Name: '{line['name']}'")
        
        cash_credit_check = [line for line in result if line['name'] in ['Cash', 'Credit', 'Check']]
        if cash_credit_check:
            print(f"\n[OK] Cash/Credit/Check found with inbound filter:")
            for line in cash_credit_check:
                print(f"   • {line['name']} (ID: {line['id']})")
        else:
            print(f"\n[!] Cash/Credit/Check NOT found with inbound filter!")
            print(f"    This may be the issue - wizard may filter by payment_type='inbound'")
    
    return result

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("INVESTIGATE: Wizard Domain Filters")
    print("="*70)
    
    # Get wizard XML
    wizard_xml = get_wizard_form_xml()
    
    # Check domain logic
    check_payment_method_line_domain()
    
    # Verify payment method lines
    all_lines = verify_payment_method_lines()
    
    # Check payment type filter
    inbound_lines = check_payment_method_type()
    
    print("\n" + "="*70)
    print("ANALYSIS:")
    print("="*70)
    print("\nThe wizard likely filters payment method lines by:")
    print("1. journal_id (Bank journal)")
    print("2. payment_method_id.payment_type = 'inbound' (for customer payments)")
    print("\nIf Cash/Credit/Check don't appear with inbound filter,")
    print("their payment_method_id may not have payment_type='inbound'")
    print("="*70)

