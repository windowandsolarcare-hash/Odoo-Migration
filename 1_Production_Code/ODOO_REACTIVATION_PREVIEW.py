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
    
    # --- SERVICE DETECTION & HISTORY ANALYSIS ---
    for o in all_orders:
        order_year = o.date_order.year if o.date_order else (current_year - 1)
        for line in o.order_line:
            product_name = line.product_id.name if line.product_id else line.name.split('\n')[0]
            clean_name = product_name.lower()
            
            # Detect service categories
            if 'window' in clean_name or 'glass' in clean_name:
                key = 'windows'
            elif 'solar' in clean_name or 'panel' in clean_name:
                key = 'solar'
            elif 'screen' in clean_name:
                key = 'screens'
            elif 'gutter' in clean_name:
                key = 'gutters'
            elif 'pressure' in clean_name or 'wash' in clean_name:
                key = 'pressure_washing'
            else:
                continue
            
            if key not in detected_services:
                detected_services[key] = {
                    'display_name': product_name,
                    'price': line.price_unit,
                    'last_year': order_year,
                    'occurrences': 0
                }
            
            detected_services[key]['occurrences'] += 1
            if order_year > detected_services[key]['last_year']:
                detected_services[key]['last_year'] = order_year
                detected_services[key]['price'] = line.price_unit
    
    if not detected_services:
        source_order.message_post(body="⚠️ No services detected in order history")
        break
    
    # Build pricing menu
    services_text_block = ""
    total_expected_revenue = 0
    for service_data in detected_services.values():
        display_name = service_data['display_name']
        price = service_data['price']
        services_text_block += f"• {display_name}: ${price:.0f}\n"
        total_expected_revenue += price
    
    # Build Calendly URL
    contact_name_encoded = full_name.replace(' ', '+')
    address_encoded = (contact_vals.get('street') or '').replace(' ', '+')
    cal_url = f"https://calendly.com/wasc/ht?name={contact_name_encoded}&a1={address_encoded}"
    
    # Build SMS message
    message_body = f"""Hi {first_name}, I hope all is well. It's Window & Solar Care.

We last serviced your home on {most_recent_visit_date}. It's been a while and we'd like to schedule an appointment again!

Your updated {current_year} estimates for services we've done for you:
{services_text_block}
Tap here to schedule Online:
{cal_url}

Or reply to this text and we will reply back with a date and time.

Dan Saunders
Window & Solar Care
855-245-2273
Text STOP to opt out"""
    
    # --- POST PREVIEW TO CHATTER ONLY ---
    try:
        # Post preview to chatter (simple format for easy copy/paste)
        preview_text = f"""📝 **PREVIEW MODE**

{message_body}

---
*To send as-is, click 'LAUNCH'*
*To modify: Copy text above → Paste into "SMS Text Modified" tab → Edit → Click 'LAUNCH'*"""
        
        source_order.message_post(body=preview_text)
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Error saving preview: {e}")
    
    break
