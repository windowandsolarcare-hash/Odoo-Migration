"""Delete Odoo Sales Order and Property for clean Path B test
NOT for Workiz - this only deletes Odoo records!"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import *
import requests

def cancel_sales_order(so_id):
    """Cancel a sales order in Odoo (required before delete)"""
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
                "action_cancel",
                [[so_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not False:
            print(f"[OK] Sales Order {so_id} cancelled successfully")
            return True
        else:
            print(f"[ERROR] Failed to cancel sales order: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception cancelling sales order: {e}")
        return False


def delete_sales_order(so_id):
    """Delete a sales order from Odoo (must be cancelled first)"""
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
                "unlink",
                [[so_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Sales Order {so_id} deleted successfully")
            return True
        else:
            print(f"[ERROR] Failed to delete sales order: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception deleting sales order: {e}")
        return False


def delete_property(property_id):
    """Delete a property record from Odoo"""
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
                "res.partner",
                "unlink",
                [[property_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Property {property_id} deleted successfully")
            return True
        else:
            print(f"[ERROR] Failed to delete property: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception deleting property: {e}")
        return False


if __name__ == "__main__":
    print("Step 1: Cancelling sales order 15780...")
    if cancel_sales_order(15780):
        print("\nStep 2: Deleting sales order 15780...")
        delete_sales_order(15780)
    
    print("\nStep 3: Deleting property 26325 (123456 Main St)...")
    delete_property(26325)
