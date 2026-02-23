# Phase 4 Changes: Webhook Integration for Phase 5
**What Changed:** Added automatic Phase 5 trigger when job marked "Done"

---

## 📝 Changes Made to Phase 4 Script

### 1. Added Configuration Variable (Top of Script)

**Location:** Line ~28 (after WORKIZ_BASE_URL)

```python
# Phase 5 Webhook URL (set this after deploying Phase 5 Zap)
PHASE5_WEBHOOK_URL = "YOUR_PHASE5_WEBHOOK_URL_HERE"  # TODO: Replace with actual webhook URL
```

**Action Required:**
- Deploy Phase 5 Zap first
- Copy webhook URL from Phase 5
- Replace `"YOUR_PHASE5_WEBHOOK_URL_HERE"` with actual URL

---

### 2. Added Webhook Call (Two Locations)

#### Location A: When SO Already Exists

**Where:** After property update, before final return (~line 990)

**What it does:**
```python
if status.lower() == 'done':
    type_of_service = workiz_job.get('type_of_service', '').lower()
    
    if 'maintenance' in type_of_service or 'on demand' in type_of_service:
        # 1. Get contact_id and property_id from SO
        # 2. Fetch customer_city from Odoo property
        # 3. Build payload with all Phase 5 needs
        # 4. POST to Phase 5 webhook
        # 5. Log success/failure
```

#### Location B: When SO Created by Phase 3

**Where:** After chatter message posted (~line 1020)

**Same logic as Location A** - triggers Phase 5 with data from newly created SO

---

## 🔍 What the Webhook Call Does

### Step 1: Check Trigger Conditions
```python
if status.lower() == 'done':                    # Job is complete
    type_of_service = workiz_job.get('type_of_service', '').lower()
    
    if 'maintenance' in type_of_service or 'on demand' in type_of_service:
        # Continue to webhook
```

### Step 2: Gather Required Data
```python
# Get IDs
contact_id = existing_so.get('partner_id')
property_id = existing_so.get('partner_shipping_id')

# Fetch city from Odoo
city_payload = {...}
city_response = requests.post(ODOO_URL, json=city_payload)
customer_city = city_result[0].get('city', '')
```

### Step 3: Send Webhook
```python
phase5_data = {
    'job_uuid': job_uuid,
    'property_id': property_id,
    'contact_id': contact_id,
    'customer_city': customer_city
}

phase5_response = requests.post(PHASE5_WEBHOOK_URL, json=phase5_data)
```

### Step 4: Log Result
```python
if phase5_response.status_code == 200:
    print("[OK] Phase 5 triggered successfully")
else:
    print(f"[!] Phase 5 webhook returned status {phase5_response.status_code}")
```

---

## ✅ Safety Features Built In

### 1. Graceful Failure
- If webhook fails, Phase 4 still completes successfully
- Error logged but doesn't break Phase 4 flow
- SO updates still saved

### 2. Configuration Check
```python
if PHASE5_WEBHOOK_URL and PHASE5_WEBHOOK_URL != "YOUR_PHASE5_WEBHOOK_URL_HERE":
    # Only trigger if URL is configured
```

- Won't attempt webhook if URL not set
- Logs: "[!] Phase 5 webhook URL not configured - skipping"

### 3. Service Type Filter
- Only triggers for Maintenance or On Demand
- Other service types skip Phase 5
- Prevents unnecessary webhook calls

---

## 🧪 Testing Checklist

### Before Testing:
- [ ] Phase 5 Zap deployed and ON
- [ ] Webhook URL copied from Phase 5
- [ ] Phase 4 code updated with URL
- [ ] Phase 4 Zap saved

### Test 1: Maintenance Job
**Input to Phase 4:**
```json
{
  "job_uuid": "IC3ZC9"  // Job with type_of_service = "Maintenance"
}
```

**Expected in Phase 4 logs:**
```
[*] Job Status: Done
[*] Triggering Phase 5: Auto-scheduler
[OK] Phase 5 triggered successfully
[OK] PHASE 4 COMPLETE - SALES ORDER UPDATED
```

**Expected in Phase 5 logs:**
- New run triggered
- Receives: job_uuid, property_id, contact_id, customer_city
- Creates new Workiz job (Path 5A)

### Test 2: On Demand Job
**Input to Phase 4:**
```json
{
  "job_uuid": "TEST123"  // Job with type_of_service = "On Demand"
}
```

**Expected in Phase 5 logs:**
- Receives data
- Creates Odoo activity (Path 5B)
- NO Workiz job created

### Test 3: Non-Maintenance Job
**Input:**
```json
{
  "job_uuid": "TEST456"  // Job without type_of_service
}
```

**Expected:**
- Phase 4 completes normally
- Phase 5 NOT triggered (skipped)

---

## 📊 Complete Flow Visualization

```
Workiz Job Status → "Done"
    ↓
┌───────────────────────────┐
│  ZAP 2: PHASE 4           │
│  (Job Status Update)      │
│                           │
│  1. Update SO             │
│  2. Add payment fields    │
│  3. Post to chatter       │
│  4. Update property       │
│                           │
│  5. Check service type    │
│     ↓                     │
│   Maintenance/On Demand?  │
│     ↓                     │
│    YES                    │
│     ↓                     │
│  6. Gather data:          │
│     - job_uuid            │
│     - property_id         │
│     - contact_id          │
│     - customer_city       │
│     ↓                     │
│  7. POST webhook          │
└─────────┬─────────────────┘
          ↓
    HTTP POST to:
    PHASE5_WEBHOOK_URL
          ↓
┌───────────────────────────┐
│  ZAP 3: PHASE 5           │
│  (Auto Scheduler)         │
│                           │
│  Receives data            │
│     ↓                     │
│  Routes to 5A or 5B       │
│     ↓                     │
│  Creates job/activity     │
└───────────────────────────┘
```

---

## 🎯 What You Need to Do

### 1. Deploy Phase 5 First
- Get webhook URL

### 2. Update Phase 4
- Find: `PHASE5_WEBHOOK_URL = "YOUR_PHASE5_WEBHOOK_URL_HERE"`
- Replace with: `PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/[YOUR_URL]"`

### 3. Test
- Trigger Phase 4 with Done job
- Verify Phase 5 receives data
- Check new job/activity created

---

## 🚨 Important Notes

**The webhook call is AUTOMATIC:**
- You don't need to add a separate Zapier action
- It's built into the Python code
- Runs automatically when conditions met

**Error handling:**
- If webhook fails, Phase 4 still succeeds
- Errors logged but don't break workflow
- Can manually trigger Phase 5 if needed

**Cost:**
- Each webhook call = 1 Zapier task
- Only triggers when job is Done + Maintenance/On Demand
- Estimated: 2-5 Phase 5 triggers per day

---

## ✅ Verification

**After deployment, verify:**
- [ ] Phase 4 Zap has webhook URL configured
- [ ] Test run shows "[OK] Phase 5 triggered"
- [ ] Phase 5 Zap history shows new runs
- [ ] New jobs appearing in Workiz (Maintenance)
- [ ] Activities appearing in Odoo (On Demand)

---

**Connection is automatic once webhook URL is set!**  
No additional Zapier actions needed - just update the URL. 🔗
