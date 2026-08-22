---
name: project_myday_booking_pin
description: "Online booking requests pin to a highlighted 'New Online Bookings' group at the TOP of My Day + fire a special (persistent, buzzing) push. Built 2026-07-03."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# Online bookings: top of My Day + special notification (2026-07-03)

DJ: "when someone books online I need a special notification and it to appear at the top of my day list." (Bibi Silvas booked → task #1221.)

**Flow:** self-hosted online booking = `routers/booking.py` (public booking page). On submit it creates a `project.task` `name='New booking request - <cust> (<date> <pref>) - review & approve'`, `x_myday_priority=3`, `date_deadline=today`, and pushes a web-push immediately (lazy-imports `myday._broadcast`/`_get_subs`).

**Top of My Day (static/owner/myday.html):** My Day's `/api/myday` sorts by date/time only (no priority), so a booking sank to the bottom of "Today." FIX: `render()` now splits out booking items into a dedicated **"🆕 New Online Bookings"** group rendered FIRST (date-independent, always top), highlighted (`.sec-h.bookings` + `.item.bk` accent). Detection reuses the EXISTING `tkBookingTarget(it)` (title starts with 'New booking request' OR note has a `/owner/booking_requests?focus=` link) via new `isBooking(it)`. No new field/type — title-prefix detection was already there for the Review button. Commit 09290cb.

**Special notification:** booking.py push now `title='🎉 NEW ONLINE BOOKING!'`, louder body, `requireInteraction:True` (stays on screen until acted on), `vibrate:[300,120,300,120,300]`. The service worker (`routers/auth.py` `_SW_JS` push handler) previously ignored those two keys — added passthrough `if(d.requireInteraction) o.requireInteraction=true; if(d.vibrate) o.vibrate=d.vibrate;`. Commits booking 0b119de, auth 1a840d8. ★ SW change needs ONE full app close/reopen to activate (title/body work immediately; persist+buzz after the SW updates). See [[project_push_notification_actions]] [[project_calendly_booking_alert]].
