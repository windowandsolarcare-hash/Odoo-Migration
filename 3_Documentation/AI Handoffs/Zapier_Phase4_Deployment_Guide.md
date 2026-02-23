# Phase 4: Workiz Job Status Update - Zapier Deployment Guide

**Generated:** 2026-02-07  
**Script:** `zapier_phase4_FLATTENED_FINAL.py`

---

## Overview

Phase 4 handles **any Workiz job status change** and updates the corresponding Sales Order in Odoo. If the Sales Order doesn't exist, it automatically calls Phase 3 logic to create it first.

### Key Features
- ✅ Updates existing Sales Orders with latest job data
- ✅ Creates missing Sales Orders via Phase 3 (Paths A/B/C)
- ✅ Adds payment fields when status = "Done"
- ✅ Updates Property "Last Visit Date" when done
- ✅ Posts formatted status updates to SO chatter

---

## Zapier Setup

### Step 1: Create New Zap

**Zap Name:** `Workiz Job Status Change → Odoo SO Update`

### Step 2: Trigger Configuration

**Trigger:** Workiz → "Job Status Changed"

**Settings:**
- Event: **Any status change** (not just "Done")
- Include all job fields in webhook payload

**Test Trigger:** Use a recent status change to verify data

---

### Step 3: Code by Zapier Configuration

**Action:** Code by Zapier → Run Python

#### Input Data

Map **one field** from Workiz trigger:

| Zapier Input | Maps to | Workiz Field |
|-------------|---------|--------------|
| `job_uuid` | → | UUID |

**Example in Zapier:**
```
job_uuid: {{trigger.UUID}}
```

#### Python Code

**Copy the entire contents** of `zapier_phase4_FLATTENED_FINAL.py` into the code editor.

**IMPORTANT:** The script is **1,046 lines**. Make sure you copy everything from line 1 to the final `output = main(input_data)` line.

---

### Step 4: Test the Zap

**Test with existing SO:**
- Job UUID: `IC3ZC9` (Blair Becker - Done job)
- Expected: Updates SO #003878, posts to chatter

**Test with missing SO:**
- Job UUID: `MOIPF9` (test job not in Odoo)
- Expected: Creates SO via Phase 3, then applies Phase 4 updates

---

## Field Mappings

### Sales Order Fields (Always Updated)

| Odoo Field | Workiz Source | Notes |
|-----------|---------------|-------|
| `x_studio_x_studio_workiz_status` | SubStatus (or Status) | Primary status display |
| `x_studio_x_studio_workiz_tech` | Team → Names | Formatted as "Name1, Name2" |
| `x_studio_x_gate_snapshot` | gate_code | Lowercase field |
| `x_studio_x_studio_pricing_snapshot` | pricing | Lowercase field |
| `x_studio_x_studio_notes_snapshot1` | JobNotes + Comments | Combined format |
| `date_order` | JobDateTime | Converted to UTC |
| `x_studio_x_studio_x_studio_job_type` | JobType | If available |
| `x_studio_x_studio_lead_source` | JobSource | If available |

### Payment Fields (Only When Status = "Done")

| Odoo Field | Workiz Source | Logic |
|-----------|---------------|-------|
| `x_studio_is_paid` | JobAmountDue | Boolean: True if amount due = 0 |
| `x_studio_tip_amount` | LineItems → "Tip" | Extracted from line items |

### Property Fields (Always Updated)

| Odoo Field | Workiz Source | Notes |
|-----------|---------------|-------|
| `x_studio_x_gate_code` | gate_code | Direct mapping |
| `x_studio_x_pricing` | pricing | Direct mapping |
| `comment` | JobNotes + Comments | Combined internal notes |
| `x_studio_x_frequency` | frequency | Custom field |
| `x_studio_x_alternating` | alternating | Custom field |
| `x_studio_x_type_of_service` | type_of_service | Custom field |
| `x_studio_x_studio_last_property_visit` | JobDateTime (date only) | **Only updated when status = "Done"** |

---

## Chatter Message Format

**When status changes:**
```
Status updated to: [SubStatus] on [LastStatusUpdate]
```

**When status = "Done" with payment:**
```
Status updated to: Done on 2026-02-06 21:09:52; Paid in Full; Tip: $15.0
```

**When status = "Done" with amount due:**
```
Status updated to: Done on 2026-02-06 21:09:52; Unpaid ($50 due)
```

**Format:** Single line, semicolon-separated, plain text (no HTML/Markdown)

---

## How It Works

### Flow Diagram

```
Workiz Job Status Change
         ↓
    Get Job UUID
         ↓
Search for SO by UUID
         ↓
    ┌────┴────┐
    ↓         ↓
  Found    Not Found
    ↓         ↓
Update SO  Call Phase 3
    ↓      (Paths A/B/C)
    ↓         ↓
    └─────┬───┘
          ↓
   Apply Updates
          ↓
  Status = "Done"?
    ┌─────┴─────┐
    ↓           ↓
   Yes         No
    ↓           ↓
 Add Payment  Skip
 Update Prop
 Post Chatter
```

### Decision Logic

**If SO exists:**
1. Update SO fields (always)
2. Update Property fields (always)
3. If status = "Done":
   - Add payment fields to SO
   - Update Property last visit date
   - Post detailed chatter message
4. Else: Post basic status update

**If SO doesn't exist:**
1. Call Phase 3 to create SO (auto-detects Path A/B/C)
2. Apply additional Phase 4 updates if needed
3. Post chatter message if applicable

---

## Testing Checklist

### Test 1: Update Existing SO (Pending → Scheduled)
- [ ] Job UUID from Workiz with status = "Scheduled"
- [ ] SO exists in Odoo
- [ ] Verify SO status field updated
- [ ] Verify chatter message posted

### Test 2: Update Existing SO (Any → Done)
- [ ] Job UUID from Workiz with status = "Done"
- [ ] SO exists in Odoo
- [ ] Verify `x_studio_is_paid` = True (if amount due = 0)
- [ ] Verify `x_studio_tip_amount` populated
- [ ] Verify Property last visit date updated
- [ ] Verify chatter message includes payment status

### Test 3: Create Missing SO (Any Status)
- [ ] Job UUID from Workiz (not in Odoo)
- [ ] SO created via Phase 3
- [ ] Phase 4 updates applied
- [ ] Verify all fields populated correctly

### Test 4: Create Missing SO (Done Status)
- [ ] Job UUID from Workiz with status = "Done" (not in Odoo)
- [ ] SO created via Phase 3
- [ ] Payment fields added immediately
- [ ] Chatter message includes payment info

---

## Common Issues

### Issue 1: "No job_uuid provided"
**Cause:** Input mapping in Zapier is incorrect  
**Fix:** Ensure `job_uuid` is mapped to `{{trigger.UUID}}`

### Issue 2: Chatter message not appearing
**Cause:** SO may not exist, or API call failed  
**Fix:** Check Zapier logs for `post_chatter_message` errors

### Issue 3: Property not updating
**Cause:** Property ID not found in SO  
**Fix:** Verify `partner_shipping_id` is set correctly on SO

### Issue 4: Payment fields not set
**Cause:** Status is not "Done" (case-sensitive)  
**Fix:** Script uses `.lower()` for comparison, should work. Check Workiz status value.

---

## Script Statistics

- **Total Lines:** 1,046
- **Total Characters:** ~36,830
- **Includes:**
  - Phase 3 complete logic (Paths A/B/C)
  - Phase 4 update logic
  - All atomic functions (search, create, update, post)
  - Utility functions (format, convert, extract)

---

## Next Steps

1. **Deploy to Zapier:** Copy script to Code by Zapier
2. **Test thoroughly:** Run all 4 test scenarios above
3. **Monitor logs:** Check first few runs for errors
4. **Enable Zap:** Turn on and monitor incoming status changes

---

## Related Documentation

- **Phase 3 Deployment:** `Zapier_Deployment_Guide_FINAL.md`
- **Modular Components:** `2_Modular_Phase3_Components/` folder
- **Field Reference:** `5_Reference_Data/Custom Field names.csv`

---

## Support Notes

**Created by:** DJ  
**AI Assistant:** Claude (Cursor IDE)  
**Last Updated:** 2026-02-07

If you need to modify the script or add features, refer to the modular components in `2_Modular_Phase3_Components/` and test locally before deploying to Zapier.
