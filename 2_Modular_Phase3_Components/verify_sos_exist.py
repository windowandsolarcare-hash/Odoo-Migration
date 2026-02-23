import sys
sys.path.append('.')
import requests
from config import *

so_ids = [15804, 15805]

for so_id in so_ids:
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "sale.order",
                "search_read",
                [[["id", "=", so_id]]],
                {
                    "fields": [
                        "name", "partner_id", "partner_shipping_id",
                        "x_studio_x_studio_workiz_uuid",
                        "x_studio_x_studio_workiz_status",
                        "x_studio_is_paid", "x_studio_tip_amount",
                        "state"
                    ]
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result:
        so = result[0]
        print(f"\n[OK] SO #{so['name']} (ID: {so['id']})")
        print(f"   Customer: {so['partner_id'][1] if isinstance(so['partner_id'], list) else so['partner_id']}")
        print(f"   Property: {so['partner_shipping_id'][1] if isinstance(so['partner_shipping_id'], list) else so['partner_shipping_id']}")
        print(f"   Workiz UUID: {so['x_studio_x_studio_workiz_uuid']}")
        print(f"   Status: {so['x_studio_x_studio_workiz_status']}")
        print(f"   Odoo State: {so['state']}")
        print(f"   Is Paid: {so.get('x_studio_is_paid')}")
        print(f"   Tip: ${so.get('x_studio_tip_amount', 0)}")
    else:
        print(f"\n[ERROR] SO {so_id} NOT FOUND")

print("\n" + "="*70)
print("Go to Odoo: Sales → Orders → Search for '003878' or '001069'")
print("="*70)
