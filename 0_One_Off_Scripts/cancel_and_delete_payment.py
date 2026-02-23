"""
Cancel and Delete Payment
==========================
A posted/paid payment cannot be deleted directly.
Need to cancel/unpost it first, then delete.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Payment State
# ==============================================================================

def check_payment_state(payment_id):
    """Check the current state of a payment."""
    print(f"\n[*] Checking payment {payment_id} state...")
    
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
                "read",
                [[payment_id]],
                {
                    "fields": ["id", "name", "state", "amount", "payment_type", "partner_type"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        payment = result[0]
        print(f"\n[OK] Payment details:")
        print(f"   ID: {payment['id']}")
        print(f"   Name: {payment.get('name', 'N/A')}")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Amount: ${payment.get('amount', 0)}")
        print(f"   Payment Type: {payment.get('payment_type', 'N/A')}")
        print(f"   Partner Type: {payment.get('partner_type', 'N/A')}")
        return payment
    else:
        print("[!] Payment not found")
        return None

# ==============================================================================
# Cancel/Unpost Payment
# ==============================================================================

def cancel_payment(payment_id):
    """Cancel/unpost a payment."""
    print(f"\n[*] Cancelling payment {payment_id}...")
    
    # First try action_draft (unpost)
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
                "action_draft",
                [[payment_id]]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Payment unposted (moved to draft)")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to unpost: {error}")
        
        # Try action_cancel instead
        print(f"\n[*] Trying action_cancel instead...")
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
                    "account.payment",
                    "action_cancel",
                    [[payment_id]]
                ]
            }
        }
        
        response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
        result2 = response2.json().get("result")
        
        if result2:
            print(f"[OK] Payment cancelled")
            return True
        else:
            error2 = response2.json().get("error", {})
            print(f"[!] Failed to cancel: {error2}")
            return False

# ==============================================================================
# Delete Payment
# ==============================================================================

def delete_payment(payment_id):
    """Delete a payment (must be in draft or cancelled state)."""
    print(f"\n[*] Deleting payment {payment_id}...")
    
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
                "unlink",
                [[payment_id]]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Payment deleted")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed to delete: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CANCEL & DELETE: Payment")
    print("="*70)
    
    # Payment ID from screenshot (PBNK1/2026/00001)
    # Let's find it by name
    print("\n[*] Finding payment PBNK1/2026/00001...")
    
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
                [[["name", "=", "PBNK1/2026/00001"]]],
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
        payment_id = result[0]["id"]
        payment_state = result[0].get("state", "unknown")
        
        print(f"[OK] Found payment: ID {payment_id}, State: {payment_state}")
        
        # Check state
        payment = check_payment_state(payment_id)
        
        if payment:
            state = payment.get("state", "")
            
            if state == "posted" or state == "paid":
                print(f"\n[*] Payment is in '{state}' state - need to cancel first")
                
                # Cancel it
                if cancel_payment(payment_id):
                    # Verify it's now draft
                    payment_after = check_payment_state(payment_id)
                    if payment_after and payment_after.get("state") == "draft":
                        # Now delete
                        if delete_payment(payment_id):
                            print(f"\n[OK] Payment successfully deleted!")
                        else:
                            print(f"\n[!] Payment cancelled but could not be deleted")
                            print(f"    You can delete it manually in Odoo UI")
                    else:
                        print(f"\n[!] Payment may still be posted - check manually")
                else:
                    print(f"\n[!] Could not cancel payment - may need to do it manually")
                    print(f"    In Odoo UI: Click 'Reset to Draft' button, then delete")
            elif state == "draft":
                print(f"\n[*] Payment is already in draft - can delete directly")
                if delete_payment(payment_id):
                    print(f"\n[OK] Payment successfully deleted!")
                else:
                    print(f"\n[!] Could not delete - check error above")
            else:
                print(f"\n[*] Payment is in '{state}' state")
                print(f"    Try deleting manually in Odoo UI")
    else:
        print("[!] Payment not found")
        print("\n[INFO] To delete a payment manually in Odoo:")
        print("1. Open the payment")
        print("2. If state is 'Paid' or 'Posted', click 'Reset to Draft' button")
        print("3. Once in 'Draft' state, click 'Delete' button")
    
    print("\n" + "="*70)
    print("MANUAL STEPS (if script doesn't work):")
    print("="*70)
    print("1. Open payment in Odoo")
    print("2. If state is 'Paid' or 'Posted', click 'Reset to Draft'")
    print("3. Once in 'Draft', click 'Delete' button")
    print("="*70)

