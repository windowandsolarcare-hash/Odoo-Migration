"""
Test Odoo instance - for migration and scripts you want to run against test only.
Use this in migrate_so_customer_to_property.py so migration runs on test, not production.

Production remains in config.py (used by Zapier and other scripts).
"""

# TEST Odoo (window-solar-care-test.odoo.com)
ODOO_URL = "https://window-solar-care-test.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care-test"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"
