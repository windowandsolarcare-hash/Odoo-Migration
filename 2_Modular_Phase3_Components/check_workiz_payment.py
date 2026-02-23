import sys
sys.path.append('.')
import requests
from config import *
import json

job_uuid = 'IC3ZC9'
url = f'{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}'

response = requests.get(url, timeout=10)
result = response.json()

if result.get('flag'):
    job = result['data'][0]
    
    print(f"Workiz Job: {job_uuid}")
    print("="*70)
    print("\nLooking for payment date: 2/6/2026 at 9:09 PM")
    print("="*70)
    print("\nALL FIELDS:\n")
    
    # Print all fields sorted alphabetically
    for key in sorted(job.keys()):
        value = job[key]
        # Don't print huge arrays, just show count
        if isinstance(value, list) and key != 'Team':
            print(f"{key}: [{len(value)} items]")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*70)
    print("FIELDS WITH 'reference', 'payment', 'check', 'confirmation':")
    print("="*70)
    found_any = False
    for key in sorted(job.keys()):
        key_lower = key.lower()
        if any(term in key_lower for term in ['reference', 'payment', 'check', 'confirmation', 'receipt']):
            print(f"{key}: {job[key]}")
            found_any = True
    
    if not found_any:
        print("No fields found with those terms.")
else:
    print(f"Error: {result}")
