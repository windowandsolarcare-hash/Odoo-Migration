# ==============================================================================
# ONE WORLD MIGRATION ENGINE
# Gold Master Version: v3.7 (Final Production - Correct MM/DD/YYYY)
# ==============================================================================
import csv
import json
import os
import sys
from datetime import datetime
import traceback

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
INPUT_FILE = 'Workiz_Export_Raw.csv'
OUTPUT_CUSTOMERS = 'Final_Import_Customers.csv'
OUTPUT_PROPERTIES = 'Final_Import_Properties.csv'
OUTPUT_ORDERS = 'Final_Import_SalesOrders.csv'

# --- PRODUCTION MODE ---
# This is the key change: Set to False to process the entire input file.
PILOT_MODE = False 
PILOT_IDS = [] # This list is ignored when PILOT_MODE is False.

# --- ODOO TECHNICAL NAMES (FINAL) ---
FIELD_LAST_SERVICE_DATE = 'x_studio_last_service_date'
FIELD_RECORD_CATEGORY = 'x_studio_record_category'
FIELD_JOB_TYPE = 'x_studio_x_studio_job_type'
FIELD_LEAD_SOURCE = 'x_studio_lead_source'
FIELD_TECH_TEAM = 'x_studio_workiz_tech'
FIELD_WORKIZ_UUID = 'x_studio_workiz_uuid'
FIELD_WORKIZ_LINK = 'x_studio_workiz_link'
FIELD_GATE_SNAPSHOT = 'x_studio_x_gate_snapshot'
FIELD_PRICING_SNAPSHOT = 'x_studio_pricing_snapshot'
FIELD_NOTES_SNAPSHOT = 'x_studio_notes_snapshot'
FIELD_GATE_CODE = 'x_studio_x_gate_code'
FIELD_FREQUENCY = 'x_studio_x_frequency'
FIELD_MAINTENANCE_STATUS = 'x_studio_x_type_of_service' 
FIELD_OK_TO_TEXT = 'x_studio_x_ok_to_text'
FIELD_ALTERNATING = 'x_studio_x_alternating'
FIELD_PRICING = 'x_studio_x_pricing'
FIELD_SERVICE_AREA = 'x_studio_service_area'
FIELD_LOCATION_ID = 'x_studio_location_id'

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def fix_date_object(date_str):
    if not date_str: return None
    if date_str.startswith("0025") or date_str.startswith("0024"): date_str = "20" + date_str[2:]
    formats = ['%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None

def format_date_for_csv(dt_obj, include_time=True):
    if not dt_obj: return ""
    if include_time:
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return dt_obj.strftime('%m/%d/%Y')

def clean_tag(tag_str):
    if not tag_str: return ""
    return tag_str.replace('[', '').replace(']', '').replace("'", "").replace('"', "").strip()

def parse_line_items(json_str):
    if not json_str or json_str == '[]': return []
    try: formatted = json_str.replace("'", '"').replace('None', 'null').replace('False', 'false').replace('True', 'true'); return json.loads(formatted)
    except:
        try: import ast; return ast.literal_eval(json_str)
        except: return []

def extract_tech_name(team_json):
    if not team_json: return ""
    try:
        teams = json.loads(team_json.replace("'", '"'))
        if isinstance(teams, list) and teams: return ", ".join([team.get('Name', '') for team in teams])
        return ""
    except: return ""

def sanitize_text(text_str):
    if not text_str: return ""
    return ' '.join(text_str.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ').strip().split())

def to_bool(value):
    if not value: return 'False'
    return 'True' if str(value).lower() in ['yes', 'true', '1', 'on'] else 'False'

def to_yes_no(value):
    if not value: return 'No'
    return 'Yes' if str(value).lower() in ['yes', 'true', '1', 'on'] else 'No'

# ==============================================================================
# 3. MIGRATION ENGINE
# ==============================================================================

def process_migration():
    print(f"[ENGINE START] Pre-calculating Last Service Dates...")
    if not os.path.exists(INPUT_FILE): print(f"[ERROR] FATAL: {INPUT_FILE} not found."); return
    
    last_service_dates = {}
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                loc_id = row.get('LocationId', '').strip()
                job_date_obj = fix_date_object(row.get('JobDateTime'))
                if loc_id and job_date_obj:
                    if loc_id not in last_service_dates or job_date_obj > last_service_dates[loc_id]:
                        last_service_dates[loc_id] = job_date_obj
    except Exception as e: print(f"[ERROR] Could not pre-calculate dates: {e}"); return
    print(f"[INFO] Found last service dates for {len(last_service_dates)} unique properties.")
    
    clients, properties, orders = {}, {}, []
    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                client_id = row.get('ClientId', '').strip()
                if not client_id: continue
                
                # This check is now effectively disabled by PILOT_MODE = False
                if PILOT_MODE and client_id not in PILOT_IDS: continue

                loc_id = row.get('LocationId', '').strip()
                uuid = row.get('UUID', '').strip()
                ext_client = f"client_{client_id}"
                ext_prop = f"property_{loc_id}" if loc_id else f"property_gen_{client_id}"
                ext_order = f"order_{uuid}"

                first, last = row.get('FirstName', '').strip(), row.get('LastName', '').strip()
                full_name = f"{first} {last}".strip() or row.get('Company', 'Unknown')
                street_address = row.get('Address', f"Property for {full_name}").strip()

                if client_id not in clients:
                    clients[client_id] = { 'id': ext_client, 'name': full_name, 'x_studio_first_name': first, 'x_studio_last_name': last, 'phone': row.get('Phone', ''), 'x_studio_second_phone': row.get('SecondPhone', ''), 'email': row.get('Email', ''), 'type': 'contact', 'is_company': 'False', 'ref': client_id, FIELD_RECORD_CATEGORY: 'Contact' }

                merged_notes = []
                if sanitize_text(row.get('JobNotes', '')): merged_notes.append(f"[Job Note]: {sanitize_text(row.get('JobNotes', ''))}")
                if sanitize_text(row.get('information_to_remember', '')): merged_notes.append(f"[Info]: {sanitize_text(row.get('information_to_remember', ''))}")
                if sanitize_text(row.get('Comments', '')): merged_notes.append(f"[Comment]: {sanitize_text(row.get('Comments', ''))}")
                final_merged_note = "\n\n".join(merged_notes)

                final_last_service_date = last_service_dates.get(loc_id)

                properties[ext_prop] = { 'id': ext_prop, 'parent_id/id': ext_client, 'name': street_address, 'type': 'delivery', FIELD_RECORD_CATEGORY: 'Property', 'street': street_address, 'street2': row.get('Unit', ''), 'city': row.get('City', ''), 'state_id': row.get('State', ''), 'zip': row.get('PostalCode', ''), 'country_id': row.get('Country', 'US'), 'category_id': clean_tag(row.get('Tags', '')), 'comment': final_merged_note, FIELD_LAST_SERVICE_DATE: format_date_for_csv(final_last_service_date, include_time=False), FIELD_GATE_CODE: row.get('gate_code', ''), FIELD_FREQUENCY: row.get('frequency', ''), FIELD_MAINTENANCE_STATUS: row.get('type_of_service', ''), FIELD_OK_TO_TEXT: to_yes_no(row.get('ok_to_text', '')), FIELD_ALTERNATING: to_bool(row.get('alternating', '')), FIELD_PRICING: row.get('pricing', ''), FIELD_SERVICE_AREA: row.get('ServiceArea', ''), FIELD_LOCATION_ID: loc_id }

                items = parse_line_items(row.get('LineItems', '')) or [{'Name': 'Legacy Service', 'Price': row.get('JobTotalPrice', 0), 'Quantity': 1, 'Description': ''}]
                for item in items:
                    orders.append({
                        'id': ext_order, 'name': row.get('SerialId', '').zfill(6), 'partner_id/id': ext_client, 'partner_shipping_id/id': ext_prop, 'date_order': format_date_for_csv(fix_date_object(row.get('JobDateTime'))), 
                        'x_studio_x_studio_job_type': row.get('JobType', ''), 'x_studio_lead_source': row.get('JobSource', ''), 
                        'x_studio_workiz_tech': extract_tech_name(row.get('Team', '')), 'x_studio_workiz_uuid': uuid, 
                        'x_studio_workiz_link': f"https://app.workiz.com/root/job/{uuid}/1", 'x_studio_x_gate_snapshot': row.get('gate_code', ''), 'x_studio_pricing_snapshot': row.get('pricing', ''),
                        'x_studio_notes_snapshot': final_merged_note,
                        'order_line/product_id/name': item.get('Name', 'Service'),
                        'order_line/name': sanitize_text(item.get('Description', '')),
                        'order_line/price_unit': item.get('Price', 0),
                        'order_line/product_uom_qty': item.get('Quantity', 1)
                    })
        
        print("[SUCCESS] Data Generation Complete.")
        if clients:
            with open(OUTPUT_CUSTOMERS, 'w', newline='', encoding='utf-8') as f: writer = csv.DictWriter(f, fieldnames=list(next(iter(clients.values())).keys())); writer.writeheader(); writer.writerows(clients.values()); print(f"  [WRITE] {OUTPUT_CUSTOMERS}: {len(clients)} records")
        if properties:
            with open(OUTPUT_PROPERTIES, 'w', newline='', encoding='utf-8') as f: writer = csv.DictWriter(f, fieldnames=list(next(iter(properties.values())).keys())); writer.writeheader(); writer.writerows(properties.values()); print(f"  [WRITE] {OUTPUT_PROPERTIES}: {len(properties)} records")
        if orders:
            with open(OUTPUT_ORDERS, 'w', newline='', encoding='utf-8') as f: writer = csv.DictWriter(f, fieldnames=orders[0].keys()); writer.writeheader(); writer.writerows(orders); print(f"  [WRITE] {OUTPUT_ORDERS}: {len(orders)} records")
        
    except Exception as e:
        print(f"[ERROR] {e}"); traceback.print_exc()

if __name__ == '__main__':
    process_migration()