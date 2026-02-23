"""
Test Script: Phase 5 Auto-Scheduler
====================================
Tests both Maintenance and On Demand paths
"""
import sys
import codecs

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

sys.path.append('.')
import json

# Import Phase 5
from phase5_auto_scheduler import main as phase5_main

# Import supporting functions for verification
from functions.workiz.get_job_details import get_job_details
from functions.odoo.get_property_city import get_property_city


def test_5a_maintenance_path():
    """
    Test Path 5A: Maintenance auto-scheduling
    
    Uses real Workiz job with Maintenance service type
    """
    print("\n" + "="*70)
    print("TEST 5A: MAINTENANCE PATH")
    print("="*70)
    
    # Use IC3ZC9 (Blair Becker) - we know this is a real Done job
    test_job_uuid = 'IC3ZC9'
    
    print(f"\n[*] Getting Workiz job: {test_job_uuid}")
    workiz_job = get_job_details(test_job_uuid)
    
    if not workiz_job:
        print("[ERROR] Could not fetch Workiz job")
        return False
    
    # Verify it has the fields we need
    print(f"\n[*] Job Details:")
    print(f"    Customer: {workiz_job.get('FirstName')} {workiz_job.get('LastName')}")
    print(f"    Address: {workiz_job.get('Address')}, {workiz_job.get('City')}")
    print(f"    Type of Service: {workiz_job.get('type_of_service', 'N/A')}")
    print(f"    Frequency: {workiz_job.get('frequency', 'N/A')}")
    print(f"    Alternating: {workiz_job.get('alternating', 'N/A')}")
    
    # Override type_of_service to Maintenance for testing
    workiz_job['type_of_service'] = 'Maintenance'
    workiz_job['frequency'] = '4 Months'  # Set a test frequency
    
    # Test data for Phase 5
    test_input = {
        'workiz_job': workiz_job,
        'property_id': 24169,  # Blair Becker property
        'contact_id': 23621,   # Blair Becker contact
        'customer_city': 'Palm Springs'
    }
    
    print(f"\n[*] Calling Phase 5 with Maintenance path...")
    print(f"    Property ID: {test_input['property_id']}")
    print(f"    Contact ID: {test_input['contact_id']}")
    print(f"    City: {test_input['customer_city']}")
    
    # Call Phase 5
    result = phase5_main(test_input)
    
    print(f"\n[*] Phase 5 Result:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print("\n✅ TEST 5A PASSED: Maintenance path executed successfully")
        return True
    else:
        print(f"\n❌ TEST 5A FAILED: {result.get('error', 'Unknown error')}")
        return False


def test_5b_ondemand_path():
    """
    Test Path 5B: On Demand follow-up reminder
    
    Uses real Workiz job but overrides type to On Demand
    """
    print("\n" + "="*70)
    print("TEST 5B: ON DEMAND PATH")
    print("="*70)
    
    # Use same test job but mark as On Demand
    test_job_uuid = 'IC3ZC9'
    
    print(f"\n[*] Getting Workiz job: {test_job_uuid}")
    workiz_job = get_job_details(test_job_uuid)
    
    if not workiz_job:
        print("[ERROR] Could not fetch Workiz job")
        return False
    
    # Override type_of_service to On Demand for testing
    workiz_job['type_of_service'] = 'On Demand'
    
    print(f"\n[*] Job Details:")
    print(f"    Customer: {workiz_job.get('FirstName')} {workiz_job.get('LastName')}")
    print(f"    Type of Service: {workiz_job.get('type_of_service')}")
    
    # Test data for Phase 5
    test_input = {
        'workiz_job': workiz_job,
        'property_id': 24169,  # Not needed for On Demand but included
        'contact_id': 23621,   # Blair Becker contact
        'customer_city': ''    # Not needed for On Demand
    }
    
    print(f"\n[*] Calling Phase 5 with On Demand path...")
    print(f"    Contact ID: {test_input['contact_id']}")
    
    # Call Phase 5
    result = phase5_main(test_input)
    
    print(f"\n[*] Phase 5 Result:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print("\n✅ TEST 5B PASSED: On Demand path executed successfully")
        return True
    else:
        print(f"\n❌ TEST 5B FAILED: {result.get('error', 'Unknown error')}")
        return False


def test_date_calculation():
    """Test date calculation and city scheduling logic"""
    print("\n" + "="*70)
    print("TEST: DATE CALCULATION & CITY ROUTING")
    print("="*70)
    
    from functions.utils.calculate_next_service_date import calculate_next_service_date
    
    test_cases = [
        ("3 Months", "Palm Springs", "Monday"),
        ("4 Months", "Rancho Mirage", "Tuesday"),
        ("6 Months", "Palm Desert", "Wednesday"),
        ("3 Months", "Indian Wells", "Thursday"),
        ("4 Months", "Indio", "Friday"),
        ("3 Months", "Desert Hot Springs", "No preference")
    ]
    
    print("\n[*] Testing date calculation with city routing:")
    
    all_passed = True
    for frequency, city, expected_day in test_cases:
        print(f"\n    {frequency}, {city}:")
        scheduled_date = calculate_next_service_date(frequency, city)
        print(f"    => {scheduled_date}")
        
        # Could add day-of-week verification here
        # For now, just check it returns a date
        if scheduled_date and len(scheduled_date) > 0:
            print(f"    ✅ Generated date")
        else:
            print(f"    ❌ Failed to generate date")
            all_passed = False
    
    return all_passed


def test_line_items_logic():
    """Test line items retrieval and formatting"""
    print("\n" + "="*70)
    print("TEST: LINE ITEMS LOGIC")
    print("="*70)
    
    from functions.utils.get_line_items_for_next_job import (
        get_line_items_for_next_job,
        format_line_items_for_custom_field
    )
    
    # Get a real job
    test_job_uuid = 'IC3ZC9'
    print(f"\n[*] Testing with job: {test_job_uuid}")
    
    workiz_job = get_job_details(test_job_uuid)
    if not workiz_job:
        print("[ERROR] Could not fetch job")
        return False
    
    # Test regular service (not alternating)
    print("\n[*] Test 1: Regular service (not alternating)")
    workiz_job['alternating'] = ''
    
    line_items = get_line_items_for_next_job(workiz_job, 24169)
    print(f"    Found {len(line_items)} line items")
    
    formatted = format_line_items_for_custom_field(line_items)
    print(f"\n    Formatted for custom field:")
    print("    " + formatted.replace("\n", "\n    "))
    
    # Test alternating service
    print("\n[*] Test 2: Alternating service")
    workiz_job['alternating'] = 'Yes'
    
    line_items_alt = get_line_items_for_next_job(workiz_job, 24169)
    print(f"    Found {len(line_items_alt)} line items (from 2 jobs back)")
    
    if len(line_items) > 0 and len(formatted) > 0:
        print("\n✅ Line items logic working")
        return True
    else:
        print("\n❌ Line items logic failed")
        return False


def test_city_lookup():
    """Test getting city from Odoo property"""
    print("\n" + "="*70)
    print("TEST: CITY LOOKUP")
    print("="*70)
    
    test_property_id = 24169  # Blair Becker
    
    print(f"\n[*] Getting city for property {test_property_id}")
    city = get_property_city(test_property_id)
    
    print(f"    City: {city}")
    
    if city and len(city) > 0:
        print("\n✅ City lookup working")
        return True
    else:
        print("\n❌ City lookup failed")
        return False


# Main test runner
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 5 COMPREHENSIVE TESTS")
    print("="*70)
    
    results = {}
    
    # Run all tests
    print("\n[1/5] Testing date calculation...")
    results['date_calc'] = test_date_calculation()
    
    print("\n[2/5] Testing city lookup...")
    results['city_lookup'] = test_city_lookup()
    
    print("\n[3/5] Testing line items logic...")
    results['line_items'] = test_line_items_logic()
    
    # Ask before running actual Phase 5 calls
    print("\n" + "="*70)
    print("READY TO TEST PHASE 5 PATHS")
    print("="*70)
    print("\nThe following tests will:")
    print("- Path 5A: Attempt to CREATE a new job in Workiz")
    print("- Path 5B: Attempt to CREATE an activity in Odoo")
    print("\nThese are REAL API calls that will create records!")
    
    proceed = input("\nProceed with Phase 5 tests? (y/n): ").strip().lower()
    
    if proceed == 'y':
        print("\n[4/5] Testing Maintenance path (5A)...")
        results['path_5a'] = test_5a_maintenance_path()
        
        print("\n[5/5] Testing On Demand path (5B)...")
        results['path_5b'] = test_5b_ondemand_path()
    else:
        print("\n⊘ Skipped Phase 5 path tests")
        results['path_5a'] = None
        results['path_5b'] = None
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        if passed is None:
            status = "⊘ SKIPPED"
        elif passed:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Overall result
    skipped = sum(1 for v in results.values() if v is None)
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("="*70)
