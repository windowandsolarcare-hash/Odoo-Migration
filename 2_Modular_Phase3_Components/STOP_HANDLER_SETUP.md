# STOP REQUEST HANDLER - Setup Guide
**Author:** DJ Sanders  
**Date:** 2026-03-08  
**Purpose:** Automated SMS opt-out compliance via Workiz → Zapier → Odoo

---

## OVERVIEW

When a customer replies "STOP" to any SMS, we must:
1. **Immediately blacklist** them in Odoo (set `is_blacklisted = True`)
2. **Never send them marketing SMS again** (reactivation script now filters these out)
3. **Log the opt-out** in their CRM Activity History

This is a **legal compliance requirement** (TCPA, CAN-SPAM).

---

## IMPLEMENTATION STATUS

### ✅ Code Deployed
- **Reactivation Script:** Now excludes `is_blacklisted = True` contacts
- **STOP Handler:** `zapier_stop_handler_FINAL.py` ready to deploy

### ⚠️ Zapier Setup Required
You need to create a new Zap to connect Workiz incoming messages → STOP handler script

---

## HOW TO SEE INCOMING MESSAGES IN WORKIZ

### Option 1: Workiz Message Center (Recommended)
1. Log into Workiz web app
2. Go to **Message Center** (usually top navigation or sidebar)
3. You'll see all incoming/outgoing SMS conversations
4. Filter by recent messages to find "STOP" replies

### Option 2: Workiz Mobile App
1. Open Workiz mobile app
2. Tap **Messages** or **Inbox**
3. Incoming customer replies appear here

### Option 3: Email Notifications
- Check if Workiz sends email notifications for incoming messages
- Go to Workiz Settings → Notifications
- Enable "Email me when customer replies"

---

## ZAPIER SETUP - Automated STOP Handler

### Step 1: Create Trigger (Workiz Webhook)

**Option A: If Workiz has Zapier integration with "New Message" trigger**
1. Zapier → Create New Zap
2. Trigger: **Workiz → New Message Received**
3. Filter: Only continue if message body contains "STOP" (case insensitive)

**Option B: If using Workiz webhook/API**
1. Zapier → Create New Zap
2. Trigger: **Webhooks by Zapier → Catch Hook**
3. Get webhook URL from Zapier
4. Configure in Workiz settings to send webhook on incoming message
5. Add **Filter by Zapier** step: Continue only if `message_body` contains "STOP"

### Step 2: Extract Data (Formatter)
- **customer_phone:** Extract from webhook payload
- **message_body:** The actual message text (e.g., "STOP", "Stop", "STOP pls")
- **workiz_job_id:** (Optional) Job ID if available in webhook

### Step 3: Run STOP Handler (Code by Zapier)
1. Action: **Code by Zapier → Run Python**
2. **Input Data:**
   - `customer_phone`: [Map from Step 1]
   - `message_body`: [Map from Step 1]
   - `workiz_job_id`: [Map from Step 1 or leave empty]

3. **Code:**
```python
import urllib.request
exec(urllib.request.urlopen('https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_stop_handler_FINAL.py').read().decode())
return main(input_data)
```

### Step 4: Error Handling (Optional)
Add a **Filter by Zapier** step:
- Only continue if status = "error"
- Send yourself an email/SMS alert if contact not found

---

## TESTING THE SETUP

### Test Case 1: Find Existing Contact
1. Use a phone number you know is in Odoo
2. Manually trigger the Zap with test data:
   ```json
   {
     "customer_phone": "5551234567",
     "message_body": "STOP",
     "workiz_job_id": "TEST123"
   }
   ```
3. Check Odoo Contact → `is_blacklisted` should be True
4. Check CRM Activity Log → "SMS Opt-Out Request" logged

### Test Case 2: Reactivation Filter
1. Run reactivation script on a Sales Order for that blacklisted contact
2. Odoo should post: `[SKIP] Contact [Name] is blacklisted (STOP request) - no SMS sent`
3. No opportunity created, no Workiz job, no SMS sent

### Test Case 3: Phone Number Not Found
1. Trigger Zap with fake phone number
2. Should return: `status: "error", message: "Contact not found"`
3. You'll need to manually find and blacklist them

---

## WORKIZ WEBHOOK CONFIGURATION

If Workiz doesn't have native Zapier "New Message" trigger, you'll need to:

1. **Log into Workiz → Settings → Integrations/Webhooks**
2. **Create webhook:** "When message received"
3. **Webhook URL:** [Paste Zapier webhook URL from Step 1 Option B]
4. **Payload format:** Ensure it includes:
   - Customer phone number
   - Message body/text
   - Job ID (if available)

**Note:** If Workiz doesn't support this webhook, you'll need **manual processing** for now:
- When you see STOP in Workiz Message Center
- Open customer in Odoo
- Check the `Blacklisted` checkbox
- Save

---

## MANUAL STOP REQUEST WORKFLOW (Fallback)

If automated setup isn't available yet:

1. **See STOP in Workiz Message Center**
2. **Find Contact in Odoo** (by name or phone)
3. **Edit Contact → Check "Blacklisted"** (in Marketing or General tab)
4. **Save**
5. **Done** - Reactivation script will now skip them

---

## WHAT HAPPENS WHEN CONTACT IS BLACKLISTED

### Reactivation Campaign
- ✅ Contact is automatically skipped
- ✅ No opportunity created
- ✅ No Workiz graveyard job
- ✅ No SMS sent
- ✅ Debug message logged: `[SKIP] Contact [Name] is blacklisted`

### Future Campaigns
- Any script that checks `is_blacklisted` will skip them
- Standard Odoo marketing modules respect this field

---

## FILES CREATED

| File | Purpose | Location |
|---|---|---|
| `zapier_stop_handler_FINAL.py` | Zapier script to blacklist contacts | GitHub main |
| `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` | Updated with blacklist filter | GitHub main |
| `STOP_HANDLER_SETUP.md` | This guide | Local/GitHub |

---

## NEXT STEPS

1. **Update Odoo Server Action** with latest reactivation script from GitHub
2. **Set up Workiz webhook** (if available) or use manual process
3. **Create Zapier zap** using `zapier_stop_handler_FINAL.py`
4. **Test with real STOP message** to verify end-to-end

---

**GitHub Links:**
- **STOP Handler:** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/2_Modular_Phase3_Components/zapier_stop_handler_FINAL.py
- **Updated Reactivation:** https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Active_Odoo_Scripts/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py
