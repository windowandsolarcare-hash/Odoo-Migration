"""Fetch current JobNotes and prepend new Calendly booking notes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from functions.workiz.get_job_details import get_job_details


def prepend_calendly_notes(job_uuid, new_notes):
    """
    Fetch current JobNotes and prepend new Calendly booking notes.
    
    Args:
        job_uuid (str): Workiz job UUID
        new_notes (str): New notes from Calendly to prepend
    
    Returns:
        str: Combined notes with delimiter, or None if no update needed
    """
    if not new_notes:
        return None
    
    current_job = get_job_details(job_uuid)
    existing_notes = current_job.get('JobNotes', '') if current_job else ''
    
    # Prepend new Calendly notes to existing notes with clear delimiter
    if existing_notes and existing_notes.strip():
        combined_notes = f"[Calendly Booking] {new_notes} |||ORIGINAL_NOTES||| {existing_notes}"
        print(f"[*] Prepending Calendly notes to existing JobNotes")
    else:
        combined_notes = f"[Calendly Booking] {new_notes}"
        print(f"[*] Adding Calendly notes as new JobNotes")
    
    return combined_notes
