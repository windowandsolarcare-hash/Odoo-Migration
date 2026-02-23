# Complete Zapier Architecture
**A Window & Solar Care - Workiz ↔ Odoo Integration**  
**Updated:** 2026-02-07

---

## 🗺️ System Overview

```
WORKIZ (Source of Truth)
    ↓
ZAPIER (Automation Layer)
    ├── Zap 1: Phase 3 (New Job Creation)
    ├── Zap 2: Phase 4 (Job Status Update)
    └── Zap 3: Phase 5 (Auto Scheduler)
    ↓
ODOO (Business Operations)
```

---

## 📊 All Zaps Summary

| Zap | Name | Trigger | Purpose | Status |
|-----|------|---------|---------|--------|
| **Zap 1** | Phase 3: New Job Creation | Workiz: New Job | Create SO in Odoo (Paths A/B/C) | ✅ Ready |
| **Zap 2** | Phase 4: Status Update | Workiz: Status Changed | Update SO + Payment fields | ✅ Ready |
| **Zap 3** | Phase 5: Auto Scheduler | Phase 4 webhook | Create next job OR reminder | ✅ Ready |

**Separate Systems:**
- **Phase 2:** Odoo Server Actions (Reactivation Engine)

---

## 🔄 Data Flow Diagram

```
NEW JOB IN WORKIZ
    ↓
┌───────────────────┐
│   ZAP 1: PHASE 3  │
│  New Job Creation │
└─────────┬─────────┘
          ↓
    Search Contact
    (by ClientId)
          ↓
    ┌─────┴─────┐
    ↓           ↓
  Found      Not Found
    ↓           ↓
Path A/B     Path C
    ↓           ↓
    └─────┬─────┘
          ↓
   Create SO in Odoo
          ↓
[SO EXISTS IN ODOO]


STATUS CHANGE IN WORKIZ
    ↓
┌───────────────────┐
│   ZAP 2: PHASE 4  │
│   Status Update   │
└─────────┬─────────┘
          ↓
    Search SO by UUID
          ↓
    ┌─────┴─────┐
    ↓           ↓
  Found      Not Found
    ↓           ↓
Update SO   Call Zap 1
    ↓        (Create)
    ↓           ↓
    └─────┬─────┘
          ↓
   Status = "Done"?
          ↓
    ┌─────┴─────┐
    ↓           ↓
   Yes         No
    ↓           ↓
Payment      Skip
 Updates
    ↓
Trigger Zap 3


DONE JOB DETECTED
    ↓
┌───────────────────┐
│   ZAP 3: PHASE 5  │
│   Auto Scheduler  │
└─────────┬─────────┘
          ↓
  Check service type
          ↓
    ┌─────┴─────┐
    ↓           ↓
Maintenance  On Demand
    ↓           ↓
Create next  Create Odoo
Workiz job   activity
    ↓           ↓
(User adds   (6 months,
line items)   Sunday)
```

---

## 📋 Zap 1: Phase 3 - New Job Creation

### Trigger
**Workiz Webhook:** New Job Created

### Input
- `job_uuid` from Workiz

### Process
1. Get job details from Workiz API
2. Search for Contact by ClientId (ref field)
3. Determine path:
   - **Path A:** Contact + Property exist → Create SO
   - **Path B:** Contact exists, Property missing → Create Property + SO
   - **Path C:** Both missing → Create Contact + Property + SO
4. Update Property fields
5. Create Sales Order with line items

### Output
- New SO created in Odoo
- Contact and/or Property created if needed

### Script
- `zapier_phase3_FLATTENED_FINAL.py` (1,118 lines)

### Deployment Guide
- `Zapier_Deployment_Guide_FINAL.md`

---

## 📋 Zap 2: Phase 4 - Job Status Update

### Trigger
**Workiz Webhook:** Job Status Changed (any status)

### Input
- `job_uuid` from Workiz

### Process
1. Get job details from Workiz API
2. Search for SO by `x_studio_x_studio_workiz_uuid`
3. If SO exists:
   - Update SO fields (status, tech, notes, etc.)
   - Update Property fields
4. If SO doesn't exist:
   - Call Phase 3 logic to create it
5. If status = "Done":
   - Add payment fields (`x_studio_is_paid`, `x_studio_tip_amount`)
   - Update Property last visit date
   - Post to chatter
   - **Trigger Zap 3** (Phase 5)

### Output
- SO updated with latest data
- Payment fields populated if Done
- Phase 5 triggered if Maintenance/On Demand

### Script
- `zapier_phase4_FLATTENED_FINAL.py` (1,046 lines)

### Deployment Guide
- `Zapier_Phase4_Deployment_Guide.md`

---

## 📋 Zap 3: Phase 5 - Auto Job Scheduler

### Trigger
**Webhooks by Zapier:** Catch Hook (from Phase 4)

### Input (from Phase 4)
- `job_uuid` - Workiz job UUID
- `property_id` - Odoo property ID
- `contact_id` - Odoo contact ID
- `customer_city` - Property city

### Process
1. Get job details from Workiz API
2. Check `type_of_service`:
   - **"Maintenance"** → Path 5A
   - **"On Demand"** → Path 5B

#### Path 5A: Maintenance
1. Parse `frequency` ("3 Months", "4 Months", etc.)
2. Calculate target date
3. Apply city-aware scheduling (route optimization)
4. Get line items:
   - If `alternating` = "Yes" → From 2 jobs back
   - Else → From current job
5. Format line items for custom field
6. Create new job in Workiz (HTTP 204)
7. User adds line items + sets status manually

#### Path 5B: On Demand
1. Calculate follow-up date (6 months, Sunday)
2. Build activity description
3. Create `mail.activity` in Odoo
4. NO Workiz job created

### Output
- **5A:** New scheduled job in Workiz (user finishes)
- **5B:** Activity reminder in Odoo (no Workiz clutter)

### Script
- `zapier_phase5_FLATTENED_FINAL.py` (680 lines)

### Deployment Guide
- `Zapier_Phase5_Deployment_Guide.md`

---

## 🔗 Zap Communication

### Zap 1 → Standalone
- No dependencies
- Creates foundation (Contact, Property, SO)

### Zap 2 → Calls Zap 1 if needed
- If SO doesn't exist, uses Phase 3 logic
- Phase 3 imported as module in Phase 4 script

### Zap 2 → Triggers Zap 3
- At end of Phase 4, if status = "Done"
- Sends webhook to Phase 5 with data
- **OR** uses Zapier Sub-Zap feature

### Zap 3 → Standalone
- Triggered only by Phase 4
- Creates jobs/activities independently

---

## ⚙️ Setup Sequence

### 1. Deploy Zap 1 (Phase 3)
- Set up Workiz "New Job" trigger
- Test with Path A, B, and C scenarios
- Verify SOs created correctly

### 2. Deploy Zap 2 (Phase 4)
- Set up Workiz "Status Changed" trigger
- Test with existing SO
- Test with missing SO (should call Phase 3)
- Test "Done" status with payment fields

### 3. Deploy Zap 3 (Phase 5)
- Set up Webhooks trigger
- Copy webhook URL
- Add to Phase 4 script (trigger Phase 5)
- Test Maintenance path
- Test On Demand path

### 4. Add Workiz Custom Field
- Field name: `next_job_line_items`
- Type: Text/Textarea
- For: Job records

### 5. Monitor & Adjust
- Watch Zapier logs for errors
- Verify data in Odoo and Workiz
- Adjust city routing if needed
- Train user on 30-second workflow

---

## 📊 Token/Cost Optimization

### Why Separate Zaps?

**Single Mega-Zap (Phase 3+4+5):**
- ❌ ~2,800+ lines of code
- ❌ Exceeds Zapier limits
- ❌ Hard to debug
- ❌ All-or-nothing testing

**Separate Zaps:**
- ✅ Each under 1,200 lines
- ✅ Within Zapier limits
- ✅ Modular testing
- ✅ Can disable Phase 5 if needed
- ✅ Clear separation of concerns

### Token Savings Strategies Used:

1. **Reuse Phase 3 in Phase 4:** Imported as module (not duplicated)
2. **Atomic functions:** Shared across phases
3. **Minimal API calls:** Only fetch needed data
4. **Smart caching:** Store data in variables vs re-fetch

---

## 🎯 Business Value

### Automation Achieved:

**New Jobs (Phase 3):**
- ✅ 100% automated contact/property/SO creation
- ✅ Eliminates manual data entry
- ✅ Ensures data consistency

**Job Updates (Phase 4):**
- ✅ 100% automated SO status sync
- ✅ Payment tracking when Done
- ✅ Property visit history
- ✅ Chatter notifications

**Next Job Scheduling (Phase 5):**
- ✅ 90% automated (line items need 30 sec manual)
- ✅ Smart city-based routing
- ✅ Alternating service logic
- ✅ Clean On Demand reminders

### Time Saved:
- **Per new job:** 2-3 minutes → ~5 seconds
- **Per status update:** 1-2 minutes → ~3 seconds
- **Per next job creation:** 5-7 minutes → 30 seconds

**Estimated annual savings:** 100-150 hours

---

## 🛠️ Maintenance

### Regular Tasks:
- Monitor Zapier task usage (monthly)
- Check error logs (weekly at first, then monthly)
- Verify data accuracy spot checks (monthly)

### When to Update:
- **Add new city:** Update `city_schedule` in Phase 5
- **Change routing:** Modify day assignments
- **New custom fields:** Add to Phase 3/4 mappings
- **Workiz API changes:** Update endpoints/fields

### Backup Strategy:
- All scripts in version control (this repo)
- Document any changes in `CHANGELOG.md` (create if needed)
- Keep modular versions for reference

---

## 📈 Future Enhancements

### Phase 5C: Route Optimization
- Consider proximity to other jobs
- Suggest optimal day based on distance
- Integration with Google Maps API

### Phase 6: Invoice Automation (Potential)
- Sync invoices from Workiz to Odoo
- Payment tracking
- Accounting integration

### Phase 7: Reporting Dashboard (Potential)
- Odoo analytics on job completion
- Revenue tracking
- Customer retention metrics

---

## ✅ Deployment Checklist

### Pre-Deployment:
- [ ] All 3 Zap scripts created and tested locally
- [ ] Workiz webhooks configured
- [ ] Custom field `next_job_line_items` added to Workiz
- [ ] Odoo custom fields verified

### Deployment:
- [ ] Zap 1 (Phase 3) deployed and tested
- [ ] Zap 2 (Phase 4) deployed and tested
- [ ] Zap 3 (Phase 5) deployed and tested
- [ ] Phase 4 → Phase 5 webhook connection tested

### Post-Deployment:
- [ ] Monitor first 10 runs of each Zap
- [ ] Verify data accuracy in Odoo
- [ ] Verify jobs created correctly in Workiz
- [ ] Train user on Phase 5 manual workflow
- [ ] Document any issues and resolutions

---

**Complete integration ready for deployment!**  
**Total Zaps:** 3  
**Total Lines of Code:** ~2,844  
**Automation Coverage:** ~95% (5% manual for line items)
