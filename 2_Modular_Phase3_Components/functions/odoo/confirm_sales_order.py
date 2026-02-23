"""Confirm sales order (Quotation -> Sales Order)"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def confirm_sales_order(sales_order_id):
    """
    Confirm sales order (Quotation -> Sales Order).
    
    Args:
        sales_order_id (int): Odoo sales order ID
    
    Returns:
        dict: {'success': bool, 'message': str (optional)}
    """
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
                "sale.order",
                "action_confirm",
                [[sales_order_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not None:
            return {'success': True}
        else:
            error = result.get("error", {})
            return {'success': False, 'message': f"Error: {error.get('message', 'Unknown')}"}
    except Exception as e:
        return {'success': False, 'message': f"Exception: {str(e)}"}
