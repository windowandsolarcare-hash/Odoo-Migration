# Window Reactivation Filter - Odoo Server Action Compatible
# Author: DJ Sanders | Generated: 2026-03-06
# 
# Shows contacts whose MOST RECENT order included window cleaning
# and haven't been serviced in 1+ year.
#
# NO IMPORTS NEEDED - Odoo provides datetime in Server Action context

# --- CONFIGURATION ---
DAYS_THRESHOLD = 365
EXCLUDE_SOLAR_ONLY = True

# Scan selected contacts or all customer contacts
if records:
    contacts_to_scan = records
else:
    contacts_to_scan = env['res.partner'].search([
        ('is_company', '=', False),
        ('parent_id', '=', False),
        ('customer_rank', '>', 0)
    ])

# --- ANALYZE EACH CONTACT ---
qualifying_contacts = []

for contact in contacts_to_scan:
    # Find most recent CONFIRMED sales order
    recent_orders = env['sale.order'].search([
        ('partner_id', '=', contact.id),
        ('state', 'in', ['sale', 'done'])
    ], order='date_order desc', limit=1)
    
    if not recent_orders:
        continue
    
    most_recent_order = recent_orders[0]
    
    if not most_recent_order.date_order:
        continue
    
    days_since_order = (datetime.datetime.now().date() - most_recent_order.date_order.date()).days
    
    if days_since_order < DAYS_THRESHOLD:
        continue
    
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
            service_names.append(product_name)
    
    # FILTER LOGIC
    if EXCLUDE_SOLAR_ONLY:
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

# Sort by days_since (oldest first)
qualifying_contacts.sort(key=lambda x: x['days_since'], reverse=True)

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
