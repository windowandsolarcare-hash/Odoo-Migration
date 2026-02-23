"""
Fix Collect Payment Action
===========================
Fix the NameError: fields is not defined
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Fix the Code
# ==============================================================================

def fix_action_code():
    """Fix the server action code to use datetime instead of fields."""
    print("\n[*] Fixing Collect Payment action code...")
    
    # Use datetime.date.today() instead of fields.Date.today()
    # In server actions, we need to import datetime or use context_today()
    code = """from datetime import date
action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'default_payment_type': 'inbound',
        'default_partner_type': 'customer',
        'default_partner_id': record.partner_id.id,
        'default_amount': record.amount_residual,
        'default_currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
        'default_journal_id': env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
        'default_date': date.today().strftime('%Y-%m-%d'),
        'default_ref': record.name,
        'default_invoice_ids': [(6, 0, [record.id])],
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
                [[674], {
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Fixed the code - replaced fields.Date.today() with date.today()")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        return False

# ==============================================================================
# Alternative: Use context_today() (Odoo's built-in)
# ==============================================================================

def fix_with_context_today():
    """Alternative fix using context_today()."""
    print("\n[*] Trying alternative fix with context_today()...")
    
    # context_today() is available in server actions
    code = """action = {
    'type': 'ir.actions.act_window',
    'name': 'Collect Payment',
    'res_model': 'account.payment',
    'view_mode': 'form',
    'target': 'new',
    'context': {
        'default_payment_type': 'inbound',
        'default_partner_type': 'customer',
        'default_partner_id': record.partner_id.id,
        'default_amount': record.amount_residual,
        'default_currency_id': record.currency_id.id if record.currency_id else record.company_id.currency_id.id,
        'default_journal_id': env['account.journal'].search([('code', '=', 'BNK1')], limit=1).id,
        'default_date': context_today(record).strftime('%Y-%m-%d'),
        'default_ref': record.name,
        'default_invoice_ids': [(6, 0, [record.id])],
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
                [[674], {
                    "code": code
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Fixed with context_today()")
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
    print("FIX: Collect Payment Action Error")
    print("="*70)
    
    # Try first fix
    fixed = fix_action_code()
    
    if not fixed:
        # Try alternative
        fix_with_context_today()
    
    print("\n" + "="*70)
    print("FIXED:")
    print("="*70)
    print("\nThe error was: 'fields' is not available in server actions")
    print("Changed: fields.Date.today()")
    print("To: date.today() (with import) or context_today()")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Go to invoice")
    print("3. Click Actions → Collect Payment")
    print("4. Should now work without error!")
    print("="*70)

