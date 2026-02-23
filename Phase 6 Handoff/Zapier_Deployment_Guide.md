# Zapier Deployment Guide - Phase 3 Inbound Engine

## Overview
This guide explains how to deploy the Phase 3 integration (Calendly → Workiz → Odoo) to Zapier using the flattened Python script and Copilot.

---

## File Locations

Due to Zapier's "Code by Zapier" character limits, the integration is split into **4 parts**:

1. **`zapier_phase3_PART1.py`** - Imports, credentials, Phases 3A-3D, helper functions
2. **`zapier_phase3_PART2.py`** - Phase 3E helper functions (excluding create_sales_order)
3. **`zapier_phase3_PART3.py`** - create_sales_order function
4. **`zapier_phase3_PART4.py`** - Phase 3E/3F processors and main orchestrator

All files are in: `1_Active_Odoo_Scripts/`

**Alternative:** For reference/testing, a complete single-file version exists at `zapier_phase3_FLATTENED.py` (not for direct Zapier use due to size)

---

## Zap Structure

### Trigger
**Calendly: Invitee Created**
- Captures new booking events from Calendly

### Action 1: Code by Zapier (Python)
**Purpose:** Execute the Phase 3 integration script

**Input Variables to Map from Calendly (Custom Questions):**
```python
input_data = {
    'event_start_time': {{Calendly Event Start Time}},                # Example: "2026-03-12T15:30:00.000000Z"
    'invitee_email': {{Calendly Invitee Email}},                      # Example: "customer@example.com"
    'invitee_name': {{Calendly Invitee Name}},                        # Example: "John Doe"
    'service_address': {{Questions and Responses 1: Answer}},         # Question 1: Service Address
    'service_type_required': {{Questions and Responses 2: Answer}},   # Question 2: Type of Service Required
    'additional_notes': {{Questions and Responses 3: Answer}}         # Question 3: Additional Notes
}
```

**Code:** Use the 4-part split files (`zapier_phase3_PART1.py` through `PART4.py`) - see deployment instructions below

**Output:** Returns dictionary with:
- `success`: True/False
- `sales_order_id`: Odoo Sales Order ID (if successful)
- `contact_id`: Odoo Contact ID
- `opportunity_id`: Odoo Opportunity ID
- `message`: Success or error message

---

## Instructions for Copilot

### Hey Copilot! Here's what you need to do:

1. **Create a new Zap with:**
   - **Trigger:** Calendly "Invitee Created"
   - **Action:** "Code by Zapier" (Python)

2. **In the Code by Zapier step:**
   - Since the full code exceeds Zapier's character limit, you'll need to use the 4-part structure:
     - **Option A:** Create 4 separate "Code by Zapier" actions, each containing one part (PART1 through PART4), then chain them together
     - **Option B:** Ask Copilot to combine the 4 parts into a single action if possible
   - Map these input variables from the Calendly trigger:
     - `event_start_time` → Calendly's "Event Start Time"
     - `invitee_email` → Calendly's "Invitee Email"
     - `invitee_name` → Calendly's "Invitee Name"
     - `service_address` → Calendly's "Questions and Responses 1: Answer" (Service Address - Question 1)
     - `service_type_required` → Calendly's "Questions and Responses 2: Answer" (Type of Service Required - Question 2)
     - `additional_notes` → Calendly's "Questions and Responses 3: Answer" (Additional Notes - Question 3)

3. **The script will automatically:**
   - Find the Odoo contact by address
   - Find the linked opportunity with Workiz UUID
   - Update the Workiz job with the new booking date/time
   - Mark the opportunity as Won
   - Create a complete Sales Order in Odoo with:
     - Order name (from Workiz SerialId)
     - Correct date/time (timezone converted)
     - Lead source (Calendly)
     - Job type
     - Team members
     - Gate code & pricing snapshots
     - Notes snapshot
     - Tags (from contact + Workiz)
     - Line items with products
     - Confirmed status (not just a quote)
   - Update the property fields
   - Update the contact email

4. **Test with real Calendly data** to make sure all fields map correctly

5. **Optional: Add error handling steps** after the Code by Zapier action to:
   - Send notifications if `success` is False
   - Log the `message` field for debugging

---

## What The Script Does - Step by Step

### Phase 3A: Contact Lookup
- Searches Odoo for a contact matching the address from Calendly
- Uses exact street address match

### Phase 3B: Opportunity Lookup  
- Finds the opportunity linked to the contact
- Must have a Workiz Graveyard UUID populated

### Phase 3C: Workiz Job Update
- Converts UTC booking time to Pacific time
- Updates Workiz job with:
  - New JobDateTime
  - Status: "Pending"
  - SubStatus: "Send Confirmation - Text"
  - JobType from Calendly Question 2 (service_type_required)
  - JobNotes from Calendly Question 3 (additional_notes)

### Phase 3D: Mark Opportunity Won
- Calls Odoo's `action_set_won` to mark the opportunity as Won

### Phase 3E: Create Sales Order
**This is the big one - creates a fully populated sales order with:**

**Basic Info:**
- Order name (formatted from Workiz SerialId: 4111 → 004111)
- Customer (contact) and delivery address (property)
- Workiz UUID and link
- Workiz substatus

**Date/Time:**
- Job/Schedule Date set to Workiz JobDateTime (not Calendly booking time)
- Timezone converted from Pacific to UTC for Odoo storage
- Set AFTER confirming the order to prevent Odoo from overriding it

**Sales Fields:**
- Lead Source: "Calendly"
- Job Type: From Workiz
- Team/Tech: Comma-separated list of team member names from Workiz

**Snapshot Fields:**
- Gate Snapshot: Gate code from Workiz
- Pricing Snapshot: Pricing info from Workiz
- Notes Snapshot: Job Notes + Comments (all newlines removed, single line)

**Tags:**
- Merges tags from Contact + Workiz
- Automatically matches to existing sales order tags

**Line Items:**
- Extracts from Workiz
- Looks up matching Odoo products by name
- Creates order lines with product IDs, quantities, and prices

**Status:**
- Confirms the order (converts from Quotation to Sales Order)

**Property Update:**
- Updates the property record with gate code and pricing

### Phase 3F: Update Contact Email
- Updates the contact's email address with the one from Calendly

---

## Error Handling

The script returns detailed error information:

```python
{
    'success': False,
    'failed_at': 'Phase 3C',  # Which phase failed
    'message': 'Error details here'
}
```

You can use this to:
- Send failure notifications
- Log errors for debugging
- Retry specific phases

---

## Testing Checklist

Before going live, test that:

✅ Contact is found by address  
✅ Opportunity has Workiz UUID  
✅ Workiz job updates successfully (including JobType and JobNotes)  
✅ Opportunity marks as Won  
✅ Sales Order creates with ALL fields:
   - Order name correct format (004111)
   - Date shows booking date (March 12, 8:30 AM) not current date
   - Lead source = "Calendly"
   - Job type populated
   - Team/tech names shown
   - Gate & pricing snapshots filled
   - Notes on one line (no line breaks)
   - Tags applied (both contact + Workiz)
   - Line items with correct products
   - Status = "Sales Order" (not "Quotation")  
✅ Property fields update  
✅ Contact email updates  

---

## Credentials

All credentials are hardcoded in the script:
- Odoo API credentials
- Workiz API credentials

**Security Note:** These are embedded in the script. If you need to use Zapier's storage secrets feature instead, Copilot can help modify the script to use environment variables.

---

## Field Dictionary Reference

For Copilot's reference, here are the key Odoo field names used:

**Sales Order Fields:**
- `x_studio_x_studio_workiz_uuid` - Workiz UUID
- `x_studio_x_workiz_link` - Workiz job link
- `x_studio_x_studio_workiz_status` - Workiz substatus
- `x_studio_x_studio_lead_source` - Lead Source ("Calendly")
- `x_studio_x_studio_x_studio_job_type` - Job Type
- `x_studio_x_studio_workiz_tech` - Team/Tech names
- `x_studio_x_gate_snapshot` - Gate code
- `x_studio_x_studio_pricing_snapshot` - Pricing info
- `x_studio_x_studio_notes_snapshot1` - Notes
- `tag_ids` - Tags (many2many)
- `date_order` - Job/Schedule Date
- `order_line` - Line items

**Property Fields:**
- `x_studio_x_gate_code` - Gate code
- `x_studio_x_pricing` - Pricing

---

## Support

If Copilot encounters any issues:
1. Check the `message` field in the output for error details
2. Verify all Calendly fields are mapped correctly
3. Test with the known working test data (Bev Hartin booking)
4. Make sure contact exists in Odoo with matching address
5. Ensure opportunity has Workiz UUID populated

---

## Next Steps After Deployment

1. **Monitor first few live runs** to ensure everything works
2. **Set up error notifications** for failed integrations
3. **Create a dashboard** to track successful bookings
4. **Consider adding** follow-up actions based on the `sales_order_id`

---

**Ready to deploy!** 🚀
