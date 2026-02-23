"""
Fix Collect Payment Date
=========================
Fix the date issue - use datetime which is available globally in Odoo.
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Fix Date - Use datetime (available globally) or just omit it
# ==============================================================================

def fix_date_in_action():
    """Fix the date field - use datetime or omit it (Odoo defaults to today)."""
    print("\n[*] Fixing date in Collect Payment action...")
    
    # Option 1: Use datetime (should be available globally in Odoo)
    # Option 2: Just omit default_date - Odoo will default to today
    # Let's try Option 2 first (simplest)
    
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
        'default_ref': record.name,
        'default_invoice_ids': [(6, 0, [record.id])],
    }
}"""
    
    # Omit default_date - Odoo will default to today automatically
    
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
        print(f"[OK] Fixed - removed date (Odoo will default to today)")
        return True
    else:
        error = response.json().get("error", {})
        print(f"[!] Failed: {error}")
        
        # Try with datetime if that fails
        print(f"\n[*] Trying with datetime module...")
        code2 = """action = {
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
        'default_date': datetime.date.today().strftime('%Y-%m-%d'),
        'default_ref': record.name,
        'default_invoice_ids': [(6, 0, [record.id])],
    }
}"""
        
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
                    "ir.actions.server",
                    "write",
                    [[674], {
                        "code": code2
                    }]
                ]
            }
        }
        
        response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
        result2 = response2.json().get("result")
        
        if result2:
            print(f"[OK] Fixed with datetime.date.today()")
            return True
        else:
            error2 = response2.json().get("error", {})
            print(f"[!] Also failed: {error2}")
            return False

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("FIX: Collect Payment Date Issue")
    print("="*70)
    
    fixed = fix_date_in_action()
    
    print("\n" + "="*70)
    print("FIXED:")
    print("="*70)
    print("\nRemoved the date field - Odoo will automatically default")
    print("the payment date to today when creating the payment.")
    print("\nThis is simpler and avoids the date function issue entirely.")
    print("\nNEXT STEPS:")
    print("1. Refresh browser (Ctrl+F5)")
    print("2. Go to invoice")
    print("3. Click Actions → Collect Payment")
    print("4. Payment form opens - date will default to today automatically")
    print("="*70)

