"""Convert Pacific time string to UTC (America/Los_Angeles, DST-aware)."""

from datetime import datetime, timedelta


def convert_pacific_to_utc(pacific_datetime_str):
    """
    Convert Pacific time (America/Los_Angeles) to UTC.
    Uses zoneinfo so daylight saving time (PST vs PDT) is correct for any date:
    - Winter (PST): UTC-8
    - Summer (PDT): UTC-7

    Args:
        pacific_datetime_str (str): Pacific time (e.g., "2026-07-15 09:30:00" or "2025-12-09 09:30:00")

    Returns:
        str: UTC time formatted as "YYYY-MM-DD HH:MM:SS"
    """
    dt_naive = datetime.strptime(pacific_datetime_str, '%Y-%m-%d %H:%M:%S')
    try:
        from zoneinfo import ZoneInfo
        pacific = ZoneInfo('America/Los_Angeles')
        dt_pacific = dt_naive.replace(tzinfo=pacific)
        dt_utc = dt_pacific.astimezone(ZoneInfo('UTC'))
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # Fallback if zoneinfo missing (e.g. Python < 3.9): rough PST/PDT by month
        # PST ~ Nov–early Mar; PDT ~ mid-Mar–Oct. Boundary is approximate.
        is_pst = dt_naive.month in (11, 12, 1, 2) or (dt_naive.month == 3 and dt_naive.day < 10)
        offset_hours = 8 if is_pst else 7
        dt_utc = dt_naive + timedelta(hours=offset_hours)
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
