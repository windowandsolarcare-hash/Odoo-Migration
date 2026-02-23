"""
Create Payment from Invoice (Direct API)
=========================================
Bypass the wizard and create payment directly via API.
Usage: python create_payment.py <invoice_id> [amount] [check_number]
"""

import requests
import sys

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

def create_payment(invoice_id, amount=None, check_number=None):
    """Create payment for invoice."""
    # Get invoice
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.move", "read", [[invoice_id]],
                {"fields": ["id", "name", "amount_residual", "currency_id", "partner_id"]}
            ]
        }
    }
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    invoice = response.json()["result"][0]
    
    # Get Bank journal
    payload2 = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.journal", "search_read",
                [[["code", "=", "BNK1"]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    journal_id = response2.json()["result"][0]["id"]
    
    # Get Check payment method
    payload3 = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment.method.line", "search_read",
                [[["journal_id", "=", journal_id], ["name", "=", "Check"]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    response3 = requests.post(ODOO_URL, json=payload3, timeout=10)
    method_line_id = response3.json()["result"][0]["id"] if response3.json()["result"] else False
    
    # Create payment
    currency_id = invoice["currency_id"][0] if invoice.get("currency_id") else 1
    payment_amount = amount if amount else invoice["amount_residual"]
    
    payload4 = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment", "create",
                [{
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "partner_id": invoice["partner_id"][0],
                    "amount": payment_amount,
                    "currency_id": currency_id,
                    "journal_id": journal_id,
                    "payment_method_line_id": method_line_id,
                    "date": "2026-02-09",
                    "ref": invoice["name"],
                    "check_number": check_number if check_number else False
                }]
            ]
        }
    }
    response4 = requests.post(ODOO_URL, json=payload4, timeout=10)
    payment_id = response4.json().get("result")
    
    if payment_id:
        # Post payment
        payload5 = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    "account.payment", "action_post", [[payment_id]]
                ]
            }
        }
        requests.post(ODOO_URL, json=payload5, timeout=10)
        print(f"Payment created: {payment_id}")
        return payment_id
    
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_payment.py <invoice_id> [amount] [check_number]")
        sys.exit(1)
    
    invoice_id = int(sys.argv[1])
    amount = float(sys.argv[2]) if len(sys.argv) > 2 else None
    check_number = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_payment(invoice_id, amount, check_number)
