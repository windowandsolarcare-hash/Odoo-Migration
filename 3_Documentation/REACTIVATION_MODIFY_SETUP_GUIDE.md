# Reactivation SMS Modify Workflow - Setup Guide

## Overview
This guide helps you set up the 2-button reactivation workflow:
- **PREVIEW** → View the composed SMS in chatter
- **Launch** → Send SMS as-is (90% of cases)
- **Launch (Modify Text)** → Edit SMS/pricing before sending (10% of edge cases)

---

## Step 1: Add Required Fields to CRM Opportunity

Go to **Settings → Studio → CRM → Opportunities**

Add these **Text fields**:

1. **Technical Name:** `x_draft_sms_message`
   - **Label:** Draft SMS Message
   - **Widget:** Text (multiline)
   - **Show on form:** Yes (for editing in modify workflow)

2. **Technical Name:** `x_draft_pricing_menu`
   - **Label:** Draft Pricing Menu
   - **Widget:** Text (multiline)
   - **Show on form:** Yes (for editing in modify workflow)

---

## Step 2: Create "PREVIEW" Server Action

**Settings → Technical → Server Actions → Create**

**Name:** `Reactivation: 1. PREVIEW`
**Model:** Sale Order (sale.order)
**Action To Do:** Execute Python Code

**Python Code:** Copy from GitHub:
```
https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/ODOO_REACTIVATION_PREVIEW.py
```

---

## Step 3: Update "Launch" Server Action

**Find existing:** `Reactivation: 2. LAUNCH Campaign`

**Python Code:** Replace with code from GitHub:
```
https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py
```

**Changes in this version:**
- ✅ SMS text: "schedule an appointment again" (instead of "love to stop by")
- ✅ Updates property's `x_studio_prices_per_service` field
- ✅ STOP compliance checks (phone_blacklisted + Do Not Contact)

---

## Step 4: Create "Launch (Modify Text)" Workflow

### Option A: Simple Approach (Manual Edit)

1. Run **PREVIEW** to save draft SMS to opportunity fields
2. In opportunity form, manually edit `x_draft_sms_message` and `x_draft_pricing_menu` fields
3. Create new Server Action: `Reactivation: 3. LAUNCH (Modify Text)`
   - **Python Code:** Copy from:
   ```
   https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/ODOO_REACTIVATION_MODIFY_WIZARD.py
   ```

### Option B: Wizard Popup (Advanced - Requires Odoo Studio or Developer)

This creates a popup form where you edit the SMS before sending.

**In Odoo Studio:**
1. Go to **CRM → Opportunities → Automation**
2. Create a new **Action** button
3. Set it to open a form view showing:
   - `x_draft_sms_message` (editable)
   - `x_draft_pricing_menu` (editable)
   - Button that triggers the MODIFY server action

---

## Workflow Summary

### **Normal Flow (90% of cases):**
```
1. Click "PREVIEW" → See SMS in chatter
2. Looks good → Click "Launch" → SMS sent immediately
```

### **Edge Cases (10% of cases):**
```
1. Click "PREVIEW" → See SMS in chatter
2. Wrong address/pricing → Click "Launch (Modify Text)"
3. Edit SMS and pricing in popup/form
4. Click "Send Modified Message" → SMS sent with edits
```

---

## What Gets Updated

### Regular "Launch":
- ✅ Sends SMS (via Workiz API)
- ✅ Creates Workiz graveyard job
- ✅ Creates CRM Opportunity
- ✅ Posts SMS to opportunity chatter
- ✅ Updates contact: `x_studio_last_reactivation_sent`
- ✅ Updates property: `x_studio_prices_per_service`
- ✅ Logs activity to contact's Activity Log

### "Launch (Modify Text)":
- ✅ Everything above
- ✅ Uses YOUR edited SMS text (not auto-generated)
- ✅ Uses YOUR edited pricing menu
- ✅ Marks in chatter as "MODIFIED SMS"

---

## Testing

1. **Create a test reactivation:**
   - Find a completed sales order with old service date
   - Click "PREVIEW" → Check chatter for composed SMS

2. **Test normal launch:**
   - Click "Launch" → Verify SMS sent to Workiz
   - Check contact: `x_studio_last_reactivation_sent` updated?
   - Check property: `x_studio_prices_per_service` updated?

3. **Test modify launch:**
   - Click "Launch (Modify Text)"
   - Change address or pricing
   - Send → Verify modified text went to Workiz

---

## GitHub Links

**All 3 scripts are on GitHub main:**

1. **PREVIEW:** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Production_Code/ODOO_REACTIVATION_PREVIEW.py

2. **LAUNCH:** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py

3. **LAUNCH (Modify Text):** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Production_Code/ODOO_REACTIVATION_MODIFY_WIZARD.py

---

## Next Steps

Once this is working, you can:
1. Delete old PREVIEW/LAUNCH actions if they exist
2. Test with a few real reactivations
3. Train team on when to use "Launch" vs "Launch (Modify Text)"
4. Monitor which edge cases come up (moved customers, wrong pricing, etc.)
