---
name: gcal-integration
description: "Google Calendar overlay on schedule calendar — iCal feed parsing, RRULE support, toggle UI"
metadata: 
  node_type: memory
  type: project
  originSessionId: bcd62e72-19be-4a09-af3f-a38378b2ba9e
---

## What was built (2026-05-14/15)
Google Calendar events overlaid on `calendar.html` scheduling app as a toggleable layer — like Google Calendar's sidebar checkboxes.

## Architecture
- **Backend:** `GET /owner/api/gcal_events?start=YYYY-MM-DD&end=YYYY-MM-DD` in dashboard.py
- **Config:** Up to 3 calendars via Render env vars: `GCAL_1_NAME`, `GCAL_1_URL`, `GCAL_2_NAME`, `GCAL_2_URL`, `GCAL_3_NAME`, `GCAL_3_URL`
- **Colors:** Cal 1 = `#fbbf24` (gold), Cal 2 = `#f472b6` (pink), Cal 3 = `#34d399` (green)
- **Frontend:** Toggle checkboxes below the legend; dots on month view; chips on week view; cards in bottom sheet

## iCal URL format
Must use **private/secret** iCal URL from Google Calendar settings (Settings → calendar name → "Secret address in iCal format"). Public URLs often 404. Format: `.../private-XXXXXXXX/basic.ics`

## Connected calendars
- GCAL_1: WSC Calendar (`windowandsolarcare@gmail.com` primary)
  - URL: `https://calendar.google.com/calendar/ical/windowandsolarcare%40gmail.com/private-2ca17ff035e008c71d6fe4d556f44ae8/basic.ics`

## RRULE recurring events — critical
Our custom iCal parser originally only read the base DTSTART date and missed all future occurrences of recurring events. Fixed 2026-05-15 to expand RRULE into individual dates within the search range.

Supported: FREQ=DAILY/WEEKLY/MONTHLY/YEARLY, INTERVAL, UNTIL, COUNT, BYMONTHDAY.

**Example that exposed the bug:** "Give Dad Financial Report" — RRULE:FREQ=MONTHLY;BYMONTHDAY=16 — appeared in Google Calendar on May 16 but not in our app until RRULE expansion was added.

**Why:** Google Calendar app natively expands recurring events; raw iCal only stores the rule + base date.
**How to apply:** Any event missing from the calendar that exists in Google Calendar — check if it's recurring. Our parser now handles it.

## Response format
```json
{"ok": true, "calendars": [{"name": "WSC Calendar", "color": "#fbbf24", "events": {"2026-05-16": [{"summary": "...", "time": "12:00 PM", "all_day": false, "location": ""}]}}]}
```
