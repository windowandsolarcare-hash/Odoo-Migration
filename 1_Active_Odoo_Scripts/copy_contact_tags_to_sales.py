"""
Copy all Contact Tags (res.partner.category) to Sales Order Tags (crm.tag)
This creates matching tags in the sales order system for all existing contact tags.
"""

import requests

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

def get_all_contact_tags():
    """Get all contact tags from res.partner.category"""
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
                "res.partner.category",
                "search_read",
                [[]],
                {"fields": ["id", "name"], "limit": 1000}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    return result.get("result", [])


def check_sales_tag_exists(tag_name):
    """Check if a sales order tag already exists"""
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
                "crm.tag",
                "search_read",
                [[["name", "=", tag_name]]],
                {"fields": ["id", "name"], "limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result") and len(result["result"]) > 0:
        return result["result"][0]["id"]
    return None


def create_sales_tag(tag_name):
    """Create a new sales order tag"""
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
                "crm.tag",
                "create",
                [{"name": tag_name}]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result"):
        return result["result"]
    return None


def main():
    print("="*70)
    print("COPY CONTACT TAGS TO SALES ORDER TAGS")
    print("="*70)
    
    # Get all contact tags
    print("\n[*] Fetching all contact tags...")
    contact_tags = get_all_contact_tags()
    print(f"[OK] Found {len(contact_tags)} contact tags")
    
    if not contact_tags:
        print("[!] No contact tags found. Nothing to do.")
        return
    
    # Process each tag
    print("\n[*] Processing tags...\n")
    created_count = 0
    existing_count = 0
    error_count = 0
    
    for tag in contact_tags:
        tag_name = tag["name"]
        print(f"   {tag_name}...", end=" ")
        
        # Check if it already exists in sales tags
        existing_id = check_sales_tag_exists(tag_name)
        
        if existing_id:
            print(f"Already exists (ID: {existing_id})")
            existing_count += 1
        else:
            # Create new sales tag
            new_id = create_sales_tag(tag_name)
            if new_id:
                print(f"Created (ID: {new_id})")
                created_count += 1
            else:
                print("ERROR creating tag")
                error_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total contact tags:     {len(contact_tags)}")
    print(f"Already existed:        {existing_count}")
    print(f"Newly created:          {created_count}")
    print(f"Errors:                 {error_count}")
    print("\n[OK] Done!")


if __name__ == "__main__":
    main()
