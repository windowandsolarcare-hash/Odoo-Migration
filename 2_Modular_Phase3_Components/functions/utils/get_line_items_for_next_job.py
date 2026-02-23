"""
Get line items for next job (handles alternating service logic)
"""
import sys
sys.path.append('../..')
from functions.odoo.search_all_sales_orders_for_property import search_all_sales_orders_for_property
from functions.workiz.get_job_details import get_job_details


def get_line_items_for_next_job(workiz_job, property_id):
    """
    Determine which line items to use for next job.
    
    Logic:
    - If alternating = "Yes"/"1" → Get from 2 jobs back
    - Else → Get from current job
    - Filter out tips, discounts, quotes
    
    Args:
        workiz_job (dict): Current completed job data
        property_id (int): Property ID in Odoo
        
    Returns:
        list: List of line item dicts from source job
    """
    alternating = str(workiz_job.get('alternating', '')).lower()
    
    # Check if alternating service
    is_alternating = alternating in ['yes', '1', 'true']
    
    if is_alternating:
        print("[*] Alternating service detected - need line items from 2 jobs back")
        
        # Get all sales orders for this property
        all_sales_orders = search_all_sales_orders_for_property(property_id)
        
        if len(all_sales_orders) >= 2:
            # [0] = current (just done), [1] = 2 jobs back
            source_so = all_sales_orders[1]
            source_uuid = source_so['x_studio_x_studio_workiz_uuid']
            
            print(f"[*] Using job {source_uuid} (2 jobs back) for line items")
            
            # Get Workiz job details
            source_job = get_job_details(source_uuid)
            if source_job:
                line_items = source_job.get('LineItems', [])
            else:
                print("[!] Could not fetch source job - using current job as fallback")
                line_items = workiz_job.get('LineItems', [])
        else:
            print(f"[!] Not enough job history ({len(all_sales_orders)} jobs) - using current job")
            line_items = workiz_job.get('LineItems', [])
    else:
        # Regular service - use current job
        print("[*] Regular service - using current job line items")
        line_items = workiz_job.get('LineItems', [])
    
    # Filter out non-service items
    filtered_items = []
    for item in line_items:
        item_name = item.get('Name', '').lower()
        # Exclude tips, discounts, quotes, legacy items
        if not any(x in item_name for x in ['tip', 'discount', 'quote', 'legacy']):
            filtered_items.append(item)
    
    print(f"[*] Found {len(filtered_items)} line items for next job")
    return filtered_items


def format_line_items_for_custom_field(line_items):
    """
    Format line items as text for Workiz custom field.
    
    Args:
        line_items (list): Line items from Workiz job
        
    Returns:
        str: Formatted string for custom field
    """
    if not line_items:
        return ""
    
    lines = []
    for item in line_items:
        name = item.get('Name', 'Service')
        price = item.get('Price', 0)
        quantity = item.get('Quantity', 1)
        
        if quantity > 1:
            lines.append(f"{name} (x{quantity}): ${float(price) * float(quantity):.2f}")
        else:
            lines.append(f"{name}: ${float(price):.2f}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test formatting
    test_items = [
        {'Name': 'Windows In & Out - Full Service', 'Price': 85, 'Quantity': 1},
        {'Name': 'Solar Panel Cleaning', 'Price': 45, 'Quantity': 1}
    ]
    
    formatted = format_line_items_for_custom_field(test_items)
    print("Formatted line items for custom field:")
    print(formatted)
