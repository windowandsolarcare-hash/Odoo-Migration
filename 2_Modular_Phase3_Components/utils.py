"""
Utility Functions Module - Timezone & Formatting
=================================================
Reusable utility functions for timezone conversion and data formatting.
"""

from datetime import datetime, timedelta


def utc_to_pacific(utc_datetime_str):
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


def pacific_to_utc(pacific_datetime_str):
    """
    Convert Pacific time string to UTC.
    
    Args:
        pacific_datetime_str (str): Pacific time (e.g., "2026-03-12 08:30:00")
    
    Returns:
        str: UTC time formatted as "YYYY-MM-DD HH:MM:SS"
    """
    # Parse Pacific time
    dt_naive = datetime.strptime(pacific_datetime_str, '%Y-%m-%d %H:%M:%S')
    
    # Convert to UTC (add 8 hours for PST or 7 hours for PDT)
    pacific_offset = timedelta(hours=8) if dt_naive.month in [11, 12, 1, 2] or (dt_naive.month == 3 and dt_naive.day < 10) else timedelta(hours=7)
    dt_utc = dt_naive + pacific_offset
    
    return dt_utc.strftime('%Y-%m-%d %H:%M:%S')


def format_serial_id(serial_id):
    """
    Format Workiz SerialId as 6-digit string with leading zeros.
    
    Args:
        serial_id: Workiz job serial ID (e.g., 4111)
    
    Returns:
        str: Formatted ID (e.g., "004111")
    """
    try:
        return str(int(serial_id)).zfill(6)
    except:
        return str(serial_id)


def clean_notes_for_snapshot(notes_text):
    """
    Remove newlines from notes text for Odoo snapshot field.
    
    Args:
        notes_text (str): Raw notes text with possible newlines
    
    Returns:
        str: Cleaned text with newlines replaced by spaces
    """
    if not notes_text:
        return ""
    return ' '.join(notes_text.strip().split())
