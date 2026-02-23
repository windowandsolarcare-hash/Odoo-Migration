# Connecting Phase 4 to Phase 5 - Webhook Setup
**Guide for linking Zap 2 (Phase 4) to Zap 3 (Phase 5)**

---

## 🔗 Overview

Phase 4 (Job Status Update) triggers Phase 5 (Auto Scheduler) when:
- Job status = "Done"
- Service type = "Maintenance" OR "On Demand"

**Method:** HTTP webhook call from Phase 4 to Phase 5

---

## 📋 Step-by-Step Setup

### STEP 1: Deploy Phase 5 Zap First

**Important:** Deploy Phase 5 BEFORE Phase 4 to get the webhook URL

1. Go to Zapier → Create New Zap
2. Name it: `Phase 5: Auto Job Scheduler`
3. **Trigger:** Webhooks by Zapier → Catch Hook
4. Click "Continue"
5. **Copy the Webhook URL** (looks like):
   ```
   https://hooks.zapier.com/hooks/catch/1234567/abcd123/
   ```
6. Save this URL - you'll need it for Step 2!
7. Add Code by Zapier action
8. Map input fields:
   - `job_uuid`
   - `property_id`
   - `contact_id`
   - `customer_city`
9. Paste `zapier_phase5_FLATTENED_FINAL.py` code
10. Test with sample data
11. Turn Zap ON

---

### STEP 2: Update Phase 4 Code with Webhook URL

**Location:** In your Phase 4 Zap code

**Find this line (near top of script):**
```python
# Phase 5 Webhook URL (set this after deploying Phase 5 Zap)
PHASE5_WEBHOOK_URL = "YOUR_PHASE5_WEBHOOK_URL_HERE"  # TODO: Replace
```

**Replace with your actual URL from Step 1:**
```python
# Phase 5 Webhook URL
PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/1234567/abcd123/"
```

**Save the Phase 4 Zap.**

---

### STEP 3: How the Webhook Call Works

**Location in Phase 4 code:** Added automatically near end of main function

**What it does:**

1. **Detects trigger conditions:**
   ```python
   if status.lower() == 'done':
       type_of_service = workiz_job.get('type_of_service', '').lower()
       
       if 'maintenance' in type_of_service or 'on demand' in type_of_service:
           # Trigger Phase 5
   ```

2. **Gathers required data:**
   - `job_uuid` - Workiz job UUID
   - `property_id` - From Odoo SO
   - `contact_id` - From Odoo SO
   - `customer_city` - Fetched from Odoo property

3. **Sends webhook to Phase 5:**
   ```python
   phase5_data = {
       'job_uuid': job_uuid,
       'property_id': property_id,
       'contact_id': contact_id,
       'customer_city': customer_city
   }
   
   requests.post(PHASE5_WEBHOOK_URL, json=phase5_data)
   ```

4. **Logs result:**
   - Success: "Phase 5 triggered successfully"
   - Failure: Logs error but doesn't break Phase 4

---

## 🧪 Testing the Connection

### Test 1: Verify Webhook URL is Set

**In Phase 4 Zap:**
1. Check the code for `PHASE5_WEBHOOK_URL`
2. Ensure it's NOT "YOUR_PHASE5_WEBHOOK_URL_HERE"
3. Should be actual Zapier webhook URL

### Test 2: Test with Maintenance Job

**Trigger Phase 4 with:**
- Job UUID of a "Done" job
- Job has `type_of_service` = "Maintenance"

**Expected:**
1. Phase 4 runs normally
2. Updates SO with payment fields
3. At end, you'll see: "[*] Triggering Phase 5: Auto-scheduler"
4. Phase 5 Zap should receive data and run
5. New job created in Workiz (or activity in Odoo)

**Check:**
- Phase 4 Zap history: Should show "[OK] Phase 5 triggered"
- Phase 5 Zap history: Should show new run with data from Phase 4

### Test 3: Test with On Demand Job

Same as Test 2, but with `type_of_service` = "On Demand"

**Expected:**
- Phase 4 completes
- Phase 5 triggered
- Activity created in Odoo (NO Workiz job)

---

## 🔍 Troubleshooting

### Issue 1: "Phase 5 webhook URL not configured"
**Cause:** `PHASE5_WEBHOOK_URL` still set to placeholder  
**Fix:** Replace with actual webhook URL from Phase 5 Zap

### Issue 2: Phase 5 never triggers
**Possible causes:**
- Webhook URL incorrect
- Service type doesn't match ("Maintenance" or "On Demand")
- Status not "Done"

**Debug:**
- Check Phase 4 logs for "Triggering Phase 5" message
- Verify `type_of_service` field value
- Test webhook URL directly (Postman or curl)

### Issue 3: Phase 5 receives wrong data
**Cause:** Field mapping mismatch  
**Fix:** Check Phase 5 input field names match webhook payload keys

---

## 📊 Data Flow Visualization

```
Phase 4 Zap Runs
    ↓
Job Status = "Done"?
    ↓
   YES
    ↓
Service Type = Maintenance or On Demand?
    ↓
   YES
    ↓
[Gather Data]
- job_uuid
- property_id (from SO)
- contact_id (from SO)
- customer_city (fetch from Odoo)
    ↓
[Send Webhook]
POST to Phase 5 URL
with JSON payload
    ↓
Phase 5 Zap Triggered
    ↓
Receives data automatically
    ↓
Routes to 5A or 5B
```

---

## ⚙️ Configuration Checklist

**Before going live:**
- [ ] Phase 5 Zap deployed and ON
- [ ] Webhook URL copied from Phase 5
- [ ] Phase 4 code updated with webhook URL
- [ ] Phase 4 Zap saved
- [ ] End-to-end test completed
- [ ] Both Zaps showing successful runs

---

## 💡 Alternative: Zapier Sub-Zap

**If you prefer not using webhooks:**

Zapier has a native "Run Sub-Zap" feature:

1. In Phase 4, add action: "Sub-Zap by Zapier"
2. Select Phase 5 Zap as target
3. Map fields directly (no webhook URL needed)
4. More expensive (uses more tasks) but simpler

**Webhook approach is recommended** for cost efficiency.

---

## 📝 Quick Reference

### Phase 4 → Phase 5 Data Flow

| Field | Source | Used By |
|-------|--------|---------|
| `job_uuid` | Phase 4 input | Both 5A and 5B |
| `property_id` | Odoo SO | Path 5A (job history) |
| `contact_id` | Odoo SO | Path 5B (activity) |
| `customer_city` | Odoo Property | Path 5A (scheduling) |

### Webhook Payload Example

```json
{
  "job_uuid": "IC3ZC9",
  "property_id": 24169,
  "contact_id": 23621,
  "customer_city": "Palm Springs"
}
```

---

## ✅ Success Criteria

**Working correctly when:**
- Phase 4 completes normally
- Phase 5 receives data automatically
- New job appears in Workiz (Maintenance) OR
- Activity appears in Odoo (On Demand)
- No errors in either Zap's history

---

**Ready to connect the Zaps!**  
Deploy Phase 5 first → Copy webhook URL → Update Phase 4 → Test!
