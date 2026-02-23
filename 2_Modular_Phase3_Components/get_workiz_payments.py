import sys
sys.path.append('.')
import requests
from config import *

job_uuid = 'IC3ZC9'

# Try to get payments for the job
endpoints = [
    f'{WORKIZ_BASE_URL}/job/getPayments/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}',
    f'{WORKIZ_BASE_URL}/job/payments/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}',
    f'{WORKIZ_BASE_URL}/job/{job_uuid}/payments/?auth_secret={WORKIZ_AUTH_SECRET}',
]

for endpoint in endpoints:
    print(f"\nTrying: {endpoint.replace(WORKIZ_API_TOKEN, 'TOKEN').replace(WORKIZ_AUTH_SECRET, 'SECRET')}")
    print("="*70)
    try:
        response = requests.get(endpoint, timeout=10)
        result = response.json()
        print(f"Status Code: {response.status_code}")
        
        if result.get('flag') or result.get('status') == 'success':
            print("✅ SUCCESS! Payment data found:")
            print(f"Response: {result}")
            
            if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                print("\n" + "="*70)
                print("PAYMENT DETAILS:")
                print("="*70)
                for payment in result['data']:
                    for key, value in payment.items():
                        print(f"{key}: {value}")
            break
        else:
            print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*70)
print("If no endpoint worked, the payment data might only be accessible")
print("through the job details or a Zapier webhook trigger.")
