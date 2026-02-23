"""
Test Script: Search for Workiz ClientId (1533) in Odoo Contact and Property records
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import *
import requests
import json

def get_all_contact_fields(contact_id):
    """Fetch ALL fields from a Contact record"""
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
                [[["id", "=", contact_id]]],
                {"limit": 1}  # No fields filter = get ALL fields
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result") and len(result["result"]) > 0:
        return result["result"][0]
    return None


def get_all_property_fields(property_id):
    """Fetch ALL fields from a Property record"""
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
                [[["id", "=", property_id]]],
                {"limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    if result.get("result") and len(result["result"]) > 0:
        return result["result"][0]
    return None


def search_for_client_id_in_record(record, client_id_to_find, record_type):
    """Search for ClientId (1533) in all fields of a record"""
    print(f"\n{'='*70}")
    print(f"SEARCHING {record_type} FOR WORKIZ CLIENT ID: {client_id_to_find}")
    print('='*70)
    
    found_fields = []
    
    for field_name, field_value in record.items():
        # Convert value to string for searching
        value_str = str(field_value)
        
        # Check if ClientId appears in the value
        if str(client_id_to_find) in value_str:
            found_fields.append({
                'field': field_name,
                'value': field_value
            })
    
    if found_fields:
        print(f"\n[OK] FOUND ClientId '{client_id_to_find}' in {len(found_fields)} field(s):")
        for item in found_fields:
            print(f"\n  Field: {item['field']}")
            print(f"  Value: {item['value']}")
    else:
        print(f"\n[NOT FOUND] ClientId '{client_id_to_find}' NOT FOUND in any field")
    
    return found_fields


def print_key_fields(record, record_type):
    """Print important fields from the record"""
    print(f"\n{'='*70}")
    print(f"KEY FIELDS - {record_type}")
    print('='*70)
    
    key_fields = [
        'id',
        'name',
        'external_id',
        '__last_update',
        'display_name',
        'x_studio_x_studio_record_category',
        'street',
        'phone',
        'email',
        'parent_id',
        'child_ids',
        'x_studio_x_studio_location_id'
    ]
    
    for field in key_fields:
        if field in record:
            print(f"  {field}: {record[field]}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST: SEARCH FOR WORKIZ CLIENT ID IN ODOO RECORDS")
    print("="*70)
    print(f"Contact: Bev Hartin (ID: 23629)")
    print(f"Property: 29 Toscana Way E (ID: 25799)")
    print(f"Workiz ClientId: 1533")
    
    # Test data
    contact_id = 23629
    property_id = 25799
    workiz_client_id = 1533
    
    # Fetch Contact data
    print(f"\n[*] Fetching Contact ID {contact_id}...")
    contact = get_all_contact_fields(contact_id)
    
    if contact:
        print(f"[OK] Contact fetched: {contact.get('name')}")
        print(f"[*] Total fields in Contact: {len(contact)}")
        
        # Print key fields
        print_key_fields(contact, "CONTACT")
        
        # Search for ClientId
        contact_matches = search_for_client_id_in_record(contact, workiz_client_id, "CONTACT")
    else:
        print(f"[ERROR] Could not fetch Contact {contact_id}")
    
    # Fetch Property data
    print(f"\n\n[*] Fetching Property ID {property_id}...")
    property_record = get_all_property_fields(property_id)
    
    if property_record:
        print(f"[OK] Property fetched: {property_record.get('street')}")
        print(f"[*] Total fields in Property: {len(property_record)}")
        
        # Print key fields
        print_key_fields(property_record, "PROPERTY")
        
        # Search for ClientId
        property_matches = search_for_client_id_in_record(property_record, workiz_client_id, "PROPERTY")
    else:
        print(f"[ERROR] Could not fetch Property {property_id}")
    
    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if contact:
        if contact_matches:
            print(f"[OK] Contact: ClientId FOUND in {len(contact_matches)} field(s)")
        else:
            print(f"[NOT FOUND] Contact: ClientId NOT FOUND")
    
    if property_record:
        if property_matches:
            print(f"[OK] Property: ClientId FOUND in {len(property_matches)} field(s)")
        else:
            print(f"[NOT FOUND] Property: ClientId NOT FOUND")
    
    print("="*70)
