# Phase 5: Automated Job Scheduling - Implementation Summary
**Created:** 2026-02-07  
**Status:** ✅ COMPLETE (Modular Components)

---

## 🎯 Overview

**Purpose:** Automatically create next service job (Maintenance) or follow-up reminder (On Demand) after job marked "Done"

**Trigger:** Phase 4 detects "Done" status + Maintenance/On Demand service type

**Integration:** Phase 4 → Phase 5 (seamless handoff)

---

## 🔀 Two Paths

### Path 5A: Maintenance (Recurring Service Agreement)
**What it does:**
- ✅ Calculates next service date based on frequency
- ✅ Applies city-aware scheduling (routes like Calendly)
- ✅ Creates new job in Workiz with all customer/job details
- ✅ Copies custom fields (gate_code, pricing, frequency, etc.)
- ✅ Formats line items as text in custom field
- ⚠️ **User adds line items manually** (30 seconds - API limitation)

### Path 5B: On Demand (No Recurring Agreement)
**What it does:**
- ✅ Creates Odoo activity reminder (NOT a Workiz job)
- ✅ Sets due date to Sunday of target week
- ✅ Includes last service details and link
- ✅ Keeps Workiz schedule clean (no "Sunday Nightmare")

---

## 📁 Files Created

### Atomic Functions

**Utility Functions:**
- `functions/utils/calculate_next_service_date.py`
  - Parses frequency ("3 Months", "4 Months", etc.)
  - Applies city-aware scheduling logic
  - Returns next service datetime

- `functions/utils/get_line_items_for_next_job.py`
  - Handles alternating service logic (2 jobs back vs current)
  - Filters out tips, discounts, quotes
  - Formats line items for custom field reference

**Workiz Functions:**
- `functions/workiz/create_next_maintenance_job.py`
  - Creates new job in Workiz (HTTP 204 response)
  - Includes line items reference in custom field
  - Adds previous job UUID to notes

**Odoo Functions:**
- `functions/odoo/create_followup_activity.py`
  - Creates `mail.activity` for On Demand follow-up
  - Sets due date 6 months out (Sunday)
  - Links to contact record

- `functions/odoo/get_property_city.py`
  - Fetches city from property for route scheduling
  - Used by Phase 4 when calling Phase 5

- `functions/odoo/search_all_sales_orders_for_property.py`
  - Gets job history for alternating logic
  - Ordered by date DESC

### Routers

- `phase5_auto_scheduler.py`
  - Main orchestrator for Phase 5
  - Routes to 5A (Maintenance) or 5B (On Demand)
  - Called by Phase 4 after "Done" detection

### Integration

- `phase4_status_update_router.py` (UPDATED)
  - Detects "Done" status + service type
  - Calls Phase 5 with required data
  - Passes workiz_job, property_id, contact_id, customer_city

---

## 🧪 Workiz API Test Results

### ✅ What Works:
- Job creation via `POST /job/create/`
- Returns HTTP 204 (success, no UUID)
- Required fields: FirstName, LastName, Address, City, State, PostalCode, Phone, JobDateTime, JobType

### ❌ API Limitation Discovered:
- **LineItems CANNOT be added via API**
- Both create and update reject LineItems as "Invalid Field"
- No separate add-line-item endpoint exists

### 💡 Solution:
- Store line items reference in **custom Workiz field** (e.g., `next_job_line_items`)
- Format: "Windows In & Out: $85\nSolar Panels: $45"
- User adds manually in Workiz UI (30 seconds)

---

## 🗺️ City-Aware Scheduling

**Route Mapping (From Actual Calendly Setup):**
```
City              → Preferred Day    → Calendly Availability
Palm Springs      → Friday           → Fri
Rancho Mirage     → Thursday         → Thu, Fri
Palm Desert       → Thursday         → Thu
Indian Wells      → Wednesday        → Wed, Thu
Indio/La Quinta   → Wednesday        → Wed
Hemet             → Tuesday          → Tue
```

**Logic:**
- Find nearest preferred day to target date (±7 days)
- Example: 3 months from today = March 15 (Thursday)
  - Customer in Palm Desert → prefer Wednesday
  - Adjust: March 14 (Wednesday) - 1 day before target

---

## 🔄 Data Flow

```
Phase 4: Job marked "Done"
    ↓
Check: type_of_service
    ↓
    ┌──────────────┴──────────────┐
    ↓                             ↓
Maintenance                   On Demand
    ↓                             ↓
Phase 5A                      Phase 5B
    ↓                             ↓
Calculate next date           Estimate 6 months
Apply city scheduling         Set to Sunday
Get line items:               Create Odoo activity
- If alternating: 2 jobs back
- Else: current job
    ↓
Format for custom field
    ↓
Create Workiz job
(HTTP 204 - no UUID)
    ↓
User adds line items
& sets status manually
```

---

## 🎯 What Gets Automated

### Maintenance Path (5A):
- ✅ Date calculation (frequency-based)
- ✅ City-aware scheduling
- ✅ Job creation with all fields except line items
- ✅ Customer info (from previous job)
- ✅ Job type, team, tags
- ✅ Custom fields (gate_code, pricing, frequency, etc.)
- ✅ Line items reference in custom field
- ✅ Link to previous job
- ⚠️ User manually: Add 2-3 line items, set status (30 sec)

### On Demand Path (5B):
- ✅ Activity creation in Odoo
- ✅ Due date calculation (6 months, Sunday)
- ✅ Service history summary
- ✅ Link to customer & last job
- ✅ NO Workiz job clutter

---

## 📊 Phase 5 Dependencies

**Requires data from Phase 4:**
- `workiz_job` - Full Workiz job data
- `property_id` - For job history lookup (alternating)
- `contact_id` - For Odoo activity
- `customer_city` - For route-based scheduling

**Phase 4 provides after:**
- Job marked "Done"
- SO updated with payment fields
- Property last visit date updated
- Chatter message posted

---

## ✅ Success Metrics

### Maintenance Customers:
- New job auto-created in Workiz
- Date calculated correctly based on frequency
- Date adjusted to city routing day
- Line items reference visible in custom field
- Previous job UUID in notes
- Customer receives "Next Job" text (after user sets status)

### On Demand Customers:
- Activity created in Odoo (visible on Contact)
- Due date on Sunday of target week
- User reminded to follow up
- NO clutter in Workiz schedule
- No fake "Sunday jobs"

---

## 🚀 Next Steps

### To Deploy:
1. **Add custom field in Workiz:**
   - Field name: `next_job_line_items` (or similar)
   - Type: Text/Textarea
   - Purpose: Store line items reference

2. **Test Phase 5A (Maintenance):**
   - Mark a maintenance job as "Done" in Workiz
   - Verify Phase 4 triggers Phase 5
   - Check new job created in Workiz
   - Verify date calculation and city scheduling
   - Confirm line items reference in custom field

3. **Test Phase 5B (On Demand):**
   - Mark an on-demand job as "Done"
   - Verify Phase 4 triggers Phase 5
   - Check activity created in Odoo
   - Verify due date (Sunday, 6 months out)
   - Confirm NO Workiz job created

4. **Flatten for Zapier:**
   - Combine Phase 3 + 4 + 5 into single script
   - Or: Keep as separate Zaps with webhooks
   - Decision based on token limits and performance

5. **User Training:**
   - Show where to find line items reference in Workiz
   - Teach 30-second manual process:
     1. Open new job
     2. Copy line items from custom field
     3. Add to job
     4. Set status to "Send Next Job - Text"

---

## 📝 Technical Notes

### Workiz Job Creation:
- Endpoint: `POST /job/create/`
- Success: HTTP 204 (No Content)
- No UUID returned in response
- Cannot retrieve UUID after creation (limitation)

### Alternating Service Logic:
- Query: Get all SOs for property, ordered by date DESC
- If alternating: Use line items from index [1] (2 jobs back)
- Else: Use line items from current job

### Custom Field Format:
```
Windows In & Out - Full Service: $85.00
Solar Panel Cleaning: $45.00
```

---

## 🔧 Known Limitations

1. **LineItems API:** Cannot add via Workiz API (user must add manually)
2. **No UUID from create:** Can't immediately update status to trigger SMS
3. **City mapping:** Currently uses simple keyword matching (could be enhanced with fuzzy matching)
4. **Activity type ID:** Hardcoded to 2 (should verify correct ID in Odoo)

---

## 💡 Future Enhancements

### Phase 5C: Smart Route Optimization
- Consider proximity to other scheduled jobs
- Suggest optimal day based on route efficiency
- Integrate with mapping/distance API
- Example: "2 miles away on Tuesday vs 10 miles on Monday → choose Tuesday"

### Enhancements:
- Auto-set status if Workiz adds webhook for job creation
- Research alternative LineItems API (contact Workiz support)
- Add fuzzy city matching for typos/variations
- Build Odoo UI widget showing "Next Job Details"

---

**Status:** ✅ Phase 5 complete and integrated with Phase 4  
**Ready for:** Testing and Zapier deployment preparation  
**Files:** All modular components created and documented
