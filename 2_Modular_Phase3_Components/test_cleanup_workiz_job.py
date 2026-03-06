"""
Cleanup Test Job in Workiz
===========================
Usage: python test_cleanup_workiz_job.py <UUID>

Marks the test job as Cancelled and adds cleanup note.
(Workiz doesn't have a delete API, so we cancel instead)
"""

import requests
import sys

# Credentials
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

def cleanup_test_job(uuid):
    """Mark test job as Cancelled"""
    
    print(f"Cancelling test job: {uuid}")
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": uuid,
        "Status": "Cancelled",
        "JobNotes": "[TEST JOB - DELETED VIA API] Safe to permanently delete"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Test job {uuid} marked as Cancelled")
            print("✅ Added deletion note")
            print("\nJob is now safe to permanently delete in Workiz UI")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CLEANUP TEST JOB IN WORKIZ")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n❌ Error: UUID required")
        print("Usage: python test_cleanup_workiz_job.py <UUID>")
        sys.exit(1)
    
    uuid = sys.argv[1]
    cleanup_test_job(uuid)
