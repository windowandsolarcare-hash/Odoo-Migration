import sys
sys.path.append('.')
import requests
from config import *

job_uuid = 'MOIPF9'
url = f'{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}'

response = requests.get(url, timeout=10)
result = response.json()

if result.get('flag'):
    job = result['data'][0]
    
    print(f"Workiz Job: {job_uuid}")
    print("="*70)
    print(f"Status: {job.get('Status')}")
    print(f"SubStatus: {job.get('SubStatus')}")
    print(f"LastStatusUpdate: {job.get('LastStatusUpdate')}")
    print(f"JobDateTime: {job.get('JobDateTime')}")
    print(f"JobTotalPrice: {job.get('JobTotalPrice')}")
    print(f"JobAmountDue: {job.get('JobAmountDue')}")
    print(f"CreatedDate: {job.get('CreatedDate')}")
    print(f"\nCustomer: {job.get('FirstName')} {job.get('LastName')}")
    print(f"Address: {job.get('Address')}")
else:
    print(f"Error: {result}")
