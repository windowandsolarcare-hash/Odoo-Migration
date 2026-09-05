---
name: project_gcal_event_deeplink
description: "The calendar 'Open in GCal' deep-link: Google's iCal export leaves the URL property EMPTY for normal events, so build the event link yourself as calendar.google.com/calendar/event?eid=base64url('<eventId> <calendarId>'), eventId = iCal UID minus '@google.com', calendarId from the feed URL's /ical/<id>/ path. Also unescape iCal text (\\, \\; \\n) before display. Lives in dashboard.py /api/gcal_events."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T18:44:34.866Z
---

**Fixed 2026-09-05 (commit d8df08f), `dashboard.py` `/api/gcal_events`** (the endpoint is in dashboard.py ~L12400, NOT calendar.py — that file exists but doesn't serve this route). Two bugs on the calendar screen (v2_calendar.html), both **server-side** (the frontend just renders `e.link` with a day-view fallback and `esc(e.location)`):

1. **"Open in GCal" never landed on the event.** The endpoint set `link = ev.get('URL','')`, but Google's iCal export only fills the `URL` property if the event body has a user-added URL — for normal events it's EMPTY, so the frontend fell back to a day-view link. **Fix:** build the real deep-link yourself: `https://calendar.google.com/calendar/event?eid=<eid>` where `eid = base64.urlsafe_b64encode(f"{eventId} {calendarId}").rstrip('=')`. `eventId` = the iCal `UID` with `@google.com` stripped (`uid.split('@')[0]`); `calendarId` = url-unquoted from the feed URL's `/ical/<calendarId>/` path segment. **The iCal parser only captured SUMMARY/DTSTART/DTEND/LOCATION/DESCRIPTION/RRULE/URL — had to ADD 'UID' to the captured keys.** Verified live: 86/86 events now emit `event?eid=` links; sample decodes to `<eventId> windowandsolarcare@gmail.com`. (Works for normal single events; recurring INSTANCES may land on the series since the iCal UID is the master's — acceptable, still better than day-view. Final proof is a real click.)

2. **Addresses showed stray backslashes** ("LabCorp\, 41865 Boardwalk\, Ste 108"). iCal escapes `,`→`\,`, `;`→`\;`, newline→`\n`. **Fix:** `_ical_unescape()` (`\\N`/`\\n`→newline, `\\,`→`,`, `\\;`→`;`, `\\\\`→`\`) applied to `location` + `summary` before returning.

**Local gotcha hit while testing:** a stray `C:\Users\dj\calendar.py` (leftover fetched app file) SHADOWS stdlib `calendar` when a script runs from `C:\Users\dj\` (Python puts the script dir on sys.path first) → `http.cookiejar` fails importing `timegm`. Run probe scripts from the scratchpad dir, not `C:\Users\dj\`.
