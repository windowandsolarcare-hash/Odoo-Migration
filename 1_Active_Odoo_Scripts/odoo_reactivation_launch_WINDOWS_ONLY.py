# ==============================================================================
# ODOO REACTIVATION ENGINE - WINDOW CUSTOMERS ONLY (v4.0)
# ==============================================================================
#
# PURPOSE:
# This script identifies dormant WINDOW CLEANING customers (excludes solar-only)
# and creates reactivation opportunities. It automatically calculates updated
# pricing, generates personalized SMS messages, and triggers Zapier webhook.
#
# KEY DIFFERENCE FROM ORIGINAL:
# ✅ ONLY processes customers whose MOST RECENT order included window cleaning
# ❌ EXCLUDES customers whose MOST RECENT order was solar-only
#
# WORKFLOW:
# 1. Filters to window cleaning customers only (checks most recent order)
# 2. Reads source sales order (dormant customer)
# 3. Extracts customer contact and service history
# 4. Detects all services previously performed
# 5. Applies 5% annual price increase (compounded) to non-solar services
# 6. Generates Calendly booking link with prefilled customer data
# 7. Creates SMS message body with updated pricing
# 8. Creates new CRM Opportunity with expected revenue
# 9. Updates contact's last reactivation date (cooldown tracking)
# 10. Triggers Zapier webhook to send SMS via Workiz
#
# DEPLOYMENT:
# This code is pasted into an Odoo Server Action and runs on-demand when a
# sales order is selected in the Odoo UI.
#
# Author: DJ Sanders
# Generated: 2026-03-06
# ==============================================================================

import datetime

# --- SETUP ---
# History log configuration
history_table_name = 'x_crm_activity_log_ids' 
history_type_field = 'x_activity_type'
history_desc_field = 'x_description'
history_order_field = 'x_related_order_id'
history_name_field = 'x_name'

# Custom field names
cooldown_field_name = 'x_studio_last_reactivation_sent'
pricing_menu_field = 'x_studio_prices_per_service'
x_odoo_contact_id_field = 'x_odoo_contact_id'
x_historical_workiz_uuid_field = 'x_historical_workiz_uuid'
x_workiz_graveyard_link_field = 'x_workiz_graveyard_link'
x_workiz_graveyard_uuid_field = 'x_workiz_graveyard_uuid'

# Opportunity configuration
reactivation_stage_id = 5  # Reactivation stage ID

# New Zapier webhook base URL
base_zapier_url = "https://hooks.zapier.com/hooks/catch/9761276/ugeosmk/"

# Date/time setup
now_utc = datetime.datetime.now()
now_pst = now_utc - datetime.timedelta(hours=8)
current_year = now_pst.year
current_date = now_pst.strftime('%m/%d/%Y')

# --- WINDOW CUSTOMER FILTER ---
def is_window_customer(contact_id):
    """
    Check if contact's MOST RECENT confirmed order included window cleaning.
    Returns: (is_window_customer: bool, most_recent_order: recordset or None)
    """
    # Find most recent confirmed order
    recent_orders = env['sale.order'].search([
        ('partner_id', '=', contact_id),
        ('state', 'in', ['sale', 'done'])
    ], order='date_order desc', limit=1)
    
    if not recent_orders:
        return (False, None)
    
    order = recent_orders[0]
    
    # Analyze products
    has_window = False
    has_solar = False
    
    for line in order.order_line:
        product_name = line.product_id.name if line.product_id else (line.name or "")
        product_lower = product_name.lower()
        
        # Skip non-service items
        if any(x in product_lower for x in ['tip', 'discount', 'legacy', 'quote']):
            continue
        
        if 'window' in product_lower:
            has_window = True
        elif 'solar' in product_lower:
            has_solar = True
    
    # INCLUDE if order has windows (even if also has solar)
    # EXCLUDE if order has ONLY solar (no windows)
    return (has_window, order)

# --- MAIN PROCESSING LOOP ---
processed_count = 0
skipped_solar_only = 0

for source_order in records:
    prop_record = source_order.partner_shipping_id
    contact = prop_record.parent_id if prop_record.parent_id else prop_record
    
    # CHECK IF THIS IS A WINDOW CUSTOMER
    is_window, most_recent_order = is_window_customer(contact.id)
    
    if not is_window:
        skipped_solar_only += 1
        source_order.message_post(body=f"⏭️ Skipped: {contact.name} is a solar-only customer (most recent order has no window cleaning)")
        continue
    
    # Continue with original reactivation logic
    contact_vals = contact.read(['phone', 'name', 'street', 'city'])[0]
    if not contact_vals.get('phone'):
        source_order.message_post(body=f"⏭️ Skipped: {contact.name} has no phone number")
        continue
        
    full_name = contact_vals.get('name') or "Client"
    first_name = full_name.split()[0]
    
    all_orders = env['sale.order'].search([('partner_id', '=', contact.id), ('state', 'in', ['sale', 'done'])], order='date_order desc')
    detected_services = {} 
    most_recent_visit_date = "recently"
    workiz_uuid = "NO_UUID_FOUND"
    
    # --- SERVICE DETECTION & HISTORY ANALYSIS ---
    if all_orders:
        anchor_order = all_orders[0]
        for o in all_orders:
            if o.amount_total > 0:
                anchor_order = o
                break
        if anchor_order.date_order:
            most_recent_visit_date = anchor_order.date_order.strftime("%a %b %d, %Y")
        
        target_uuid_field = 'x_studio_x_studio_workiz_uuid'
        if target_uuid_field in anchor_order._fields:
            uuid_val = anchor_order.read([target_uuid_field])[0].get(target_uuid_field)
            if uuid_val:
                workiz_uuid = uuid_val

        for o in all_orders:
            order_year = o.date_order.year if o.date_order else (current_year - 1)
            for line in o.order_line:
                product_name = line.product_id.name if line.product_id else line.name.split('\n')[0]
                clean_name = product_name.lower()
                if any(x in clean_name for x in ['tip', 'discount', 'legacy', 'quote']):
                    continue
                if product_name not in detected_services:
                    detected_services[product_name] = {'base_price': line.price_subtotal, 'last_seen_year': order_year, 'name_display': product_name}

    # Default service if none detected
    if not detected_services:
        detected_services["Window Cleaning"] = {'base_price': 150.0, 'last_seen_year': current_year - 1, 'name_display': "Window Cleaning"}

    # --- REVENUE CALCULATION & PRICE ENGINE ---
    total_expected_revenue = 0.0
    service_lines = []
    
    for k, data in detected_services.items():
        base_price = data['base_price']
        is_solar = "solar" in data['name_display'].lower()
        
        if is_solar:
            final_price = int(base_price)
        else:
            years_elapsed = current_year - data['last_seen_year']
            if years_elapsed < 1: 
                years_elapsed = 1
            compounded_amount = base_price * (1.05 ** years_elapsed)
            final_price = int(5 * round(compounded_amount / 5))
        
        if final_price < 85: 
            final_price = 85
        
        # Add to total revenue
        total_expected_revenue += final_price
        
        service_lines.append(f"• {data['name_display']}: ${final_price}")

    services_text_block = "\n".join(service_lines)
    primary_service_str = service_lines[0].lstrip('• ').strip() if service_lines else ""
    estimate_word = "estimate" if len(service_lines) <= 1 else "estimates"
    
    # --- BOOKING LINK LOGIC ---
    city = contact_vals.get('city') or ''
    city_slug = "gb"  # Default: General Booking
    
    # Map cities to Calendly event slugs
    if "Palm Springs" in city:
        city_slug = "pmsg"
    elif "Rancho Mirage" in city:
        city_slug = "rm"
    elif "Palm Desert" in city:
        city_slug = "pd"
    elif "Indian Wells" in city:
        city_slug = "iw"
    elif "Indio" in city or "La Quinta" in city:
        city_slug = "indlaq"
    elif "Hemet" in city:
        city_slug = "ht"
    
    # Get name and address for URL
    full_name = contact_vals.get('name') or "Client"
    street_address = contact_vals.get('street') or ""
    
    # Simple URL encoding (spaces and special chars)
    name_encoded = full_name.replace(' ', '+').replace('&', '%26')
    address_encoded = street_address.replace(' ', '+').replace('#', '%23').replace('&', '%26')
    
    # Build Calendly URL with prefilled data
    cal_url = f"https://calendly.com/wasc/{city_slug}?name={name_encoded}&a1={address_encoded}"

    # --- MESSAGE BODY ---
    message_body = f"""Hi {first_name}, I hope all is well. It's Window & Solar Care.

We last serviced your home on {most_recent_visit_date}. It's been a while and we'd love to stop by again!

Your updated {current_year} {estimate_word} for services we've done for you:
{services_text_block}

Tap here to schedule Online:
{cal_url}

Or reply to this text and we will reply back with a date and time.

Dan Saunders
Window & Solar Care
855-245-2273
Text STOP to opt out"""

    # --- CREATE NEW OPPORTUNITY ---
    try:
        opportunity_description = f"""--- CALCULATED PRICE LIST ---
{services_text_block}

--- SYSTEM REFERENCE DATA ---
Source Order: {source_order.name}
Source Order ID: {source_order.id}
Primary Service: {primary_service_str}"""
        
        opportunity_vals = {
            'name': f"Reactivation Campaign - {full_name} - {current_date}",
            'partner_id': contact.id,
            'stage_id': reactivation_stage_id,
            'type': 'opportunity',
            'campaign_id': 1,
            'expected_revenue': total_expected_revenue,
            'description': opportunity_description,
            'x_primary_service': primary_service_str,
            'x_price_list_text': services_text_block,
            x_odoo_contact_id_field: contact.id,
            x_historical_workiz_uuid_field: workiz_uuid,
            x_workiz_graveyard_link_field: '',
            x_workiz_graveyard_uuid_field: '',
        }
        
        new_opportunity = env['crm.lead'].create(opportunity_vals)
        opportunity_id = new_opportunity.id
        
        # Post SMS message to Opportunity chatter
        new_opportunity.message_post(body=message_body)
        
        # Update contact's last reactivation sent date
        contact.write({'x_studio_last_reactivation_sent': current_date})
        
        # Log success message
        source_order.message_post(body=f"✅ Created Opportunity #{opportunity_id} for {full_name} (WINDOW CUSTOMER) with expected revenue: ${total_expected_revenue:.2f}")
        
        processed_count += 1
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Error: Failed to create opportunity. Error: {e}")
        continue
    
    # --- NEW WEBHOOK LAUNCH ---
    try:
        final_url = f"{base_zapier_url}?opportunity_id={opportunity_id}"
        
        action = {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'new'}
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Error: Failed to trigger webhook. Error: {e}")
    
    break

# --- SUMMARY ---
if records:
    records[0].message_post(body=f"""
🎯 Window Reactivation Campaign Complete

✅ Processed: {processed_count} window customers
⏭️ Skipped: {skipped_solar_only} solar-only customers
""")
