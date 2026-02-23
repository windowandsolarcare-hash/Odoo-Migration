# Complete Deployment Checklist
**A Window & Solar Care - Workiz ↔ Odoo Integration**  
**Follow this exact order for smooth deployment**

---

## 🎯 Pre-Deployment Setup

### 1. Create Workiz Custom Field
- [ ] Log into Workiz
- [ ] Go to Settings → Custom Fields
- [ ] Create new field:
  - **Model:** Job
  - **Field Name:** `next_job_line_items` (or your preference)
  - **Type:** Text or Textarea
  - **Purpose:** Store line items reference for Phase 5
- [ ] Save and note the exact field name

### 2. Verify Workiz Webhooks
- [ ] Go to Workiz Settings → Integrations → Webhooks
- [ ] Verify webhooks exist for:
  - "New Job Created"
  - "Job Status Changed"
- [ ] Copy webhook URLs (you'll need them)

---

## 🚀 Deployment Order

Deploy in this exact order to avoid dependency issues:

---

## 📦 STEP 1: Deploy Zap 3 (Phase 5) FIRST

**Why first?** You need the webhook URL for Phase 4

### 1.1 Create Zap
- [ ] Go to Zapier → Create New Zap
- [ ] Name: `Phase 5: Auto Job Scheduler`

### 1.2 Configure Trigger
- [ ] Trigger: **Webhooks by Zapier**
- [ ] Event: **Catch Hook**
- [ ] Click Continue
- [ ] **COPY THE WEBHOOK URL** (critical!)
  ```
  Example: https://hooks.zapier.com/hooks/catch/1234567/abcd123/
  ```
- [ ] Save this URL somewhere safe

### 1.3 Configure Code Action
- [ ] Action: **Code by Zapier** → Run Python
- [ ] Set up Input Data (4 fields) - **MUST SELECT FROM DROPDOWN, NOT TYPE:**
  - `job_uuid` → (will come from Phase 4 webhook)
  - `property_id` → (will come from Phase 4 webhook)
  - `contact_id` → (will come from Phase 4 webhook)
  - `customer_city` → (will come from Phase 4 webhook)
- [ ] Paste entire contents of `zapier_phase5_FLATTENED_FINAL.py` (555 lines)
- [ ] **Key Features:**
  - Preserves JobNotes from previous job
  - City-aware scheduling (Palm Springs → Friday, Hemet → Tuesday, etc.)
  - Handles alternating service logic
  - Formats line items with context in custom field
- [ ] Test with sample data:
  ```json
  {
    "job_uuid": "MSAZ9N",
    "property_id": 24147,
    "contact_id": 23025,
    "customer_city": "Hemet"
  }
  ```

### 1.4 Verify & Turn On
- [ ] Test should show date calculation and either:
  - "Job created" (Maintenance), OR
  - "Activity created" (On Demand)
- [ ] Turn Zap **ON**
- [ ] Phase 5 complete! ✅

---

## 📦 STEP 2: Deploy Zap 1 (Phase 3)

### 2.1 Create Zap
- [ ] Create New Zap
- [ ] Name: `Phase 3: New Job Creation`

### 2.2 Configure Trigger
- [ ] Trigger: **Webhooks by Zapier** → Catch Hook
- [ ] OR: **Workiz** (if native integration available)
- [ ] Event: New Job Created
- [ ] Test trigger with real/sample data

### 2.3 Configure Code Action
- [ ] Action: **Code by Zapier** → Run Python
- [ ] Set up Input Data (1 field):
  - `job_uuid` → Map to `{{trigger.UUID}}`
- [ ] Paste entire contents of `zapier_phase3_FLATTENED_FINAL.py`
- [ ] Review code (1,118 lines)

### 2.4 Test All Three Paths
- [ ] **Test Path A:** Use job with existing Contact + Property
- [ ] **Test Path B:** Use job with existing Contact, new Property
- [ ] **Test Path C:** Use job with new Contact + Property
- [ ] Verify SOs created in Odoo for each

### 2.5 Turn On
- [ ] All tests pass
- [ ] Turn Zap **ON**
- [ ] Phase 3 complete! ✅

---

## 📦 STEP 3: Deploy Zap 2 (Phase 4) with Phase 5 Connection

### 3.1 Create Zap
- [ ] Create New Zap
- [ ] Name: `Phase 4: Job Status Update`

### 3.2 Configure Trigger
- [ ] Trigger: **Webhooks by Zapier** → Catch Hook
- [ ] OR: **Workiz** (if native integration available)
- [ ] Event: Job Status Changed
- [ ] Test trigger

### 3.3 Configure Code Action
- [ ] Action: **Code by Zapier** → Run Python
- [ ] Set up Input Data (1 field):
  - `job_uuid` → Map to `{{trigger.UUID}}`
- [ ] Paste entire contents of `zapier_phase4_FLATTENED_FINAL.py`

### 3.4 **CRITICAL:** Update Phase 5 Webhook URL

**Find this line in the code (near top):**
```python
PHASE5_WEBHOOK_URL = "YOUR_PHASE5_WEBHOOK_URL_HERE"
```

**Replace with the URL from Step 1.2:**
```python
PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/1234567/abcd123/"
```

**This connects Phase 4 → Phase 5!**

### 3.5 Test Phase 4
- [ ] Test 1: Update existing SO (any status)
- [ ] Test 2: Update existing SO (status = Done, Maintenance)
  - Should trigger Phase 5
  - Check Phase 5 Zap history for new run
- [ ] Test 3: Create missing SO (via Phase 3 logic)
- [ ] Test 4: Done status with On Demand
  - Should create Odoo activity via Phase 5

### 3.6 Turn On
- [ ] All tests pass
- [ ] Webhook to Phase 5 working
- [ ] Turn Zap **ON**
- [ ] Phase 4 complete! ✅

---

## 🧪 End-to-End Testing

### Test Complete Workflow

**Scenario 1: New Maintenance Job → Done → Next Job Created**

1. Create new job in Workiz
   - Trigger: Zap 1 (Phase 3)
   - Result: SO created in Odoo ✅

2. Mark job as "Done" in Workiz
   - Trigger: Zap 2 (Phase 4)
   - Result: SO updated, payment fields added ✅

3. Phase 4 triggers Phase 5
   - Trigger: Webhook from Phase 4
   - Result: New job created in Workiz for next service ✅

4. User adds line items (30 sec)
   - See `next_job_line_items` custom field
   - Add items manually
   - Set status to "Send Next Job - Text" ✅

**Scenario 2: On Demand Job → Done → Reminder Created**

1-2. Same as above

3. Phase 4 triggers Phase 5
   - Result: Activity created in Odoo ✅
   - NO Workiz job (keeps schedule clean) ✅

---

## 📊 Monitoring First Week

### Daily Checks (Days 1-7):
- [ ] Check Zapier task history (all 3 Zaps)
- [ ] Verify data accuracy in Odoo
- [ ] Verify jobs in Workiz
- [ ] Look for any error patterns

### What to Monitor:
- **Zap 1 (Phase 3):**
  - SOs created correctly
  - Paths (A/B/C) working
  - Custom fields populated

- **Zap 2 (Phase 4):**
  - Status updates syncing
  - Payment fields correct
  - Chatter messages formatted
  - Phase 5 triggers when expected

- **Zap 3 (Phase 5):**
  - Jobs scheduled on correct days
  - Line items reference visible
  - Activities created for On Demand
  - City routing working

### Common First-Week Issues:
1. **Field name mismatches** → Update script
2. **Webhook timeouts** → Increase timeout
3. **City not in routing** → Add to city_schedule
4. **Custom field empty** → Verify field name matches

---

## 🔧 Configuration Reference

### Webhook URLs to Set:

**In Phase 4 script:**
```python
PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/[YOUR_PHASE5_URL]"
```

**In Phase 5 script:**
```python
# Custom field name (line ~204)
'next_job_line_items': line_items_text  # Update if your field name differs
```

### Zapier Input Mappings:

**Zap 1 (Phase 3):**
- `job_uuid` = `{{trigger.UUID}}`

**Zap 2 (Phase 4):**
- `job_uuid` = `{{trigger.UUID}}`

**Zap 3 (Phase 5):**
- `job_uuid` = `{{trigger.job_uuid}}`
- `property_id` = `{{trigger.property_id}}`
- `contact_id` = `{{trigger.contact_id}}`
- `customer_city` = `{{trigger.customer_city}}`

---

## ✅ Deployment Complete Checklist

### Phase 5 (Zap 3):
- [ ] Custom field created in Workiz
- [ ] Zap created and configured
- [ ] Webhook URL copied
- [ ] Code pasted (680 lines)
- [ ] Tested with sample data
- [ ] Turned ON

### Phase 3 (Zap 1):
- [ ] Zap created and configured
- [ ] Workiz trigger set up
- [ ] Code pasted (1,118 lines)
- [ ] All 3 paths tested
- [ ] Turned ON

### Phase 4 (Zap 2):
- [ ] Zap created and configured
- [ ] Workiz trigger set up
- [ ] Code pasted (1,047+ lines with webhook)
- [ ] **Phase 5 webhook URL configured**
- [ ] Status update tested
- [ ] Done status tested
- [ ] Phase 5 trigger verified
- [ ] Turned ON

### Verification:
- [ ] All 3 Zaps showing in Zapier dashboard
- [ ] All 3 Zaps turned ON
- [ ] Test run of each Zap successful
- [ ] End-to-end test complete
- [ ] User trained on Phase 5 manual process

---

## 🎉 Success!

**When all checked:**
- ✅ Complete automation live
- ✅ 95% of work automated
- ✅ Clean data flow Workiz ↔ Odoo
- ✅ ~225 hours/year saved

---

## 📞 Support Resources

**Documentation:**
- `Zapier_Deployment_Guide_FINAL.md` (Phase 3)
- `Zapier_Phase4_Deployment_Guide.md` (Phase 4)
- `Zapier_Phase5_Deployment_Guide.md` (Phase 5)
- `Connecting_Phase4_to_Phase5.md` (This guide)
- `Phase4_Changes_for_Phase5.md` (What changed)

**Scripts:**
- `zapier_phase3_FLATTENED_FINAL.py`
- `zapier_phase4_FLATTENED_FINAL.py` (includes webhook)
- `zapier_phase5_FLATTENED_FINAL.py`

**Test Scripts:**
- `test_phase5.py` (for local testing)

---

**Deployment Order:** 5 → 3 → 4  
**Total Time:** 1-2 hours  
**Ready to launch!** 🚀
