# ==============================================================================
# DIAGNOSTIC: Inspect Workiz Job Data to Find Gate Code & Pricing Fields
# ==============================================================================
# Purpose: Examine all fields returned by Workiz API for job SG6AMX
# Created: 2026-02-05
# ==============================================================================

import requests
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================

WORKIZ_API_BASE = "https://api.workiz.com/api/v1"
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"

# Test job (Bev Hartin)
TEST_JOB_UUID = "SG6AMX"

# ==============================================================================
# WORKIZ DATA INSPECTION
# ==============================================================================

def get_workiz_job_full_dump(job_uuid):
    """Get complete job details from Workiz and dump ALL fields."""
    url = f"{WORKIZ_API_BASE}/{WORKIZ_API_TOKEN}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    print(f"[*] Fetching Workiz job: {job_uuid}")
    print(f"[*] URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            response_json = response.json()
            job_data = response_json.get('data', {})
            
            if isinstance(job_data, list) and len(job_data) > 0:
                job_data = job_data[0]
            
            print(f"[OK] Job data retrieved")
            return job_data
        else:
            print(f"[ERROR] Workiz API error: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error fetching Workiz job: {e}")
        return None


def analyze_job_fields(job_data, search_terms):
    """Analyze job data and highlight fields matching search terms."""
    print(f"\n{'='*70}")
    print(f"ANALYZING {len(job_data)} WORKIZ FIELDS")
    print(f"{'='*70}\n")
    
    # Group fields by whether they match search terms
    matching_fields = {}
    other_fields = {}
    
    for key, value in job_data.items():
        # Check if key matches any search term
        matches = [term for term in search_terms if term.lower() in key.lower()]
        
        if matches:
            matching_fields[key] = value
        else:
            other_fields[key] = value
    
    # Print matching fields first
    if matching_fields:
        print(f"{'='*70}")
        print(f"FIELDS MATCHING SEARCH TERMS: {search_terms}")
        print(f"{'='*70}\n")
        
        for key in sorted(matching_fields.keys()):
            value = matching_fields[key]
            value_str = str(value)[:200] if value else "(empty)"
            print(f"[MATCH] {key}:")
            print(f"        Type: {type(value).__name__}")
            print(f"        Value: {value_str}")
            print()
    
    # Print all other fields
    print(f"{'='*70}")
    print(f"ALL OTHER FIELDS ({len(other_fields)})")
    print(f"{'='*70}\n")
    
    for key in sorted(other_fields.keys()):
        value = other_fields[key]
        
        # Truncate long values
        if isinstance(value, str):
            value_preview = value[:100] + "..." if len(value) > 100 else value
        elif isinstance(value, (list, dict)):
            value_preview = json.dumps(value, indent=2)[:150] + "..." if len(str(value)) > 150 else json.dumps(value, indent=2)
        else:
            value_preview = str(value)
        
        print(f"{key}:")
        print(f"  Type: {type(value).__name__}")
        print(f"  Value: {value_preview}")
        print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    
    print("="*70)
    print("WORKIZ JOB FIELD INSPECTION")
    print("="*70)
    
    # Get job data
    job_data = get_workiz_job_full_dump(TEST_JOB_UUID)
    
    if not job_data:
        print("[ERROR] Could not retrieve job data")
        exit(1)
    
    # Search for fields related to gate, pricing, notes, etc.
    search_terms = ['gate', 'pricing', 'price', 'note', 'comment', 'information', 'remember', 'custom']
    
    # Analyze all fields
    analyze_job_fields(job_data, search_terms)
    
    # Summary
    print("="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nKey findings:")
    print("- Look for fields with actual gate code data (not just 'Gate Code' text)")
    print("- Look for fields with actual pricing notes (not just 'Pricing' text)")
    print("- Custom fields often have 'information_to_remember' or 'cf_' prefix")
    print("="*70)
