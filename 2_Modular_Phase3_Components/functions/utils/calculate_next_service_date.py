"""
Calculate next service date with city-aware scheduling
"""
from datetime import datetime, timedelta
import re


def calculate_next_service_date(frequency_str, customer_city):
    """
    Calculate next service date based on frequency and city routing.
    
    Args:
        frequency_str (str): Frequency like "3 Months", "4 Months", "6 Months"
        customer_city (str): Customer's city for route-based scheduling
        
    Returns:
        str: Next service date in "YYYY-MM-DD HH:MM:SS" format (Pacific time)
    """
    # Parse frequency (e.g., "3 Months", "4 months", "6 Months")
    match = re.search(r'(\d+)\s*(month|week)', frequency_str, re.IGNORECASE)
    
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit == 'month':
            target_date = datetime.now() + timedelta(days=value * 30)
        elif unit == 'week':
            target_date = datetime.now() + timedelta(weeks=value)
    else:
        # Default: 3 months if can't parse
        print(f"[!] Could not parse frequency '{frequency_str}', defaulting to 3 months")
        target_date = datetime.now() + timedelta(days=90)
    
    # Apply city-aware scheduling
    scheduled_date = apply_city_schedule(target_date, customer_city)
    
    # Format as Workiz expects (Pacific time, no timezone indicator)
    return scheduled_date.strftime('%Y-%m-%d 10:00:00')


def apply_city_schedule(target_date, city):
    """
    Find best service day based on city routing (matching Calendly).
    
    City-to-Day Mapping (from actual Calendly setup):
    - Palm Springs → Friday (4)
    - Rancho Mirage → Thursday (3) (also Friday)
    - Palm Desert → Thursday (3)
    - Indian Wells → Wednesday (2) (also Thursday)
    - Indio/La Quinta → Wednesday (2)
    - Hemet → Tuesday (1)
    """
    city_schedule = {
        'palm springs': 4,      # Friday
        'rancho mirage': 3,     # Thursday (primary, also Fri available)
        'palm desert': 3,       # Thursday
        'indian wells': 2,      # Wednesday (primary, also Thu available)
        'indio': 2,             # Wednesday
        'la quinta': 2,         # Wednesday
        'hemet': 1              # Tuesday
    }
    
    city_lower = city.lower() if city else ''
    preferred_weekday = None
    
    # Find matching city
    for city_name, weekday in city_schedule.items():
        if city_name in city_lower:
            preferred_weekday = weekday
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][weekday]
            print(f"[*] City '{city}' -> {day_name}")
            break
    
    if preferred_weekday is None:
        # No city match - use target date as-is
        print(f"[*] City '{city}' not in routing map - using target date as-is")
        return target_date
    
    # Find nearest preferred day (within ±7 days)
    target_weekday = target_date.weekday()
    days_diff = preferred_weekday - target_weekday
    
    # Adjust within ±7 days (prefer forward if exactly between)
    if days_diff < -3:
        days_diff += 7
    elif days_diff > 3:
        days_diff -= 7
    
    scheduled_date = target_date + timedelta(days=days_diff)
    
    print(f"[*] Target date: {target_date.strftime('%Y-%m-%d (%A)')}")
    print(f"[*] Adjusted to: {scheduled_date.strftime('%Y-%m-%d (%A)')}")
    
    return scheduled_date


if __name__ == "__main__":
    # Test
    print("Testing date calculation:")
    print("="*60)
    
    # Test 1: 4 months, Palm Springs
    result1 = calculate_next_service_date("4 Months", "Palm Springs")
    print(f"\n4 Months from now, Palm Springs: {result1}")
    
    # Test 2: 3 months, Rancho Mirage
    result2 = calculate_next_service_date("3 Months", "Rancho Mirage")
    print(f"\n3 Months from now, Rancho Mirage: {result2}")
    
    # Test 3: 6 months, unknown city
    result3 = calculate_next_service_date("6 Months", "Desert Hot Springs")
    print(f"\n6 Months from now, Desert Hot Springs: {result3}")
