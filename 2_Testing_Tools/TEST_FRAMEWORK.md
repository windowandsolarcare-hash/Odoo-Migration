# Testing Framework - Automated Test Data Creation & Cleanup
**Last Updated:** 2026-03-05  
**Author:** DJ Sanders  
**Purpose:** Create/delete test data in Workiz/Odoo for testing Zapier phases

---

## 🎯 Testing Workflow

```
1. Make code changes locally
   ↓
2. Push to GitHub main (gh api)
   ↓
3. Claude creates test data via API
   ↓
4. Test triggers Zapier (webhook or manual)
   ↓
5. Verify results in Odoo/Workiz
   ↓
6. Claude deletes test data via API
   ↓
7. Confirm cleanup complete
```

---

## 🧪 Test Data Creation Scripts

### Test Phase 3: New Job → Sales Order

**Create Test Job in Workiz:**
```python
import requests
import json
from datetime import datetime, timedelta

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

def create_test_job():
    """Create a test job in Workiz that will trigger Phase 3"""
    
    # Use existing test customer (find one in Workiz first)
    test_data = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "ClientId": "12345",  # Replace with actual test customer ID
        "FirstName": "Test",
        "LastName": "Customer",
        "Phone": "555-0100",
        "Address": "123 Test Street",
        "City": "Palm Springs",
        "State": "CA",
        "PostalCode": "92262",
        "JobDateTime": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "JobType": "Windows Inside & Outside Plus Screens",
        "JobSource": "API Test",
        "Status": "Scheduled"  # Will trigger Phase 3
    }
    
    url = f"{WORKIZ_BASE_URL}/job/create/"
    response = requests.post(url, json=test_data, timeout=10)
    
    if response.status_code in [200, 204]:
        print("✅ Test job created")
        # Note: Workiz doesn't return UUID on create (HTTP 204)
        # Need to fetch it via GET /job/all/
        return fetch_latest_job_uuid()
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

def fetch_latest_job_uuid():
    """Fetch the most recently created job to get its UUID"""
    url = f"{WORKIZ_BASE_URL}/job/all/?auth_secret={WORKIZ_AUTH_SECRET}"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        jobs = response.json().get('data', [])
        if jobs:
            latest = jobs[0]  # Most recent job
            return latest.get('UUID')
    return None

def delete_test_job(uuid):
    """Delete test job from Workiz"""
    # Workiz doesn't have a delete endpoint, so we:
    # 1. Cancel the job (set status to "Cancelled")
    # 2. Or keep it but add "TEST - DELETE" to notes
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": uuid,
        "Status": "Cancelled",
        "JobNotes": "[TEST JOB - SAFE TO DELETE]"
    }
    
    response = requests.post(url, json=payload, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ Test job {uuid} marked for deletion")
        return True
    else:
        print(f"❌ Failed to mark job: {response.text}")
        return False

# Usage:
# test_uuid = create_test_job()
# # ... run test ...
# delete_test_job(test_uuid)
```

---

### Test Phase 4: Status Update → SO Update

**Trigger Status Change:**
```python
def trigger_phase4_test(job_uuid):
    """Update job status to trigger Phase 4"""
    
    url = f"{WORKIZ_BASE_URL}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "Status": "In Progress",  # Change to trigger Phase 4
        "SubStatus": "Tech En Route"
    }
    
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status update: {response.status_code}")
    return response.status_code == 200
```

---

### Test Phase 5: Auto Scheduling

**Mark Job Done to Trigger Phase 5:**
```python
def trigger_phase5_test(job_uuid):
    """Mark job Done to trigger Phase 6 → Phase 5 flow"""
    
    # First, add a payment in Odoo (this triggers Phase 6)
    # Phase 6 marks job Done in Workiz
    # Done status triggers Phase 5
    
    # OR manually mark Done:
    url = f"{WORKIZ_BASE_URL}/job/update/"
    payload = {
        "auth_secret": WORKIZ_AUTH_SECRET,
        "UUID": job_uuid,
        "Status": "Done"
    }
    
    response = requests.post(url, json=payload, timeout=10)
    return response.status_code == 200
```

---

### Test Phase 6: Payment Sync

**Create Test Payment in Odoo:**
```python
def create_test_payment_in_odoo(invoice_id, amount):
    """Create a payment in Odoo to trigger Phase 6"""
    
    ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
    ODOO_DB = "window-solar-care"
    ODOO_USER_ID = 2
    ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"
    
    # Step 1: Get invoice details
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.move", "read",
                [[invoice_id]],
                {"fields": ["partner_id", "amount_total", "currency_id"]}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    invoice = response.json()["result"][0]
    
    # Step 2: Create payment
    payment_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment", "create",
                [{
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "partner_id": invoice["partner_id"][0],
                    "amount": amount,
                    "currency_id": invoice["currency_id"][0],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "journal_id": 7,  # BNK1 - verify your journal ID
                    "payment_method_line_id": 1,  # Manual - verify your payment method
                    "memo": "Test payment - Check #TEST123"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payment_payload, timeout=10)
    payment_id = response.json()["result"]
    
    # Step 3: Post the payment (confirm it)
    post_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment", "action_post",
                [[payment_id]]
            ]
        }
    }
    
    requests.post(ODOO_URL, json=post_payload, timeout=10)
    print(f"✅ Created and posted payment {payment_id}")
    
    # This will trigger Phase 6 webhook
    return payment_id

def delete_test_payment(payment_id):
    """Cancel/delete test payment"""
    
    # Set payment to draft, then delete
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment", "button_draft",
                [[payment_id]]
            ]
        }
    }
    
    requests.post(ODOO_URL, json=payload, timeout=10)
    
    # Now delete
    delete_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.payment", "unlink",
                [[payment_id]]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=delete_payload, timeout=10)
    print(f"✅ Deleted test payment {payment_id}")
```

---

## 🧹 Cleanup Scripts

### Delete Test Sales Order
```python
def delete_test_sales_order(so_id):
    """Cancel and delete test SO"""
    
    # Step 1: Cancel (unlock it)
    cancel_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "action_cancel",
                [[so_id]]
            ]
        }
    }
    
    requests.post(ODOO_URL, json=cancel_payload, timeout=10)
    
    # Step 2: Delete
    delete_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "unlink",
                [[so_id]]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=delete_payload, timeout=10)
    print(f"✅ Deleted SO {so_id}")
```

### Delete Test Invoice
```python
def delete_test_invoice(invoice_id):
    """Set invoice to draft and delete"""
    
    # Button draft
    draft_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.move", "button_draft",
                [[invoice_id]]
            ]
        }
    }
    
    requests.post(ODOO_URL, json=draft_payload, timeout=10)
    
    # Delete
    delete_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "account.move", "unlink",
                [[invoice_id]]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=delete_payload, timeout=10)
    print(f"✅ Deleted invoice {invoice_id}")
```

---

## 🎬 Complete Test Scenarios

### Scenario 1: Test Phase 3 (New Job → SO)

```python
# 1. Create test job
test_uuid = create_test_job()

# 2. Wait for Zapier to process (check Zapier dashboard)
time.sleep(30)

# 3. Verify SO created in Odoo
so_id = search_so_by_uuid(test_uuid)
if so_id:
    print(f"✅ SO created: {so_id}")
else:
    print("❌ SO not found")

# 4. Cleanup
delete_test_sales_order(so_id)
delete_test_job(test_uuid)
```

### Scenario 2: Test Phase 6 (Payment → Workiz)

```python
# 1. Find existing SO with Workiz UUID
so_id = 12345  # Replace with actual SO
invoice_id = create_invoice_from_so(so_id)

# 2. Create payment (triggers Phase 6)
payment_id = create_test_payment_in_odoo(invoice_id, 100.00)

# 3. Wait for Phase 6 to run
time.sleep(30)

# 4. Verify in Workiz (check payment added, job marked Done)
verify_workiz_payment(job_uuid)

# 5. Cleanup
delete_test_payment(payment_id)
delete_test_invoice(invoice_id)
```

---

## 📋 Standard Testing Checklist

After code changes:

- [ ] Push code to GitHub main
- [ ] Create test data via API (I do this)
- [ ] Trigger Zapier (webhook or manual)
- [ ] Check Zapier task history logs
- [ ] Verify results in Odoo/Workiz
- [ ] Delete test data via API (I do this)
- [ ] Confirm cleanup complete

**DJ doesn't touch Workiz/Odoo UI for testing!**

---

## 🔑 Test Customer Data

**Keep these IDs handy for testing:**
- Test ClientId: [Find one existing customer to use]
- Test Property Address: [Use existing address]
- Test SO ID: [Keep one test SO for payment testing]

**OR create dedicated test customer:**
- Name: "TEST Customer - Safe to Delete"
- Address: "999 Test Drive, Palm Springs, CA 92262"
- Mark clearly in both systems

---

## ⚠️ Safety Rules

1. **Always mark test data** with "TEST" in name/notes
2. **Delete immediately after test**
3. **Use existing test customer** when possible (don't create new each time)
4. **Never test on real customer data**
5. **Verify cleanup** before ending session

---

**END OF TEST FRAMEWORK**
