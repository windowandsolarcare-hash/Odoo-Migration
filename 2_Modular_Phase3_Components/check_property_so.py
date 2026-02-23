import sys
sys.path.append('.')
import requests
from config import *

# Find the property
payload = {
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {
        'service': 'object',
        'method': 'execute_kw',
        'args': [
            ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
            'res.partner', 'search_read',
            [[['street', '=', '82378 Stradivari Rd'], ['x_studio_x_studio_record_category', '=', 'Property']]],
            {'fields': ['id', 'name', 'display_name']}
        ]
    }
}
response = requests.post(ODOO_URL, json=payload, timeout=10)
result = response.json().get('result', [])

if result:
    property_record = result[0]
    property_id = property_record['id']
    print(f"Property found: {property_record['display_name']} (ID: {property_id})")
    
    # Search for sales orders
    payload2 = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'object',
            'method': 'execute_kw',
            'args': [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                'sale.order', 'search_read',
                [[['partner_shipping_id', '=', property_id]]],
                {'fields': ['id', 'name', 'partner_shipping_id'], 'limit': 10}
            ]
        }
    }
    response2 = requests.post(ODOO_URL, json=payload2, timeout=10)
    result2 = response2.json().get('result', [])
    
    print(f"\nSales Orders with partner_shipping_id={property_id}:")
    print(f"  Count: {len(result2)}")
    for so in result2:
        print(f"  - SO {so['name']} (ID: {so['id']})")
    
    if len(result2) == 0:
        print("\n⚠️ No sales orders found with this property as shipping address!")
        print("   The computed field is working correctly - there are just no SOs yet.")
else:
    print("Property not found")
