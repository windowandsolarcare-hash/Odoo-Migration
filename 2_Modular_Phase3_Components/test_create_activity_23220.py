"""
One-off test: create a mail.activity on contact 23220 (Barbara Rago) in your Odoo.
Uses same credentials as Phase 5. Run from this folder: python test_create_activity_23220.py
"""
import requests
from datetime import datetime, timedelta

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

CONTACT_ID = 23220  # Barbara Rago

def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")

def main():
    print("Test: create mail.activity on contact", CONTACT_ID, "(Barbara Rago)")
    print()

    # 1) Verify partner exists
    print("1. Reading res.partner", CONTACT_ID, "...")
    partners = odoo_rpc("res.partner", "read", [[CONTACT_ID]], {"fields": ["id", "name"]})
    if not partners:
        print("   FAIL: Contact not found.")
        return
    print("   OK:", partners[0].get("name"), "id=", partners[0].get("id"))

    # 2) Get ir.model id for res.partner
    print("2. Getting ir.model id for res.partner ...")
    models = odoo_rpc("ir.model", "search_read", [[["model", "=", "res.partner"]]], {"fields": ["id"], "limit": 1})
    if not models:
        print("   FAIL: ir.model for res.partner not found.")
        return
    res_model_id = models[0]["id"]
    print("   OK: res_model_id =", res_model_id)

    # 3) Create activity (due in 7 days for easy spotting)
    followup_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    activity_vals = {
        "res_model_id": res_model_id,
        "res_id": CONTACT_ID,
        "activity_type_id": 2,
        "summary": "Test activity from script (can delete)",
        "note": "Created by test_create_activity_23220.py to verify activity creation works.",
        "date_deadline": followup_date,
        "user_id": ODOO_USER_ID,
    }
    print("3. Creating mail.activity ...")
    print("   vals:", activity_vals)
    try:
        activity_id = odoo_rpc("mail.activity", "create", [activity_vals])
        print()
        print("SUCCESS: Activity created. activity_id =", activity_id)
        print("Check contact", CONTACT_ID, "in Odoo (Barbara Rago) - you should see this activity. You can delete it after.")
    except Exception as e:
        print()
        print("FAIL:", e)

if __name__ == "__main__":
    main()
