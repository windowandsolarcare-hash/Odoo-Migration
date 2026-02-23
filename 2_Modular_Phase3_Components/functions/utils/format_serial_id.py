"""Format Workiz SerialId as 6-digit string with leading zeros"""


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
