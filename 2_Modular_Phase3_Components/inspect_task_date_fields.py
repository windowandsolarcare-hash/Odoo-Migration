"""
One-time script: Inspect project.task date/datetime fields by fetching a task you filled in
(e.g. "Royal Palm Desert" with Feb 20 2:00 AM - 3:00 AM). Prints field names and values so we
can set ODOO_TASK_START_DATETIME_FIELD and ODOO_TASK_END_DATETIME_FIELD correctly in Phase 4.

Run from 2_Modular_Phase3_Components:
  python inspect_task_date_fields.py
  python inspect_task_date_fields.py "Royal"   # search name containing "Royal"
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import requests

try:
    from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY
except ImportError:
    ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
    ODOO_DB = "window-solar-care"
    ODOO_USER_ID = 2
    ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

SEARCH_NAME = (sys.argv[1] if len(sys.argv) > 1 else "Palm Desert").strip()


def odoo_call(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0", "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params},
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    # 1) Get all fields on project.task; keep date and datetime
    print(f"Fetching project.task field list (date/datetime only)...")
    fields_get = odoo_call("project.task", "fields_get", [], {"attributes": ["type", "string"]})
    date_fields = [f for f, attrs in fields_get.items() if attrs.get("type") in ("date", "datetime")]
    print(f"Found {len(date_fields)} date/datetime fields: {date_fields}\n")

    # 2) Search for a task whose name contains SEARCH_NAME
    domain = [["name", "ilike", SEARCH_NAME]]
    tasks = odoo_call("project.task", "search_read", [domain], {"fields": ["id", "name"] + date_fields, "limit": 5})
    if not tasks:
        print(f"No task found with name containing '{SEARCH_NAME}'. Try: python inspect_task_date_fields.py 'Royal'")
        return
    print(f"Found {len(tasks)} task(s) with name containing '{SEARCH_NAME}':\n")
    for t in tasks:
        print(f"  ID {t.get('id')}: {t.get('name', '')[:60]}")
    task = tasks[0]
    task_id = task["id"]
    print(f"\nUsing first task ID {task_id} for field inspection.\n")

    # 3) Print each date/datetime field and its value
    print("Date/Datetime field names and values (use these in Phase 4 config):")
    print("-" * 60)
    for f in sorted(date_fields):
        val = task.get(f)
        if val is not None and val is not False:
            print(f"  {f}: {val}")
        else:
            print(f"  {f}: (empty)")
    print("-" * 60)
    print("\nUse the field name(s) above as start/end in Phase 4 config.")


if __name__ == "__main__":
    main()
