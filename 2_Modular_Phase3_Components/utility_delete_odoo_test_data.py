"""
Utility Script: Delete Odoo Test Data (Sales Orders & Properties)
NOT for Workiz - this only deletes Odoo records!

Handles proper workflow: Cancel SO → Delete SO → Delete Property
"""

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
            print(f"[OK] Sales Order {so_id} cancelled")
            return True
        else:
            print(f"[ERROR] Failed to cancel SO: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception cancelling SO: {e}")
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
            print(f"[OK] Sales Order {so_id} deleted")
            return True
        else:
            print(f"[ERROR] Failed to delete SO: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception deleting SO: {e}")
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
            print(f"[OK] Property {property_id} deleted")
            return True
        else:
            print(f"[ERROR] Failed to delete property: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception deleting property: {e}")
        return False


def cleanup_test_data(sales_order_ids=None, property_ids=None):
    """
    Clean up test data with proper workflow.
    
    Args:
        sales_order_ids (list): List of sales order IDs to delete
        property_ids (list): List of property IDs to delete
    """
    if sales_order_ids:
        for so_id in sales_order_ids:
            print(f"\n[*] Processing Sales Order {so_id}...")
            if cancel_sales_order(so_id):
                delete_sales_order(so_id)
    
    if property_ids:
        for prop_id in property_ids:
            print(f"\n[*] Processing Property {prop_id}...")
            delete_property(prop_id)


if __name__ == "__main__":
    print("="*70)
    print("ODOO TEST DATA CLEANUP UTILITY (SALES ORDERS & PROPERTIES)")
    print("="*70)
    
    # Example: Customize these for your test
    test_sales_orders = [15779, 15780]  # Path A and Path B test SOs
    test_properties = []  # Only delete if no SO references
    
    cleanup_test_data(
        sales_order_ids=test_sales_orders,
        property_ids=test_properties
    )
    
    print("\n" + "="*70)
    print("CLEANUP COMPLETE")
    print("="*70)
