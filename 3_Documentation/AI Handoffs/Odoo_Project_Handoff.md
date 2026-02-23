# Odoo Project Handoff Document

**Project:** A Window and Solar Care - Odoo Migration  
**Document Type:** Project Handoff & Context Preservation  
**Created:** February 5, 2026

---

## Document Purpose

This document serves as a comprehensive handoff guide for the Odoo migration project. It contains critical context, decisions, and implementation details that should be referenced when:

- Starting a new AI agent session
- Onboarding new team members
- Troubleshooting integration issues
- Making architectural decisions

---

## Quick Links to Key Documentation

### Primary Reference Documents

1. **AI Agent Master Manual** (`AI_Agent_Master_Manual_OPTIMIZED.md`)
   - Complete technical reference
   - API protocols and authentication
   - Field dictionaries and proven methods
   - Critical rules and failure patterns

2. **Phase 3 Session Summary** (`Session_Summary_2026-02-05_Phase3.md`)
   - Current work status
   - Known issues and blockers
   - Test data and credentials
   - Next steps

---

## Project Context

### Mission
Migrate 6 years of historical data from Workiz (Field Service Management) to Odoo (CRM) and establish a bi-directional "Mirror" integration to build a "Dormant Client Reactivation Engine" in Odoo that triggers actions back in Workiz.

### Core Principle: "One Number Strategy"
Customers must **NEVER** receive SMS directly from Odoo. All communications route through the Workiz Message Center so customers only see one phone number.

---

## System Architecture

### The Three-System Model

```
┌─────────────────────────────────────────────────────┐
│                     ODOO (Brain)                    │
│  • Analytics & Logic                                │
│  • Dormant Client Detection                         │
│  • Data Storage & History                           │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  ZAPIER (Bridge)                     │
│  • Data Transport                                    │
│  • Format Transformation                             │
│  • Webhook Management                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│                  WORKIZ (Voice)                      │
│  • SMS Sender                                        │
│  • Field Tech Interface                              │
│  • Job Scheduling                                    │
└─────────────────────────────────────────────────────┘
```

---

## Critical Architecture Rules

### Rule #1: Property is the Brain
Service data (Gate Codes, Maintenance Status, Service Frequency) belongs to the **ADDRESS/PROPERTY record** (`partner_shipping_id`), NOT the billing contact (`partner_id`).

**Why?** A single client may have multiple properties with different service requirements.

### Rule #2: Data Type Strictness
When passing record IDs to Odoo via Zapier webhooks:
- ✅ **CORRECT:** `[[123], {...}]` (integer)
- ❌ **WRONG:** `[["123"], {...}]` (string)

**Impact:** String IDs fail silently - Zapier reports success but Odoo ignores the operation.

### Rule #3: The Lever Pull (SMS Mechanism)
To send SMS via Workiz:
1. Create job with `POST /job/create/` (status omitted)
2. Immediately update with `POST /job/update/` (set status)
3. Status change triggers Workiz automation → SMS sent

**Never attempt to send SMS directly from Odoo.**

---

## Project Phases

### Phase 1: Historical Data Migration ✅ COMPLETE
- Migrated 6 years of Workiz data (4,000+ records)
- Created three linked datasets:
  - Contacts (Billing Entities)
  - Properties (Service Addresses)
  - Sales Orders (Job History)
- External ID format: `workiz_[id]` (Mirror V31.11 logic)

### Phase 2: Live Integration ✅ COMPLETE
- Bi-directional sync between Workiz and Odoo
- Triggers:
  - New job in Workiz → Create/Update Contact & Pipeline in Odoo
  - Job marked "Done/Paid" in Workiz → Update Odoo Sales Order

### Phase 3: Reactivation Engine 🔄 IN PROGRESS
**Current Status:** Phase 3A-3F mostly working, one blocker remaining

#### Phase 3 Workflow (Calendly → Workiz → Odoo)

**Phase 3A - Contact Lookup** ✅
- Searches Odoo contact by exact street address from Calendly
- File: `1_Active_Odoo_Scripts/phase3a_contact_lookup.py`

**Phase 3B - Opportunity Lookup** ✅
- Finds opportunity linked to contact with `x_workiz_graveyard_uuid` populated
- File: `1_Active_Odoo_Scripts/phase3b_opportunity_lookup.py`

**Phase 3C - Workiz Job Update** ✅
- Converts UTC → Pacific time
- Updates Workiz job datetime, status, substatus, job type
- API: `POST /api/v1/{API_TOKEN}/job/update/`
- File: `1_Active_Odoo_Scripts/phase3c_workiz_update.py`

**Phase 3D - Mark Opportunity Won** ✅
- Calls Odoo `action_set_won` method
- File: `1_Active_Odoo_Scripts/phase3d_mark_won.py`

**Phase 3E - Create Sales Order** ⚠️ PARTIAL
- ✅ Sales order created with correct order name
- ✅ Date/time handling correct
- ✅ Line items transferred
- ❌ **BLOCKER:** Gate Code and Pricing Snapshot fields empty in Odoo
  - Data IS extracted from Workiz (visible in terminal)
  - Fields remain empty in Odoo Sales Order
  - Need to verify field names: `x_studio_gate_snapshot`, `x_studio_x_studio_pricing_snapshot`
- File: `1_Active_Odoo_Scripts/phase3e_sales_order_COMPLETE.py`

**Phase 3F - Update Contact Email** ✅
- Updates contact email from Calendly booking
- File: `1_Active_Odoo_Scripts/phase3f_update_contact.py`

---

## Current Blocker

### Issue: Gate Code & Pricing Snapshot Not Saving to Odoo SO

**Evidence:**
```
Terminal Output:
Gate Code: Gate Code
Pricing: Pricing

Odoo SO #15737: [FIELDS EMPTY]
```

**Field Names Being Used:**
- `x_studio_gate_snapshot`
- `x_studio_x_studio_pricing_snapshot`

**Suspected Causes:**
1. Incorrect Odoo field names
2. Data type mismatch (Text vs HTML vs Char)
3. Field write permissions
4. Field validation issues

**Next Steps:**
1. Verify correct Odoo field names via API inspection
2. Check field type definitions in Odoo Studio
3. Test simple write operation to isolate issue
4. Confirm field is writable via API

---

## Test Data

### Test Contact: Bev Hartin
- **Contact ID:** 23629
- **Property ID:** 25799
- **Opportunity ID:** 41
- **Workiz UUID:** SG6AMX
- **Workiz Job #:** 4111
- **Test Booking:** March 12, 2026 at 8:30 AM
- **Latest SO Created:** #15737

---

## Key Decisions Made

### Decision 1: Job Type & Lead Source Fields
**Status:** Temporarily removed from sales order creation  
**Reason:** Dropdown validation errors  
**Future Action:** Re-add once Calendly/Workiz/Odoo dropdowns are synchronized

### Decision 2: Date Handling
**Solution:** Odoo expects UTC, Workiz expects Pacific  
**Status:** Conversion working correctly

### Decision 3: Architecture Approach
**Approach:** Zapier "Code by Zapier" hybrid  
**Workflow:** Build complex logic in Python (Cursor) → Deploy flattened version to Zapier

---

## API Credentials

### Workiz API
```
API Token: api_1hu6lroiy5zxomcpptuwsg8heju97iwg
API Secret: sec_334084295850678330105471548
Base URL: https://api.workiz.com/api/v1/{API_TOKEN}/
```

### Odoo API
```
Database: window-solar-care
User ID: 2
API Key: 7e92006fd5c71e4fab97261d834f2e6004b61dc6
Endpoint: https://window-solar-care.odoo.com/jsonrpc
```

---

## Critical Field Mappings

### Contact/Property Fields
| Purpose | Odoo Field | Field Type |
|---------|------------|------------|
| Gate Code | `x_studio_x_gate_code` | char |
| Service Frequency | `x_studio_x_frequency` | char |
| Pricing Note | `x_studio_x_pricing` | char |
| Last Service Date | `x_last_service_date` | date |
| OK to Text | `x_studio_x_studio_ok_to_text` | selection |

### Sales Order Fields
| Purpose | Odoo Field | Field Type |
|---------|------------|------------|
| Workiz UUID | `x_studio_x_studio_workiz_uuid` | char |
| Workiz Link | `x_studio_x_studio_workiz_link` | char |
| Gate Snapshot | `x_studio_gate_snapshot` | char |
| Pricing Snapshot | `x_studio_x_studio_pricing_snapshot` | char |
| Notes Snapshot | `x_studio_x_studio_notes_snapshot1` | text |
| Workiz Status | `x_studio_x_studio_workiz_status` | char |
| Job Type | `x_studio_x_studio_x_studio_job_type` | selection |

### CRM Lead/Opportunity Fields
| Purpose | Odoo Field | Field Type |
|---------|------------|------------|
| Workiz Graveyard UUID | `x_workiz_graveyard_uuid` | text |
| Workiz Graveyard Link | `x_workiz_graveyard_link` | char |
| Historical Workiz UUID | `x_historical_workiz_uuid` | char |

---

## Common Pitfalls & Solutions

### Pitfall 1: Odoo Search Domain Format
❌ **WRONG:** `[["field", "=", "value"]]`  
✅ **CORRECT:** `[[["field", "=", "value"]]]`

**Why:** Odoo `search_read` requires double-wrapped domains.

### Pitfall 2: Creating Related Records
❌ **WRONG:** Direct `create` on custom child model  
✅ **CORRECT:** Write to parent record using `[0, 0, {...}]` magic command

**Why:** Direct creates on custom models are unreliable.

### Pitfall 3: Odoo Server Actions
❌ **WRONG:** `import datetime`  
✅ **CORRECT:** Use built-in `datetime` global

**Why:** Odoo sandbox blocks `IMPORT_NAME` opcode.

### Pitfall 4: Workiz Job Creation
❌ **WRONG:** Create job with status in one call  
✅ **CORRECT:** Two-step process (create without status, then update with status)

**Why:** Status change triggers automation (the "lever pull").

---

## File Structure

```
Migration to Odoo/
├── 1_Active_Odoo_Scripts/
│   ├── phase3a_contact_lookup.py
│   ├── phase3b_opportunity_lookup.py
│   ├── phase3c_workiz_update.py
│   ├── phase3d_mark_won.py
│   ├── phase3e_sales_order_COMPLETE.py
│   └── phase3f_update_contact.py
│
├── 3_Documentation/
│   ├── AI Handoffs/
│   │   ├── AI_Agent_Master_Manual_OPTIMIZED.md
│   │   ├── Odoo_Project_Handoff.md (this file)
│   │   └── Session_Summary_2026-02-05_Phase3.md
│   └── [other documentation files]
│
└── Workiz_6Year_Done_History_Master.csv
```

---

## Next Session Checklist

When starting a new AI agent session:

1. ✅ Read `AI_Agent_Master_Manual_OPTIMIZED.md` (Section 0 minimum)
2. ✅ Read latest `Session_Summary_*.md` file
3. ✅ Review current blocker (Gate/Pricing fields issue)
4. ✅ Verify you understand:
   - One Number Strategy
   - Property vs Contact distinction
   - Integer vs String ID requirement
   - Lever Pull SMS mechanism
5. ✅ Locate test data (Bev Hartin info above)
6. ✅ Begin troubleshooting or continue development

---

## Handoff Notes for Next Developer

**Where We Are:**
- Phase 3 (Calendly → Workiz → Odoo) is 95% complete
- All 6 sub-phases (3A-3F) are working except one issue
- One blocker: Gate/Pricing fields not saving to Odoo SO

**What's Working:**
- Contact lookup by address ✅
- Opportunity lookup ✅
- Workiz job updates ✅
- Marking opportunities won ✅
- Sales order creation with line items ✅
- Date/time conversion ✅
- Contact email updates ✅

**What's Not Working:**
- Gate Code and Pricing Snapshot fields remain empty in Odoo SO
- Data IS extracted from Workiz API (confirmed in terminal output)
- Suspected field name or data type issue

**To Fix This:**
1. Inspect `phase3e_sales_order_COMPLETE.py`
2. Verify Odoo field names: `x_studio_gate_snapshot` and `x_studio_x_studio_pricing_snapshot`
3. Check if fields exist and are writable via API
4. Test simple write with hardcoded string
5. Check field type (Char vs Text vs HTML)

**After Fix:**
1. Create master integration script combining all 6 phases
2. Flatten for Zapier deployment
3. End-to-end test with real Calendly webhook
4. Re-add Job Type & Lead Source fields (once dropdowns aligned)

---

## Critical Reference: Data Hierarchy

```
Client (Billing Contact)
    ├── Property 1 (Service Address)
    │   ├── Gate Code: ABC123
    │   ├── Frequency: Monthly
    │   ├── Last Service: 2025-12-15
    │   └── Sales Orders
    │       ├── SO #001 (2024-01-15)
    │       ├── SO #002 (2024-02-15)
    │       └── SO #003 (2024-03-15)
    │
    └── Property 2 (Service Address)
        ├── Gate Code: XYZ789
        ├── Frequency: Quarterly
        ├── Last Service: 2025-11-20
        └── Sales Orders
            ├── SO #004 (2024-01-20)
            └── SO #005 (2024-04-20)
```

**Key Insight:** Service data lives on the PROPERTY, not the CLIENT.

---

## Resources

### Master CSV File
`Workiz_6Year_Done_History_Master.csv` - Complete historical data export from Workiz

### External ID Format
`workiz_[id]` - All Workiz records use this format for `external_id` (Mirror V31.11 logic)

### Developer Mode
Always enable Odoo Developer Mode to see:
- Technical field names
- Record IDs in URLs
- Model names
- Debugging info

**How to Enable:** Settings → Activate Developer Mode

---

## Questions to Ask Before Making Changes

1. **Does this maintain the "One Number Strategy"?**
   - Will customer see only Workiz phone number?

2. **Are we using the correct data hierarchy?**
   - Is service data on Property, not Contact?

3. **Are IDs being passed as integers?**
   - Critical for Odoo API calls via Zapier

4. **Are we following the "Lever Pull" for SMS?**
   - Two-step job creation process?

5. **Have we consulted the Master Manual?**
   - Check Section 0 (Quick Start) minimum

---

## Contact & Support

**Primary Documentation:**
- `AI_Agent_Master_Manual_OPTIMIZED.md` - Complete technical reference
- `Session_Summary_*.md` files - Session-specific progress tracking

**Development Environment:**
- IDE: Cursor
- Language: Python 3.x
- Deployment: Zapier "Code by Zapier"

---

**Document Last Updated:** February 5, 2026  
**Next Review:** After Gate/Pricing fields issue resolved  
**Status:** Active Development - Phase 3 Blocker
