"""
Create Test Job in Workiz for Testing Phase 3
==============================================
Usage: python test_create_workiz_job.py

Creates a test job in Workiz, returns the UUID for testing.
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Credentials
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

def create_test_job():
    """Create a test job in Workiz"""
    
    # Use test data - you'll need to provide a real ClientId
    test_data = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": "YOUR_TEST_CLIENT_ID",  # ⚠️ Replace with actual test customer
        "FirstName": "TEST",
        "LastName": "Customer",
        "Phone": "555-0100",
        "Address": "999 Test Drive",
        "City": "Palm Springs",
        "State": "CA",
        "PostalCode": "92262",
        "JobDateTime": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 10:00:00"),
        "JobType": "Windows Inside & Outside Plus Screens",
        "JobSource": "API Test",
        "Status": "Scheduled",
        "JobNotes": "[TEST JOB - SAFE TO DELETE] Created by automation test"
    }
    
    print("Creating test job in Workiz...")
    url = f"{WORKIZ_BASE_URL}/job/create/"
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"✅ Test job created (HTTP {response.status_code})")
            
            # Workiz returns 204 No Content, so we need to fetch the UUID
            print("Fetching job UUID...")
            time.sleep(2)  # Wait for job to be indexed
            
            uuid = fetch_latest_test_job()
            if uuid:
                print(f"✅ Job UUID: {uuid}")
                print(f"\nTo test Phase 3:")
                print(f"1. Check Zapier dashboard for new job trigger")
                print(f"2. Verify SO created in Odoo with UUID: {uuid}")
                print(f"\nTo cleanup:")
                print(f"python test_cleanup_workiz_job.py {uuid}")
                return uuid
            else:
                print("❌ Could not fetch UUID. Check Workiz manually.")
                return None
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fetch_latest_test_job():
    """Fetch the most recent test job UUID"""
    
    url = f"{WORKIZ_BASE_URL}/job/all/?auth_secret={WORKIZ_AUTH_SECRET}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json().get('data', [])
            
            # Find the test job we just created
            for job in jobs[:5]:  # Check recent jobs
                if "[TEST JOB" in str(job.get('JobNotes', '')):
                    return job.get('UUID')
            
            # If not found by notes, return most recent
            if jobs:
                return jobs[0].get('UUID')
                
        return None
        
    except Exception as e:
        print(f"Error fetching UUID: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("CREATE TEST JOB IN WORKIZ")
    print("=" * 60)
    
    # Check if ClientId is set
    if "YOUR_TEST_CLIENT_ID" in open(__file__).read():
        print("\n⚠️  WARNING: You need to set a real ClientId first!")
        print("1. Find a test customer in Workiz")
        print("2. Edit this file and replace YOUR_TEST_CLIENT_ID")
        print("3. Run again")
    else:
        create_test_job()
