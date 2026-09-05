---
name: project_operator_login
description: "Dedicated \"Operator\" owner-role login (res.partner 27204) + key file lets the headless Operator session auth its /owner/* calls so AUTH_ENFORCE=1 can be re-enabled (Cheryl-silo go-live)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T07:14:01.879Z
---

The headless **Operator** session performs DJ's live ops via the app's `/owner/*` HTTP endpoints with NO login cookie — which is why flipping `AUTH_ENFORCE=1` 401'd it and forced a rollback ([[project_auth_enforce_operator_gap]]). Fix (DJ chose DEDICATED over reusing his own login, 2026-09-05):

- **Dedicated login:** `res.partner` **id 27204**, `name="Operator"`, `x_render_role="owner"`, `x_render_pin` set (a 4-digit PIN, NOT DJ's). Cleaner audit trail (its feed acks read "Operator", not "Dan") and DJ's personal PIN never sits in a file.
- **Key file (Specialists wrote it, has local file access):** `C:\Users\dj\_operator_owner_login.json` = `{"name":"Operator","pin":"<pin>"}`. The Operator session reads it.
- **Login flow (Operator wires client-side):** `POST https://wsc-field-assistant.onrender.com/api/login {"name":"operator","pin":<from file>}` → capture the `wsc_session` cookie from `Set-Cookie` → send `Cookie: wsc_session=<token>` on EVERY `/owner/*` call → on any 401, re-login + retry. Session is 180-day.
- **Verified end-to-end (2026-09-05):** login returns `role:owner`, session `{n:Operator,r:owner,p:27204}`, and `/owner/api/feed/list` is accepted WITH the cookie. So the app already supports it — no app code change needed; `authz.session_from_request` reads the cookie regardless of client.

**Go-live sequence to re-enable the Cheryl silo (Lead orchestrates):** (a) Operator wires the login+cookie flow + re-login-on-401; (b) controlled ~2-min `AUTH_ENFORCE=1` flip with the Operator PAUSED, verify owner-cookie ops succeed + a cheryl session is denied `/owner` (401) but reaches `/cheryl/*` + no-cookie=401, then flip off; (c) the real `AUTH_ENFORCE=1` go-live (Lead flips), which also auto-sends Cheryl's intro email. Cheryl's whole side is already live ([[project_cheryl_hud_v1]]).
