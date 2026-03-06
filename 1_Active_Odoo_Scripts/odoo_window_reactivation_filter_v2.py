# ==============================================================================
# ODOO REACTIVATION - WINDOW CLEANING FILTER (V2 - CONTACTS VIEW)
# ==============================================================================
#
# PURPOSE:
# Server Action that filters contacts to show ONLY those whose most recent
# confirmed sales order was for WINDOW CLEANING (not solar-only) and haven't
# been serviced in 1+ year.
#
# DEPLOYMENT:
# This code is pasted into an Odoo Server Action:
# 1. Settings → Technical → Automation → Server Actions → Create
# 2. Fill in:
#    - Name: "Window Reactivation: 1+ Year (Window Customers Only)"
#    - Model: Contact (res.partner)
#    - Action To Do: Execute Python Code
#    - Paste this code below
# 3. Save
# 4. Go to Contacts → Action menu → Your new action will appear
#
# USAGE OPTIONS:
# A. Run from Contacts → Action menu (no selection needed)
# B. Select specific contacts → Action menu (filters selection)
#
# FEATURES:
# - Finds contacts with 1+ year since last order
# - Only includes customers whose LAST order had window cleaning
# - Excludes solar-only customers
# - Shows results in tree view with contact details
# - Logs summary to system log
#
# Author: DJ Sanders
# Generated: 2026-03-06
# ==============================================================================

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
DAYS_THRESHOLD = 365  # 1 year (change to 730 for 2 years, etc.)
EXCLUDE_SOLAR_ONLY = True  # False = include all service types

# If running on selected records, filter those; otherwise scan all contacts
if records:
    contacts_to_scan = records
    _logger.info(f"[REACTIVATION] Scanning {len(contacts_to_scan)} selected contacts...")
else:
    # No selection - scan all customer contacts
    contacts_to_scan = env['res.partner'].search([
        ('is_company', '=', False),
        ('parent_id', '=', False),  # Only parent contacts
        ('customer_rank', '>', 0)   # Only customers
    ])
    _logger.info(f"[REACTIVATION] Scanning ALL {len(contacts_to_scan)} contacts...")

# --- ANALYZE EACH CONTACT ---
qualifying_contacts = []

for contact in contacts_to_scan:
    # Find most recent CONFIRMED sales order
    recent_orders = env['sale.order'].search([
        ('partner_id', '=', contact.id),
        ('state', 'in', ['sale', 'done'])
    ], order='date_order desc', limit=1)
    
    if not recent_orders:
        continue  # No confirmed orders
    
    most_recent_order = recent_orders[0]
    
    # Check date threshold
    if not most_recent_order.date_order:
        continue
    
    days_since_order = (datetime.now().date() - most_recent_order.date_order.date()).days
    
    if days_since_order < DAYS_THRESHOLD:
        continue  # Too recent
    
    # ANALYZE PRODUCTS IN MOST RECENT ORDER
    has_window = False
    has_solar = False
    service_names = []
    
    for line in most_recent_order.order_line:
        product_name = line.product_id.name if line.product_id else (line.name or "")
        
        if not product_name:
            continue
        
        product_lower = product_name.lower()
        
        # Skip non-service items
        if any(x in product_lower for x in ['tip', 'discount', 'legacy', 'quote']):
            continue
        
        # Detect service type
        if 'window' in product_lower:
            has_window = True
            service_names.append(product_name)
        elif 'solar' in product_lower:
            has_solar = True
            service_names.append(product_name)
        else:
            # Other service (screen repair, etc.)
            service_names.append(product_name)
    
    # FILTER LOGIC
    if EXCLUDE_SOLAR_ONLY:
        # INCLUDE if order has window service (even if also has solar)
        # EXCLUDE if order has ONLY solar (no windows)
        if has_window:
            qualifying_contacts.append({
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
                'city': contact.city,
                'days_since': days_since_order,
                'last_order': most_recent_order.name,
                'last_order_date': most_recent_order.date_order.strftime('%Y-%m-%d'),
                'services': ', '.join(service_names[:3]) if service_names else 'Unknown',
                'has_window': has_window,
                'has_solar': has_solar
            })
    else:
        # Include all service types
        if has_window or has_solar:
            qualifying_contacts.append({
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
                'city': contact.city,
                'days_since': days_since_order,
                'last_order': most_recent_order.name,
                'last_order_date': most_recent_order.date_order.strftime('%Y-%m-%d'),
                'services': ', '.join(service_names[:3]) if service_names else 'Unknown',
                'has_window': has_window,
                'has_solar': has_solar
            })

# --- RESULTS ---
contact_ids = [c['id'] for c in qualifying_contacts]

_logger.info(f"[REACTIVATION] Found {len(contact_ids)} window cleaning candidates")

# Sort by days_since (oldest first)
qualifying_contacts.sort(key=lambda x: x['days_since'], reverse=True)

# Log top 20 to system log
_logger.info("=" * 60)
_logger.info("TOP 20 WINDOW REACTIVATION CANDIDATES:")
_logger.info("=" * 60)
for i, info in enumerate(qualifying_contacts[:20]):
    years = round(info['days_since'] / 365.25, 1)
    _logger.info(f"{i+1}. {info['name']} ({info['city']}) - {years} yrs ago - {info['services']}")

# --- DISPLAY FILTERED CONTACTS ---
action = {
    'type': 'ir.actions.act_window',
    'name': f'Window Reactivation Candidates ({len(contact_ids)} found)',
    'res_model': 'res.partner',
    'view_mode': 'tree,form',
    'domain': [('id', 'in', contact_ids)],
    'context': {
        'search_default_customer': 1,
    },
    'target': 'current',
}
