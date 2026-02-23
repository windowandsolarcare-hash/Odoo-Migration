"""
Update Post Payment to Auto-Apply
==================================
Update Post Payment action to automatically apply payment to invoice after posting.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Update Post Payment Action
# ==============================================================================

def update_post_payment_action():
    """Update Post Payment action to auto-apply after posting."""
    print("\n[*] Updating Post Payment action to auto-apply...")
    
    code = """# Post payment and automatically apply to invoice
for payment in records:
    # Post the payment if in draft
    if payment.state == 'draft':
        payment.action_post()
    elif payment.state != 'posted':
        # Try to post anyway
        payment.action_post()
    
    # Now apply/reconcile with invoice
    if payment.invoice_ids and payment.move_id:
        # Get invoice receivable lines (positive balance)
        invoice_lines = []
        for invoice in payment.invoice_ids:
            lines = invoice.line_ids.filtered(
                lambda l: l.account_id.internal_type == 'receivable'
                and l.balance > 0
                and not l.reconciled
            )
            invoice_lines.extend(lines)
        
        # Get payment receivable lines (negative balance)
        payment_lines = payment.move_id.line_ids.filtered(
            lambda l: l.account_id.internal_type == 'receivable'
            and l.balance < 0
            and not l.reconciled
        )
        
        # Reconcile
        if invoice_lines and payment_lines:
            (invoice_lines + payment_lines).reconcile()

# Show success
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Posted & Applied',
        'message': 'Payment has been posted and applied to invoice. Amount due should now be $0.00.',
        'type': 'success',
        'sticky': False,
    }
}"""
    
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
                "write",
                [[675], {  # Post Payment action
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Updated Post Payment action to auto-apply")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("UPDATE: Post Payment to Auto-Apply")
    print("="*70)
    
    updated = update_post_payment_action()
    
    if updated:
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print("\nThe 'Post Payment' action has been updated.")
        print("It will now:")
        print("1. Post the payment (creates move and move lines)")
        print("2. Automatically apply/reconcile with invoice")
        print("3. Invoice should show as paid with $0.00 due")
        print("\nHOW TO USE:")
        print("1. Create payment (via Collect Payment or standard Pay button)")
        print("2. Fill in payment details")
        print("3. Click Actions → Post Payment")
        print("4. Payment is posted AND applied to invoice automatically")
        print("\nALTERNATIVE:")
        print("If Post Payment doesn't work, use:")
        print("Actions → Apply Payment to Invoice (ID: 677)")
        print("="*70)
    else:
        print("\n[!] Update failed - use 'Apply Payment to Invoice' action (ID: 677) manually")

