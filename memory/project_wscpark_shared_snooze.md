---
name: project_wscpark_shared_snooze
description: "WSCPark = ONE shared snooze/remove/STOP/bring-back sheet (static/owner/wsc_park.js) for BOTH the Outreach page and the Customer Brain. Plus Outreach-page name search + restore (un-stop) action."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Why:** DJ's DRY rule — the Customer-Brain snooze (field.html `#snooze-modal`/`doSnooze` → `/api/outreach/defer`, only 3/6mo/season) was DIFFERENT from the Outreach-page sheet (`/api/outreach/park`, 1/3/6mo/Oct/date + Moved/Deceased/Not-interested/STOP). He wants ONE implementation. See [[feedback_reuse_canonical_endpoint]].

**WSCPark (`static/owner/wsc_park.js`, new 2026-07-13, commit 94286bb):** a self-contained shared component like WSCReeng/WSCMiniCal. `WSCPark.open({partner_id, name, stopped?}, {onDone:fn})` injects a bottom-sheet and posts every action to **`/owner/api/outreach/park`**. Options: reason box + snooze (1/3/6mo, 🍁 Until October, pick date) + permanent (Moved/Deceased/Not interested/🛑 STOP). If `stopped:true` it shows instead a single green **↩️ Bring back** (`action:'restore'`) plus a note that the customer must text **START** to Twilio (opt-out is separate). Theme via chained `var(--card,var(--bg-card,#161b22))` fallbacks so it renders on both pages' CSS-var schemes. Base URL = `window.API || '/owner'`.

**Backend (outreach.py, commit 7a8ff75):**
- **`GET /api/outreach/find?q=`** — customer name search for the Outreach page search bar. Word-start match, `company_id in [1,False]`, **includes archived/STOPPED** (`context active_test:False`), skips property/child rows (parent_id set), returns `[{partner_id, name, phone, stopped}]` (stopped = archived OR Do Not Contact).
- **`park` action `'restore'`** — bring back a stopped customer: `active=True`, `x_studio_activelead='Active'`, clear `x_snooze_until`, remove phone from `phone.blacklist`, log ↩️. ⚠ Twilio opt-out is NOT touched — customer must text START.

**Outreach page (outreach.html, commit 48ada75):** added a **🔎 Find any customer by name** search bar at top of `.wrap` (`findCust()` debounced → `/api/outreach/find`, results tap → `openFind(i)` → `WSCPark.open`). Removed the old inline `#park-ov` sheet + `doPark/doParkDate/hidePark`; `openPark(it)` now just calls `WSCPark.open`. STOPPED customers show a red STOPPED chip and open the bring-back action.

**Stage 2 DONE (2026-07-13, commits outreach.py 7991b09 / field.html 97bb78f):** field.html includes `wsc_park.js` and `openSnoozeFromMenu` (the job 3-dot "🔕 Not ready — snooze") now calls `WSCPark.open(...)` → same shared sheet. The old `#snooze-modal`/`doSnooze`/`closeSnoozeModal` (which posted to `/api/outreach/defer`) are left as DEAD code (unreferenced — kept per the no-remove rule, safe to delete later). onDone → `loadField()` reload so the snoozed job drops off. ★ To make park safe in the field context, `/api/outreach/park` **snooze** now writes `x_snooze_until` on the ORIGINAL partner AND its parent (mirrors defer L1371-1378) — the field menu passes the property CHILD but the Command Center overdue filter is parent-preferring, so both must be stamped. park is now a true superset of the defer snooze. See [[project_stop_optout_true_count]], [[project_touch_note_banner_myday]], [[project_snooze_scheduled_sos]].
