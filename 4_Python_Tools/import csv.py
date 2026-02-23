import csv
import json
import os
import sys
from datetime import datetime

# ==============================================================================
# 1. CONFIGURATION & MAPPING
# ==============================================================================
INPUT_FILE = 'Workiz_Export_Raw.csv'
OUTPUT_CUSTOMERS = 'Import_1_Customers.csv'
OUTPUT_PROPERTIES = 'Import_2_Properties.csv'
OUTPUT_ORDERS = 'Import_3_SalesOrders.csv'

# --- ODOO TECHNICAL NAMES (LOCKED) ---

# PROPERTY FIELDS (The Brain) - Must exist on 'res.partner'
FIELD_GATE_CODE = 'x_studio_x_gate_code'
FIELD_FREQUENCY = 'x_studio_x_frequency'
FIELD_MAINTENANCE_STATUS = 'x_studio_x_type_of_service' # Maps to 'type_of_service'
FIELD_OK_TO_TEXT = 'x_studio_x_ok_to_text'
FIELD_ALTERNATING = 'x_studio_x_alternating'
FIELD_PRICING = 'x_studio_x_pricing'
FIELD_SERVICE_AREA = 'x_studio_service_area'            # Maps to 'ServiceArea'
FIELD_LOCATION_ID = 'x_studio_location_id'

# SALES ORDER FIELDS (The History) - Must exist on 'sale.order'
FIELD_JOB_TYPE = 'x_studio_x_studio_job_type'           # Maps to 'JobType'
FIELD_LEAD_SOURCE = 'x_studio_lead_source'              # Maps to 'JobSource'
FIELD_TECH_TEAM = 'x_studio_workiz_tech'                # Maps to 'Team'
FIELD_WORKIZ_UUID = 'x_studio_workiz_uuid'              # Maps to 'UUID'

# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================

def clean_tag(tag_str):
    """
    Removes brackets/quotes: "['Snow Bird', 'CF']" -> "Snow Bird, CF"
    """
    if not tag_str:
        return ""
    return tag_str.replace('[', '').replace(']', '').replace("'", "").replace('"', "").strip()

def fix_date(date_str):
    """
    Fixes '0025' year bug and handles multiple date formats.
    Returns: YYYY-MM-DD HH:MM:SS
    """
    if not date_str:
        return ""
    
    # Fix the "Time Traveler" Bug (0025 -> 2025)
    if date_str.startswith("0025") or date_str.startswith("0024"):
        date_str = "20" + date_str[2:]
    
    # Try parsing
    formats = ['%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%Y-%m-%d']
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
    return date_str # Return raw if all fail

def parse_line_items(json_str):
    """
    Parses Workiz JSON. Handles 'single quote' Python-style dicts.
    """
    if not json_str or json_str == '[]':
        return []
    try:
        # Simple fix for Python dict string
        formatted = json_str.replace("'", '"').replace('None', 'null').replace('False', 'false').replace('True', 'true')
        return json.loads(formatted)
    except:
        try:
            import ast
            return ast.literal_eval(json_str)
        except:
            return []

def to_bool(value):
    """Maps Yes/No/1/0 to 'True'/'False'"""
    if not value: return 'False'
    return 'True' if str(value).lower() in ['yes', 'true', '1', 'on'] else 'False'

# ==============================================================================
# 3. MIGRATION ENGINE
# ==============================================================================

def process_migration():
    print(f"🚀 ENGINE START: Processing {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ FATAL: {INPUT_FILE} not found in directory.")
        return

    # Storage
    clients = {}      # Key: ClientId
    properties = {}   # Key: LocationId (or composite)
    orders = []       # List of order dictionaries

    try:
        with open(INPUT_FILE, mode='r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # --- 1. IDS ---
                client_id = row.get('ClientId', '').strip()
                loc_id = row.get('LocationId', '').strip()
                uuid = row.get('UUID', '').strip()
                
                if not client_id: continue # Skip orphans

                # Generate External IDs
                ext_client = f"client_{client_id}"
                ext_prop = f"property_{loc_id}" if loc_id else f"property_gen_{client_id}"
                ext_order = f"order_{uuid}"

                # --- 2. CLIENTS (File 1) ---
                if client_id not in clients:
                    first = row.get('FirstName', '').strip()
                    last = row.get('LastName', '').strip()
                    full_name = f"{first} {last}".strip() or row.get('Company', 'Unknown')
                    
                    clients[client_id] = {
                        'id': ext_client,
                        'name': full_name,
                        'x_studio_first_name': first, # Custom split fields
                        'x_studio_last_name': last,
                        'phone': row.get('Phone', ''),      # Primary
                        'mobile': row.get('SecondPhone', ''), # Spouse/Alt
                        'email': row.get('Email', ''),
                        'type': 'contact',
                        'is_company': 'False',
                        'ref': client_id
                    }

                # --- 3. PROPERTIES (File 2) ---
                # Merging Notes
                notes = []
                if row.get('information_to_remember'): notes.append(f"[Info]: {row.get('information_to_remember')}")
                if row.get('JobNotes'): notes.append(f"[Job Note]: {row.get('JobNotes')}")
                
                properties[ext_prop] = {
                    'id': ext_prop,
                    'parent_id/id': ext_client,
                    'type': 'delivery',
                    'street': row.get('Address', ''),
                    'street2': row.get('Unit', ''), # Unit goes here
                    'city': row.get('City', ''),
                    'state_id': row.get('State', ''),
                    'zip': row.get('PostalCode', ''),
                    'country_id': row.get('Country', 'US'),
                    'category_id': clean_tag(row.get('Tags', '')),
                    'comment': "\n".join(notes),
                    
                    # CUSTOM FIELDS
                    FIELD_GATE_CODE: row.get('gate_code', ''),
                    FIELD_FREQUENCY: row.get('frequency', ''),
                    FIELD_MAINTENANCE_STATUS: row.get('type_of_service', ''),
                    FIELD_OK_TO_TEXT: to_bool(row.get('ok_to_text', '')),
                    FIELD_ALTERNATING: row.get('alternating', ''),
                    FIELD_PRICING: row.get('pricing', ''),
                    FIELD_SERVICE_AREA: row.get('ServiceArea', ''),
                    FIELD_LOCATION_ID: loc_id
                }

                # --- 4. SALES ORDERS (File 3) ---
                items = parse_line_items(row.get('LineItems', ''))
                order_date = fix_date(row.get('JobDateTime', ''))
                
                # If no line items, create a dummy one to save the order header
                if not items:
                    items = [{'Name': 'Legacy Service', 'Price': row.get('JobTotalPrice', 0), 'Quantity': 1}]

                for item in items:
                    orders.append({
                        'id': ext_order,
                        'name': row.get('SerialId', ''), # Workiz Job #
                        'partner_id/id': ext_client,
                        'partner_shipping_id/id': ext_prop,
                        'date_order': order_date,
                        'state': 'sale', # Confirmed
                        'amount_total': row.get('JobTotalPrice', ''),
                        'note': row.get('Comments', ''), # Transactional Notes
                        
                        # CUSTOM HEADER FIELDS
                        FIELD_JOB_TYPE: row.get('JobType', ''),
                        FIELD_LEAD_SOURCE: row.get('JobSource', ''),
                        FIELD_TECH_TEAM: row.get('Team', ''),
                        FIELD_WORKIZ_UUID: uuid,
                        
                        # LINE ITEMS
                        'order_line/product_id/name': item.get('Name', 'Service'),
                        'order_line/name': item.get('Description', item.get('Name', '')),
                        'order_line/price_unit': item.get('Price', 0),
                        'order_line/product_uom_qty': item.get('Quantity', 1)
                    })

        # --- WRITE FILES ---
        print(f"✅ Parsing Complete. Writing Files...")

        # File 1
        with open(OUTPUT_CUSTOMERS, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(clients[next(iter(clients))].keys()))
            w.writeheader()
            w.writerows(clients.values())
        
        # File 2
        with open(OUTPUT_PROPERTIES, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(properties[next(iter(properties))].keys()))
            w.writeheader()
            w.writerows(properties.values())

        # File 3
        with open(OUTPUT_ORDERS, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(orders[0].keys()))
            w.writeheader()
            w.writerows(orders)

        print(f"🎉 SUCCESS! Created 3 files:")
        print(f"   1. {OUTPUT_CUSTOMERS} ({len(clients)} records)")
        print(f"   2. {OUTPUT_PROPERTIES} ({len(properties)} records)")
        print(f"   3. {OUTPUT_ORDERS} ({len(orders)} lines)")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    process_migration()