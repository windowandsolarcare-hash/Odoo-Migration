# Phase 5: Slot Availability (Future Workaround)

**Status:** Design / discussion — not implemented.

**Problem:** We currently set the new maintenance job time to a **fixed 10:00 AM** on the chosen date. We do not check whether that slot is actually open on the Workiz schedule (no calendar API).

**Proposed workaround (no calendar API):**

1. **Before** committing the job time (or before we call job/create with `JobDateTime`):
   - Call **job/all** (or equivalent) for **that date only** (e.g. `start_date=YYYY-MM-DD`, `records=10`).
   - Assume we never have more than 5 jobs that day; fetch 10 to be safe.

2. **Filter** the results to jobs that are **on that same date** (same service area / team if needed — “that day” for the route).

3. **Use start and end times** of those jobs:
   - Each job has a start time and an end time.
   - Slots are roughly **every 1.5 hours**.
   - Find the **next available opening** after the last job ends (or after a default like 10:00), and set our new job’s `JobDateTime` to that slot.

4. **Configurable parameters** (for later):
   - Slot duration or interval (e.g. 1.5 hours).
   - Earliest start (e.g. 10:00).
   - How to handle “no jobs that day” (default to 10:00).

**Order in Phase 5 would become:**  
Pick date (city routing) → **fetch jobs for that date** → **compute next open slot** → create job with that datetime → assign team → set status.

**Notes:**
- job/all returns jobs; we need to confirm it can be filtered by date (and ideally service area) so we only look at “that day” for the right route.
- We’d need to parse `JobDateTime` (and any end time field, if returned) to build a list of occupied slots and then pick the next free one.

This doc is for future implementation when you’re ready to add slot-aware scheduling.
