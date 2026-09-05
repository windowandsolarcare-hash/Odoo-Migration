---
name: project_notify_dj_sms_tier
description: "notify_dj has a two-surface reach: the in-app flashing banner AND an SMS tier that texts DJ when he's away. 'Away' = his banner hasn't polled GET /owner/api/dj_alerts within NOTIFY_AWAY_SECONDS (default 300s). SMS reuses sms.py _send_sms; POST body sms mode = auto|always|never."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T14:32:03.868Z
---

**Shipped 2026-09-05 (commit 24788388), master-queue #6 half.** `routers/owner/notify.py` (the agent-session→DJ alert channel, store `wsc.dj.alerts`) now reaches DJ two ways off the SAME store: (1) the in-app flashing banner (`v2_needsyou_banner.js`, polls `GET /owner/api/dj_alerts` every 30s while the tab is visible), and (2) an **SMS tier** that texts DJ when he isn't looking at the banner.

**How "away" is detected (no external presence system needed):** the banner's own poll IS the heartbeat. In the `dj_alerts` GET handler, when it's the banner's exact call (`role==''` AND `status=='open'`), it touches `ir.config_parameter wsc.dj.last_seen = now`. DJ's reply/act also touch it. **Fleet-session polls do NOT touch it** — sessions read `?role=<self>&status=answered`, which is excluded — so a session checking its answers can't mask DJ's absence. `_is_away()` = last_seen is missing OR older than `NOTIFY_AWAY_SECONDS` (env, default 300s).

**POST /owner/api/notify_dj `sms` mode** (optional body field): `auto` (default — text only if `_is_away()`), `always` (force a text regardless), `never` (banner only). Response now includes `sms_sent: bool`. Alert dict gained `sms_sent` (iso ts when texted, else None).

**SMS send:** lazy-imports `from .sms import _send_sms, DJ_PHONE_NUMBER` (avoids module-load coupling — see [[project_shared_star_import_scoping_gap]]). Best-effort: the alert is already stored before the SMS attempt, and `_sms_dj` never raises. Body = `🔔 <role> needs you / <summary> / Q: <question> / Reply: <choices> / Answer in the app: <APP_BASE>/owner/command`. `APP_BASE` = env `APP_BASE_URL` or `https://wsc-field-assistant.onrender.com`. Note `_send_sms` appends DJ's stacked business signature (harmless on an internal alert). Twilio env: TWILIO_ACCOUNT_SID/AUTH_TOKEN/BUSINESS_NUMBER (or MESSAGING_SERVICE_SID), DJ_PHONE_NUMBER — all already set for the inbox.

**Why:** the banner only reaches DJ when he has a banner-bearing page (v2_command/field/hud/inbox) open+visible; in the field he often doesn't, so an agent's blocking question would sit unseen. The SMS tier closes that gap without any always-on presence tracking.

**Verify:** `POST /owner/api/notify_dj {summary,question,sms:'never'}` → `{ok:true,id,sms_sent:false}` proves the deploy is live (the `sms_sent` key only exists post-24788388). Clean up test alerts via `/owner/api/dj_alerts/act {id,op:'dismiss'}` — the banner shows ALL open alerts (no role filter) so leftover QC alerts WILL appear to DJ. NOTE: `/healthz` returns only `{"ok":true}` — no commit field; don't poll it for commit-match, verify by endpoint behavior (or Render MCP get_deploy) instead.
