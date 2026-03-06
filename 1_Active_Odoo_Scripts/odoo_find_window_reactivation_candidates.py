# ==============================================================================
# ODOO REACTIVATION - WINDOW CLEANING CUSTOMERS ONLY
# ==============================================================================
#
# PURPOSE:
# Finds contacts whose MOST RECENT confirmed sales order was for WINDOW CLEANING
# (not solar panel) and haven't been serviced in 1+ year.
#
# DEPLOYMENT:
# This code is pasted into an Odoo Server Action:
# - Settings → Technical → Automation → Server Actions → Create
# - Name: "Find Window Reactivation Candidates"
# - Model: Contact (res.partner)
# - Action To Do: Execute Python Code
# - Paste this code below
#
# USAGE:
# - Go to Contacts
# - Click "Action" → "Find Window Reactivation Candidates"
# - Script will display matching contacts in a tree view
#
# Author: DJ Sanders
# Generated: 2026-03-06
# ==============================================================================

from datetime import datetime, timedelta

# --- CONFIGURATION ---
DAYS_THRESHOLD = 365  # 1 year
EXCLUDE_SOLAR_ONLY = True  # Set False to include solar-only customers

# --- FIND QUALIFYING CONTACTS ---
qualifying_contact_ids = []
qualifying_contacts_info = []

# Get all contacts (parent records only, not properties)
all_contacts = env['res.partner'].search([
    ('is_company', '=', False),
    ('parent_id', '=', False),  # Only parent contacts, not delivery addresses
    ('customer_rank', '>', 0)   # Only customers
])

log_messages = []
log_messages.append(f"[*] Scanning {len(all_contacts)} contacts...")

for contact in all_contacts:
    # Find most recent CONFIRMED sales order for this contact
    recent_orders = env['sale.order'].search([
        ('partner_id', '=', contact.id),
        ('state', 'in', ['sale', 'done'])
    ], order='date_order desc', limit=1)
    
    if not recent_orders:
        continue  # No confirmed orders for this contact
    
    most_recent_order = recent_orders[0]
    
    # Check if order is older than threshold
    if not most_recent_order.date_order:
        continue
    
    order_date = most_recent_order.date_order
    days_since_order = (datetime.now().date() - order_date.date()).days
    
    if days_since_order < DAYS_THRESHOLD:
        continue  # Too recent, skip
    
    # Analyze products in most recent order
    has_window_service = False
    has_solar_service = False
    
    for line in most_recent_order.order_line:
        product_name = line.product_id.name if line.product_id else line.name
        if not product_name:
            continue
        
        product_lower = product_name.lower()
        
        # Skip non-service items
        if any(x in product_lower for x in ['tip', 'discount', 'legacy', 'quote']):
            continue
        
        # Check for window vs solar
        if 'window' in product_lower:
            has_window_service = True
        elif 'solar' in product_lower:
            has_solar_service = True
    
    # FILTER LOGIC:
    # - If order has window service → INCLUDE (even if also has solar)
    # - If order has ONLY solar service → EXCLUDE
    # - If order has neither (rare) → SKIP
    
    if EXCLUDE_SOLAR_ONLY:
        if has_window_service:
            # This is a window customer (may also do solar, but windows are primary)
            qualifying_contact_ids.append(contact.id)
            qualifying_contacts_info.append({
                'contact': contact,
                'order': most_recent_order,
                'days_since': days_since_order,
                'has_window': has_window_service,
                'has_solar': has_solar_service
            })
        elif has_solar_service and not has_window_service:
            # Solar-only customer, exclude
            pass
    else:
        # Include all customers (window + solar)
        if has_window_service or has_solar_service:
            qualifying_contact_ids.append(contact.id)
            qualifying_contacts_info.append({
                'contact': contact,
                'order': most_recent_order,
                'days_since': days_since_order,
                'has_window': has_window_service,
                'has_solar': has_solar_service
            })

# --- DISPLAY RESULTS ---
log_messages.append(f"[*] Found {len(qualifying_contact_ids)} window cleaning reactivation candidates")

# Log summary to current record (if running from SO view)
if records:
    summary = f"""
✅ Window Reactivation Candidate Search Complete

Found: {len(qualifying_contact_ids)} contacts
- Last order: 1+ year ago
- Most recent order included: Window Cleaning
- Excluded: Solar-only customers

Top 10 Candidates:
"""
    for i, info in enumerate(qualifying_contacts_info[:10]):
        contact = info['contact']
        days = info['days_since']
        order_name = info['order'].name
        years = round(days / 365.25, 1)
        summary += f"\n{i+1}. {contact.name} - {years} years ago (Order: {order_name})"
    
    records[0].message_post(body=summary)

# --- RETURN ACTION ---
# Display matching contacts in tree view
action = {
    'type': 'ir.actions.act_window',
    'name': 'Window Reactivation Candidates (1+ Year)',
    'res_model': 'res.partner',
    'view_mode': 'tree,form',
    'domain': [('id', 'in', qualifying_contact_ids)],
    'context': {'search_default_customer': 1},
    'target': 'current',
}
