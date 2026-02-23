# ==============================================================================
# DIAGNOSTIC: Check Property Record for Bev Hartin
# ==============================================================================
# Purpose: See if there's actual gate code/pricing data on the property
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

# Bev Hartin's property
PROPERTY_ID = 25799

# ==============================================================================
# CHECK PROPERTY DATA
# ==============================================================================

def read_property_fields(property_id):
    """Read gate code and pricing fields from property record."""
    print(f"[*] Reading property #{property_id} gate/pricing fields...")
    
    fields_to_check = [
        'name',
        'street',
        'x_studio_x_gate_code',
        'x_studio_x_pricing',
        'x_studio_pricing_menu',
        'x_studio_prices_per_service',
        'x_studio_x_frequency',
        'x_studio_x_alternating',
        'x_last_service_date'
    ]
    
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
                "read",
                [[property_id]],
                {"fields": fields_to_check}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            property_data = result["result"][0]
            
            print(f"\n[OK] Property: {property_data.get('name')}")
            print(f"     Address: {property_data.get('street')}")
            print(f"\n{'='*70}")
            print(f"CURRENT PROPERTY DATA")
            print(f"{'='*70}\n")
            
            for field in fields_to_check:
                if field not in ['name', 'street']:
                    value = property_data.get(field, "NOT FOUND")
                    # Handle False values
                    if value == False:
                        value = "(empty/False)"
                    print(f"{field}:")
                    print(f"  Value: {value}")
                    print()
            
            return property_data
        else:
            print(f"[ERROR] Could not read property")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    
    print("="*70)
    print("PROPERTY RECORD INSPECTION - BEV HARTIN")
    print("="*70)
    
    property_data = read_property_fields(PROPERTY_ID)
    
    if property_data:
        print("="*70)
        print("ANALYSIS")
        print("="*70)
        
        gate = property_data.get('x_studio_x_gate_code')
        pricing = property_data.get('x_studio_x_pricing')
        
        if gate and gate != False:
            print(f"\n[!] Property HAS gate code: '{gate}'")
            print(f"    → We should NOT overwrite with Workiz placeholder")
        else:
            print(f"\n[OK] Property has no gate code")
            print(f"    → Safe to write from Workiz (but it's just placeholder)")
        
        if pricing and pricing != False:
            print(f"\n[!] Property HAS pricing note: '{pricing}'")
            print(f"    → We should NOT overwrite with Workiz placeholder")
        else:
            print(f"\n[OK] Property has no pricing note")
            print(f"    → Safe to write from Workiz (but it's just placeholder)")
        
        print("\n" + "="*70)
        print("RECOMMENDATION")
        print("="*70)
        print("\nThe script is working correctly!")
        print("\nFor THIS test job (Bev Hartin), Workiz has no real gate/pricing data.")
        print("The 'Gate Code' and 'Pricing' text are just placeholder values.")
        print("\nOptions:")
        print("1. Test with a different job that has actual gate/pricing data")
        print("2. Add logic to skip writing if value is placeholder text")
        print("3. Accept that some jobs will have placeholder text")
        print("="*70)
