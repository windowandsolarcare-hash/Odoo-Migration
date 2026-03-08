# ==============================================================================
# ODOO REACTIVATION ENGINE - PREVIEW ONLY (v15.4 - Calendly + Quote Filter)
# ==============================================================================
# This script posts a preview to the Chatter and forces a screen reload
# to ensure the new message is visible immediately.

now = datetime.datetime.now()
current_year = now.year

for source_order in records:
    prop_record = source_order.partner_shipping_id
    contact = prop_record.parent_id if prop_record.parent_id else prop_record
    
    contact_vals = contact.read(['phone', 'name', 'street', 'city', 'x_studio_last_visit_all_properties'])[0]
    if not contact_vals.get('phone'):
        continue
        
    full_name = contact_vals.get('name') or "Client"
    first_name = full_name.split()[0]
    
    # Use Contact's aggregated last visit date (Phase 4 maintains this)
    most_recent_visit_date = "recently"
    last_visit = contact_vals.get('x_studio_last_visit_all_properties')
    if last_visit:
        if isinstance(last_visit, str):
            # Try both date formats (ISO and US)
            try:
                last_visit = datetime.datetime.strptime(last_visit, '%Y-%m-%d').date()
            except ValueError:
                last_visit = datetime.datetime.strptime(last_visit, '%m/%d/%Y').date()
        most_recent_visit_date = last_visit.strftime("%a %b %d, %Y")
    
    # Get all properties for this contact to analyze service history
    all_properties = env['res.partner'].search([('parent_id', '=', contact.id), ('x_studio_x_studio_record_category', '=', 'Property')])
    all_orders = env['sale.order'].search([('partner_shipping_id', 'in', all_properties.ids), ('state', 'in', ['sale', 'done'])], order='date_order desc')
    detected_services = {}
    
    for o in all_orders:
        order_year = o.date_order.year if o.date_order else (current_year - 1)
        for line in o.order_line:
            product_name = line.product_id.name if line.product_id else line.name.split('\n')[0]
            clean_name = product_name.lower()
            if any(x in clean_name for x in ['tip', 'discount', 'legacy', 'quote']):
                continue
            if product_name not in detected_services:
                detected_services[product_name] = {'base_price': line.price_subtotal, 'last_seen_year': order_year, 'name_display': product_name}
    
    service_lines = []
    if not detected_services:
        detected_services["Window Cleaning"] = {'base_price': 150.0, 'last_seen_year': current_year - 1, 'name_display': "Window Cleaning"}

    for k, data in detected_services.items():
        base_price = data['base_price']
        is_solar = "solar" in data['name_display'].lower()
        if is_solar:
            final_price = int(base_price)
        else:
            years_elapsed = current_year - data['last_seen_year']
            if years_elapsed < 1: years_elapsed = 1
            compounded_amount = base_price * (1.05 ** years_elapsed)
            final_price = int(5 * round(compounded_amount / 5))
        if final_price < 85: final_price = 85
        service_lines.append(f"• {data['name_display']}: ${final_price}")

    services_text_block = "\n".join(service_lines)
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
Reply STOP to unsubscribe"""

    source_order.message_post(body=f"📝 **PREVIEW MODE**\n\n{message_body}\n\n---\n*To send, use the 'LAUNCH Reactivation' button.*")
    
    # --- THIS IS THE FIX ---
    # This action tells the Odoo web client to reload the current view.
    # It is the most reliable way to show updated data.
    action = {
        'type': 'ir.actions.client',
        'tag': 'reload_context',
    }
    break
