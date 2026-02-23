# ==============================================================================
# ODOO UTILITY FUNCTIONS
# Reusable, tested, debugged functions for Odoo API integrations
# ==============================================================================
# Created: 2026-02-03
# Purpose: Centralized library of Odoo API functions to avoid code duplication
#          and ensure bug fixes propagate to all scripts using these functions.
# ==============================================================================

import requests
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# CONTACT FUNCTIONS
# ==============================================================================

def search_odoo_contact_by_address(street_address):
    """
    Search for Odoo contact by street address.
    
    Args:
        street_address (str): Street address to search for
        
    Returns:
        dict: Contact record with id, name, phone, email, street, city
        None: If no contact found
        
    TESTED: 2026-02-03 - Working with special characters in address
    NOTES: Filters by x_studio_record_category = "Contact" to exclude properties
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
                "res.partner",
                "search_read",
                [[["street", "=", street_address], ["x_studio_record_category", "=", "Contact"]]],
                {"fields": ["id", "name", "phone", "email", "street", "city"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]
        return None
    except Exception as e:
        print(f"Error searching Odoo contact: {e}")
        return None


def update_contact_field(contact_id, field_name, field_value):
    """
    Update a single field on an Odoo contact.
    
    Args:
        contact_id (int): Odoo contact ID
        field_name (str): Technical field name (e.g., 'x_studio_last_reactivation_sent')
        field_value: Value to set (string, int, date, etc.)
        
    Returns:
        bool: True if successful, False otherwise
        
    TESTED: 2026-02-03 - Working for date fields
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
                "res.partner",
                "write",
                [[contact_id], {field_name: field_value}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        return result.get("result") == True
    except Exception as e:
        print(f"Error updating contact field: {e}")
        return False

# ==============================================================================
# OPPORTUNITY FUNCTIONS
# ==============================================================================

def find_opportunity_by_contact(contact_id, stage_id=5):
    """
    Find active opportunity for a contact by stage.
    
    Args:
        contact_id (int): Odoo contact ID
        stage_id (int): Stage ID to filter by (default: 5 = Reactivation)
        
    Returns:
        dict: Opportunity record with id, name, x_workiz_graveyard_uuid
        None: If no opportunity found
        
    TESTED: 2026-02-03 - Correctly handles multiple opportunities
    NOTES: Returns most recent opportunity (sorted by create_date desc)
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
                "crm.lead",
                "search_read",
                [[["partner_id", "=", contact_id], ["stage_id", "=", stage_id]]],
                {"fields": ["id", "name", "x_workiz_graveyard_uuid", "x_historical_workiz_uuid"], 
                 "order": "create_date desc", "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            return result["result"][0]
        return None
    except Exception as e:
        print(f"Error finding opportunity: {e}")
        return None


def mark_opportunity_won(opportunity_id):
    """
    Mark an Odoo opportunity as Won using the action_set_won method.
    
    Args:
        opportunity_id (int): Odoo opportunity ID
        
    Returns:
        bool: True if successful, False otherwise
        
    TESTED: 2026-02-03
    NOTES: Uses action_set_won (not simple write) to trigger Odoo reporting logic
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
                "crm.lead",
                "action_set_won",
                [[opportunity_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        return result.get("result") is not None
    except Exception as e:
        print(f"Error marking opportunity won: {e}")
        return False

# ==============================================================================
# SALES ORDER FUNCTIONS
# ==============================================================================

def create_sales_order(contact_id, line_items, order_date=None):
    """
    Create an Odoo sales order.
    
    Args:
        contact_id (int): Odoo contact ID
        line_items (list): List of dicts with 'product_id', 'quantity', 'price_unit'
        order_date (str): Optional order date (YYYY-MM-DD format)
        
    Returns:
        dict: Created sales order with id
        None: If creation failed
        
    TESTED: Not yet tested - placeholder
    TODO: Add full implementation for Phase 3
    """
    # Placeholder - to be implemented when we build Phase 3
    pass

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def format_odoo_domain(filters):
    """
    Helper to format Odoo search domains correctly.
    
    Args:
        filters (list): List of filter tuples [('field', 'operator', 'value')]
        
    Returns:
        list: Properly formatted domain for Odoo API
        
    NOTES: Odoo requires double-wrapped list for JSON-RPC
    """
    return [[list(f) for f in filters]]

# ==============================================================================
# END OF UTILITY FUNCTIONS
# ==============================================================================
