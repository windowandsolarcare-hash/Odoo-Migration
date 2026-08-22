---
name: project_reengagement_autopilot
description: "Re-engagement auto-pilot (approve-first) — daily 8AM scan of due Phase-5 re-engagement To-Dos, pushes DJ, he reviews+sends on /owner/reengage. Reuses the exact followup send. No Twilio."
metadata: 
  node_type: memory
  type: project
  originSessionId: 979da23a-b812-4db3-a7ba-e4e53a145a20
---

**DJ wants automation for the re-engagement activities (2026-06-16). Chose: approve-first.** When a Phase-5B "Re-engagement: <customer>" To-Do (project.task) comes due, instead of DJ digging into Activities to Launch Reactivation, the system surfaces it for a one-tap review+send.

## SHIPPED 2026-06-16 — `routers/owner/reengage.py` + `static/owner/reengage.html`
- **Daily 8 AM scan** (`scan_and_notify`, APScheduler in main.py `_scheduled_reengage` hour=8) → `find_due()`: open project.tasks named "Re-engagement:" with `date_deadline <= today`, whose CONTACT passes `_gates_ok` (not phone_blacklisted/STOP, not activelead='Do Not Contact', has phone, **no** x_studio_next_job_date, past **45-day** followup cooldown `x_studio_last_followup_sent`). Snapshots to param `reengage.due`. **Pushes DJ via My Day web-push infra** (`from .myday import _get_subs, _broadcast`): digest "N reactivations ready" if ≥3, else individual pings. Tap → /owner/reengage.
- **Screen `/owner/reengage`**: `GET /api/reengage/due` returns due items + each one's **built SMS preview** (reuses `POST /api/followup/preview`). Each card = name/last-visit/city/due + **editable** SMS textarea + **Send** / **Skip 1 week**. Plus a recent-activity log.
- **`POST /api/reengage/act` {task_id,partner_id,action,sms_text}**: `send` → reuses the EXACT manual path: `POST /api/followup/launch` (clones latest Workiz job → SubStatus 'Re-engagement Trigger' → Workiz automation sends; writes last_followup_sent; all gates re-checked) THEN `POST /api/followup/markdone {source:'task'}` (the launch only archives mail.activity, but these To-Dos are project.task → must close separately). `skip` → snooze task +7 days. Logs to `reengage.log` (cap 200).
- **No Twilio**: reactivation texts go via Workiz automation (existing). The approval prompt = web push, not SMS.
- Dashboard tile "🔄 Reactivations Due" added to Marketing & Retention.
- VERIFIED read-side: 2 due (Barbara Rago 23220, Dwight Fichtner 23204), SMS previews build (~430 chars). Did NOT trigger a live send.

## ⚠ GOTCHA — self-HTTP from an async endpoint DEADLOCKS (cost a debug cycle)
reengage reuses the followup endpoints via internal `requests.post('http://127.0.0.1:8000/owner/api/followup/...')`. The `/api/reengage/due` + `/api/reengage/act` endpoints MUST be **sync `def`** (not `async`). The app runs one event loop; a blocking `requests.post` to ITSELF inside an `async def` ties up the loop so it can't service the inbound self-call → 20s timeout, empty result. Sync `def` endpoints run in FastAPI's threadpool, so the loop stays free to serve the self-call. Use `body: dict = Body(...)` to read the POST body in a sync endpoint (can't `await request.json()`).

## ON-NOTIFICATION BUTTONS — SHIPPED 2026-06-16 (DJ: "both options")
Push now carries `actions:[{action:'reengage-send',title:'✅ Send'},{action:'reengage-skip',title:'Skip'}]` + `data:{task_id,partner_id,name,token,url}` (individual pushes only; digest stays tap-to-open). **SW in auth.py `_SW_JS`** extended: `push` passes `d.actions`→`o.actions` and `d.data`→`o.data`; `notificationclick` handles `e.action` reengage-send/skip → `fetch POST /owner/api/reengage/act` with the data+token → shows a result notification ("✅ Reactivation sent to X"). No action (body tap) → opens `data.url` (/owner/reengage). So BOTH: one-tap on the notification AND tap-to-open the review screen. Backward-compatible with My Day pushes (no actions/data).
- **Token**: `_token(task_id)=hmac(CRON_SECRET,'reengage:'+id)[:16]`. The SW path sends it; `/act` rejects a bad token (`hmac.compare_digest`). Screen path sends no token (owner context) → allowed. Server generates + validates with the same fn so the real token always matches.
- iOS caveat: web-push action buttons need the installed PWA + recent iOS; where unsupported, the body-tap → screen path still works.
- ⚠ TEST LESSON: I hit `/act` before reengage.py finished deploying (auth.py was live, reengage lagged in the same build) → the OLD no-token version ran my test skip for real. When testing a multi-file deploy, confirm the deploy is `live` first, and probe token gates with a no-op action (no side effect either way).

## NEXT (not built)
- Other automations DJ may want later: auto-process reactivation candidates, auto-finish maintenance jobs (line items+tech), review-requests-after-Done (THIS one needs Twilio A2P — [[project_twilio_a2p_and_entity]]).
