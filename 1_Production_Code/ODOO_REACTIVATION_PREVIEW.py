# ==============================================================================
# ODOO REACTIVATION PREVIEW - Saves Draft SMS to Opportunity
# ==============================================================================
# This script composes the reactivation SMS and saves it to fields for preview
# NO SMS is sent - this is for review only
#
# After running this:
# - You can see the composed SMS in the opportunity's chatter
# - Click "Launch" to send as-is
# - Click "Launch (Modify Text)" to edit before sending
#
# REQUIRED FIELDS ON SALE ORDER (sale.order):
# - x_studio_manual_sms_override (Text) - in "SMS Text Modified" tab
# ==============================================================================

# NOTE: datetime is pre-loaded in Odoo, no import needed

# Date/time setup
now_utc = datetime.datetime.now()
now_pst = now_utc - datetime.timedelta(hours=8)
current_year = now_pst.year
current_date_display = now_pst.strftime('%m/%d/%Y')

# --- MAIN PROCESSING LOOP ---
for source_order in records:
    source_order.message_post(body="[DEBUG] PREVIEW script started...")
    
    prop_record = source_order.partner_shipping_id
    contact = prop_record.parent_id if prop_record.parent_id else prop_record
    
    contact_vals = contact.read(['phone', 'name', 'street', 'city', 'x_studio_last_visit_all_properties', 'phone_blacklisted', 'x_studio_activelead'])[0]
    
    # STOP COMPLIANCE: Skip blacklisted contacts
    if contact_vals.get('phone_blacklisted') or contact_vals.get('x_studio_activelead') == 'Do Not Contact':
        source_order.message_post(body=f"⚠️ Contact {contact_vals.get('name')} is blacklisted - cannot send reactivation")
        break
    
    if not contact_vals.get('phone'):
        source_order.message_post(body="⚠️ No phone number - cannot send SMS")
        break
        
    full_name = contact_vals.get('name') or "Client"
    first_name = full_name.split()[0]
    
    # Use Contact's aggregated last visit date
    most_recent_visit_date = "recently"
    last_visit = contact_vals.get('x_studio_last_visit_all_properties')
    
    if last_visit:
        if isinstance(last_visit, str):
            try:
                last_visit = datetime.datetime.strptime(last_visit, '%Y-%m-%d').date()
            except ValueError:
                try:
                    last_visit = datetime.datetime.strptime(last_visit, '%m/%d/%Y').date()
                except ValueError:
                    last_visit = None
        most_recent_visit_date = last_visit.strftime("%a %b %d, %Y") if last_visit else "recently"
    
    # Get all properties for this contact to analyze service history
    all_properties = env['res.partner'].search([('parent_id', '=', contact.id), ('x_studio_x_studio_record_category', '=', 'Property')])
    all_orders = env['sale.order'].search([('partner_shipping_id', 'in', all_properties.ids), ('state', 'in', ['sale', 'done'])], order='date_order desc')
    detected_services = {}
    
    # --- SERVICE DETECTION & HISTORY ANALYSIS (MATCH LAUNCH LOGIC) ---
    for o in all_orders:
        order_year = o.date_order.year if o.date_order else (current_year - 1)
        for line in o.order_line:
            product_name = line.product_id.name if line.product_id else line.name.split('\n')[0]
            clean_name = product_name.lower()
            
            # Skip tip, discount, legacy, quote
            if any(x in clean_name for x in ['tip', 'discount', 'legacy', 'quote']):
                continue
            
            # Store by product name (not category) with base price
            if product_name not in detected_services:
                detected_services[product_name] = {
                    'base_price': line.price_subtotal,
                    'last_seen_year': order_year,
                    'name_display': product_name
                }
    
    # Default service if none detected
    if not detected_services:
        detected_services["Window Cleaning"] = {
            'base_price': 150.0,
            'last_seen_year': current_year - 1,
            'name_display': "Window Cleaning"
        }
    
    # --- REVENUE CALCULATION & PRICE ENGINE (5% ANNUAL INCREASE) ---
    total_expected_revenue = 0.0
    service_lines = []
    
    for k, data in detected_services.items():
        base_price = data['base_price']
        is_solar = "solar" in data['name_display'].lower()
        is_addon = base_price < 70  # Add-on items (mirrors, garage doors, etc.) stay at original price
        
        if is_addon:
            # Add-on services: keep original price (no inflation, no minimum)
            final_price = int(base_price)
        elif is_solar:
            # Solar: keep original price (no inflation)
            final_price = int(base_price)
        else:
            # Regular services: apply 5% annual inflation + $85 minimum
            years_elapsed = current_year - data['last_seen_year']
            if years_elapsed < 1:
                years_elapsed = 1
            compounded_amount = base_price * (1.05 ** years_elapsed)
            final_price = int(5 * round(compounded_amount / 5))  # Round to nearest $5
            
            if final_price < 85:
                final_price = 85
        
        total_expected_revenue += final_price
        service_lines.append(f"• {data['name_display']}: ${final_price}")
    
    services_text_block = "\n".join(service_lines)
    estimate_word = "estimate" if len(service_lines) <= 1 else "estimates"
    
    # --- BOOKING LINK LOGIC (MATCH LAUNCH) ---
    city = contact_vals.get('city') or ''
    city_slug = "gb"
    
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
    
    name_encoded = full_name.replace(' ', '+').replace('&', '%26')
    address_encoded = (contact_vals.get('street') or "").replace(' ', '+').replace('#', '%23').replace('&', '%26')
    
    cal_url = f"https://calendly.com/wasc/{city_slug}?name={name_encoded}&a1={address_encoded}"
    
    # Build SMS message
    message_body = f"""Hi {first_name}, I hope all is well. It's Window & Solar Care.

We last serviced your home on {most_recent_visit_date}. It's been a while and we'd like to schedule an appointment again!

Your updated {current_year} {estimate_word} for services we've done for you:
{services_text_block}

Tap here to schedule Online:
{cal_url}

Or reply to this text and we will reply back with a date and time.

Dan Saunders
Window & Solar Care
855-245-2273
Text STOP to opt out"""
    
    # --- SAVE TO FIELD & POST TO CHATTER ---
    try:
        # Write formatted SMS to field (preserves line breaks)
        source_order.write({
            'x_studio_manual_sms_override': message_body
        })
        
        # Also post to chatter for quick viewing
        source_order.message_post(body=f"📝 **PREVIEW MODE**\n\n{message_body}\n\n---\n*To send as-is, click 'LAUNCH'*\n*To modify: Go to 'SMS Text Modified' tab → Edit the field → Click 'LAUNCH'*")
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Error saving preview: {e}")
    
    break
