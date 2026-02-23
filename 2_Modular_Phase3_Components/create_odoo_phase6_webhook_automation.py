"""
Try to create the Odoo automation "Send Webhook when invoice paid" via API.
If your Odoo version/plan allows it, this will create the rule. If not, follow
Phase 6 Handoff/Odoo_Send_Webhook_When_Invoice_Paid.md and set it up in the UI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/9761276/uegifni/"


def odoo_call(model, method, args, kwargs=None):
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
        raise RuntimeError(data["error"])
    return data.get("result")


def main():
    print("Creating Phase 6 automation (Send Webhook when invoice paid)...")
    # Resolve account.move model id
    model_ids = odoo_call("ir.model", "search", [[["model", "=", "account.move"]]])
    if not model_ids:
        print("ERROR: Model account.move not found.")
        sys.exit(1)
    model_id = model_ids[0]

    # Check what action types exist on ir.actions.server
    fields_result = odoo_call("ir.actions.server", "fields_get", [], {"attributes": ["string", "type"]})
    state_ok = "state" in fields_result
    # Common possibilities for "send webhook" in Studio: state might be 'object_write' with webhook_url, or a custom state
    webhook_url_ok = "webhook_url" in fields_result or "webhook_request_url" in fields_result or "url" in fields_result

    if not state_ok:
        print("ERROR: Cannot determine server action structure.")
        print("Set up the automation manually. See: Phase 6 Handoff/Odoo_Send_Webhook_When_Invoice_Paid.md")
        sys.exit(1)

    # Try to create a server action that does HTTP POST (state 'code' with urllib - may be blocked on Odoo Online)
    # Alternatively some Odoo have state 'object_write' + webhook_request_url
    action_vals = {
        "name": "Phase 6: POST invoice id to Zapier",
        "model_id": model_id,
        "state": "code",
        "code": f"""
import json
import urllib.request
url = "{ZAPIER_WEBHOOK_URL}"
data = json.dumps({{"id": record.id}}).encode("utf-8")
req = urllib.request.Request(url, data=data, method="POST", headers={{"Content-Type": "application/json"}})
urllib.request.urlopen(req, timeout=10)
""",
    }
    try:
        action_id = odoo_call("ir.actions.server", "create", [action_vals])
        print(f"  Created server action id={action_id}")
    except Exception as e:
        print(f"  Server action create failed: {e}")
        print("  (Odoo Online often blocks Execute Code / outbound HTTP.)")
        print("Set up the automation manually using Send Webhook Notification in the UI.")
        print("See: Phase 6 Handoff/Odoo_Send_Webhook_When_Invoice_Paid.md")
        sys.exit(1)

    # Create base.automation: trigger on save when invoice is paid
    filter_domain = "[('move_type','=','out_invoice'),('payment_state','=','paid')]"
    automation_vals = {
        "name": "Phase 6: Notify Zapier when invoice paid",
        "model_id": model_id,
        "trigger": "on_create_or_write",
        "filter_domain": filter_domain,
        "action_server_ids": [(6, 0, [action_id])],
        "active": True,
    }
    try:
        auto_id = odoo_call("base.automation", "create", [automation_vals])
        print(f"  Created base.automation id={auto_id}")
        print("Done. When a customer invoice is marked Paid, Odoo will POST its id to your Zapier webhook.")
    except Exception as e:
        print(f"  base.automation create failed: {e}")
        # Clean up the server action we created
        try:
            odoo_call("ir.actions.server", "unlink", [[action_id]])
        except Exception:
            pass
        print("Set up the automation manually. See: Phase 6 Handoff/Odoo_Send_Webhook_When_Invoice_Paid.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
