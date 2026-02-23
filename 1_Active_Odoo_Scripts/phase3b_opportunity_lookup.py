# ==============================================================================
# PHASE 3B: OPPORTUNITY LOOKUP BY GRAVEYARD UUID
# ==============================================================================
# Purpose: Find the active opportunity with graveyard UUID for the contact
# Created: 2026-02-05
# Status: Development - Ready for testing with Bev Hartin
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
# PHASE 3B FUNCTION
# ==============================================================================

def find_opportunity_by_contact(contact_id):
    """
    Find active opportunity with graveyard UUID for a contact.
    
    Args:
        contact_id (int): Odoo contact ID (res.partner)
        
    Returns:
        dict: Opportunity record with id, name, x_workiz_graveyard_uuid, etc.
        None: If no opportunity found
        
    TESTED: 2026-02-05 - Testing with Bev Hartin contact ID 23629
    NOTES: 
    - Searches for opportunities where x_workiz_graveyard_uuid is populated
    - Does NOT filter by stage_id (works across all campaigns)
    - Returns most recent opportunity (order by create_date desc)
    - Assumes customer is responding to latest campaign
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
                [
                    [
                        ["partner_id", "=", contact_id],
                        ["x_workiz_graveyard_uuid", "!=", False],
                        ["x_workiz_graveyard_uuid", "!=", ""]
                    ]
                ],
                {
                    "fields": [
                        "id",
                        "name",
                        "partner_id",
                        "stage_id",
                        "x_workiz_graveyard_uuid",
                        "x_workiz_graveyard_link",
                        "x_historical_workiz_uuid",
                        "x_odoo_contact_id",
                        "expected_revenue",
                        "create_date"
                    ],
                    "order": "create_date desc",
                    "limit": 1
                }
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            opportunity = result["result"][0]
            print(f"[OK] Opportunity found: {opportunity['name']} (ID: {opportunity['id']})")
            print(f"   Graveyard UUID: {opportunity['x_workiz_graveyard_uuid']}")
            return opportunity
        else:
            print(f"[ERROR] No opportunity with graveyard UUID found for contact ID: {contact_id}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error searching opportunity: {e}")
        return None


def process_phase3b(contact):
    """
    Phase 3B handler: Find opportunity for the contact from Phase 3A.
    
    Args:
        contact (dict): Contact record from Phase 3A
        
    Returns:
        dict: {
            'success': bool,
            'opportunity': dict or None,
            'contact': dict,
            'message': str
        }
    """
    
    print("\n" + "="*70)
    print("PHASE 3B: OPPORTUNITY LOOKUP")
    print("="*70)
    print(f"Contact ID: {contact['id']}")
    print(f"Contact Name: {contact['name']}")
    print("="*70 + "\n")
    
    # Search for opportunity
    opportunity = find_opportunity_by_contact(contact['id'])
    
    if opportunity:
        return {
            'success': True,
            'opportunity': opportunity,
            'contact': contact,
            'message': f"Opportunity found: {opportunity['name']} (ID: {opportunity['id']})"
        }
    else:
        return {
            'success': False,
            'opportunity': None,
            'contact': contact,
            'message': f"No opportunity with graveyard UUID found for {contact['name']}"
        }


# ==============================================================================
# INTEGRATION: PHASE 3A + 3B
# ==============================================================================

def phase3a_and_3b_combined(calendly_data):
    """
    Combined Phase 3A + 3B test: From Calendly booking to Opportunity.
    
    Args:
        calendly_data (dict): Calendly webhook payload
        
    Returns:
        dict: Combined results from both phases
    """
    from phase3a_contact_lookup import process_calendly_webhook
    
    print("\n" + "🚀 "*35)
    print("TESTING PHASE 3A + 3B INTEGRATION")
    print("🚀 "*35 + "\n")
    
    # Phase 3A: Find contact
    phase3a_result = process_calendly_webhook(calendly_data)
    
    if not phase3a_result['success']:
        print("\n[ERROR] Phase 3A failed - cannot proceed to Phase 3B")
        return phase3a_result
    
    # Phase 3B: Find opportunity
    phase3b_result = process_phase3b(phase3a_result['contact'])
    
    # Combine results
    combined_result = {
        'success': phase3b_result['success'],
        'contact': phase3a_result['contact'],
        'opportunity': phase3b_result['opportunity'],
        'booking_info': phase3a_result['booking_info'],
        'message': phase3b_result['message']
    }
    
    return combined_result


# ==============================================================================
# TEST WITH BEV HARTIN DATA
# ==============================================================================

if __name__ == "__main__":
    
    # Test 1: Direct opportunity lookup with known contact ID
    print("\n" + "🧪 "*35)
    print("TEST 1: Direct Opportunity Lookup (Phase 3B Only)")
    print("🧪 "*35 + "\n")
    
    test_contact = {
        'id': 23629,
        'name': 'Bev Hartin',
        'email': 'xxxxxxOdoo@gmail.com',
        'phone': '+1 951-972-6946',
        'street': '29 Toscana Way E',
        'city': 'Rancho Mirage'
    }
    
    result = process_phase3b(test_contact)
    
    print("\n" + "="*70)
    print("PHASE 3B RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['opportunity']:
        opp = result['opportunity']
        print(f"\nOpportunity Details:")
        print(f"  ID: {opp['id']}")
        print(f"  Name: {opp['name']}")
        print(f"  Stage: {opp['stage_id']}")
        print(f"  Expected Revenue: ${opp['expected_revenue']}")
        print(f"  Graveyard UUID: {opp['x_workiz_graveyard_uuid']}")
        print(f"  Graveyard Link: {opp.get('x_workiz_graveyard_link', 'N/A')}")
        print(f"  Historical UUID: {opp.get('x_historical_workiz_uuid', 'N/A')}")
        print(f"  Created: {opp['create_date']}")
    
    print("="*70 + "\n")
    
    # Test 2: Combined Phase 3A + 3B
    print("\n" + "🧪 "*35)
    print("TEST 2: Combined Phase 3A + 3B (Full Integration)")
    print("🧪 "*35 + "\n")
    
    test_calendly_data = {
        'Name': 'Bev Hartin',
        'Email': 'dansyourrealtor@gmail.com',
        'Service Address': '29 Toscana Way E',
        'Service Type': 'Windows Inside & Outside Plus Screens',
        'Additional Notes': 'Test',
        'Event Type': 'Rancho Mirage Service',
        'Booking Time': '2026-03-12T15:30:00.000000Z',
        'Timezone': 'America/Los_Angeles',
        'Status': 'active'
    }
    
    combined_result = phase3a_and_3b_combined(test_calendly_data)
    
    print("\n" + "="*70)
    print("COMBINED PHASE 3A + 3B RESULT:")
    print("="*70)
    print(f"Success: {combined_result['success']}")
    print(f"Message: {combined_result['message']}")
    
    if combined_result['success']:
        print(f"\n[OK] COMPLETE DATA FOR PHASE 3C:")
        print(f"   Contact ID: {combined_result['contact']['id']}")
        print(f"   Contact Name: {combined_result['contact']['name']}")
        print(f"   Opportunity ID: {combined_result['opportunity']['id']}")
        print(f"   Graveyard UUID: {combined_result['opportunity']['x_workiz_graveyard_uuid']}")
        print(f"   Booking Time: {combined_result['booking_info']['booking_time']}")
        print(f"\n🎯 Ready for Phase 3C: Update Workiz job {combined_result['opportunity']['x_workiz_graveyard_uuid']}")
    
    print("="*70 + "\n")
