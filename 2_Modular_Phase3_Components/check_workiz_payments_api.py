import sys
sys.path.append('.')
import requests
from config import *

job_uuid = 'IC3ZC9'

# Try different payment endpoints
endpoints = [
    f'{WORKIZ_BASE_URL}/payment/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}',
    f'{WORKIZ_BASE_URL}/payments/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}',
    f'{WORKIZ_BASE_URL}/job/{job_uuid}/payments/?auth_secret={WORKIZ_AUTH_SECRET}',
    f'{WORKIZ_BASE_URL}/invoice/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}',
]

for endpoint in endpoints:
    print(f"\nTrying: {endpoint.replace(WORKIZ_API_TOKEN, 'TOKEN').replace(WORKIZ_AUTH_SECRET, 'SECRET')}")
    print("="*70)
    try:
        response = requests.get(endpoint, timeout=10)
        result = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {result}")
        if result.get('flag') or result.get('status') == 'success':
            print("\n✅ SUCCESS! This endpoint works!")
            break
    except Exception as e:
        print(f"Error: {e}")
