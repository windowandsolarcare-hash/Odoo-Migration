"""
Create Payment Method Lines for Cash, Credit, Check
====================================================
Creates 3 payment method lines linked to Bank journal.
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
# Get Required IDs
# ==============================================================================

def get_manual_payment_method_id():
    """Get the Manual Payment method ID."""
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
                [[["code", "=", "manual"], ["payment_type", "=", "inbound"]]],
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
        method_id = result[0]["id"]
        print(f"[OK] Found Manual Payment method: ID {method_id}")
        return method_id
    else:
        print("[!] Manual Payment method not found")
        return None

def get_bank_journal_id():
    """Get the Bank journal ID."""
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
                    "fields": ["id", "name"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        journal_id = result[0]["id"]
        print(f"[OK] Found Bank journal: ID {journal_id}")
        return journal_id
    else:
        print("[!] Bank journal not found")
        return None

# ==============================================================================
# Check if Payment Method Lines Already Exist
# ==============================================================================

def check_existing_lines():
    """Check if Cash, Credit, Check lines already exist."""
    print("\n[*] Checking for existing payment method lines...")
    
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
                [[["name", "in", ["Cash", "Credit", "Check"]]]],
                {
                    "fields": ["id", "name"],
                    "limit": 10
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        print(f"[!] Found {len(result)} existing lines:")
        for line in result:
            print(f"   • {line['name']} (ID: {line['id']})")
        return [line['name'] for line in result]
    else:
        print("[OK] No existing Cash/Credit/Check lines found")
        return []

# ==============================================================================
# Create Payment Method Lines
# ==============================================================================

def create_payment_method_line(name, payment_method_id, journal_id):
    """Create a payment method line."""
    print(f"\n[*] Creating payment method line: {name}...")
    
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
                "create",
                [{
                    "name": name,
                    "payment_method_id": payment_method_id,
                    "journal_id": journal_id
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Created {name} (ID: {result})")
        return result
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to create {name}: {error}")
        return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CREATE: Payment Method Lines (Cash, Credit, Check)")
    print("="*70)
    
    # Check for existing lines
    existing = check_existing_lines()
    
    # Get required IDs
    payment_method_id = get_manual_payment_method_id()
    journal_id = get_bank_journal_id()
    
    if not payment_method_id or not journal_id:
        print("\n[!] Cannot proceed - missing required IDs")
        exit(1)
    
    # Create lines that don't exist
    lines_to_create = {
        "Cash": "cash",
        "Credit": "credit", 
        "Check": "check"
    }
    
    created = []
    for name, workiz_type in lines_to_create.items():
        if name not in existing:
            line_id = create_payment_method_line(name, payment_method_id, journal_id)
            if line_id:
                created.append((name, line_id, workiz_type))
        else:
            print(f"\n[*] Skipping {name} - already exists")
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    if created:
        print(f"\n[OK] Created {len(created)} payment method lines:")
        for name, line_id, workiz_type in created:
            print(f"   • {name} (ID: {line_id}) -> Workiz: '{workiz_type}'")
    else:
        print("\n[OK] All payment method lines already exist")
    print("\n[OK] These will now appear in the payment form dropdown")
    print("="*70)

