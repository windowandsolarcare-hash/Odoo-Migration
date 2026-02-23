"""Get allowed values for an Odoo Selection field (for validation before create/update)."""

import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY


def get_selection_values(model, field_name):
    """
    Return list of allowed values for a Selection field on an Odoo model.
    Uses fields_get(); selection is a list of (value, label) tuples.

    Returns:
        list: Allowed values (strings), or [] on error / if not a selection field.
    """
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
                model,
                "fields_get",
                [],
                {"allfields": [field_name]}
            ]
        }
    }
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        if result.get("error"):
            return []
        fields = result.get("result", {})
        meta = fields.get(field_name, {})
        sel = meta.get("selection")
        if sel and isinstance(sel, list):
            return [pair[0] for pair in sel if isinstance(pair, (list, tuple)) and len(pair) >= 1]
        return []
    except Exception:
        return []
