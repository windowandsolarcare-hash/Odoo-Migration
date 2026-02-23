"""Remove newlines from notes text for Odoo snapshot field"""


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
