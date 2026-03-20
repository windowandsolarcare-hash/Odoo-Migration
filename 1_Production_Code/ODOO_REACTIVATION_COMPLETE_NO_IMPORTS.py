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
x_historical_workiz_link_field = 'x_studio_x_historical_workiz_link'
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
    
    contact_vals = contact.read(['phone', 'name', 'street', 'city', 'x_studio_last_visit_all_properties', 'phone_blacklisted', 'x_studio_activelead'])[0]
    
    # Extract campaign info dynamically (format: [id, "name"] or False)
    campaign_id = 1
    campaign_name = "2026 Reactivation Campaign"
    if source_order.campaign_id:
        campaign_id = source_order.campaign_id.id
        campaign_name = source_order.campaign_id.name
    
    source_order.message_post(body=f"[DEBUG] Contact: {contact_vals.get('name')}")
    source_order.message_post(body=f"[DEBUG] Campaign: {campaign_name} (ID: {campaign_id})")
    
    # STOP COMPLIANCE: Skip if blacklisted OR "Do Not Contact" (OR condition)
    is_blacklisted = contact_vals.get('phone_blacklisted')
    is_do_not_contact = contact_vals.get('x_studio_activelead') == 'Do Not Contact'
    
    if is_blacklisted or is_do_not_contact:
        # Determine which reason(s) apply
        reasons = []
        if is_blacklisted:
            reasons.append("Phone is blacklisted (STOP request received)")
        if is_do_not_contact:
            reasons.append("Active/Lead status is 'Do Not Contact'")
        
        reason_text = " AND ".join(reasons)
        
        skip_message = f"""
<p><strong>⛔ REACTIVATION SKIPPED - STOP Compliance</strong></p>
<ul>
<li><strong>Contact:</strong> {contact_vals.get('name')}</li>
<li><strong>Reason:</strong> {reason_text}</li>
<li><strong>Time:</strong> {now_pst.strftime('%Y-%m-%d %H:%M:%S PST')}</li>
</ul>
<p><em>No SMS sent. Contact will remain in Do Not Contact status until manually changed.</em></p>
"""
        contact.message_post(body=skip_message)
        source_order.message_post(body=f"[SKIP] Contact {contact_vals.get('name')} - {reason_text} - no SMS sent")
        break
    
    if not contact_vals.get('phone'):
        source_order.message_post(body="[DEBUG] No phone - skipping")
        continue
        
    full_name = contact_vals.get('name') or "Client"
    first_name = full_name.split()[0]
    phone_sanitized = contact_vals.get('phone', '')
    
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

    # --- READ SMS FROM FIELD (WRITTEN BY PREVIEW) ---
    manual_override = source_order.x_studio_manual_sms_override or ''
    
    if not manual_override.strip():
        source_order.message_post(body="⚠️ ERROR: No SMS text found. Run PREVIEW first!")
        break
    
    # Use SMS from field (either auto-composed by PREVIEW or manually edited by user)
    message_body = manual_override.strip()
    source_order.message_post(body="📤 Sending SMS from 'SMS Text Modified' field...")
    
    # Extract actual price list from SMS (in case user edited prices)
    actual_prices_sent = services_text_block  # Default to calculated
    try:
        # Extract everything between "for services we've done for you:" and "Tap here"
        start_marker = "for services we've done for you:"
        end_marker = "Tap here to schedule"
        
        if start_marker in message_body and end_marker in message_body:
            start_idx = message_body.index(start_marker) + len(start_marker)
            end_idx = message_body.index(end_marker)
            extracted = message_body[start_idx:end_idx].strip()
            
            # Only use if it contains bullet points (user didn't delete the price list)
            if '•' in extracted or '$' in extracted:
                actual_prices_sent = extracted
                source_order.message_post(body="[DEBUG] Extracted actual prices from manual SMS")
    except Exception as e:
        source_order.message_post(body=f"[DEBUG] Could not extract prices from SMS, using calculated: {e}")

    # --- CREATE NEW OPPORTUNITY ---
    try:
        source_order.message_post(body=f"[DEBUG] Creating opportunity for {full_name}")
        
        opportunity_description = f"""--- SYSTEM REFERENCE DATA ---
Source Order: {source_order.name}
Source Order ID: {source_order.id}
Primary Service: {primary_service_str}"""
        
        # Build clickable link for historical Workiz job
        historical_workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
        
        opportunity_vals = {
            'name': f"Reactivation Campaign - {full_name} - {current_date_display}",
            'partner_id': contact.id,
            'stage_id': reactivation_stage_id,
            'type': 'opportunity',
            'campaign_id': campaign_id,
            'expected_revenue': total_expected_revenue,
            'description': opportunity_description,
            'x_primary_service': primary_service_str,
            'x_price_list_text': actual_prices_sent,
            x_odoo_contact_id_field: contact.id,
            x_historical_workiz_uuid_field: workiz_uuid,
            x_historical_workiz_link_field: historical_workiz_link,
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
        
        # Update property's pricing menu with actual prices sent
        prop_record.write({'x_studio_prices_per_service': actual_prices_sent})
        
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
        
        # Log which custom fields exist vs will use fallbacks
        custom_fields_status = []
        field_checks = [
            ('JobSource', 'Referral'),
            ('type_of_service', 'On Request'),
            ('frequency', 'Unknown'),
            ('confirmation_method', 'Cell Phone'),
            ('ok_to_text', 'Yes'),
            ('gate_code', ''),
            ('pricing', ''),
            ('last_date_cleaned', '')
        ]
        
        for field_name, fallback in field_checks:
            hist_value = historical_job.get(field_name) or historical_job.get(field_name.replace('_', '').title())
            if hist_value and str(hist_value).strip():
                custom_fields_status.append(f"  ✓ {field_name}: '{hist_value}' (from historical)")
            elif fallback:
                custom_fields_status.append(f"  ⚠ {field_name}: '{fallback}' (FALLBACK - empty in historical)")
        
        if custom_fields_status:
            fields_log = "<br/>".join(custom_fields_status)
            source_order.message_post(body=f"<p><strong>[DEBUG] Custom field sources:</strong></p>{fields_log}")
        
        # STEP 2: Create graveyard job
        client_id_raw = historical_job.get("ClientId")
        client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
        
        if not client_id:
            source_order.message_post(body="⚠️ No ClientId found")
            continue
        
        # Fix year bug: Workiz sometimes returns 0025 instead of 2025
        raw_last_date = str(historical_job.get("last_date_cleaned") or "")
        if raw_last_date and len(raw_last_date) >= 4 and int(raw_last_date[:4]) < 100:
            fixed_last_date = str(int(raw_last_date[:4]) + 2000) + raw_last_date[4:]
        else:
            fixed_last_date = raw_last_date

        # Build graveyard job with custom field data from historical job
        # NOTE: LineItems, Team, Tags cannot be set via create API - they're read-only or require separate API calls
        graveyard_data = {
            "auth_secret": WORKIZ_AUTH_SECRET,
            "ClientId": client_id,
            "FirstName": str(historical_job.get("FirstName") or ""),
            "LastName": str(historical_job.get("LastName") or ""),
            "Address": str(historical_job.get("Address") or ""),
            "City": str(historical_job.get("City") or ""),
            "State": str(historical_job.get("State") or ""),
            "PostalCode": ''.join(filter(str.isdigit, str(historical_job.get("PostalCode") or "")))[:5],
            "JobType": "Reactivation Lead",
            "Unit": str(historical_job.get("Unit") or ""),
            "ServiceArea": str(historical_job.get("ServiceArea") or contact.x_studio_x_studio_service_area or "Hemet"),
            "JobSource": str(historical_job.get("JobSource") or "Referral"),
            "information_to_remember": message_body,
            "JobNotes": str(historical_job.get("JobNotes") or ""),
            # Phone omitted - ClientId already identifies the client in Workiz (Phone field causes validation error)
            # ENRICHMENT: Copy custom field data from historical job
            "gate_code": str(historical_job.get("gate_code") or historical_job.get("GateCode") or ""),
            "pricing": str(historical_job.get("pricing") or historical_job.get("Pricing") or ""),
            "type_of_service": str(historical_job.get("type_of_service") or "On Request"),
            "frequency": str(historical_job.get("frequency") or "Unknown"),
            "last_date_cleaned": fixed_last_date,
            "ok_to_text": str(historical_job.get("ok_to_text") or "Yes"),
            "confirmation_method": str(historical_job.get("confirmation_method") or "Cell Phone"),
            # LINE ITEMS: Actual prices sent in SMS (for manual entry when customer books)
            "next_job_line_items": actual_prices_sent
        }
        
        source_order.message_post(body=f"[DEBUG] Creating graveyard job...")
        source_order.message_post(body=f"[DEBUG] Request URL: {WORKIZ_BASE_URL}/job/create/")
        source_order.message_post(body=f"[DEBUG] ClientId: {client_id}")
        
        create_response = requests.post(f"{WORKIZ_BASE_URL}/job/create/", json=graveyard_data, timeout=10)
        
        source_order.message_post(body=f"[DEBUG] Create response status: {create_response.status_code}")
        source_order.message_post(body=f"[DEBUG] Create response body: {create_response.text[:500]}")
        
        graveyard_uuid = None
        graveyard_success = False
        
        if create_response.status_code not in [200, 204]:
            source_order.message_post(body=f"⚠️ Failed to create graveyard job (HTTP {create_response.status_code})")
            source_order.message_post(body=f"[DEBUG] Full response: {create_response.text}")
            source_order.message_post(body=f"[INFO] Opportunity created but SMS not sent - check Workiz field validation")
        else:
            source_order.message_post(body=f"[DEBUG] Graveyard job created (HTTP {create_response.status_code})")
            
            # Extract UUID from response
            # Workiz format: {"flag":true, "data":[{"UUID":"MJUERK", ...}]}
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
            else:
                graveyard_success = True
        
        # Only proceed with SMS triggering if graveyard job was created successfully
        if graveyard_success and graveyard_uuid:
            source_order.message_post(body=f"[DEBUG] Graveyard UUID: {graveyard_uuid}")
            
            # Wait for Workiz to fully commit the job before updating status (prevent race condition)
            source_order.message_post(body=f"[DEBUG] Waiting 3 seconds for Workiz to commit job...")
            wait_start = datetime.datetime.now()
            while (datetime.datetime.now() - wait_start).total_seconds() < 3:
                pass
            source_order.message_post(body=f"[DEBUG] Wait complete")
            
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
            graveyard_link = f"https://app.workiz.com/root/job/{graveyard_uuid}/1"
            
            new_opportunity.write({
                'x_workiz_graveyard_uuid': graveyard_uuid,
                'x_workiz_graveyard_link': graveyard_link
            })
            
            source_order.message_post(body=f"[DEBUG] Opportunity linked to graveyard job")
            
            # STEP 5: Log activity to Contact
            activity_data = {
                "x_name": f"{campaign_name} | {current_date_display} | Job #{source_order.name} | {primary_service_str}",
                "x_description": message_body,
                "x_related_order_id": int(source_order.id),
                "x_contact_id": int(contact.id),
                "x_campaign_id": campaign_id,
                "x_activity_type": "reactivation_sms"
            }
            
            contact.write({
                "x_crm_activity_log_ids": [[0, 0, activity_data]]
            })
            
            source_order.message_post(body=f"[DEBUG] Activity logged to Contact")
            
            source_order.message_post(body=f"✅ COMPLETE: {graveyard_link}")
            
            # Archive SMS to opportunity chatter
            try:
                timestamp = now_pst.strftime('%Y-%m-%d %H:%M:%S PST')
                
                sms_archive_message = f"""📤 **SMS SENT - Reactivation**

**Time:** {timestamp}
**Recipient:** {full_name} ({phone_sanitized})
**Graveyard Job:** {graveyard_link}

**Message:**
{message_body}"""
                
                new_opportunity.message_post(body=sms_archive_message)
                source_order.message_post(body="[DEBUG] SMS archived to opportunity chatter")
                
            except Exception as e:
                source_order.message_post(body=f"⚠️ Error archiving SMS: {e}")
        
        # ALWAYS clear SMS field (whether graveyard job succeeded or not)
        try:
            source_order.write({'x_studio_manual_sms_override': ''})
            source_order.message_post(body="[DEBUG] SMS field cleared (ready for next campaign)")
        except Exception as e:
            source_order.message_post(body=f"⚠️ Error clearing SMS field: {e}")
        
    except Exception as e:
        source_order.message_post(body=f"⚠️ Workiz integration error: {e}")
    
    # Break after first record (Server Actions process one selected record at a time)
    break
