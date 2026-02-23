"""
One-off: Update ALL products in Odoo:
  1. Create on Order (selection) -> Task
  2. Category (many2one) -> Service
  3. Project (many2one) -> Field Service (project id 2) so tasks created from these products go to Field Service by default.

Run from this folder: python update_all_products_task_and_service.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, DEFAULT_PROJECT_ID


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(
        ODOO_URL,
        json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    # 1) Find category "Service"
    cats = odoo_rpc(
        "product.category",
        "search_read",
        [[["name", "ilike", "Service"]]],
        {"fields": ["id", "name"], "limit": 10},
    )
    service_categ_id = None
    for c in cats:
        if c.get("name") and c["name"].strip().lower() == "service":
            service_categ_id = c["id"]
            break
    if not service_categ_id and cats:
        service_categ_id = cats[0]["id"]
        print(f"[*] Using category: {cats[0].get('name')} (id {service_categ_id})")
    if not service_categ_id:
        print("[!] No 'Service' category found. Create it in Odoo or adjust the name.")
        return
    print(f"[OK] Category 'Service' id = {service_categ_id}")

    # 2) Get all product templates
    product_templates = odoo_rpc(
        "product.template",
        "search_read",
        [[]],
        {"fields": ["id", "name", "categ_id", "service_tracking"]},
    )
    if not product_templates:
        print("[!] No products found.")
        return
    print(f"[*] Found {len(product_templates)} product(s).")

    # 3) Get allowed value for "Task" from service_tracking selection
    fields_info = odoo_rpc("product.template", "fields_get", [], {"attributes": ["selection"]})
    selection = (fields_info.get("service_tracking") or {}).get("selection") or []
    task_value = None
    for sel in selection:
        if isinstance(sel, (list, tuple)) and len(sel) >= 2:
            if "task" in str(sel[1]).lower() or (sel[0] and "task" in str(sel[0]).lower()):
                task_value = sel[0]
                break
    if not task_value and selection:
        task_value = selection[0][0] if isinstance(selection[0], (list, tuple)) else selection[0]
    if not task_value:
        print("[!] Could not determine service_tracking value for Task. Selection: %s" % selection)
        return
    print(f"[*] Using service_tracking = {task_value!r}")

    # 4) Build updates: Create on Order = Task, Category = Service, Project = Field Service (2)
    updates = {
        "categ_id": service_categ_id,
        "service_tracking": task_value,
    }
    if DEFAULT_PROJECT_ID:
        updates["project_id"] = DEFAULT_PROJECT_ID
        print(f"[*] Setting default project = Field Service (id {DEFAULT_PROJECT_ID}) on all products.")

    # 5) Write in batches (Odoo accepts list of ids)
    ids = [p["id"] for p in product_templates]
    try:
        odoo_rpc("product.template", "write", [ids, updates])
    except Exception as e:
        if "project_id" in str(e) or "Invalid" in str(e):
            print(f"[!] Write failed (maybe product.template has no 'project_id' field in your app): {e}")
            print("    Removing project_id from update and retrying...")
            updates.pop("project_id", None)
            odoo_rpc("product.template", "write", [ids, updates])
        else:
            raise
    print(f"[OK] Updated {len(ids)} product(s): Create on Order = Task, Category = Service" + (", Project = Field Service." if updates.get("project_id") else "."))
    for p in product_templates[:5]:
        print(f"    - {p.get('name')} (id {p['id']})")
    if len(product_templates) > 5:
        print(f"    ... and {len(product_templates) - 5} more.")


if __name__ == "__main__":
    main()
