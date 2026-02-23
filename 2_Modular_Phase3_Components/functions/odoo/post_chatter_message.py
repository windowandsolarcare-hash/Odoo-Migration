"""
Post a message to Sales Order chatter
"""
import sys
sys.path.append('../..')
import requests
from config import *


def post_chatter_message(so_id, message):
    """
    Post a message to the Sales Order chatter/activity log.
    
    Args:
        so_id (int): Sales Order ID
        message (str): Message to post (plain text with \n for newlines)
        
    Returns:
        bool: True if successful
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
                "sale.order",
                "message_post",
                [so_id],
                {
                    "body": message  # Send plain text - Odoo will format it
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    # message_post returns the message ID if successful
    return "result" in result


if __name__ == "__main__":
    # Test - post to a test SO
    test_so_id = 15777
    test_message = "Test message from Python script"
    success = post_chatter_message(test_so_id, test_message)
    print(f"Chatter post {'successful' if success else 'failed'}")
