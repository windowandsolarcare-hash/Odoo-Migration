"""
Deep Dive: Wizard Payment Method Filtering
===========================================
Check the actual compute logic and see what's filtering out Cash/Credit/Check.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check if Domain Override Actually Applied
# ==============================================================================

def check_domain_override():
    """Check if our domain override view is active."""
    print("\n[*] Checking if domain override view is active...")
    
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
                [[2406]],  # Our domain override view
                {
                    "fields": ["id", "name", "arch", "active", "inherit_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        view = result[0]
        print(f"[OK] Domain override view:")
        print(f"   ID: {view['id']}")
        print(f"   Name: {view.get('name', 'N/A')}")
        print(f"   Active: {view.get('active', True)}")
        print(f"   Inherit ID: {view.get('inherit_id', [])}")
        arch = view.get("arch", "")
        if "domain" in arch:
            print(f"   -> Has domain attribute")
        return view
    else:
        print("[!] Domain override view not found")
        return None

# ==============================================================================
# Test Payment Method Lines Directly
# ==============================================================================

def test_payment_method_lines_directly():
    """Test if we can see Cash/Credit/Check when querying directly."""
    print("\n[*] Testing payment method lines directly...")
    
    # Test 1: Get all for Bank journal
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
                "search_read",
                [[["journal_id.code", "=", "BNK1"]]],
                {
                    "fields": ["id", "name"],
                    "limit": 20
                }
            ]
        }
    }
    
    response1 = requests.post(ODOO_URL, json=payload1, timeout=10)
    result1 = response1.json().get("result", [])
    
    print(f"\n[OK] All payment method lines for Bank journal ({len(result1)} total):")
    for line in result1:
        print(f"   • ID: {line['id']}, Name: '{line['name']}'")
    
    # Test 2: With inbound filter
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
                [[
                    ["journal_id.code", "=", "BNK1"],
                    ["payment_method_id.payment_type", "=", "inbound"]
                ]],
                {
                    "fields": ["id", "name"],
                    "limit": 20
                }
            ]
        }
    }
    
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get("result", [])
    
    print(f"\n[OK] With inbound filter ({len(result2)} total):")
    for line in result2:
        print(f"   • ID: {line['id']}, Name: '{line['name']}'")
    
    cash_credit_check = [line for line in result2 if line['name'] in ['Cash', 'Credit', 'Check']]
    if cash_credit_check:
        print(f"\n[OK] Cash/Credit/Check found in query results!")
    else:
        print(f"\n[!] Cash/Credit/Check NOT in query results - this is the problem!")

# ==============================================================================
# Check Payment Method Line Active Status
# ==============================================================================

def check_payment_method_line_active():
    """Check if Cash/Credit/Check lines are active."""
    print("\n[*] Checking if payment method lines are active...")
    
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
                [[6, 7, 8]],  # Cash, Credit, Check
                {
                    "fields": ["id", "name", "active", "journal_id", "payment_method_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"\n[OK] Cash/Credit/Check lines:")
        for line in result:
            active = line.get("active", True)
            journal = line.get("journal_id", [])
            journal_name = journal[1] if isinstance(journal, list) and len(journal) > 1 else 'N/A'
            print(f"   • {line['name']} (ID: {line['id']}): Active={active}, Journal={journal_name}")
            if not active:
                print(f"     [!] This line is INACTIVE - that's why it's not showing!")

# ==============================================================================
# Try Different Approach: Check Wizard's Compute Method
# ==============================================================================

def check_wizard_compute_logic():
    """Check what the wizard's compute method does."""
    print("\n[*] Checking wizard compute logic...")
    
    print("[INFO] The wizard model (account.payment.register) has a compute method")
    print("       that determines available_payment_method_line_ids.")
    print("\n[INFO] This compute method likely checks:")
    print("       1. Journal compatibility")
    print("       2. Payment type (inbound/outbound)")
    print("       3. Currency compatibility")
    print("       4. Company compatibility")
    print("\n[INFO] If Cash/Credit/Check don't appear, the compute method may be")
    print("       filtering them out based on one of these criteria.")

# ==============================================================================
# Alternative: Rename Existing Methods
# ==============================================================================

def check_if_we_should_rename():
    """Check if we should rename existing methods instead."""
    print("\n[*] Alternative approach: Rename existing methods...")
    
    # Check what "Checks" (ID: 4) is
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
                [[4]],  # "Checks"
                {
                    "fields": ["id", "name", "journal_id", "payment_method_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        checks_line = result[0]
        print(f"\n[OK] 'Checks' line (ID: 4):")
        print(f"   Name: {checks_line.get('name', 'N/A')}")
        journal = checks_line.get("journal_id", [])
        journal_name = journal[1] if isinstance(journal, list) and len(journal) > 1 else 'N/A'
        print(f"   Journal: {journal_name}")
        print(f"\n   [!] Maybe we should rename 'Checks' to 'Check' and use that?")
        print(f"   Or rename 'Manual Payment' to 'Cash' or 'Credit'?")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("DEEP DIVE: Wizard Payment Method Filtering")
    print("="*70)
    
    # Check domain override
    override_view = check_domain_override()
    
    # Test directly
    test_payment_method_lines_directly()
    
    # Check active status
    check_payment_method_line_active()
    
    # Check compute logic
    check_wizard_compute_logic()
    
    # Alternative approach
    check_if_we_should_rename()
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("\nIf Cash/Credit/Check still don't appear after domain override,")
    print("the wizard's compute method may be filtering them out.")
    print("\nALTERNATIVE SOLUTION:")
    print("Instead of creating new payment method lines, we could:")
    print("1. Rename existing 'Checks' (ID: 4) to 'Check'")
    print("2. Rename 'Manual Payment' (ID: 1 or 3) to 'Cash' or 'Credit'")
    print("3. Create one more for the third option")
    print("\nThis way we use existing lines that the wizard already recognizes.")
    print("="*70)

