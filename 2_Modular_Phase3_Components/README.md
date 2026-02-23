# Phase 3 Modular Architecture
## Workiz → Odoo Integration (All Job Sources)

**Created:** 2026-02-05  
**Updated:** 2026-02-05 (Path A Complete)  
**Purpose:** Maintainable modular structure for Workiz → Odoo integration that can be flattened for Zapier deployment

---

## 🎯 PROJECT STATUS

✅ **All Paths COMPLETE & TESTED**  
- **Path A:** Existing Contact + Existing Property → Create Sales Order ✅
- **Path B:** Existing Contact + New Property → Create Property + Sales Order ✅
- **Path C:** New Contact → Create Contact + Property + Sales Order ✅

🔑 **Key Features:**
- ClientId-based routing (single source of truth - no fuzzy matching)
- Mirror V31.11 hierarchy: Contact → Property → Job
- Full field population including service details (frequency, alternating, type of service)
- State ID = 13 (California US)
- Property fields: pricing, last visit date, frequency, alternating, type of service, comments

📦 **All 22 Atomic Functions Extracted** (100% complete)  
✅ **Master Router Ready:** `tier3_workiz_master_router.py`

---

## Folder Structure

```
2_Modular_Phase3_Components/
├── README.md                 # This file - architecture documentation
├── config.py                 # ✅ Credentials & constants
├── utils.py                  # ✅ Timezone, formatting utilities  
├── workiz_api.py            # ✅ Workiz API helper functions
├── odoo_api.py              # 🔄 Odoo API helper functions (LARGE FILE)
├── phase3a_lookup.py        # Property & Contact lookup
├── phase3b_opportunity.py   # Opportunity lookup
├── phase3c_workiz.py        # Workiz job update with notes prepending
├── phase3d_won.py           # Mark opportunity won
├── phase3e_sales.py         # Sales order creation (complex)
├── phase3f_contact.py       # Contact email update
├── orchestrator.py          # Main function - imports and orchestrates all phases
└── flatten_to_zapier.py     # Script to create zapier_phase3_FLATTENED.py
```

---

## Module Descriptions

### Core Modules

#### `config.py`
- Odoo API credentials (URL, DB, User ID, API Key)
- Workiz API credentials (Token, Auth Secret, Base URL)
- **No external dependencies**

#### `utils.py`
- `utc_to_pacific()` - Convert UTC datetime to Pacific time
- `pacific_to_utc()` - Convert Pacific time to UTC
- `format_serial_id()` - Format Workiz SerialId as 6-digit string
- `clean_notes_for_snapshot()` - Remove newlines from notes
- **Dependencies:** `datetime`, `timedelta` (standard library)

#### `workiz_api.py`
- `get_job_details()` - Fetch complete Workiz job data by UUID
- `update_job()` - Update Workiz job (date/time, status, type, notes)
- `prepend_calendly_notes_to_job()` - Fetch current notes and prepend Calendly booking notes
- **Dependencies:** `requests`, `config`

#### `odoo_api.py` (LARGE - 600+ lines)
**Lookup Functions:**
- `search_property_and_contact_by_address()` - Find Property → get Contact from parent_id
- `find_opportunity_with_workiz_uuid()` - Find opportunity linked to contact
- `search_odoo_product_by_name()` - Product lookup for line items
- `get_contact_tag_names()` - Get tags from contact's category_id
- `get_sales_tag_ids()` - Convert tag names to crm.tag IDs

**Sales Order Functions:**
- `create_sales_order()` - Create sales order with complete Workiz data
- `confirm_sales_order()` - Convert quotation to sales order (action_confirm)
- `update_sales_order_date()` - Update date_order field post-confirmation

**Update Functions:**
- `mark_opportunity_won()` - Call action_set_won on crm.lead
- `update_property_fields()` - Update gate code and pricing on property
- `update_contact_email()` - Update contact email from Calendly

**Dependencies:** `requests`, `config`, `utils`

---

### Phase Modules

#### `phase3a_lookup.py`
**Function:** `execute_phase3a(service_address)`
- Searches for Property by address
- Gets Contact from Property's parent_id
- Returns: `{'property_id', 'contact_id', 'property_name', 'contact_name'}`
- **Imports:** `odoo_api.search_property_and_contact_by_address()`

#### `phase3b_opportunity.py`
**Function:** `execute_phase3b(contact_id)`
- Finds opportunity linked to contact with Workiz UUID
- Returns: `{'success': bool, 'opportunity': dict}`
- **Imports:** `odoo_api.find_opportunity_with_workiz_uuid()`

#### `phase3c_workiz.py`
**Function:** `execute_phase3c(job_uuid, booking_time_utc, job_type, additional_notes)`
- Converts UTC → Pacific time
- Prepends Calendly notes to existing JobNotes (with delimiter)
- Updates Workiz job (DateTime, Status, SubStatus, JobType, JobNotes)
- Returns: `{'success': bool}`
- **Imports:** `workiz_api.prepend_calendly_notes_to_job()`, `workiz_api.update_job()`, `utils.utc_to_pacific()`

#### `phase3d_won.py`
**Function:** `execute_phase3d(opportunity_id)`
- Marks Odoo opportunity as Won
- Returns: `{'success': bool}`
- **Imports:** `odoo_api.mark_opportunity_won()`

#### `phase3e_sales.py` (COMPLEX - 200+ lines)
**Function:** `execute_phase3e(contact_id, property_id, opportunity, booking_info)`
- Fetches complete Workiz job data
- Extracts all Workiz fields (UUID, SubStatus, Tags, Gate Code, Pricing, Team, Line Items, Notes)
- Formats Notes Snapshot (Calendly notes first, then Job Notes, then Comments)
- Creates Sales Order with all fields
- Confirms Sales Order (Quotation → Sales Order)
- Updates date_order post-confirmation (prevents Odoo override)
- Updates Property fields (gate code, pricing)
- Returns: `{'success': bool, 'sales_order_id': int}`
- **Imports:** Multiple from `odoo_api`, `workiz_api`, `utils`

#### `phase3f_contact.py`
**Function:** `execute_phase3f(contact_id, new_email)`
- Updates contact email from Calendly booking
- Returns: `{'success': bool}`
- **Imports:** `odoo_api.update_contact_email()`

---

### Orchestration

#### `orchestrator.py`
**Function:** `main(input_data)`

**Input Data Structure** (from Calendly webhook via Zapier):
```python
input_data = {
    'event_start_time': str,       # UTC datetime "2026-03-12T15:30:00.000000Z"
    'invitee_email': str,          # Customer email
    'invitee_name': str,           # Customer full name
    'service_address': str,        # Question 1: Service address
    'service_type_required': str,  # Question 2: Type of service
    'additional_notes': str        # Question 3: Additional notes
}
```

**Execution Flow:**
1. Parse booking data and extract street address
2. **Phase 3A:** Lookup Property & Contact
3. **Phase 3B:** Find Opportunity with Workiz UUID
4. **Phase 3C:** Update Workiz job (prepend Calendly notes)
5. **Phase 3D:** Mark Opportunity as Won
6. **Phase 3E:** Create & Confirm Sales Order
7. **Phase 3F:** Update Contact Email

**Returns:**
```python
{
    'success': bool,
    'contact_id': int,
    'property_id': int,
    'opportunity_id': int,
    'sales_order_id': int,
    'message': str
}
```

**Imports:** All phase modules

---

### Flattening for Zapier

#### `flatten_to_zapier.py`
**Purpose:** Combine all modular files into single `zapier_phase3_FLATTENED.py` for Zapier deployment

**Process:**
1. Read all module files in dependency order
2. Strip import statements
3. Combine into single file with proper ordering:
   - Imports (requests, datetime)
   - Constants from config.py
   - Utilities from utils.py
   - Workiz API from workiz_api.py
   - Odoo API from odoo_api.py
   - Phase functions (3A-3F)
   - Main orchestrator
   - Output statement: `output = main(input_data)`

**Output:** `../1_Active_Odoo_Scripts/zapier_phase3_FLATTENED.py`

---

## Development Workflow

### Local Development
```python
# Import modular components
from phase3a_lookup import execute_phase3a
from phase3b_opportunity import execute_phase3b
# ... etc

# Test individual phases
result = execute_phase3a("29 Toscana Way E")
```

### Zapier Deployment
```bash
# 1. Make changes to modular files
# 2. Run flattening script
python flatten_to_zapier.py

# 3. Copy flattened file to Zapier
# File: 1_Active_Odoo_Scripts/zapier_phase3_FLATTENED.py
```

---

## Key Technical Details

### Mirror V31.11 Hierarchy
- **Client** (Contact with parent_id = NULL)
  - **Property** (Contact with parent_id = Client ID, record_category = "Property")
    - **Job** (Opportunity/Sales Order linked to Property)

**Critical:** Always lookup Property FIRST, then get Contact from `parent_id`.

### Timezone Handling
- **Calendly** sends UTC with 'Z' suffix
- **Workiz** expects Pacific time (PST/PDT) without timezone
- **Odoo** expects UTC for date_order field
- **Conversion:** Built-in datetime (no pytz dependency for Zapier compatibility)

### Notes Management
- **Calendly notes** (Question 3) are **prepended** to existing Workiz JobNotes
- **Delimiter:** `|||ORIGINAL_NOTES|||` separates Calendly from original
- **Odoo Notes Snapshot** format: `[Calendly Booking] {text} [Job Notes] {text} [Comments] {text}`
- **Newlines:** Removed for Odoo snapshot field

### Tags
- **Sources:** Contact tags (res.partner.category) + Workiz tags (Tags/JobTags)
- **Combined:** Deduplicated and converted to crm.tag IDs
- **Field:** `tag_ids` with many2many format: `[(6, 0, [id1, id2])]`

### Sales Order Confirmation
- **date_order** must be set AFTER confirmation (Odoo overwrites it during confirm)
- **Sequence:** Create → Confirm → Update date_order

---

## For Future AI Agents

### Common Tasks

**Add a new field to Sales Order:**
1. Update `odoo_api.create_sales_order()` function
2. Extract field from Workiz job data
3. Add to `order_data` dictionary with correct Odoo field name
4. Test locally
5. Run `flatten_to_zapier.py`

**Modify Workiz update logic:**
1. Edit `workiz_api.update_job()` or `phase3c_workiz.py`
2. Test locally
3. Run `flatten_to_zapier.py`

**Change timezone conversion:**
1. Edit `utils.py` functions
2. Update both `utc_to_pacific()` and `pacific_to_utc()`
3. Test locally
4. Run `flatten_to_zapier.py`

### Testing
- Use `orchestrator.py` with test data (Bev Hartin booking)
- Test individual phases before full integration
- Verify in Odoo UI after each test run

### Deployment Checklist
- [ ] Test locally with modular files
- [ ] Run `flatten_to_zapier.py`
- [ ] Verify flattened file has no syntax errors
- [ ] Copy to Zapier Code by Zapier action
- [ ] Map 6 input variables from Calendly
- [ ] Test in Zapier with real webhook data
- [ ] Verify Sales Order in Odoo has all fields populated

---

## Dependencies

**Local Development:**
- Python 3.x
- `requests` library
- Standard library: `datetime`, `timedelta`

**Zapier Deployment:**
- Python 3.x (Zapier built-in)
- `requests` (Zapier built-in)
- NO `pytz` (not available in Zapier - use datetime only)

---

## File Sizes (Approximate)
- config.py: ~20 lines
- utils.py: ~60 lines
- workiz_api.py: ~120 lines
- odoo_api.py: ~650 lines
- phase3a-3f.py: ~50-200 lines each
- orchestrator.py: ~150 lines
- **Total:** ~1,200 lines split across modules
- **Flattened:** ~1,040 lines (imports consolidated)

---

## Version History
- **v1.0** (2026-02-05): Initial modular architecture
  - Property → Contact lookup fixed
  - Workiz API data extraction fixed (`data[0]`)
  - Calendly notes prepending implemented
  - Timezone conversion without pytz
  - All 6 phases tested and working

---

## Support Documentation
- `3_Documentation/AI Handoffs/Odoo_Project_Handoff.md`
- `3_Documentation/AI Handoffs/AI_Agent_Master_Manual_OPTIMIZED.md`
- `3_Documentation/AI Handoffs/Zapier_Deployment_Guide.md`
