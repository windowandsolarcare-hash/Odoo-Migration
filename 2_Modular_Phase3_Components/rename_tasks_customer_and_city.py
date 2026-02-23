"""
One-time script: Rename existing project tasks (linked to SO lines) to "Customer Name - City".
Task partner_id is the Property; Contact = Property.parent_id. We set task name = Contact name (or Property name) + " - " + city.

Usage (run from 2_Modular_Phase3_Components):
  python rename_tasks_customer_and_city.py --dry-run    # list changes only
  python rename_tasks_customer_and_city.py              # apply on LIVE (uses config.py credentials)

Uses config.py for Odoo (production). No test config — run --dry-run first to see what would change.
"""
import argparse
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


def odoo_search_read(model, domain, fields, limit=5000):
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "search_read", [domain], {"fields": fields, "limit": limit}]
        }
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result", [])


def odoo_write(model, ids, vals):
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "write", [ids, vals]]
        }
    }
    r = requests.post(ODOO_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    parser = argparse.ArgumentParser(description="Rename tasks to 'Customer Name - City'.")
    parser.add_argument("--dry-run", action="store_true", help="Only list changes; do not write.")
    args = parser.parse_args()
    dry_run = getattr(args, "dry_run", False)

    # Tasks linked to an SO line (created from sales orders)
    tasks = odoo_search_read("project.task", [["sale_line_id", "!=", False]], ["id", "name", "partner_id"])
    if not tasks:
        print("No tasks with sale_line_id found.")
        return

    # Resolve partner_id (can be [id] or id)
    def pid(t):
        p = t.get("partner_id")
        if p is None:
            return None
        return p[0] if isinstance(p, (list, tuple)) else p

    pids = list({pid(t) for t in tasks if pid(t)})
    if not pids:
        print("No partner_id on any task; nothing to rename.")
        return

    # Load all Property (partner) records
    partners = odoo_search_read("res.partner", [["id", "in", pids]], ["id", "name", "parent_id", "city"])
    partner_by_id = {p["id"]: p for p in partners}
    contact_ids = list({(p["parent_id"][0] if isinstance(p.get("parent_id"), (list, tuple)) else p.get("parent_id")) for p in partners if p.get("parent_id")})
    contacts = []
    if contact_ids:
        contacts = odoo_search_read("res.partner", [["id", "in", contact_ids]], ["id", "name"])
    contact_by_id = {c["id"]: c for c in contacts}

    # Build pid -> (customer_name, city)
    def name_and_city(partner_id):
        p = partner_by_id.get(partner_id)
        if not p:
            return (None, None)
        city = (p.get("city") or "").strip()
        parent = p.get("parent_id")
        contact_id = parent[0] if isinstance(parent, (list, tuple)) else parent if parent else None
        customer_name = (p.get("name") or "").strip()
        if contact_id and contact_id in contact_by_id:
            customer_name = (contact_by_id[contact_id].get("name") or customer_name).strip()
        return (customer_name or None, city or None)

    # Compute new name for each task
    updates = []  # (task_id, old_name, new_name)
    for t in tasks:
        tid = t["id"]
        old_name = (t.get("name") or "").strip()
        p = pid(t)
        if not p:
            continue
        customer_name, city = name_and_city(p)
        if not customer_name and not city:
            continue
        new_name = f"{customer_name or ''} - {city or ''}".strip(" - ").strip()
        if not new_name:
            new_name = customer_name or city or old_name
        if new_name != old_name:
            updates.append((tid, old_name, new_name))

    print(f"Tasks with sale_line_id: {len(tasks)}. Would update {len(updates)} task(s).")
    if not updates:
        print("No task names to change.")
        return

    for tid, old_name, new_name in updates[:50]:
        print(f"  ID {tid}: {repr(old_name)[:50]} -> {repr(new_name)[:50]}")
    if len(updates) > 50:
        print(f"  ... and {len(updates) - 50} more.")

    if dry_run:
        print("\n[DRY-RUN] No changes written. Run without --dry-run to apply.")
        return

    # Group by new_name to minimize writes (same name can be written to many tasks)
    from collections import defaultdict
    by_name = defaultdict(list)
    for tid, _old, new_name in updates:
        by_name[new_name].append(tid)
    written = 0
    for new_name, ids in by_name.items():
        odoo_write("project.task", ids, {"name": new_name})
        written += len(ids)
    print(f"\n[OK] Updated {written} task(s).")


if __name__ == "__main__":
    main()
