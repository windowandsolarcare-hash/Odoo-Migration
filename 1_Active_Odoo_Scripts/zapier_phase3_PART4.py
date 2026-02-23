# ==============================================================================
# ZAPIER PHASE 3 - PART 4 of 4
# ==============================================================================
# Main Processing & Orchestrator
# Paste this LAST, after PART 1, 2, and 3
# ==============================================================================

def process_phase3e(contact, opportunity, booking_info, won_result):
    """Phase 3E: Create sales order with full Workiz data + confirm + update property."""
    
    if not won_result.get('success'):
        return {'success': False, 'sales_order_id': None, 'message': 'Opportunity not Won'}
    
    property_id = get_property_for_contact(contact['street'])
    if not property_id:
        property_id = contact['id']
    
    workiz_job = get_workiz_job_details(opportunity['x_workiz_graveyard_uuid'])
    if not workiz_job:
        return {'success': False, 'sales_order_id': None, 'message': 'Could not fetch Workiz job'}
    
    serial_id = workiz_job.get('SerialId', '')
    order_name = format_serial_id_for_odoo(serial_id) if serial_id else None
    
    gate_code = workiz_job.get('GateCode') or workiz_job.get('gate_code') or workiz_job.get('Gate') or workiz_job.get('information_to_remember', '')
    pricing = workiz_job.get('Pricing') or workiz_job.get('pricing') or workiz_job.get('PricingNote') or workiz_job.get('price_note', '')
    
    job_datetime_pacific = workiz_job.get('JobDateTime', '')
    
    if job_datetime_pacific:
        pacific = pytz.timezone('America/Los_Angeles')
        utc = pytz.UTC
        
        dt_naive = datetime.strptime(job_datetime_pacific, '%Y-%m-%d %H:%M:%S')
        dt_pacific = pacific.localize(dt_naive)
        dt_utc = dt_pacific.astimezone(utc)
        
        booking_datetime_for_odoo = dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    else:
        booking_datetime_for_odoo = booking_info['booking_time'].replace('T', ' ').replace('Z', '').split('.')[0]
    
    so_result = create_sales_order(contact['id'], property_id, workiz_job, booking_datetime_for_odoo, order_name)
    
    if not so_result['success']:
        return so_result
    
    confirm_result = confirm_sales_order(so_result['sales_order_id'])
    
    if confirm_result['success']:
        update_sales_order_date(so_result['sales_order_id'], booking_datetime_for_odoo)
    
    update_property_fields(property_id, gate_code, pricing)
    
    return so_result


def process_phase3f(contact, booking_info):
    """Phase 3F: Update contact email from Calendly."""
    new_email = booking_info.get('email', '')
    
    if not new_email:
        return {'success': False, 'message': 'No email provided'}
    
    return update_contact_email(contact['id'], new_email)


def main(input_data):
    """Main function for Zapier - orchestrates all 6 phases."""
    
    booking_info = {
        'booking_time': input_data.get('event_start_time'),
        'service_type': input_data.get('service_type_required'),
        'additional_notes': input_data.get('additional_notes', ''),
        'email': input_data.get('invitee_email'),
        'name': input_data.get('invitee_name')
    }
    
    service_address = input_data.get('service_address', '')
    address_parts = service_address.split(',')
    street = address_parts[0].strip() if address_parts else ''
    
    if not street:
        return {'success': False, 'message': 'No service address provided'}
    
    contact = search_contact_by_address(street)
    
    if not contact:
        return {'success': False, 'failed_at': 'Phase 3A', 'message': f'Contact not found for address: {street}'}
    
    opportunity_result = find_opportunity_with_workiz_uuid(contact['id'])
    
    if not opportunity_result['success']:
        return {'success': False, 'failed_at': 'Phase 3B', 'message': opportunity_result['message']}
    
    opportunity = opportunity_result['opportunity']
    
    workiz_result = update_workiz_job(
        opportunity['x_workiz_graveyard_uuid'],
        booking_info['booking_time'],
        booking_info['service_type'],
        booking_info['additional_notes']
    )
    
    if not workiz_result['success']:
        return {'success': False, 'failed_at': 'Phase 3C', 'message': workiz_result['message']}
    
    won_result = mark_opportunity_won(opportunity['id'])
    
    if not won_result['success']:
        return {'success': False, 'failed_at': 'Phase 3D', 'message': won_result['message']}
    
    so_result = process_phase3e(contact, opportunity, booking_info, won_result)
    
    if not so_result['success']:
        return {'success': False, 'failed_at': 'Phase 3E', 'message': so_result['message']}
    
    sales_order_id = so_result['sales_order_id']
    
    email_result = process_phase3f(contact, booking_info)
    
    if not email_result['success']:
        return {'success': False, 'failed_at': 'Phase 3F', 'message': email_result['message']}
    
    return {
        'success': True,
        'contact_id': contact['id'],
        'opportunity_id': opportunity['id'],
        'sales_order_id': sales_order_id,
        'message': 'Integration completed successfully'
    }


# Output for Zapier
output = main(input_data)
