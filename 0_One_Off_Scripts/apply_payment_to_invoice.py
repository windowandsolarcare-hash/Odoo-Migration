"""
Apply Payment to Invoice
========================
The payment is posted but not applied to the invoice.
Need to reconcile the payment move lines with the invoice move lines.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Check Current Payment Status
# ==============================================================================

def check_payment_status():
    """Check the most recent payment and its invoice link."""
    print("\n[*] Checking most recent payment...")
    
    # Get most recent payment
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
                [[["name", "=", "PAY00010"]]],
                {
                    "fields": ["id", "name", "state", "move_id", "invoice_ids", "amount", "partner_id"]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    payment_result = response.json().get("result", [])
    
    if payment_result:
        payment = payment_result[0]
        print(f"\n[OK] Payment {payment.get('name')} (ID: {payment.get('id')}):")
        print(f"   State: {payment.get('state', 'N/A')}")
        print(f"   Move ID: {payment.get('move_id', [None])[0] if payment.get('move_id') else None}")
        print(f"   Invoice IDs: {payment.get('invoice_ids', [])}")
        print(f"   Amount: ${payment.get('amount', 0):.2f}")
        
        move_id = payment.get('move_id', [None])[0] if payment.get('move_id') else None
        invoice_ids = payment.get('invoice_ids', [])
        
        if move_id and invoice_ids:
            return payment.get('id'), move_id, invoice_ids[0]
    
    return None, None, None

# ==============================================================================
# Reconcile Payment with Invoice
# ==============================================================================

def reconcile_payment_invoice(payment_id, move_id, invoice_id):
    """Reconcile the payment move lines with invoice move lines."""
    print(f"\n[*] Reconciling payment {payment_id} with invoice {invoice_id}...")
    
    # Get invoice receivable line (positive balance)
    payload_invoice_lines = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "account.move.line",
                "search_read",
                [[["move_id", "=", invoice_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", ">", 0]]],
                {
                    "fields": ["id", "name", "balance", "account_id"]
                }
            ]
        }
    }
    
    response_invoice = requests.post(ODOO_URL, json=payload_invoice_lines, timeout=10)
    invoice_lines = response_invoice.json().get("result", [])
    
    print(f"\n[INFO] Invoice receivable lines: {len(invoice_lines)}")
    for line in invoice_lines:
        print(f"   Line {line.get('id')}: Balance ${line.get('balance', 0):.2f}")
    
    # Get payment move receivable line (negative balance)
    payload_payment_lines = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "account.move.line",
                "search_read",
                [[["move_id", "=", move_id], ["account_id.internal_type", "=", "receivable"], ["reconciled", "=", False], ["balance", "<", 0]]],
                {
                    "fields": ["id", "name", "balance", "account_id"]
                }
            ]
        }
    }
    
    response_payment = requests.post(ODOO_URL, json=payload_payment_lines, timeout=10)
    payment_lines = response_payment.json().get("result", [])
    
    print(f"\n[INFO] Payment receivable lines: {len(payment_lines)}")
    for line in payment_lines:
        print(f"   Line {line.get('id')}: Balance ${line.get('balance', 0):.2f}")
    
    # Reconcile if we have matching lines
    if invoice_lines and payment_lines:
        line_ids = [line.get('id') for line in invoice_lines + payment_lines]
        
        print(f"\n[*] Reconciling {len(line_ids)} lines...")
        
        payload_reconcile = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB,
                    ODOO_USER_ID,
                    ODOO_API_KEY,
                    "account.move.line",
                    "reconcile",
                    [line_ids]
                ]
            }
        }
        
        response_reconcile = requests.post(ODOO_URL, json=payload_reconcile, timeout=10)
        result_reconcile = response_reconcile.json().get("result")
        
        if result_reconcile:
            print(f"[OK] Reconciliation successful!")
            return True
        else:
            error = response_reconcile.json().get("error", {})
            print(f"[!] Reconciliation failed: {error}")
            return False
    else:
        print(f"\n[!] Cannot reconcile - missing lines")
        if not invoice_lines:
            print(f"    No invoice receivable lines found")
        if not payment_lines:
            print(f"    No payment receivable lines found")
        return False

# ==============================================================================
# Create Server Action to Apply Payment
# ==============================================================================

def create_apply_payment_action():
    """Create a server action that applies payment to invoice."""
    print("\n[*] Creating 'Apply Payment to Invoice' action...")
    
    # Get account.payment model ID
    payload_model = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "ir.model",
                "search_read",
                [[["model", "=", "account.payment"]]],
                {
                    "fields": ["id", "model"],
                    "limit": 1
                }
            ]
        }
    }
    
    response_model = requests.post(ODOO_URL, json=payload_model, timeout=10)
    model_result = response_model.json().get("result", [])
    
    if model_result:
        model_id = model_result[0]["id"]
        
        # Create action that reconciles payment with invoice
        code = """# Apply payment to invoice (reconcile)
for payment in records:
    if not payment.invoice_ids:
        raise UserError("Payment must be linked to an invoice")
    
    if not payment.move_id:
        raise UserError("Payment must be posted first (has no move)")
    
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
    else:
        raise UserError("Cannot reconcile - missing move lines")

# Show success
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Payment Applied',
        'message': 'Payment has been applied to invoice. Amount due should now be $0.00.',
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
                    "create",
                    [{
                        "name": "Apply Payment to Invoice",
                        "model_id": model_id,
                        "binding_model_id": model_id,
                        "binding_view_types": "form",
                        "state": "code",
                        "code": code
                    }]
                ]
            }
        }
        
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json().get("result")
        
        if result:
            print(f"[OK] Created 'Apply Payment to Invoice' action (ID: {result})")
            print(f"     This will appear in Actions menu on payment form")
            return result
        else:
            error = response.json().get("error", {})
            print(f"[!] Failed: {error}")
            return None
    
    return None

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("APPLY PAYMENT TO INVOICE")
    print("="*70)
    
    # Check current status
    payment_id, move_id, invoice_id = check_payment_status()
    
    if payment_id and move_id and invoice_id:
        # Try to reconcile
        reconciled = reconcile_payment_invoice(payment_id, move_id, invoice_id)
        
        if reconciled:
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print("\nPayment has been applied to invoice.")
            print("Invoice should now show as paid with $0.00 due.")
            print("\nPlease refresh the invoice page to see the update.")
        else:
            print("\n[!] Automatic reconciliation failed")
            print("    Creating server action for manual application...")
            action_id = create_apply_payment_action()
            
            if action_id:
                print("\n" + "="*70)
                print("ACTION CREATED")
                print("="*70)
                print("\nI've created an 'Apply Payment to Invoice' action.")
                print("To use it:")
                print("1. Go to the payment (PAY00010)")
                print("2. Click Actions menu")
                print("3. Select 'Apply Payment to Invoice'")
                print("4. This will reconcile the payment with the invoice")
                print("5. Invoice should then show as paid")
    else:
        print("\n[!] Could not find payment or invoice")
        print("    Creating server action anyway for future use...")
        action_id = create_apply_payment_action()
    
    print("="*70)

