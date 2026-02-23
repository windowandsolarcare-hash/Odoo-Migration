# Phase 5: Auto Job Scheduler - Zapier Deployment Guide
**Generated:** 2026-02-07  
**Script:** `zapier_phase5_FLATTENED_FINAL.py`  
**Zap Type:** SEPARATE ZAP (triggered by Phase 4)

---

## 🎯 Overview

Phase 5 automatically creates next service job (Maintenance) OR follow-up reminder (On Demand) after job marked "Done"

**Two Paths:**
- **5A - Maintenance:** Creates next scheduled job in Workiz
- **5B - On Demand:** Creates follow-up reminder activity in Odoo

---

## 🔗 Zap Architecture: Separate Zaps

### Why Separate Zaps?

1. **Token Limits:** Combined Phase 3+4+5 would exceed Zapier limits
2. **Modular Testing:** Easier to test and debug individually
3. **Flexibility:** Can enable/disable Phase 5 independently
4. **Clarity:** Each Zap has single, clear purpose

### How Zaps Communicate

```
Phase 4 Zap (Job Status Update)
    ↓
Detects "Done" status + Maintenance/On Demand
    ↓
Triggers Phase 5 Zap
(via Webhooks by Zapier OR direct sub-zap call)
    ↓
Phase 5 Zap (Auto Scheduler)
    ↓
Creates job OR activity
```

---

## 📋 Zapier Setup

### Step 1: Create New Zap

**Zap Name:** `Phase 5: Auto Job Scheduler`

### Step 2: Trigger Configuration

**Option A: Webhooks by Zapier (Recommended)**

1. **Trigger:** Webhooks by Zapier → "Catch Hook"
2. **Webhook URL:** Copy the generated URL
3. **Test:** Send test data from Phase 4

**Option B: Direct Sub-Zap Call**

1. Use Zapier's "Sub-Zap" feature
2. Phase 4 calls Phase 5 directly
3. Passes data inline

---

### Step 3: Code by Zapier Configuration

**Action:** Code by Zapier → Run Python

#### Input Data Fields

Map these fields from trigger (Phase 4 webhook/sub-zap):

| Zapier Input | Type | Required | Source |
|-------------|------|----------|--------|
| `job_uuid` | string | Yes | From Phase 4: Workiz job UUID |
| `property_id` | integer | Yes (5A) | From Phase 4: Odoo property ID |
| `contact_id` | integer | Yes (5B) | From Phase 4: Odoo contact ID |
| `customer_city` | string | Yes (5A) | From Phase 4: Property city |

**Example mapping:**
```
job_uuid: {{trigger.job_uuid}}
property_id: {{trigger.property_id}}
contact_id: {{trigger.contact_id}}
customer_city: {{trigger.customer_city}}
```

#### Python Code

**Copy the entire contents** of `zapier_phase5_FLATTENED_FINAL.py` into the code editor.

**Script Stats:**
- Total Lines: ~680
- Includes: Both 5A and 5B paths, all utilities, API functions
- No external dependencies

---

## 🔄 Integration with Phase 4

### Phase 4 Updates Needed

Add this code to Phase 4 Zap AFTER "Done" detection:

```python
# At end of Phase 4, after payment updates
if status.lower() == 'done':
    type_of_service = workiz_job.get('type_of_service', '').lower()
    
    if 'maintenance' in type_of_service or 'on demand' in type_of_service:
        # Trigger Phase 5 Zap
        import requests
        
        phase5_webhook_url = 'YOUR_PHASE_5_WEBHOOK_URL_HERE'
        
        phase5_data = {
            'job_uuid': workiz_job['UUID'],
            'property_id': property_id,  # From Phase 4
            'contact_id': contact_id,    # From Phase 4
            'customer_city': customer_city  # Fetch or pass from Phase 4
        }
        
        requests.post(phase5_webhook_url, json=phase5_data)
        print("[*] Phase 5 triggered")
```

**OR** use Zapier's native "Run Sub-Zap" action in Phase 4.

---

## 🧪 Testing

### Pre-Deployment: Add Workiz Custom Field

**IMPORTANT:** Before deploying, add custom field in Workiz:

1. Go to Workiz Settings → Custom Fields
2. Create new field for "Job" type
3. **Field Name:** `next_job_line_items` (or your preference)
4. **Type:** Text/Textarea
5. **Purpose:** Store line items reference for user

### Test Path 5A: Maintenance

**Test Data:**
```json
{
  "job_uuid": "IC3ZC9",
  "property_id": 24169,
  "contact_id": 23621,
  "customer_city": "Palm Springs"
}
```

**Expected Results:**
- ✅ New job created in Workiz
- ✅ Date calculated (4 months from now, adjusted to Monday for Palm Springs)
- ✅ Custom field contains: "Windows In & Out - Full Service: $85.00"
- ✅ JobNotes contains: "AUTO-SCHEDULED - Next 4 Months service"
- ⚠️ User must add line items and set status manually

**Verify in Workiz:**
1. Search for new job (by customer name + future date)
2. Check custom field `next_job_line_items` has pricing
3. Check JobNotes has previous job UUID reference

### Test Path 5B: On Demand

**Test Data (override service type):**
```json
{
  "job_uuid": "IC3ZC9",
  "property_id": 24169,
  "contact_id": 23621,
  "customer_city": ""
}
```

Note: You'll need to temporarily override `type_of_service` to "On Demand" in test

**Expected Results:**
- ✅ Activity created in Odoo
- ✅ Due date: Sunday, 6 months from now
- ✅ Activity visible on Contact record
- ✅ NO job created in Workiz

**Verify in Odoo:**
1. Open Contact record (ID: 23621)
2. Check Activities panel
3. Verify due date and description

---

## 🗺️ City-Aware Scheduling

### Route Mapping (From Actual Calendly Setup)

| City | Preferred Day | Weekday | Calendly Days Available |
|------|---------------|---------|------------------------|
| Palm Springs | Friday | 4 | Fri |
| Rancho Mirage | Thursday | 3 | Thu, Fri |
| Palm Desert | Thursday | 3 | Thu |
| Indian Wells | Wednesday | 2 | Wed, Thu |
| Indio / La Quinta | Wednesday | 2 | Wed |
| Hemet | Tuesday | 1 | Tue |
| Unknown | No change | Target date | N/A |

**Note:** For cities with multiple days (like Rancho Mirage), the primary day is used for scheduling. The secondary days provide flexibility for customer booking.

### Logic Example

**Scenario:** 4-month job, customer in Palm Desert

1. Today: Feb 7, 2026
2. Target: June 7, 2026 (Sunday)
3. Preferred: Thursday (per Calendly setup)
4. Nearest Thursday: June 4, 2026 (-3 days)
5. **Result:** June 4, 2026 10:00 AM

---

## 📊 Field Mappings

### Maintenance Path (5A)

#### Workiz Job Creation Fields:

**Required by API:**
- `ClientId`, `FirstName`, `LastName`
- `Address`, `City`, `State`, `PostalCode`, `Phone`
- `JobDateTime`, `JobType`

**Custom Fields:**
- `frequency`, `alternating`, `type_of_service`
- `gate_code`, `pricing`
- **`next_job_line_items`** - LINE ITEMS REFERENCE (your custom field)

**Generated:**
- `JobNotes` - Auto-generated with previous job reference

#### Line Items Format:

**In custom field:**
```
Windows In & Out - Full Service: $85.00
Solar Panel Cleaning: $45.00
```

**User workflow (30 seconds):**
1. Open new job in Workiz
2. See custom field with pricing
3. Add line items manually
4. Set status to "Send Next Job - Text"

### On Demand Path (5B)

#### Odoo Activity Fields:

- `res_model`: "res.partner"
- `res_id`: Contact ID
- `activity_type_id`: 2 (Follow-Up)
- `summary`: "Follow-up: [Customer Name]"
- `note`: Description with last service details
- `date_deadline`: Sunday, 6 months out
- `user_id`: Your user ID

---

## ⚙️ Configuration Options

### Customizable Settings (in script):

**Date Calculation:**
- Default frequency if can't parse: 3 months (line 41)
- Default follow-up for On Demand: 6 months (line 335)

**City Schedule:**
- Modify `city_schedule` dict (lines 48-56) to change routing

**Activity Type:**
- Change `activity_type_id` (line 376) if needed

**Custom Field Name:**
- Change `'next_job_line_items'` (line 204) to match your Workiz field

---

## 🚨 Known Limitations

### 1. LineItems API Limitation
**Issue:** Workiz API does not support adding LineItems  
**Impact:** User must add 2-3 line items manually (30 seconds)  
**Mitigation:** Stored as text reference in custom field

### 2. No UUID from Job Creation
**Issue:** Workiz returns HTTP 204 (no UUID in response)  
**Impact:** Cannot immediately set status to trigger SMS  
**Mitigation:** User sets status manually after adding line items

### 3. Activity Type ID
**Issue:** Hardcoded to ID 2 (may vary by Odoo instance)  
**Solution:** Verify correct ID in your Odoo, update script if needed

---

## 📝 Deployment Checklist

### Pre-Deployment:
- [ ] Create `next_job_line_items` custom field in Workiz
- [ ] Update Phase 4 Zap to trigger Phase 5 (webhook or sub-zap)
- [ ] Copy webhook URL from Phase 5 to Phase 4

### Deployment:
- [ ] Create new Zap: "Phase 5: Auto Job Scheduler"
- [ ] Set trigger: Webhooks (Catch Hook) or Sub-Zap
- [ ] Add Code by Zapier action
- [ ] Map input fields: `job_uuid`, `property_id`, `contact_id`, `customer_city`
- [ ] Paste `zapier_phase5_FLATTENED_FINAL.py` code
- [ ] Test with Path 5A (Maintenance) data
- [ ] Test with Path 5B (On Demand) data

### Post-Deployment:
- [ ] Monitor first few runs in Zapier logs
- [ ] Verify jobs created in Workiz (check dates and custom field)
- [ ] Verify activities created in Odoo
- [ ] Train user on 30-second manual workflow
- [ ] Update city routing if needed

---

## 🔍 Troubleshooting

### Issue 1: "Missing job_uuid"
**Cause:** Phase 4 webhook not sending data correctly  
**Fix:** Check Phase 4 webhook call, ensure all fields mapped

### Issue 2: Custom field empty in Workiz
**Cause:** Field name mismatch  
**Fix:** Verify field name in Workiz matches script (`next_job_line_items`)

### Issue 3: Wrong service day
**Cause:** City not in routing map  
**Fix:** Add city to `city_schedule` dict or check spelling

### Issue 4: Activity not appearing in Odoo
**Cause:** Wrong activity_type_id or contact_id  
**Fix:** Verify IDs, check Odoo logs for error

---

## 📈 Success Metrics

### Maintenance Customers (5A):
- ✅ Job auto-created in Workiz
- ✅ Date calculated correctly
- ✅ Date adjusted to city routing day
- ✅ Line items reference in custom field
- ✅ User adds items + sets status (30 sec)
- ✅ Customer receives "Next Job" SMS

### On Demand Customers (5B):
- ✅ Activity created in Odoo
- ✅ Due on Sunday of target week
- ✅ Visible on Contact record
- ✅ NO job clutter in Workiz
- ✅ User reminded to follow up

---

## 🔗 Related Documentation

- **Phase 4 Deployment:** `Zapier_Phase4_Deployment_Guide.md`
- **Phase 5 Implementation:** `Phase5_Implementation_Summary.md`
- **Workiz API Tests:** `Workiz_API_Test_Results.md`
- **Complete Overview:** `COMPLETE_PHASE_OVERVIEW.md`

---

## 💡 Future Enhancements

1. **Phase 5C: Route Optimization**
   - Consider proximity to other scheduled jobs
   - Suggest optimal day based on route efficiency

2. **Auto-Status Setting**
   - If Workiz adds webhook for job creation
   - Auto-set status to trigger SMS

3. **LineItems API Research**
   - Contact Workiz support
   - Check for undocumented endpoints

---

**Phase 5 is ready for deployment as a separate Zap!**  
**Estimated setup time:** 15-20 minutes  
**Zap Status:** Flattened, tested logic, ready for Zapier
