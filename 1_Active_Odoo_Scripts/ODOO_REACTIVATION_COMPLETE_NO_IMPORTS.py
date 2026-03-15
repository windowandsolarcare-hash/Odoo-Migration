# ==============================================================================
# ODOO REACTIVATION ENGINE - COMPLETE (NO EXTERNAL IMPORTS)
# ==============================================================================
# This is the complete, self-contained reactivation workflow
# NO Zapier, NO GitHub fetches during runtime
# Copy/paste this entire file into your "Reactivation: 2. LAUNCH Campaign" Server Action

# --- CONFIGURATION ---
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

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
reactivation_stage_id = 5

# Date/time setup
now_utc = datetime.datetime.now()
now_pst = now_utc - datetime.timedelta(hours=8)
current_year = now_pst.year
current_date_display = now_pst.strftime('%m/%d/%Y')
current_date_iso = now_pst.strftime('%Y-%m-%d')

# --- MAIN PROCESSING LOOP ---
for source_order in records:
    source_order.message_post(body="[DEBUG] LAUNCH script started...")
    
    prop_record = source_order.partner_shipping_id
    contact = prop_record.parent_id if prop_record.parent_id else prop_record
    
    contact_vals = contact.read(['phone', 'name', 'street', 'city', 'x_studio_last_visit_all_properties'])[0]
    
    source_order.message_post(body=f"[DEBUG] Contact: {contact_vals.get('name')}")
    
    if not contact_vals.get('phone'):
        source_order.message_post(body="[DEBUG] No phone - skipping")
        continue
        
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
    workiz_uuid = "NO_UUID_FOUND"
    
    # --- SERVICE DETECTION & HISTORY ANALYSIS ---
    if all_orders:
        anchor_order = all_orders[0]
        for o in all_orders:
            if o.amount_total > 0:
                anchor_order = o
                break
        
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
        
        total_expected_revenue += final_price
        service_lines.append(f"• {data['name_display']}: ${final_price}")

    services_text_block = "\n".join(service_lines)
    primary_service_str = service_lines[0].lstrip('• ').strip() if service_lines else ""
    estimate_word = "estimate" if len(service_lines) <= 1 else "estimates"
    
    # --- BOOKING LINK LOGIC ---
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
        source_order.message_post(body=f"[DEBUG] Creating opportunity for {full_name}")
        
        opportunity_description = f"""--- CALCULATED PRICE LIST ---
{services_text_block}

--- SYSTEM REFERENCE DATA ---
Source Order: {source_order.name}
Source Order ID: {source_order.id}
Primary Service: {primary_service_str}"""
        
        opportunity_vals = {
            'name': f"Reactivation Campaign - {full_name} - {current_date_display}",
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
        
        source_order.message_post(body=f"[DEBUG] Opportunity #{opportunity_id} created")
        
        # Post SMS to Opportunity chatter
        new_opportunity.message_post(body=message_body)
        
        # Update contact's last reactivation sent date
        contact.write({'x_studio_last_reactivation_sent': current_date_iso})
        
        source_order.message_post(body=f"✅ Opportunity #{opportunity_id} created - ${total_expected_revenue:.2f}")
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Error creating opportunity: {e}")
        continue
    
    # --- WORKIZ INTEGRATION (DIRECT API CALLS) ---
    try:
        source_order.message_post(body=f"[DEBUG] Starting Workiz integration...")
        
        # STEP 1: Get historical Workiz job
        source_order.message_post(body=f"[DEBUG] Fetching historical job: {workiz_uuid}")
        
        hist_url = f"{WORKIZ_BASE_URL}/job/get/{workiz_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
        
        hist_response = requests.get(hist_url, timeout=10)
        
        if hist_response.status_code != 200:
            source_order.message_post(body=f"⚠️ Failed to fetch historical job (HTTP {hist_response.status_code})")
            continue
        
        hist_result = hist_response.json()
        hist_data = hist_result.get('data', [])
        
        if hist_data and len(hist_data) > 0:
            historical_job = hist_data[0]
        else:
            source_order.message_post(body=f"⚠️ Historical job returned empty data")
            continue
        
        source_order.message_post(body=f"[DEBUG] Historical job found")
        
        # STEP 2: Create graveyard job
        client_id_raw = historical_job.get("ClientId")
        client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
        
        if not client_id:
            source_order.message_post(body="⚠️ No ClientId found")
            continue
        
        graveyard_data = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "ClientId": client_id,
            "FirstName": historical_job.get("FirstName", ""),
            "LastName": historical_job.get("LastName", ""),
            "Address": historical_job.get("Address", ""),
            "City": historical_job.get("City", ""),
            "State": historical_job.get("State", ""),
            "PostalCode": historical_job.get("PostalCode", ""),
            "JobType": "Reactivation Lead",
            "Unit": historical_job.get("Unit", ""),
            "ServiceArea": historical_job.get("ServiceArea", ""),
            "JobSource": historical_job.get("JobSource", "Reactivation"),
            "information_to_remember": message_body,
            "JobNotes": historical_job.get("JobNotes", ""),
            "Phone": historical_job.get("Phone", "")
        }
        
        source_order.message_post(body=f"[DEBUG] Creating graveyard job...")
        source_order.message_post(body=f"[DEBUG] Request URL: {WORKIZ_BASE_URL}/job/create/")
        source_order.message_post(body=f"[DEBUG] ClientId: {client_id}")
        
        create_response = requests.post(f"{WORKIZ_BASE_URL}/job/create/", json=graveyard_data, timeout=10)
        
        source_order.message_post(body=f"[DEBUG] Create response status: {create_response.status_code}")
        source_order.message_post(body=f"[DEBUG] Create response body: {create_response.text[:500]}")
        
        if create_response.status_code not in [200, 204]:
            source_order.message_post(body=f"⚠️ Failed to create graveyard job (HTTP {create_response.status_code})")
            source_order.message_post(body=f"[DEBUG] Full response: {create_response.text}")
            continue
        
        source_order.message_post(body=f"[DEBUG] Graveyard job created (HTTP {create_response.status_code})")
        
        # Extract UUID from response
        # Workiz format: {"flag":true, "data":[{"UUID":"MJUERK", ...}]}
        graveyard_uuid = None
        if create_response.status_code == 200:
            create_result = create_response.json()
            
            # Get UUID from data array
            if isinstance(create_result, dict):
                data_list = create_result.get('data', [])
                if data_list and len(data_list) > 0:
                    graveyard_uuid = data_list[0].get('UUID')
            elif isinstance(create_result, list):
                # Fallback: direct list
                if len(create_result) > 0:
                    graveyard_uuid = create_result[0].get('UUID')
        
        if not graveyard_uuid:
            source_order.message_post(body="⚠️ Could not extract graveyard UUID from response")
            continue
        
        source_order.message_post(body=f"[DEBUG] Graveyard UUID: {graveyard_uuid}")
        
        # STEP 3: Update status to trigger SMS
        source_order.message_post(body=f"[DEBUG] Triggering SMS for UUID: {graveyard_uuid}")
        source_order.message_post(body=f"[DEBUG] Update URL: {WORKIZ_BASE_URL}/job/update/")
        
        status_payload = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "UUID": graveyard_uuid,
            "Status": "Pending",
            "SubStatus": "API SMS Test Trigger"
        }
        
        source_order.message_post(body=f"[DEBUG] Status payload: {status_payload}")
        
        status_response = requests.post(f"{WORKIZ_BASE_URL}/job/update/", json=status_payload, timeout=10)
        
        source_order.message_post(body=f"[DEBUG] Status update response: {status_response.status_code}")
        source_order.message_post(body=f"[DEBUG] Status update body: {status_response.text[:500]}")
        
        if status_response.status_code == 200:
            source_order.message_post(body=f"[DEBUG] SMS triggered successfully")
        else:
            source_order.message_post(body=f"⚠️ SMS trigger failed (HTTP {status_response.status_code})")
            source_order.message_post(body=f"[DEBUG] Full status response: {status_response.text}")
        
        # STEP 4: Update Opportunity with graveyard link
        graveyard_link = f"https://app.workiz.com/jobs/view/{graveyard_uuid}"
        
        new_opportunity.write({
            'x_workiz_graveyard_uuid': graveyard_uuid,
            'x_workiz_graveyard_link': graveyard_link
        })
        
        source_order.message_post(body=f"[DEBUG] Opportunity linked to graveyard job")
        
        # STEP 5: Log activity to Contact
        activity_data = {
            "x_related_order_id": int(source_order.id),
            "x_activity_type": "reactivation_sent",
            "x_description": f"SMS sent via graveyard job {graveyard_uuid}",
            "x_name": f"Reactivation sent for Order {source_order.name}",
            "x_date": current_date_iso,
            "x_campaign": "2026 Reactivation Campaign"
        }
        
        contact.write({
            "x_crm_activity_log_ids": [[0, 0, activity_data]]
        })
        
        source_order.message_post(body=f"[DEBUG] Activity logged to Contact")
        
        source_order.message_post(body=f"✅ COMPLETE: {graveyard_link}")
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Workiz integration error: {e}")
    
    # Break after first record (Server Actions process one selected record at a time)
    break
