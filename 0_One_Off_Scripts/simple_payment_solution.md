# Simple Payment Solution

## The Problem
The payment wizard has too many issues (currency disappearing, amount not editable, check number missing, etc.)

## Simple Solution: Use Standard Odoo Payment Form

Instead of the wizard, create the payment directly:

1. **Go to:** Accounting > Payments > Create
2. **Fill in:**
   - Payment Type: **Receive** (inbound)
   - Partner: Select customer
   - Amount: Enter amount
   - Currency: USD
   - Journal: Bank
   - Payment Method: Check (or Cash/Credit)
   - Date: Today
   - Check Number: Enter if paying by check
   - Memo: Optional reference

3. **Click:** Create
4. **Then:** Go back to invoice and register this payment

## Alternative: Python Script

I created a script: `0_One_Off_Scripts/create_payment_direct.py`

Usage:
```bash
python create_payment_direct.py <invoice_id> [amount] [check_number]
```

Example:
```bash
python create_payment_direct.py 2 65.00 1234
```

This creates and posts the payment automatically.

## Recommendation

For now, use the standard payment form (Accounting > Payments > Create) until we can properly fix the wizard or create a better server action.

