# Migrate Reactivation Zap to GitHub Pattern
**Date:** 2026-03-05  
**Zap:** "Odoo to Workiz: Reactivation Outbound Event"

---

## 🎯 What We're Doing

**BEFORE:** 20 separate Zapier steps (formatters, webhooks, etc.)  
**AFTER:** 2 steps total (webhook + code from GitHub)

---

## ✅ Code Now on GitHub

**File:** `zapier_reactivation_sms_FINAL.py`  
**Location:** `2_Modular_Phase3_Components/`  
**GitHub:** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/2_Modular_Phase3_Components/zapier_reactivation_sms_FINAL.py

**What it does (all 20 steps consolidated):**
1. Gets Opportunity details from Odoo
2. Gets SMS message from chatter
3. Gets historical Workiz job
4. Creates graveyard job in Workiz
5. Triggers SMS (updates status to "API SMS Test Trigger")
6. Logs activity in Odoo
7. Updates contact reactivation date
8. Links graveyard job back to Opportunity

---

## 🔄 How to Update the Zap

### **Step 1: Open the Zap**
- Go to: https://zapier.com/editor/343856639
- Click "Edit" mode

### **Step 2: Keep Step 1 (Webhook Trigger)**
**Do NOT change this:**
- Step 1: Webhooks by Zapier - Catch Hook
- This stays exactly as is (same webhook URL)

### **Step 3: Delete Steps 2-20**
**Delete ALL of these:**
- Step 2: Odoo - Get Opportunity Details
- Step 3: Odoo - Get Chatter Message
- Step 4: Formatter - Clean SMS Body
- Step 5: Clean SMS for Odoo
- Step 6: Formatter - Extract Source Order
- Step 7: Formatter - Clean Source Order
- Step 8: Extract Sales Order ID
- Step 9: Clean Sales Order ID
- Step 10: Workiz - Get Historical Job
- Step 11: Workiz - Create Graveyard Job
- Step 12: Workiz - Update Status to Send SMS
- Step 13: Formatter - Get Current Date
- Step 14: JSON Escape Description
- Step 15: Extract Campaign Name
- Step 16: Extract Campaign ID
- Step 17: Odoo - Update Contact CRM Activity
- Step 18: JSON Escape Price List Text
- Step 19: Odoo - Update Reactivation Sent
- Step 20: Odoo - Update Opportunity

**How to delete:**
- Click the "..." menu on each step
- Select "Delete this step"
- Confirm deletion
- Repeat for all 19 steps (2-20)

### **Step 4: Add New Code Step**
**Add ONE step:**
- Click "+ Add step"
- Choose "Code by Zapier"
- Action Event: "Run Python"

### **Step 5: Configure Code Step**

**Input Data:**
```
opportunity_id: 1. Querystring Opportunity Id
```

**Code:**
```python
import urllib.request

# Fetch code from GitHub
url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_reactivation_sms_FINAL.py"
code = urllib.request.urlopen(url).read().decode()

# Execute with input_data
exec(code, {**globals(), 'input_data': input_data})
```

### **Step 6: Test**
- Click "Test step"
- Use a real opportunity_id (e.g., 43)
- Verify:
  - ✅ Graveyard job created in Workiz
  - ✅ Job status set to "API SMS Test Trigger"
  - ✅ Activity logged in Odoo
  - ✅ Contact updated
  - ✅ Opportunity linked

### **Step 7: Publish**
- Click "Publish"
- Turn Zap ON

---

## 📊 Before vs After

### **BEFORE:**
```
1. Catch Hook
2. Odoo API - Get Opportunity
3. Odoo API - Get Chatter
4. Formatter - HTML Tags
5. Formatter - Newlines
6. Formatter - Split Source Order
7. Formatter - Clean Order
8. Formatter - Split Order ID
9. Formatter - Clean ID
10. Workiz API - Get Job
11. Workiz API - Create Job
12. Workiz API - Update Status
13. Formatter - Date
14. Formatter - Escape JSON
15. Formatter - Extract Campaign
16. Formatter - Extract Campaign ID
17. Odoo API - Log Activity
18. Formatter - Escape Price List
19. Odoo API - Update Contact
20. Odoo API - Update Opportunity
```
**Total:** 20 steps, code in Zapier UI

### **AFTER:**
```
1. Catch Hook
2. Code by Zapier (fetches from GitHub)
```
**Total:** 2 steps, code in GitHub

---

## ✅ Benefits

**Maintainability:**
- ✅ One Python file (not 20 Zapier steps)
- ✅ Version control (GitHub history)
- ✅ Easy to update (push to GitHub)
- ✅ Can test locally before deploying

**Performance:**
- ✅ Faster execution (fewer HTTP hops)
- ✅ Single Zapier task count
- ✅ Fewer failure points

**Consistency:**
- ✅ Same pattern as Phases 3-6
- ✅ Same deployment workflow
- ✅ Same testing approach

---

## 🧪 Testing After Migration

**Use the test framework:**
1. Run Odoo Server Action on a dormant SO
2. Odoo triggers webhook with opportunity_id
3. New code fetches from GitHub
4. Verify graveyard job created
5. Verify SMS sent
6. Check Odoo activity log

**If issues:**
- Edit `zapier_reactivation_sms_FINAL.py` locally
- Push to GitHub main
- Next trigger fetches new code automatically

---

## ⚠️ CRITICAL: Input Field Mapping

**In Step 2 (Code by Zapier), map input_data:**

```python
# Input Data section in Zapier:
opportunity_id: {{1__querystring__opportunity_id}}
```

**This creates the input_data dict:**
```python
input_data = {
    "opportunity_id": "43"  # From webhook
}
```

---

## 🔗 Webhook URL (Don't Change)

The webhook URL from Step 1 stays the same:
```
https://hooks.zapier.com/hooks/catch/9761276/ugeosmk/
```

This is the URL Odoo calls (line 64 in `odoo_reactivation_launch.py`)

---

## 📋 Checklist

- [ ] Open Zap in edit mode
- [ ] Keep Step 1 (Catch Hook)
- [ ] Delete Steps 2-20
- [ ] Add Code by Zapier step
- [ ] Map input: `opportunity_id`
- [ ] Paste 3-line exec() code
- [ ] Test with real opportunity
- [ ] Verify graveyard job + SMS
- [ ] Publish Zap
- [ ] Monitor first 3-5 runs

---

**Ready to update the Zap! Code is on GitHub and waiting.**
