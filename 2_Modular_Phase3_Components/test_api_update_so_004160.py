"""
Test API credentials against TEST Odoo: update SO 004160 Frequency SO to "4 Months".
Uses config_test (window-solar-care-test.odoo.com).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from config_test import ODOO_URL, ODOO_DB, ODOO_USER_ID, ODOO_API_KEY

FREQ_FIELD = "x_studio_x_studio_frequency_so"


def odoo_rpc(model, method, args, kwargs=None):
    params = [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args]
    if kwargs:
        params.append(kwargs)
    r = requests.post(ODOO_URL, json={
        "jsonrpc": "2.0", "method": "call",
        "params": {"service": "object", "method": "execute_kw", "args": params},
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data.get("error"))
    return data.get("result")


def main():
    print(f"Using: {ODOO_URL}  DB: {ODOO_DB}")
    sos = odoo_rpc("sale.order", "search_read", [[["name", "=", "004160"]]], {
        "fields": ["id", "name", FREQ_FIELD],
        "limit": 1,
    })
    if not sos:
        print("SO 004160 not found on test instance.")
        return
    so = sos[0]
    so_id = so["id"]
    print(f"Found SO 004160 (id {so_id}). Current {FREQ_FIELD}: {so.get(FREQ_FIELD)}")
    odoo_rpc("sale.order", "write", [[so_id], {FREQ_FIELD: "4 Months"}])
    print("Updated Frequency SO to '4 Months'.")
    # Verify
    check = odoo_rpc("sale.order", "read", [[so_id]], {"fields": [FREQ_FIELD]})
    print(f"Verified: {FREQ_FIELD} = {check[0].get(FREQ_FIELD)}")


if __name__ == "__main__":
    main()
