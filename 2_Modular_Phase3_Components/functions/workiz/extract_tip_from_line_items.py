"""
Extract tip amount from Workiz LineItems
"""


def extract_tip_from_line_items(line_items):
    """
    Extract tip amount from Workiz job line items.
    
    Args:
        line_items (list): List of line item dictionaries from Workiz
        
    Returns:
        float: Tip amount (0 if no tip found)
    """
    if not line_items or not isinstance(line_items, list):
        return 0.0
    
    for item in line_items:
        item_name = item.get('Name', '').lower()
        if 'tip' in item_name:
            return float(item.get('Price', 0))
    
    return 0.0


if __name__ == "__main__":
    # Test with sample data
    test_items = [
        {'Name': 'Windows Service', 'Price': 85},
        {'Name': 'Tip', 'Price': 15}
    ]
    tip = extract_tip_from_line_items(test_items)
    print(f"Tip found: ${tip}")
