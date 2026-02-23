# Phase 5: Automated Job Scheduling - Technical Plan
**Created:** 2026-02-07  
**Status:** Planning & Testing

---

## 🎯 Overview

**Trigger:** Job status changes to "Done" in Workiz (detected by Phase 4)

**Two Paths:**
1. **Maintenance** → Create next scheduled job in Workiz
2. **On Demand** → Create follow-up reminder activity in Odoo

---

## 🔀 Decision Tree

```
Phase 4 detects "Done" status
    ↓
Check: type_of_service
    ↓
    ┌──────────────┴──────────────┐
    ↓                             ↓
"Maintenance"               "On Demand"
(Recurring agreement)       (No agreement)
    ↓                             ↓
Read: frequency field       Estimate follow-up
(3 months, 6 months)        (Default: 6 months)
    ↓                             ↓
Calculate next date         Create Odoo Activity
Apply city-aware           (Reminder, not job)
scheduling                  Due: Sunday of week
    ↓                             ↓
Get line items:            Link to Contact
- If alternating: 2 jobs back
- Else: current job
    ↓
Create new Workiz job
    ↓
Set status: "Send Next Job - Text"
```

---

## 🧪 Phase 5A: Maintenance Path (Priority 1)

### Step 1: Detect Completion in Phase 4

**Integration Point:** Add to `phase4_status_update_router.py`

```python
def main(input_data):
    # ... existing Phase 4 logic ...
    
    if status.lower() == 'done':
        # Existing payment updates
        # ...
        
        # NEW: Trigger Phase 5 if maintenance customer
        type_of_service = workiz_job.get('type_of_service', '').lower()
        
        if 'maintenance' in type_of_service:
            # Call Phase 5A: Schedule next maintenance job
            phase5a_result = schedule_next_maintenance_job(workiz_job, property_id)
            print(f"[Phase 5A] Next job scheduled: {phase5a_result}")
        
        elif 'on demand' in type_of_service or 'on-demand' in type_of_service:
            # Call Phase 5B: Create follow-up reminder
            phase5b_result = create_followup_reminder(workiz_job, contact_id)
            print(f"[Phase 5B] Follow-up reminder created: {phase5b_result}")
```

### Step 2: Calculate Next Service Date

```python
def calculate_next_service_date(frequency_str, customer_city):
    """
    Calculate next service date with city-aware scheduling.
    
    Args:
        frequency_str: "3 months", "4 months", "6 months", etc.
        customer_city: Property city for route-based scheduling
        
    Returns:
        str: Next service date in "YYYY-MM-DD HH:MM:SS" format
    """
    # Parse frequency
    import re
    match = re.search(r'(\d+)\s*(month|week)', frequency_str, re.IGNORECASE)
    
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit == 'month':
            target_date = datetime.now() + timedelta(days=value * 30)
        elif unit == 'week':
            target_date = datetime.now() + timedelta(weeks=value)
    else:
        # Default: 3 months
        target_date = datetime.now() + timedelta(days=90)
    
    # Apply city-aware scheduling
    scheduled_date = apply_city_schedule(target_date, customer_city)
    
    return scheduled_date.strftime('%Y-%m-%d 10:00:00')  # Default 10am


def apply_city_schedule(target_date, city):
    """
    Find best service day based on city routing.
    
    City-to-Day Mapping (like Calendly):
    - Palm Springs → Mondays
    - Rancho Mirage → Tuesdays
    - Palm Desert → Wednesdays
    - Indian Wells → Thursdays
    - Indio/La Quinta → Fridays
    - Hemet → Saturdays
    """
    city_schedule = {
        'palm springs': 0,      # Monday
        'rancho mirage': 1,     # Tuesday
        'palm desert': 2,       # Wednesday
        'indian wells': 3,      # Thursday
        'indio': 4,             # Friday
        'la quinta': 4,         # Friday
        'hemet': 5              # Saturday
    }
    
    city_lower = city.lower()
    preferred_weekday = None
    
    for city_name, weekday in city_schedule.items():
        if city_name in city_lower:
            preferred_weekday = weekday
            break
    
    if preferred_weekday is None:
        # No city match - use target date as-is
        return target_date
    
    # Find nearest preferred day (within ±7 days)
    target_weekday = target_date.weekday()
    days_diff = preferred_weekday - target_weekday
    
    # Adjust within ±7 days
    if days_diff < -3:
        days_diff += 7
    elif days_diff > 3:
        days_diff -= 7
    
    scheduled_date = target_date + timedelta(days=days_diff)
    return scheduled_date
```

### Step 3: Get Line Items (Handle Alternating)

```python
def get_line_items_for_next_job(workiz_job, property_id):
    """
    Determine which line items to copy to next job.
    
    Logic:
    - If alternating = "Yes" → Get from 2 jobs back
    - Else → Get from current job
    - Filter out tips, discounts
    """
    alternating = workiz_job.get('alternating', '').lower()
    
    if alternating in ['yes', '1', 'true']:
        # Need 2 jobs back
        print("[*] Alternating service - getting line items from 2 jobs back")
        
        # Get all jobs for this property from Odoo
        all_sales_orders = search_all_sales_orders_for_property(property_id)
        
        if len(all_sales_orders) >= 2:
            # [0] = current (just done), [1] = previous, [2] = 2 jobs back
            source_uuid = all_sales_orders[1]['x_studio_x_studio_workiz_uuid']
            print(f"[*] Using job {source_uuid} for line items")
            
            source_job = get_job_details(source_uuid)
            line_items = source_job.get('LineItems', [])
        else:
            # Fallback: use current job
            print("[!] Not enough job history - using current job")
            line_items = workiz_job.get('LineItems', [])
    else:
        # Use current job
        print("[*] Regular service - using current job line items")
        line_items = workiz_job.get('LineItems', [])
    
    # Filter out non-service items
    filtered_items = []
    for item in line_items:
        item_name = item.get('Name', '').lower()
        if not any(x in item_name for x in ['tip', 'discount', 'quote', 'legacy']):
            filtered_items.append(item)
    
    print(f"[*] Found {len(filtered_items)} line items to copy")
    return filtered_items


def search_all_sales_orders_for_property(property_id):
    """Get all sales orders for a property, ordered by date DESC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "search_read",
                [[
                    ["partner_shipping_id", "=", property_id],
                    ["state", "in", ["sale", "done"]]
                ]],
                {
                    "fields": ["id", "name", "x_studio_x_studio_workiz_uuid", "date_order"],
                    "order": "date_order desc"
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    return result
```

### Step 4: Create New Job in Workiz

**CRITICAL: Based on testing results**

```python
def create_next_workiz_job(completed_job_data, scheduled_date, line_items):
    """
    Create new Workiz job for next service.
    
    Two-step process per Workiz API docs:
    1. Create job WITHOUT status
    2. Update job to set status (triggers SMS automation)
    """
    # Step 1: Create job (no status)
    new_job_data = {
        'auth_secret': WORKIZ_AUTH_SECRET,
        'ClientId': completed_job_data['ClientId'],
        'LocationId': completed_job_data['LocationId'],
        'JobDateTime': scheduled_date,
        'JobType': completed_job_data.get('JobType', 'Window Cleaning'),
        'Team': completed_job_data.get('Team', []),
        'Tags': completed_job_data.get('Tags', []),
        'frequency': completed_job_data.get('frequency', ''),
        'alternating': completed_job_data.get('alternating', ''),
        'type_of_service': completed_job_data.get('type_of_service', ''),
        'gate_code': completed_job_data.get('gate_code', ''),
        'pricing': completed_job_data.get('pricing', ''),
        
        # TODO: Test if LineItems can be included here
        'LineItems': line_items  # TEST THIS
    }
    
    create_url = f'{WORKIZ_BASE_URL}/job/create/'
    
    print("[*] Creating new Workiz job...")
    create_response = requests.post(create_url, json=new_job_data, timeout=10)
    create_result = create_response.json()
    
    if not create_result.get('flag'):
        print(f"[ERROR] Job creation failed: {create_result.get('msg')}")
        return None
    
    # Extract new job UUID
    new_uuid = create_result.get('data', {}).get('UUID') or create_result.get('UUID')
    print(f"[OK] New job created: {new_uuid}")
    
    # Step 2: Update job to set status (triggers SMS)
    update_url = f'{WORKIZ_BASE_URL}/job/update/'
    update_data = {
        'auth_secret': WORKIZ_AUTH_SECRET,
        'UUID': new_uuid,
        'Status': 'Submitted',
        'SubStatus': 'Send Next Job - Text'
    }
    
    print("[*] Setting job status to trigger SMS...")
    update_response = requests.post(update_url, json=update_data, timeout=10)
    update_result = update_response.json()
    
    if update_result.get('flag'):
        print(f"[OK] Job status updated - SMS automation triggered")
    else:
        print(f"[ERROR] Status update failed: {update_result.get('msg')}")
    
    return new_uuid
```

---

## 🔔 Phase 5B: On Demand Path (Priority 2)

### Create Odoo Activity (Not Workiz Job)

```python
def create_followup_reminder(workiz_job, contact_id):
    """
    Create Odoo activity for future follow-up.
    No Workiz job created - keeps schedule clean!
    """
    # Calculate follow-up date (default 6 months)
    followup_date = datetime.now() + timedelta(days=180)
    
    # Set to Sunday of that week
    days_to_sunday = 6 - followup_date.weekday()
    followup_date = followup_date + timedelta(days=days_to_sunday)
    
    # Get customer info
    customer_name = f"{workiz_job.get('FirstName', '')} {workiz_job.get('LastName', '')}".strip()
    service_address = workiz_job.get('Address', '')
    last_service_date = workiz_job.get('JobDateTime', '')
    
    # Build activity description
    description = f"""Follow-up with customer about next service.

Last Service: {last_service_date}
Services Performed: {', '.join([item['Name'] for item in workiz_job.get('LineItems', [])])}
Property: {service_address}

Action: Call/text customer to schedule next visit."""
    
    # Create activity
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "mail.activity", "create",
                [{
                    "res_model": "res.partner",
                    "res_id": contact_id,
                    "activity_type_id": 2,  # TODO: Get correct activity type ID
                    "summary": f"Follow-up: {customer_name}",
                    "note": description,
                    "date_deadline": followup_date.strftime('%Y-%m-%d'),
                    "user_id": ODOO_USER_ID
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    activity_id = response.json().get("result")
    
    if activity_id:
        print(f"[OK] Follow-up activity created: ID {activity_id}")
        print(f"[*] Due date: {followup_date.strftime('%Y-%m-%d')} (Sunday)")
        return {'success': True, 'activity_id': activity_id}
    else:
        print(f"[ERROR] Failed to create activity")
        return {'success': False}
```

---

## 🧪 Testing Checklist

### Pre-Phase 5 Tests (REQUIRED)
- [ ] Run `test_workiz_create_job.py` to determine:
  - ✅ Correct create endpoint (`/job/create/`)
  - ❓ Can LineItems be included in create payload?
  - ❓ Or must LineItems be added via update after creation?
  - ✅ Confirm two-step process (create → update status)

### Phase 5A Tests (Maintenance)
- [ ] Test with 3-month frequency customer
- [ ] Test with 6-month frequency customer
- [ ] Test alternating service (line items from 2 jobs back)
- [ ] Test regular service (line items from current job)
- [ ] Test city-aware scheduling (Palm Springs → Monday)
- [ ] Verify new job appears in Workiz with correct:
  - Date/time
  - Line items
  - Status: "Send Next Job - Text"
  - SMS sent to customer

### Phase 5B Tests (On Demand)
- [ ] Test activity creation in Odoo
- [ ] Verify activity appears on Contact record
- [ ] Verify due date is Sunday of target week
- [ ] Verify NO job created in Workiz

---

## 📁 File Structure

```
2_Modular_Phase3_Components/
├── phase5a_schedule_maintenance.py (NEW)
│   ├── calculate_next_service_date()
│   ├── apply_city_schedule()
│   ├── get_line_items_for_next_job()
│   └── create_next_workiz_job()
│
├── phase5b_create_reminder.py (NEW)
│   └── create_followup_reminder()
│
├── functions/workiz/
│   └── create_job.py (NEW - after testing)
│
└── test_workiz_create_job.py (TEST SCRIPT)
```

---

## 🚀 Implementation Steps

### Step 1: Run Tests (NOW)
```bash
cd "2_Modular_Phase3_Components"
python test_workiz_create_job.py
```

**Critical findings needed:**
1. LineItems structure from GET
2. Can LineItems be in create payload?
3. Response format after create

### Step 2: Build Atomic Functions
- `calculate_next_service_date(frequency, city)`
- `get_line_items_for_next_job(job, property_id)`
- `create_workiz_job(data, line_items)`
- `create_odoo_activity(contact_id, description, due_date)`

### Step 3: Build Phase 5A Router
- Integrate with Phase 4 (detect "Done" + "Maintenance")
- Orchestrate the full flow
- Error handling

### Step 4: Build Phase 5B Router
- Integrate with Phase 4 (detect "Done" + "On Demand")
- Create activity in Odoo

### Step 5: Testing
- Local testing with real jobs
- Zapier integration testing

### Step 6: Flatten for Zapier
- Combine Phase 3 + 4 + 5 into single script
- Or: Keep as separate Zap (triggered by Phase 4)

---

## ❓ Open Questions

1. **Workiz create endpoint:** Does `/job/create/` accept LineItems in payload? → **Test to find out**
2. **Activity type ID:** What's the correct ID for "Follow-Up" activity in Odoo? → **Query Odoo**
3. **Frequency parsing:** What are all possible formats? ("3 months", "3 Months", "Quarterly"?) → **Check data**
4. **Status values:** What's exact status/substatus to trigger SMS? → **Verify with Workiz**
5. **Route optimization:** Phase 5C or separate phase? → **User decision**

---

## 🎯 Success Criteria

**Phase 5A (Maintenance):**
- ✅ New job auto-created in Workiz after job marked "Done"
- ✅ Date calculated correctly based on frequency
- ✅ Date adjusted to city routing day (±7 days)
- ✅ Line items copied correctly (handles alternating)
- ✅ Status set to trigger SMS automation
- ✅ Customer receives "Send Next Job" text

**Phase 5B (On Demand):**
- ✅ Activity created in Odoo (not Workiz)
- ✅ Due date on Sunday of target week
- ✅ Activity visible on Contact record
- ✅ User receives reminder to follow up
- ✅ NO clutter in Workiz schedule

---

**Next Step:** Run `test_workiz_create_job.py` to answer critical LineItems question!
