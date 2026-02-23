# ==============================================================================
# DIAGNOSTIC: Test Gate Code & Pricing Snapshot Fields in Odoo
# ==============================================================================
# Purpose: Verify correct field names and test write operations
# Created: 2026-02-05
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

# Test Sales Order ID (Bev Hartin's SO #15737)
TEST_SO_ID = 15737

# ==============================================================================
# STEP 1: SEARCH FOR GATE/PRICING FIELDS IN SALE.ORDER MODEL
# ==============================================================================

def search_fields_in_model(model_name, search_term):
    """Search for fields containing a specific term in their name."""
    print(f"\n[*] Searching for '{search_term}' fields in {model_name}...")
    
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
                "ir.model.fields",
                "search_read",
                [[
                    ["model", "=", model_name],
                    ["name", "ilike", search_term]
                ]],
                {"fields": ["name", "field_description", "ttype"], "limit": 10}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result"):
            print(f"[OK] Found {len(result['result'])} matching fields:")
            for field in result["result"]:
                print(f"   • {field['name']} ({field['ttype']}) - \"{field['field_description']}\"")
            return result["result"]
        else:
            print(f"[!] No fields found")
            return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []


# ==============================================================================
# STEP 2: READ EXISTING SALES ORDER TO SEE CURRENT VALUES
# ==============================================================================

def read_sales_order_fields(so_id, field_names):
    """Read specific fields from a sales order."""
    print(f"\n[*] Reading SO #{so_id} fields: {field_names}")
    
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
                "read",
                [[so_id]],
                {"fields": field_names}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            print(f"[OK] Current values:")
            for field_name in field_names:
                value = result["result"][0].get(field_name, "FIELD NOT FOUND")
                print(f"   {field_name}: '{value}'")
            return result["result"][0]
        else:
            print(f"[!] Could not read SO")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# ==============================================================================
# STEP 3: TEST WRITE TO FIELDS
# ==============================================================================

def test_write_to_so(so_id, field_name, test_value):
    """Test writing to a specific field."""
    print(f"\n[*] Testing write to '{field_name}' with value '{test_value}'...")
    
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
                [[so_id], {field_name: test_value}]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") == True:
            print(f"[OK] Write successful!")
            
            # Read back to verify
            verify_payload = {
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
                        "read",
                        [[so_id]],
                        {"fields": [field_name]}
                    ]
                }
            }
            
            verify_response = requests.post(ODOO_URL, json=verify_payload, timeout=10)
            verify_result = verify_response.json()
            
            if verify_result.get("result"):
                actual_value = verify_result["result"][0].get(field_name)
                print(f"[✓] Verified: '{actual_value}'")
                return True
            else:
                print(f"[!] Could not verify write")
                return False
        else:
            error = result.get("error", {})
            print(f"[ERROR] Write failed: {error}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


# ==============================================================================
# MAIN DIAGNOSTIC
# ==============================================================================

if __name__ == "__main__":
    
    print("="*70)
    print("ODOO SALES ORDER FIELD DIAGNOSTIC")
    print("="*70)
    
    # STEP 1: Search for gate and pricing fields
    print("\n" + "="*70)
    print("STEP 1: SEARCHING FOR GATE FIELDS")
    print("="*70)
    gate_fields = search_fields_in_model("sale.order", "gate")
    
    print("\n" + "="*70)
    print("STEP 1: SEARCHING FOR PRICING FIELDS")
    print("="*70)
    pricing_fields = search_fields_in_model("sale.order", "pricing")
    
    # STEP 2: Identify the most likely candidates
    print("\n" + "="*70)
    print("STEP 2: FIELD CANDIDATES IDENTIFIED")
    print("="*70)
    
    gate_candidates = [f['name'] for f in gate_fields if 'snapshot' in f['name'].lower()]
    pricing_candidates = [f['name'] for f in pricing_fields if 'snapshot' in f['name'].lower()]
    
    print(f"\nGate Snapshot candidates: {gate_candidates}")
    print(f"Pricing Snapshot candidates: {pricing_candidates}")
    
    if not gate_candidates:
        print("\n[!] No gate snapshot fields found - using fallback")
        gate_candidates = ['x_studio_gate_snapshot']
    
    if not pricing_candidates:
        print("\n[!] No pricing snapshot fields found - using fallback")
        pricing_candidates = ['x_studio_x_studio_pricing_snapshot']
    
    # STEP 3: Read current values
    print("\n" + "="*70)
    print("STEP 3: READING CURRENT VALUES FROM TEST SO")
    print("="*70)
    
    all_test_fields = gate_candidates + pricing_candidates
    current_values = read_sales_order_fields(TEST_SO_ID, all_test_fields)
    
    # STEP 4: Test writes
    print("\n" + "="*70)
    print("STEP 4: TESTING WRITE OPERATIONS")
    print("="*70)
    
    for field in gate_candidates:
        success = test_write_to_so(TEST_SO_ID, field, "TEST GATE CODE 123")
        if success:
            print(f"[OK] {field} is WRITABLE")
        else:
            print(f"[ERROR] {field} is NOT writable or doesn't exist")
    
    for field in pricing_candidates:
        success = test_write_to_so(TEST_SO_ID, field, "TEST PRICING NOTE $299")
        if success:
            print(f"[OK] {field} is WRITABLE")
        else:
            print(f"[ERROR] {field} is NOT writable or doesn't exist")
    
    # SUMMARY
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Check Odoo UI to see if test values appear in SO #15737")
    print("2. Update phase3e script with correct field names")
    print("3. Re-run Phase 3E test")
    print("="*70)
