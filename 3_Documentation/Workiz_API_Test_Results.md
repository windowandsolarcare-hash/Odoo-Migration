# Workiz API Test Results - Job Creation
**Date:** 2026-02-07  
**Purpose:** Determine how to create jobs with LineItems for Phase 5

**Use this file as the source of truth for Workiz API field names (e.g. LineItems structure). Do not guess field names — look them up here or in Phase_3_4_5_Reference_Summary.md, or ask the user.**

---

## ✅ Test Results

### Test 1: Get LineItems Structure ✅ PASS
**Endpoint:** `GET /job/get/{UUID}`

**LineItems Structure (field names to use in code):**
```json
[
  {
    "Id": 30113789,
    "Quantity": 1,
    "Price": 85,
    "Cost": 0,
    "Taxable": 0,
    "InventorySync": 0,
    "Name": "Windows In & Out - Full Service",
    "Description": "...",
    "BrandName": "",
    "BrandId": "",
    "Type": "service",
    "ModelNum": ""
  }
]
```

**Key Fields for Phase 5:**
- `JobType`: 'Windows Inside & Outside Plus Screens' (must match exactly)
- `type_of_service`: 'Maintenance' or 'On Demand'
- `frequency`: '4 Months', '3 Months', '6 Months', etc.
- `alternating`: '' (empty) or '1'/'0' or 'Yes'/'No'

---

### Test 2: Create Job WITHOUT LineItems ✅ SUCCESS

**Endpoint:** `POST /job/create/`

**Response:** **HTTP 204 No Content** (Success! Job created)

**Required Fields:**
- ✅ `ClientId` - Customer ID (required)
- ✅ `FirstName` - Required
- ✅ `LastName` - Required
- ✅ `Address` - Required
- ✅ `City` - Required
- ✅ `State` - Required
- ✅ `PostalCode` - Required
- ✅ `Phone` - Required
- ✅ `JobDateTime` - Required (format: 'YYYY-MM-DD HH:MM:SS')
- ✅ `JobType` - Required (must match exact value in Workiz system)

**Fields NOT Allowed:**
- ❌ `LocationId` - Auto-assigned from ClientId, cannot be in create payload
- ❌ `LineItems` - Invalid Field (see Test 3)

**Important Notes:**
1. Workiz returns **HTTP 204** (No Content) on success
2. **No UUID is returned** in the response
3. To get the new job's UUID, would need to:
   - Search jobs by ClientId + JobDateTime
   - Or use Workiz webhook for "Job Created" event
   - Or wait for user to manually note the UUID

---

### Test 3: Create Job WITH LineItems ❌ FAIL

**Endpoint:** `POST /job/create/`

**Result:** **400 Bad Request** - "Invalid Field"

**Error Response:**
```json
{
  "error": true,
  "code": 400,
  "msg": "Error Validating Fields",
  "details": {
    "LineItems": "Invalid Field"
  }
}
```

**Conclusion:** LineItems **cannot** be included in create payload.

---

### Test 4: Update Job to Add LineItems ❌ FAIL

**Endpoint:** `POST /job/update/`

**Result:** **400 Bad Request** - "Invalid Field"

**Error Response:**
```json
{
  "error": true,
  "code": 400,
  "msg": "Error Validating Fields",
  "details": {
    "LineItems": "Invalid Field"
  }
}
```

**Conclusion:** LineItems **cannot** be added via update either.

---

## 🔴 Critical Discovery

### LineItems Cannot Be Managed Via Workiz API

**Both create and update reject LineItems as "Invalid Field"**

This means:
- ❌ Cannot include LineItems in `POST /job/create/`
- ❌ Cannot add LineItems via `POST /job/update/`
- ❌ No separate `POST /job/addLineItem/` endpoint exists

**Possible Explanations:**
1. LineItems can only be managed via Workiz UI
2. There's a separate undocumented endpoint for LineItems
3. LineItems require different authentication/permissions
4. LineItems must be added after job is in specific status

---

## 💡 Phase 5 Implications

### Impact on Automated Job Scheduling

**Original Plan:** Create next job with line items from previous job

**Reality:** Cannot automate line item copying via API

### Solutions for Phase 5:

#### Option 1: Create Job Without LineItems (Recommended)
- ✅ Create job with all other fields (datetime, type, team, tags, etc.)
- ✅ Set status to trigger SMS to customer
- ⚠️ User must manually add line items in Workiz UI
- 💡 Could add reminder in job notes: "ADD LINE ITEMS: [list items here]"

#### Option 2: Include Pricing in Job Notes
- ✅ Create job without line items
- ✅ Add field like `JobNotes` with line item details:
  ```
  LINE ITEMS TO ADD:
  - Window Cleaning: $150
  - Solar Panel Cleaning: $85
  ```
- ⚠️ User still adds manually, but has pricing reference

#### Option 3: Hybrid Approach
- ✅ Create job in Workiz (no line items)
- ✅ Store expected line items in Odoo custom field on SO
- ✅ User copies from Odoo when adding to Workiz
- 💡 Could even build Odoo UI widget to show "Next Job Details"

#### Option 4: Research Alternative (Future)
- 🔍 Contact Workiz support about LineItems API
- 🔍 Check if there's a different endpoint or method
- 🔍 Review Workiz API documentation for updates

---

## ✅ What We CAN Automate

Even without LineItems API, Phase 5 can still automate:

### Maintenance Path:
- ✅ Calculate next service date based on frequency
- ✅ Apply city-aware scheduling (route optimization)
- ✅ Create new job in Workiz with:
  - Date/time
  - Customer info (pulled from original job)
  - Job type
  - Team assignment
  - Tags
  - Custom fields (gate_code, pricing, frequency, etc.)
  - Status to trigger SMS
- ✅ Add note about which line items to add
- ✅ Link to previous job for reference

### On Demand Path:
- ✅ Create Odoo activity reminder (no Workiz job)
- ✅ Set due date for follow-up
- ✅ Include last service details
- ✅ Link to customer record

---

## 📊 Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Create Job | ✅ Works | HTTP 204, no UUID returned |
| Required Fields | ✅ Confirmed | FirstName, LastName, Address, City, State, PostalCode, Phone, JobDateTime, JobType |
| LocationId | ❌ Invalid | Auto-assigned from ClientId |
| LineItems in Create | ❌ Invalid | Cannot include in payload |
| LineItems via Update | ❌ Invalid | Cannot add after creation |
| Get Job Details | ✅ Works | Can see LineItems from existing jobs |

---

## 🎯 Recommended Phase 5 Approach

1. **Create job with all fields EXCEPT LineItems**
2. **Add detailed note in JobNotes with pricing:**
   ```
   AUTO-SCHEDULED - Next 4-month service
   
   PRICING FROM PREVIOUS JOB:
   • Windows In & Out - Full Service: $85
   • (Add manually in Workiz)
   
   Previous Job: [UUID link]
   ```

3. **User workflow:**
   - Receives notification of new job created
   - Opens job in Workiz
   - Copies line items from note or previous job
   - Saves

4. **Still provides value:**
   - ✅ Eliminates date calculation
   - ✅ Automates city-based scheduling
   - ✅ Pre-fills all customer/job details
   - ✅ Triggers SMS to customer
   - ⚠️ User adds 2-3 line items manually (30 seconds)

---

**Next Steps:**
1. Update Phase 5 technical plan with LineItems limitation
2. Implement job creation without LineItems
3. Add pricing details to JobNotes for user reference
4. Consider future research into LineItems API possibility

---

**Test Files:**
- `test_workiz_create_job_auto.py` - Automated test script
- Clean up: Jobs were not created with UUIDs we can delete (HTTP 204 limitation)
