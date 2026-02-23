"""
Create Custom Payment Wizard
============================
Create a transient model wizard that:
1. Collects payment method, check number, amount, date
2. Creates payment
3. Posts it automatically
All in one step after clicking "Create Payment"
"""

import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# Create Custom Wizard Model
# ==============================================================================

def create_wizard_model():
    """Create a transient model for the payment wizard."""
    print("\n[*] Creating custom payment wizard model...")
    
    # Create transient model
    model_code = """from odoo import models, fields, api

class CollectPaymentWizard(models.TransientModel):
    _name = 'collect.payment.wizard'
    _description = 'Collect Payment Wizard'
    
    invoice_id = fields.Many2one('account.move', required=True)
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method', required=True)
    check_number = fields.Char(string='Check Number')
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True)
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'invoice_id' in self._context:
            invoice = self.env['account.move'].browse(self._context['invoice_id'])
            res['invoice_id'] = invoice.id
            res['amount'] = invoice.amount_residual
            res['currency_id'] = invoice.currency_id.id or invoice.company_id.currency_id.id
        return res
    
    def action_create_and_post_payment(self):
        self.ensure_one()
        # Get Bank journal
        journal = self.env['account.journal'].search([('code', '=', 'BNK1')], limit=1)
        if not journal:
            raise UserError("Bank journal not found")
        
        # Create payment
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.invoice_id.partner_id.id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'journal_id': journal.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'check_number': self.check_number if self.payment_method_line_id.name == 'Check' else False,
            'payment_date': self.payment_date,
            'memo': self.invoice_id.name,
            'invoice_ids': [(6, 0, [self.invoice_id.id])],
        })
        
        # Post the payment
        payment.action_post()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Payment Created',
                'message': f'Payment {payment.name} created and posted successfully.',
                'type': 'success',
                'sticky': False,
            }
        }"""
    
    # Actually, we can't create Python models via API easily
    # We'd need to create it as a custom module
    
    print("[!] Cannot create Python models via API")
    print("    Would need to create as custom module")
    print("\n    ALTERNATIVE: Use existing approach with 'Post Payment' action")
    return None

# ==============================================================================
# Alternative: Modify Server Action to Create Then Auto-Post
# ==============================================================================

def create_improved_action():
    """Create improved action that opens form, then we'll add auto-post button."""
    print("\n[*] Since we can't create custom wizard easily, let's improve")
    print("    the existing approach by adding a button to payment form")
    print("    that creates and posts in one click.")
    
    # Actually, the best we can do via API is:
    # 1. Open payment form (done)
    # 2. Add a server action to post (done)
    # 3. User workflow: Fill form → Create → Click "Post Payment" action
    
    # But user wants it fully automated after Create
    # We'd need to modify the payment form view to add a button
    # that does both create and post, OR use a custom wizard
    
    print("\n[INFO] Best solution: Create a custom module with wizard")
    print("       OR use the current approach (form + Post Payment action)")
    print("       OR modify payment form to add 'Create & Post' button")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CREATE: Custom Payment Wizard")
    print("="*70)
    
    wizard = create_wizard_model()
    
    if not wizard:
        create_improved_action()
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("\nFor full automation (form → auto-post), we need a custom wizard.")
    print("This requires creating a Python module, which is more complex.")
    print("\nCURRENT SOLUTION (2 clicks):")
    print("1. Invoice → Actions → Collect Payment")
    print("2. Fill form → Create")
    print("3. Payment form → Actions → Post Payment")
    print("4. Done")
    print("\nWould you like me to:")
    print("A) Keep current solution (form + separate Post action)")
    print("B) Create custom wizard module (requires more setup)")
    print("="*70)

