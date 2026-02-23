"""
Configuration Module - Credentials and Constants
================================================
Contains all API credentials and configuration constants for the Phase 3 integration.

SECURITY NOTE: In production, consider using environment variables or Zapier's storage secrets.
"""

# ==============================================================================
# ODOO CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

# ==============================================================================
# WORKIZ CREDENTIALS
# ==============================================================================

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# Default Odoo project ID for sales orders with line items that create tasks.
# Set to the project ID (integer). Renaming the project in Odoo does not change its ID.
# Flattened Zapier scripts (Phase 3/4) have their own DEFAULT_PROJECT_ID constant; set it there too when deploying.
DEFAULT_PROJECT_ID = 2
