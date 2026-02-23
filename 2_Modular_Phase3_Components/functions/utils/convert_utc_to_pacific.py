"""Convert UTC datetime string to Pacific time"""

from datetime import datetime, timedelta


def convert_utc_to_pacific(utc_datetime_str):
    """
    Convert UTC datetime string to Pacific time.
    
    Args:
        utc_datetime_str (str): UTC datetime (e.g., "2026-03-12T15:30:00.000000Z")
    
    Returns:
        str: Pacific time formatted as "YYYY-MM-DD HH:MM:SS"
    """
    # Parse UTC datetime
    dt_utc = datetime.fromisoformat(utc_datetime_str.replace('Z', '+00:00'))
    
    # Convert to Pacific (UTC-8 for PST, UTC-7 for PDT)
    # Simplified DST check: PST roughly Nov-March, PDT March-Nov
    pacific_offset = timedelta(hours=-8) if dt_utc.month in [11, 12, 1, 2, 3] and dt_utc.day < 10 else timedelta(hours=-7)
    dt_pacific = dt_utc + pacific_offset
    
    return dt_pacific.strftime('%Y-%m-%d %H:%M:%S')
