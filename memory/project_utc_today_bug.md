---
name: project_utc_today_bug
description: "Client-side 'today' computed via new Date().toISOString().slice(0,10) is UTC — after ~5pm Pacific it reads as TOMORROW. Use a Pacific-anchored date instead."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Bug class (found 2026-06-24 via Command Center showing Thu Jun 25 at 11pm Wed Jun 24).** `new Date().toISOString().slice(0,10)` returns the **UTC** date. PDT is UTC−7 / PST UTC−8, so any time after ~5pm Pacific, UTC has already rolled to the next day → "today" is computed as TOMORROW. Breaks the today label, today/overdue badge classification, default date pickers, date-range queries.

**Why:** the business is Pacific-time; the backend uses `today_pt()` correctly, but client JS used UTC.

**Fix (Pacific-anchored, tz-independent):**
```js
function isoPlus(days){
  var pt=new Date().toLocaleDateString('en-CA',{timeZone:'America/Los_Angeles'}).split('-'); // YYYY-MM-DD in PT
  var d=new Date(Date.UTC(+pt[0], +pt[1]-1, +pt[2]));
  d.setUTCDate(d.getUTCDate()+days);
  return d.toISOString().slice(0,10);
}
```
For a one-off "today": `new Date().toLocaleDateString('en-CA',{timeZone:'America/Los_Angeles'})`.
NOTE: `toLocaleDateString('en-US',{timeZone:'America/Los_Angeles'})` (used for the *label* in field.html renderSchedule) is already PT-correct — only the `toISOString().slice(0,10)` pattern is wrong.

**Fixed:** schedule_hub.html (Command Center) `isoPlus` + openAddBlock default date — commit e7f71e7.

**FIXED 2026-06-24** (replaced `new Date().toISOString().slice(0,10)` → `new Date().toLocaleDateString('en-CA',{timeZone:'America/Los_Angeles'})`):
- activities.html (3, commit c9a8059), calendar.html (1, 48487ee), stale_sos.html (1, 688c311), hr.html (2, 1cf1cfb), field.html (7, 1ddf084 — fetched live, stayed 5866 lines).
Pattern eliminated from all known owner pages. If it reappears, same fix.
