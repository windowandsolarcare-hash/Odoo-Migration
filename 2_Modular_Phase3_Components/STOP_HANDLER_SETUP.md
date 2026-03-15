# STOP REQUEST HANDLER - Setup Guide
**Author:** DJ Sanders  
**Date:** 2026-03-08  
**Purpose:** Automated SMS opt-out compliance via Workiz → Odoo Webhook (NO ZAPIER)

---

## OVERVIEW

When a customer replies "STOP" to any SMS:
1. **You see it in Workiz Message Center** (manual)
2. **You change job status to:** `STOP - do not CALL or TEXT` (manual trigger)
3. **Workiz webhook fires → Odoo catches it** (automated)
4. **Odoo blacklists the contact** (automated)
5. **Future campaigns skip them** (automated)

This is a **legal compliance requirement** (TCPA, CAN-SPAM).

---

## IMPLEMENTATION STATUS

### ✅ Code Deployed
- **Reactivation Script:** Now excludes `is_blacklisted = True` contacts
- **Webhook Handler:** `odoo_webhook_stop_handler.py` ready to deploy

### ⚠️ Setup Required
1. Create Odoo Studio webhook (5 minutes)
2. Configure Workiz webhook on status change (5 minutes)

---

## STEP 1: CREATE ODOO WEBHOOK (Odoo Studio)

### 1. Open Studio and Create Webhook
1. **Log into Odoo → Open Studio**
2. **Studio → Webhooks → New**
3. **Webhook Settings:**
   - **Name:** `Workiz STOP Request Handler`
   - **Target Model:** `Contact (res.partner)`
   - **Enable "Log Calls"** (for debugging)

### 2. Add Handler Code
1. **Scroll to "Target Record code" section**
2. **Open GitHub:**  
   https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Active_Odoo_Scripts/odoo_webhook_stop_handler.py
3. **Copy entire file contents**
4. **Paste into Odoo Studio code editor**
5. **Save webhook**

### 3. Get Webhook URL
- After saving, Odoo generates a **confidential webhook URL**
- Format: `https://window-solar-care-migration-dj-sanders-main-15099858.dev.odoo.com/webhooks/abc123def456...`
- **Copy this URL** for Step 2

---

## STEP 2: CONFIGURE WORKIZ WEBHOOK

### Option A: Workiz Has Webhook Settings
1. **Workiz → Settings → Integrations/Webhooks**
2. **Create New Webhook:**
   - **Event:** "Job Status Changed" or "Job Updated"
   - **Filter/Condition:** Status = `STOP - do not CALL or TEXT`
   - **URL:** [Paste Odoo webhook URL from Step 1]
   - **Method:** POST
   - **Content-Type:** application/json
3. **Save**

### Option B: Workiz Doesn't Support Webhooks
**Fallback to manual process:**
- See STOP in Workiz → Open Contact in Odoo → Check "Blacklisted" → Save

---

## STEP 3: CREATE WORKIZ STATUS

If status `STOP - do not CALL or TEXT` doesn't exist:

1. **Workiz → Settings → Job Statuses**
2. **Add New Status:**
   - **Name:** `STOP - do not CALL or TEXT`
   - **Internal Name:** `stop__do_not_call_or_text`
   - **Category:** Cancelled or Custom
   - **Color:** Red (warning)
3. **Save**

---

## DAILY WORKFLOW (When Customer Sends STOP)

### What You Do (Manual - 10 seconds):
1. Open Workiz Message Center
2. See customer replied "STOP"
3. Open that job
4. Change status to `STOP - do not CALL or TEXT`
5. Save

### What Happens Automatically:
1. ✅ Workiz webhook fires to Odoo
2. ✅ Odoo finds Contact by phone or Workiz ClientId
3. ✅ Odoo sets `is_blacklisted = True`
4. ✅ Activity logged: "SMS Opt-Out Request"
5. ✅ You get notification in Odoo (webhook log)
6. ✅ Future campaigns skip them automatically

**No Zapier. No manual Odoo updates.**

---

## TESTING THE SETUP

### Test 1: End-to-End Webhook Test
1. Pick a test customer in Workiz (existing job)
2. Change job status to `STOP - do not CALL or TEXT`
3. **Check Odoo:**
   - Studio → Webhooks → "Workiz STOP Request Handler" → Call History
   - Should show successful webhook call
4. **Check Contact in Odoo:**
   - Find the customer by name
   - `Blacklisted` checkbox should be checked
   - CRM Activity Log should have "SMS Opt-Out Request" entry

### Test 2: Reactivation Filter
1. Find a Sales Order for that blacklisted contact
2. Run "Reactivation: 2. LAUNCH Campaign" Server Action
3. Check Opportunity chatter:
   - Should see: `[SKIP] Contact [Name] is blacklisted (STOP request)`
4. Verify no opportunity created, no Workiz job

### Test 3: Already Blacklisted
1. Trigger webhook again for same contact
2. Webhook should return: "Contact [Name] was already blacklisted"
3. No duplicate activity log created

---

## TROUBLESHOOTING

### Webhook Not Firing
**Check:**
- Workiz webhook URL is correct (from Odoo Studio)
- Workiz status filter matches exactly: `STOP - do not CALL or TEXT`
- Workiz webhook is enabled/active

### Contact Not Found
**Check:**
- Phone number in Workiz matches Odoo format
- Try searching by Workiz ClientId instead (more reliable)
- Check webhook logs in Odoo Studio for exact payload received

### Blacklist Not Applied
**Check:**
- Webhook code saved in Odoo Studio
- Webhook "Log Calls" enabled
- Review Call History for error messages

---

## WHAT HAPPENS WHEN CONTACT IS BLACKLISTED

### Immediate Protection
- ✅ Reactivation campaigns skip them
- ✅ Odoo Marketing module respects blacklist
- ✅ Manual campaigns show warning when trying to contact

### Future-Proof
- ✅ Any new campaign code that checks `is_blacklisted` respects opt-out
- ✅ No chance of accidental SMS to opted-out customers
- ✅ Legal compliance maintained

---

## FILES & LINKS

**GitHub:**
- Webhook Handler: https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Active_Odoo_Scripts/odoo_webhook_stop_handler.py
- Reactivation Script: https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Active_Odoo_Scripts/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py

**NO ZAPIER REQUIRED**
