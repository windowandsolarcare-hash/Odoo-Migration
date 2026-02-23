"""
One-off: Find the "Follow-up: Joan Greene" calendar event and set its description
to the clickable link format so you can see it without re-running the full test.

Run from this folder: python fix_joan_greene_calendar_description.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

ODOO_BASE = ODOO_URL.replace("/jsonrpc", "")


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs is not None:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": params}}, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    # Find calendar events with "Joan Greene" in the name
    events = odoo_rpc(
        "calendar.event",
        "search_read",
        [[["name", "ilike", "Joan Greene"]]],
        {"fields": ["id", "name", "partner_ids", "description"], "limit": 5},
    )
    if not events:
        print("No calendar event found with 'Joan Greene' in the name.")
        return
    event = events[0]
    event_id = event["id"]
    partner_ids = event.get("partner_ids") or []
    # Prefer Joan Greene's contact id (customer) for the link
    joan = odoo_rpc("res.partner", "search_read", [[["name", "ilike", "Joan Greene"]]], {"fields": ["id", "name"], "limit": 1})
    contact_id = joan[0]["id"] if joan else (partner_ids[0] if partner_ids else 23408)
    contact_link = f"{ODOO_BASE}/web#id={contact_id}&model=res.partner&view_type=form"
    new_description = (
        'Call/text customer about next service.<br/><br/>'
        f'<a href="{contact_link}" target="_blank">View activity on contact</a>'
    )
    odoo_rpc("calendar.event", "write", [[event_id], {"description": new_description}])
    print(f"Updated calendar event ID {event_id} ({event.get('name')}).")
    print(f"Description now has clickable link to contact {contact_id}. Open the event in Odoo to see it.")


if __name__ == "__main__":
    main()
