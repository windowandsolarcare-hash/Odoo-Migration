"""Update sales order date_order field (Job/Schedule Date)"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def update_sales_order_date(sales_order_id, date_order):
    """
    Update sales order date_order field (Job/Schedule Date).
    IMPORTANT: Must be called AFTER confirming the sales order (Odoo overwrites during confirm).
    
    Args:
        sales_order_id (int): Odoo sales order ID
        date_order (str): Date/time in format "YYYY-MM-DD HH:MM:SS" (UTC)
    
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
                "write",
                [[sales_order_id], {"date_order": date_order}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            return {'success': True}
        else:
            return {'success': False, 'message': result.get('error', {}).get('message', 'Unknown error')}
    except Exception as e:
        return {'success': False, 'message': str(e)}
