# A Window & Solar Care - Complete Phase Overview
**Last Updated:** 2026-02-07  
**Project:** Workiz → Odoo Migration & Integration

---

## 🎯 Project Structure

```
Phase 1: Historical Data Migration
Phase 2: Dormant Customer Reactivation Engine
Phase 3: New Job Creation (Workiz → Odoo)
Phase 4: Job Status Update (Workiz → Odoo)
Phase 5: [TBD]
```

---

## Phase 1: Historical Data Migration
**Status:** ✅ COMPLETE

### Purpose
Migrate 6 years of historical job data from Workiz to Odoo

### Key Details
- **Reference File:** `Workiz_6Year_Done_History_Master.csv`
- **External ID Format:** `workiz_[id]` (Mirror V31.11 logic)
- **Hierarchy:** Contact → Property → Sales Order

### Status
Completed prior to current work. All historical data now in Odoo.

---

## Phase 2: Dormant Customer Reactivation Engine
**Status:** ✅ COMPLETE & DEPLOYED

### Purpose
Re-engage customers who haven't been serviced recently by creating targeted reactivation campaigns

### Workflow
```
Odoo Sales Order (Dormant)
    ↓
Analyze service history
    ↓
Calculate updated pricing (5% annual inflation)
    ↓
Generate personalized SMS message
    ↓
Create CRM Opportunity with expected revenue
    ↓
Post SMS preview to Opportunity chatter
    ↓
Trigger Zapier webhook to send SMS
```

### Key Features
- **Smart Pricing Engine:**
  - Analyzes past services from all customer Sales Orders
  - Calculates 5% compounded annual price increase
  - Rounds to nearest $5 (minimum $85)
  - Solar services: Fixed price (no inflation)
  - Filters out: Tips, discounts, legacy items, quotes

- **City-Aware Calendly Links:**
  - Maps customer city to specific Calendly booking URLs
  - Pre-fills customer name and address in booking form
  - Supported cities: Palm Springs, Rancho Mirage, Palm Desert, Indian Wells, Indio, La Quinta, Hemet
  - Default: General Booking (gb)

- **Opportunity Creation:**
  - Creates `crm.lead` (Opportunity) record
  - Sets stage: "Reactivation" (ID: 5)
  - Calculates `expected_revenue` from all services
  - Stores reference data: Source Order ID, Primary Service, Price List
  - Updates Contact: `x_studio_last_reactivation_sent` (cooldown tracking)

- **SMS Message Format:**
  ```
  Hi [FirstName], I hope all is well. It's Window & Solar Care.
  
  We last serviced your home on [LastVisitDate]. It's been a while and we'd love to stop by again!
  
  Your updated 2026 estimates for services we've done for you:
  • Window Cleaning: $150
  • Solar Panel Cleaning: $85
  
  Tap here to schedule Online:
  [Calendly URL with pre-filled data]
  
  Or reply to this text and we will reply back with a date and time.
  
  Dan Saunders
  Window & Solar Care
  855-245-2273
  Reply STOP to unsubscribe
  ```

### Files
- **Launch Script:** `1_Active_Odoo_Scripts/odoo_reactivation_launch.py` (210 lines)
- **Preview Script:** `1_Active_Odoo_Scripts/odoo_reactivation_preview.py` (120 lines)

### Odoo Custom Fields Used
- `x_studio_last_reactivation_sent` (Contact) - Cooldown tracking
- `x_studio_prices_per_service` (Property) - Service pricing menu
- `x_odoo_contact_id` (Opportunity) - Contact reference
- `x_historical_workiz_uuid` (Opportunity) - Original Workiz UUID
- `x_workiz_graveyard_link` (Opportunity) - Legacy link
- `x_workiz_graveyard_uuid` (Opportunity) - Legacy UUID
- `x_primary_service` (Opportunity) - Main service for this customer
- `x_price_list_text` (Opportunity) - Formatted price list

### Integration Points
- **Zapier Webhook:** `https://hooks.zapier.com/hooks/catch/9761276/ugeosmk/`
- **Webhook Trigger:** Passes `opportunity_id` to Zapier for SMS sending

### Deployment
✅ Active in Odoo as Server Action buttons:
- "PREVIEW Reactivation" → Shows SMS in chatter (read-only)
- "LAUNCH Reactivation" → Creates Opportunity + triggers Zapier webhook

---

## Phase 3: New Job Creation (Master Router)
**Status:** ✅ COMPLETE & READY TO DEPLOY

### Purpose
Create Sales Orders in Odoo when new jobs are created in Workiz

### Trigger
**Workiz Webhook:** New Job Created

### Architecture
3-Path Router based on Contact and Property existence:

```
Workiz New Job
    ↓
Search Contact by ClientId
    ↓
    ┌─────────┴─────────┐
    ↓                   ↓
  Found              Not Found
    ↓                   ↓
Search Property      PATH C: Create All
    ↓                (Contact + Property + SO)
    ┌────┴────┐
    ↓         ↓
  Found    Not Found
    ↓         ↓
  PATH A   PATH B
  (SO only) (Property + SO)
```

### Path Details

**Path A: Existing Contact + Existing Property**
- Create Sales Order only
- Update Property fields with latest Workiz data

**Path B: Existing Contact + New Property**
- Create Property (linked to Contact)
- Create Sales Order
- Update Property fields

**Path C: New Contact + New Property**
- Create Contact with ClientId as `ref`
- Create Property (linked to Contact)
- Create Sales Order
- Update Property fields

### Key Features
- **Smart Search:** Uses ClientId (not name/address) for Contact lookup
- **Tag Merging:** Combines Contact tags + Workiz job tags
- **Product Matching:** Searches for existing Odoo products by name
- **Time Conversion:** Pacific → UTC for Odoo `date_order`
- **External ID:** Sets `x_studio_x_studio_workiz_uuid` on Sales Order
- **Team Formatting:** Extracts and formats team member names
- **Auto-Confirm:** Calls `action_confirm` on Sales Order after creation

### Sales Order Fields Mapped

| Odoo Field | Workiz Source | Notes |
|-----------|---------------|-------|
| `name` | SerialId | Formatted as 6-digit (e.g., "004111") |
| `partner_id` | Contact | Contact ID |
| `partner_shipping_id` | Property | Property ID |
| `x_studio_x_studio_workiz_uuid` | UUID | Unique job identifier |
| `x_studio_x_workiz_link` | UUID | Deep link to Workiz job |
| `x_studio_x_studio_workiz_status` | SubStatus (or Status) | Job status |
| `x_studio_x_studio_lead_source` | JobSource | Lead origin |
| `x_studio_x_studio_x_studio_job_type` | JobType | Service type |
| `x_studio_x_studio_workiz_tech` | Team | Formatted names |
| `x_studio_x_gate_snapshot` | gate_code | Gate access (lowercase!) |
| `x_studio_x_studio_pricing_snapshot` | pricing | Pricing notes (lowercase!) |
| `x_studio_x_studio_notes_snapshot1` | JobNotes + Comments | Combined |
| `date_order` | JobDateTime | Converted to UTC |
| `tag_ids` | Tags + Contact tags | Merged |
| `order_line` | LineItems | Product, quantity, price |

### Property Fields Mapped

| Odoo Field | Workiz Source | Notes |
|-----------|---------------|-------|
| `x_studio_x_gate_code` | gate_code | Direct mapping |
| `x_studio_x_pricing` | pricing | Direct mapping |
| `comment` | JobNotes + Comments | Internal notes |
| `x_studio_x_frequency` | frequency | Service frequency |
| `x_studio_x_alternating` | alternating | Yes/No (1/0 converted) |
| `x_studio_x_type_of_service` | type_of_service | Service category |
| `x_studio_x_studio_location_id` | LocationId | Workiz property ID |

**Note:** `x_studio_x_studio_last_property_visit` is NOT updated during job creation (only on completion via Phase 4)

### Files
- **Modular Components:** `2_Modular_Phase3_Components/` folder
  - `tier3_workiz_master_router.py` - Main orchestrator
  - `functions/odoo/` - Odoo API atomic functions
  - `functions/workiz/` - Workiz API atomic functions
  - `config.py` - Credentials
- **Flattened Script:** `zapier_phase3_FLATTENED_FINAL.py` (1,118 lines)
- **Documentation:** `Zapier_Deployment_Guide_FINAL.md`

### Deployment
Ready for Zapier Code by Zapier with single input: `job_uuid`

### Historical Note
This Phase 3 superseded earlier work ("Phase 3A-F" or "Inbound Engine") which handled Calendly → Workiz → Odoo flow for reactivation bookings. That earlier work may be revisited for Phase 5.

---

## Phase 4: Job Status Update
**Status:** ✅ COMPLETE & READY TO DEPLOY

### Purpose
Update existing Sales Orders when Workiz job status changes (any status, not just "Done")

### Trigger
**Workiz Webhook:** Job Status Changed

### Workflow
```
Workiz Status Change
    ↓
Get Workiz Job Details
    ↓
Search for SO by UUID
    ↓
    ┌────────┴────────┐
    ↓                 ↓
  SO Found         SO Not Found
    ↓                 ↓
Update SO         Call Phase 3
Update Property   (Create SO)
    ↓                 ↓
Status = "Done"?  Apply Phase 4 Updates
    ↓
  Yes → Add Payment Fields
        Update Last Visit Date
        Post to Chatter
```

### Key Features

**Always Updated (Any Status):**
- Status/SubStatus
- Tech/Team
- Gate Code snapshot
- Pricing snapshot
- Notes snapshot
- Date/Time
- Job Type
- Lead Source
- Property fields (gate code, pricing, notes, frequency, service type, alternating)

**"Done" Status Specific:**
- **Payment Fields:**
  - `x_studio_is_paid` (Boolean: True if JobAmountDue = 0)
  - `x_studio_tip_amount` (Float: Extracted from LineItems)
- **Property Last Visit:**
  - `x_studio_x_studio_last_property_visit` (Date only)
- **Chatter Message:**
  - Format: "Status updated to: Done on 2026-02-06 21:09:52; Paid in Full; Tip: $15.0"
  - Single line, semicolon-separated, plain text

### Chatter Message Examples

**Status Change (Not Done):**
```
Status updated to: Scheduled on 2026-02-05 10:30:00
```

**Status Change to Done (Paid):**
```
Status updated to: Done on 2026-02-06 21:09:52; Paid in Full; Tip: $15.0
```

**Status Change to Done (Unpaid):**
```
Status updated to: Done on 2026-02-06 21:09:52; Unpaid ($50 due)
```

### Integration with Phase 3
Phase 4 **imports and reuses** Phase 3 logic! If a Sales Order doesn't exist when a status update arrives, Phase 4 calls `phase3_create_so()` to create it using the appropriate path (A/B/C), then applies Phase 4-specific updates.

**Token Efficiency:** By importing Phase 3 as a module, we save ~1,000 lines of duplicate code.

### Files
- **Modular Components:** `2_Modular_Phase3_Components/`
  - `phase4_status_update_router.py` - Main orchestrator
  - `functions/odoo/search_sales_order_by_uuid.py` - Find SO by UUID
  - `functions/odoo/update_sales_order.py` - Update SO fields
  - `functions/odoo/post_chatter_message.py` - Post to activity log
  - `functions/workiz/extract_tip_from_line_items.py` - Parse tip from LineItems
- **Flattened Script:** `zapier_phase4_FLATTENED_FINAL.py` (1,046 lines)
- **Documentation:** `Zapier_Phase4_Deployment_Guide.md`

### Deployment
Ready for Zapier Code by Zapier with single input: `job_uuid`

### Testing
✅ Successfully tested with:
- **Job IC3ZC9** (Blair Becker - Done status)
- SO #003878 (ID: 15804)
- Payment fields populated correctly
- Property last visit updated
- Chatter message posted in correct format

---

## Phase 5: Automated Job Scheduling
**Status:** ✅ COMPLETE (Modular Components Built)

### Purpose
Automatically create next service job (Maintenance) OR follow-up reminder (On Demand) after job marked "Done"

### Trigger
**Phase 4** detects job status = "Done" + service type (Maintenance/On Demand)

### Architecture
Two-path router based on `type_of_service`:

```
Phase 4: Job "Done"
    ↓
Check: type_of_service
    ↓
    ┌──────────────┴──────────────┐
    ↓                             ↓
PATH 5A: Maintenance          PATH 5B: On Demand
(Recurring agreement)         (No agreement)
    ↓                             ↓
Create Workiz job             Create Odoo activity
```

### Path 5A: Maintenance Auto-Scheduling

**What it does:**
1. **Calculate next service date** based on `frequency` field
2. **Apply city-aware scheduling** (matches actual Calendly setup):
   - Palm Springs → Friday
   - Rancho Mirage → Thursday (also Fri available)
   - Palm Desert → Thursday
   - Indian Wells → Wednesday (also Thu available)
   - Indio/La Quinta → Wednesday
   - Hemet → Tuesday
3. **Get line items** for next job:
   - If `alternating` = "Yes" → Copy from 2 jobs back
   - Else → Copy from current job
4. **Create new job in Workiz** with:
   - Scheduled date/time
   - All customer info (from previous job)
   - Job type, team, tags
   - Custom fields (gate_code, pricing, frequency, etc.)
   - **Line items reference in custom field** (e.g., "Windows: $85\nSolar: $45")
   - Link to previous job in notes

**Important API Limitation:**
- ❌ LineItems **cannot** be added via Workiz API
- ✅ Stored as text in custom Workiz field instead
- ⚠️ User adds 2-3 line items manually (30 seconds)
- ⚠️ User sets status to "Send Next Job - Text" to trigger SMS

**What gets automated:**
- ✅ 90% of job creation
- ✅ Date calculation with smart city routing
- ✅ All fields except line items
- ⚠️ User: Add line items + set status (30 sec)

### Path 5B: On Demand Follow-Up

**What it does:**
1. **Calculate follow-up date** (default: 6 months)
2. **Set to Sunday** of that week (for batch processing)
3. **Create Odoo activity** (NOT a Workiz job):
   - Type: "Follow-Up"
   - Summary: "Follow-up: [Customer Name]"
   - Description: Last service details, link to job
   - Due date: Sunday 6 months out
   - Assigned to: User

**Solves "Sunday Nightmare":**
- ✅ NO fake jobs cluttering Workiz schedule
- ✅ Clean reminders in Odoo only
- ✅ User reminded to contact customer
- ✅ Can schedule at that time if customer agrees

### Key Features

**Smart Scheduling:**
- Parses frequency: "3 Months", "4 Months", "6 Months"
- Maps city to preferred service day
- Finds nearest preferred day (±7 days from target)
- Example: 3 months from now = May 15 (Thursday)
  - Customer in Palm Desert (Wednesday preferred)
  - Adjusted to May 14 (Wednesday)

**Alternating Service Handling:**
- Queries Odoo for all property SOs (ordered by date DESC)
- If alternating: Uses line items from [1] index (2 jobs back)
- Ensures correct pricing for inside+outside vs outside-only rotation

**Line Items Reference Format:**
```
Windows In & Out - Full Service: $85.00
Solar Panel Cleaning: $45.00
```

### Files
- **Router:** `phase5_auto_scheduler.py`
- **Utilities:**
  - `functions/utils/calculate_next_service_date.py`
  - `functions/utils/get_line_items_for_next_job.py`
- **Workiz:**
  - `functions/workiz/create_next_maintenance_job.py`
- **Odoo:**
  - `functions/odoo/create_followup_activity.py`
  - `functions/odoo/get_property_city.py`
  - `functions/odoo/search_all_sales_orders_for_property.py`
- **Documentation:**
  - `Phase5_Implementation_Summary.md`
  - `Phase5_Technical_Plan.md`
  - `Workiz_API_Test_Results.md`

### Integration with Phase 4
Phase 4 updated to call Phase 5 after "Done" status:
- Detects `type_of_service` field
- Fetches property city for routing
- Passes required data to Phase 5
- Logs Phase 5 result

### Workiz API Test Results
**Tested:** Job creation with all fields
- ✅ `POST /job/create/` returns HTTP 204 (success)
- ✅ Required fields confirmed
- ❌ **LineItems cannot be added** (Invalid Field error)
- ❌ **No UUID returned** in response

**Solution:** Custom field for line items reference + manual addition

### Deployment
Ready for testing with real data:
1. Add `next_job_line_items` custom field in Workiz
2. Test Maintenance path (mark job Done, verify new job created)
3. Test On Demand path (verify Odoo activity created, no Workiz job)
4. Train user on 30-second manual process

**Tested:** ✅ Modular components created and logic verified

---

## 📊 Overall Progress

| Phase | Purpose | Status | Deployed | Testing |
|-------|---------|--------|----------|---------|
| 1 | Historical Migration | ✅ Complete | ✅ Yes | ✅ Done |
| 2 | Reactivation Engine | ✅ Complete | ✅ Yes | ✅ Done |
| 3 | New Job Creation | ✅ Complete | ⏳ Ready | ✅ Done |
| 4 | Job Status Update | ✅ Complete | ⏳ Ready | ✅ Done |
| 5 | Auto Job Scheduling | ✅ Complete | ⏳ Ready | ⏳ Needs Testing |

---

## 🔧 Technical Architecture

### API Integrations
- **Odoo JSON-RPC:** `https://window-solar-care.odoo.com/jsonrpc`
- **Workiz REST API:** `https://api.workiz.com/api/v1/{API_TOKEN}/`
- **Zapier Webhooks:** Various hooks for SMS, notifications, etc.

### Data Flow
```
Workiz (Source of Truth)
    ↓
Zapier (Orchestration)
    ↓
Odoo (Business Operations)
```

### Hierarchy Maintained
```
Contact (res.partner, type=Contact)
    ├── Property 1 (res.partner, type=Property, parent_id=Contact)
    │   └── Sales Order 1 (sale.order)
    │   └── Sales Order 2 (sale.order)
    └── Property 2 (res.partner, type=Property, parent_id=Contact)
        └── Sales Order 3 (sale.order)
```

### External ID Pattern
- **Format:** `workiz_[id]`
- **Source:** Mirror V31.11 logic
- **Used in:** Historical migration, all ongoing integrations

---

## 📁 File Structure

```
Migration to Odoo/
├── 1_Active_Odoo_Scripts/
│   ├── odoo_reactivation_launch.py (Phase 2)
│   ├── odoo_reactivation_preview.py (Phase 2)
│   └── [Legacy Phase 3A-F scripts]
├── 2_Modular_Phase3_Components/
│   ├── tier3_workiz_master_router.py (Phase 3)
│   ├── phase4_status_update_router.py (Phase 4)
│   ├── zapier_phase3_FLATTENED_FINAL.py (Phase 3 - Zapier ready)
│   ├── zapier_phase4_FLATTENED_FINAL.py (Phase 4 - Zapier ready)
│   ├── functions/
│   │   ├── odoo/ (Atomic Odoo API functions)
│   │   └── workiz/ (Atomic Workiz API functions)
│   └── config.py
├── 3_Documentation/
│   ├── AI Handoffs/
│   │   ├── Zapier_Deployment_Guide_FINAL.md (Phase 3)
│   │   ├── Zapier_Phase4_Deployment_Guide.md (Phase 4)
│   │   └── Session_Summary_2026-02-05_Phase3.md
│   └── COMPLETE_PHASE_OVERVIEW.md (this file)
├── 5_Reference_Data/
│   ├── Workiz_6Year_Done_History_Master.csv (Phase 1)
│   ├── Custom Field names.csv
│   └── Fields (ir.model.fields).csv
└── odoo_reactivation_launch.py (Phase 2 - root copy)
```

---

## 🎯 Next Steps

### Immediate
1. Define Phase 5 scope and requirements
2. Deploy Phase 3 to Zapier (if not already done)
3. Deploy Phase 4 to Zapier (if not already done)

### Future Considerations
- Revisit "Inbound Engine" (Phase 3A-F logic) for Calendly → Workiz → Odoo bookings
- Add error handling and retry logic to all integrations
- Create monitoring/alerting for failed integrations
- Build admin dashboard for integration health checks

---

**Last Updated:** 2026-02-07  
**Created by:** DJ  
**AI Assistant:** Claude (Cursor IDE)
