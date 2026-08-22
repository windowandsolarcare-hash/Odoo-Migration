---
name: project_authz_block_b
description: Auth layer (Block B) LIVE IN MONITOR MODE 2026-07-26 — routers/authz.py + gate in main.py. Blocks NOTHING until env AUTH_ENFORCE=1. Read the would-block report before flipping.
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-08-05T13:48:30.632Z
---

Shipped 2026-07-26 (lead lane): `routers/authz.py` (new) + surgical edits to `routers/auth.py` (login lockout + session cookie) + gate middleware in `main.py`.

- Session: signed cookie `wsc_session` = v1.<b64 {n,r,exp}>.<hmac-sha256>. 180-day, sliding renewal past half-life (middleware re-sets it). Secret = SESSION_SECRET env, FALLBACK ODOO_API_KEY (works now; set a dedicated SESSION_SECRET on Render eventually — rotating the Odoo key would log everyone out).
- Login (`POST /api/login`): unchanged UX/response; now sets the cookie on success + per-IP lockout (5 fails → 15 min, in-memory). Verified live: bad PIN → 401 no cookie; good login → 200 + Set-Cookie HttpOnly/Secure/SameSite=lax/Max-Age=15552000. `POST /api/logout` clears it. WSCSignOut still only clears localStorage — wire it to /api/logout before enforcement.
- Gate: protects `/owner /tech /cheryl`; PUBLIC_PREFIXES = /api/login, /api/logout, /healthz, /static (UI shells only — keeps SW/offline model), /book, /c/, /sw.js. Role check: owner=all, tech=/tech, cheryl=/cheryl.
- **MONITOR MODE (current): blocks NOTHING until env `AUTH_ENFORCE=1` on Render.** Would-blocks recorded per METHOD+trimmed-path+UA: `GET /owner/api/authz/report` (process-local, resets on deploy). Verified: no-cookie hit to /owner/api/feed/list returned 200 AND appeared in the report.

FLIP CHECKLIST (before setting AUTH_ENFORCE=1):
1. Let monitor run 24-48h of NORMAL use (DJ phone, Danny, Cheryl, Twilio webhooks, OwnTracks, Zapier, crons, Render Claude self-calls) then read the report.
2. Whitelist every legitimate external caller found (add to PUBLIC_PREFIXES or give it a secret-header bypass).
3. Wire WSCSignOut → POST /api/logout.
4. DJ + Danny + Cheryl must each log in once (mints cookies) BEFORE the flip.
5. Set env var via Render API POST per-var — NEVER PUT the full env list ([[feedback_render_env_var_patch_not_put]]).
6. After flip: watch /owner/api/authz/report (still counts) + app behavior; flip back = unset the var.

**Why:** approval inbox + credentials vault + bank data are gated on this (HUD spec Phase 2). Enforcement without the monitor pass would break unknown external callers or lock DJ out in the field.
**How to apply:** any new endpoint that must stay public (webhook/cron) needs its own secret AND a PUBLIC_PREFIXES entry; anything else is protected by default once enforced.

---

**UPDATE 2026-07-29 (first real report read + reset):** Report showed 47 distinct would-block patterns. Categorized:
- **Machines that CANNOT hold a session (must exempt, they live under /owner so they're NOT currently public):** `POST /owner/api/owntracks/webhook` (6038 hits — GPS, auth via OWNTRACKS_SECRET), `/owner/api/cron/*` (daily_sync, a2p_watch, submitted_jobs_scan — python-requests), `/owner/api/scheduler/best-fit`. Flipping today kills GPS + all crons.
- **Customer-facing PUBLIC under /owner (must exempt):** `/owner/api/stripe/tip_page`, `/stripe/payment_link`, `/stripe/logo`, `/owner/api/booking/intake`, `/owner/api/booking_requests`. Only `/book` + `/c/` are public today; the APIs those pages call are under /owner → customers would get 401 paying/booking.
- **DJ/Danny traffic:** field-app core boot calls (dashboard/whoami/upcoming/payroll) appeared only 1-4× (occasional), HUD+Library calls (library/list, library/add, feed/badge, feed/list, appver) appeared 10-17× (consistent).
- **curl (me/specialists tests) + specialists' server-side jobs** (billing sweep, paywatch tick, briefing run) hit /owner too → need a SERVICE TOKEN or they break under enforce.

**KEY NUANCE — the tally is CUMULATIVE across weeks/many deploys** (flush_monitor persists to ir.config_parameter `wsc.authz.monitor` specifically so pushes don't wipe it). So a count of 17 is NOT "17 times today" — it spans the whole build period, including before HUD/Library were behind login. Do NOT read counts as current-day.

**LOGIN CONFIRMED WORKING:** `static/login.html` "Saunders Group / YOUR NAME + PIN" (the ONLY door — DJ is ALWAYS logged in, app icon start_url="/" = this screen) → `POST /api/login` (routers/auth.py) looks up res.partner by name + `x_render_pin` + `x_render_role`, then **calls `authz.set_session_cookie(authz.make_session(name, role))`** — so login DOES mint the owner cookie. My earlier "nobody logged in" read was WRONG.

**HUD/Library are NOT separate apps/hosts** — HUD = `/static/owner/v2_hud.html`, Library = `/owner/library`, both inside this app, all data calls RELATIVE (same host). No host mismatch, no credentials:'omit', SW does NOT intercept /owner/api GETs. So with DJ always logged in + same host, cookie SHOULD reach them → leading theory for why they're in the report is CUMULATIVE HISTORY (pre-auth-wiring) + stale cached launcher, NOT a live logged-out state.

**RESET DONE 2026-07-29:** zeroed `wsc.authz.monitor` to `{}` via odoo set_param (no reset endpoint exists; clears only the diagnostic log, no behavior change). Experiment running: DJ uses app normally 1 day (always logged in), re-read report. HUD/Library GONE → history, fine, proceed to enforce prep. STILL present from Android UA while logged in → real live gap, instrument the exact call. DJ nudge to resume = "check auth".

**RE-READ + INSTRUMENT 2026-08-03 (lead):** re-read live report — `enforcing:False`, **62 distinct** would-block patterns (up from 47). OwnTracks 4804 (down from 6038 = confirms the 7-29 zero took; fresh 4-day count). Interesting rows are the **Android** ones (`/owner/api/library/*`, `/owner/library`, `/owner/api/journal/list`, `/owner/api/notes/:id/text`) — reappeared POST-reset from DJ's logged-in phone = the real live gap. Several other report rows are **curl/8.18.0 + Windows UA = my/specialist test traffic, NOT DJ** — discount those. **Instrument shipped:** authz.py `record_would_block` now stores a **reason** per row via `_block_reason` (`no-cookie` = cookie never reached us / split cookie-jar / PWA webview / logged-out; `bad-or-expired` = cookie came but bad sig or past exp; `role-mismatch` = valid session, wrong role for path). Reason back-fills onto existing keys on next hit (NO re-zero needed — count history preserved). `/owner/api/authz/report` rows now carry `reason`. **NEXT (after ~1 day soak): re-read report, read the reason on the Android rows** → tells us the exact fix (no-cookie → cookie isn't reaching that context, likely add `credentials:'include'` to jfetch/library fetch or fix launcher cookie-jar; bad-or-expired → re-login/renewal; role-mismatch → DJ's res.partner x_render_role not 'owner'). THEN whitelist machine callers (OwnTracks/crons/Twilio/Stripe/booking) + flip AUTH_ENFORCE. Client fetch note: `v2_hud.html` jfetch (L211) + `library.html` (L257) call `fetch(url,opts)` with **no `credentials`** — same-origin default sends cookies, but if a no-cookie reason shows, add `credentials:'include'` there. DJ nudge = "check auth"; the re-read IS already done this session.

**DON'T-FORGET REMINDER SET (2026-08-03):** to avoid forgetting the soak re-read (we forgot once), dropped a **snoozed feed card** straight into `wsc.feed.items` (id `authz:soak-read`, source `authz`, status `snoozed`, `snooze_until`=2026-08-05T10:21Z) — it auto-surfaces in DJ's HUD "Needs you" tab Tue Aug 5, links to `/owner/api/authz/report`, survives deploys (Odoo param), no cron needed. **Reusable pattern for any future follow-up:** write an entry to `wsc.feed.items` with `status:'snoozed'` + `snooze_until` (format `%Y-%m-%dT%H:%M:%SZ` UTC, string-compared); `feed.list_items` flips it to 'seen' and shows it once the time passes. Item schema (validate_item): required `id,kind('attention'|'approval'),source,title(<=80),why_now,urgency('interrupt'|'today'|'glance'),action{label,href},created`.

**RE-READ 2026-08-05 (the soak-read we set up) — reasons diagnosed:**
Report: `enforcing:False`, 74 patterns. Reason breakdown: no-cookie 30, role-mismatch 4, blank 40 (pre-instrument rows). Login users (res.partner x_render_role): **Dan Saunders id3 = 'owner'** ✓, Danny Saunders id26586 = 'tech', Cheryl id23243 = 'cheryl'.
- **DJ is NOT going to lock himself out** — his role is correctly 'owner' (owner opens everything). The fresh **role-mismatch** rows (all on /owner/library, library/list, library/add, fetch_title from an Android UA) = a NON-owner (tech/cheryl) hitting owner-only pages → the role gate WORKING, correct to block. Not a bug.
- **THE real pre-flip blocker = machine callers show `no-cookie`** and would break on enforce: `/owner/api/owntracks/webhook` (9126 hits, GPS), Twilio webhooks (`/owner/voice/incoming|dj-status|hold|voicemail-redirect`, `/owner/api/sms/incoming`), crons (`/owner/api/cron/*`). They can't hold a session — must be WHITELISTED (they carry own secrets: OWNTRACKS_SECRET / CRON_SECRET / Twilio sig) before AUTH_ENFORCE=1.
- **NEXT: build the whitelist** — add the webhook/cron paths to `PUBLIC_PREFIXES` (or a secret-header bypass) in authz.py. Then everyone logs in once → DJ flips AUTH_ENFORCE=1 (his call). Curl/Windows-Mozilla no-cookie rows = my + specialist test traffic, discount.

**WHITELIST SHIPPED 2026-08-05 (lead, authz.py — DJ approved).** Behavior-neutral in monitor mode; only matters on flip. Two new sets in authz.py:
- `PUBLIC_PREFIXES` extended (startswith): `/owner/api/owntracks/webhook`, `/owner/api/cron/`, `/owner/api/payroll/cron`, `/owner/api/tasker/`, `/owner/api/sms/incoming`, `/owner/api/booking/intake`, `/owner/api/stripe/tip_page`, `/owner/api/stripe/logo`, `/owner/api/stripe/check_payment`.
- `PUBLIC_EXACT` (frozenset, EXACT match) = the 11 Twilio VOICE webhooks: incoming, hold, dj-bridge, dj-status, voicemail-redirect, recording-done, transcription, outbound-bridge, consent-whisper, recording-saved, transcript-ready. **EXACT on purpose** — `/owner/voice/` is a mix; a prefix would wrongly expose DJ-only siblings (`/voice/dial` places real calls, `/voice/incoming-latest`, `/voice/numbers`, `/voice/callcard`, `/voice/resolve`, `/voice/rec`). check() now tests `path in PUBLIC_EXACT` before the prefix loop.
- Deliberately KEPT PROTECTED: `/voice/dial`, `/voice/numbers`, `/voice/callcard`, `/voice/resolve`, `/voice/rec`, `/voice/incoming-latest`, `/voice/vi-setup`, `/voice/recent`, `/voice/setup`, `/voice/trusthub`, `/voice/a2p`; `/owner/api/stripe/payment_link` + all `record_*`/`process_payment` (DJ logged in); `/owner/api/booking_requests` (DJ's view).
- Self-test (ast-extract both sets, check startswith/exact): 11 machine PUBLIC + 11 DJ-only PROTECTED all pass. **★ If ANY new Twilio webhook route is added later, it MUST be added to PUBLIC_EXACT or it 401s on flip.**
- **Remaining before flip:** (1) DJ + Danny + Cheryl each log in once; (2) wire WSCSignOut→POST /api/logout; (3) DJ sets AUTH_ENFORCE=1 via Render POST-per-var (his call); (4) watch report + behavior, unset to roll back.

**THIRD-AI AUDIT (2026-08-03) — all 3 concerns verified TRUE against live code:** (1) enforce not flipped (above). (2) **No audit trail of who approved** — `feed.py api_feed_ack` writes only `status`+`updated` timestamp, NO actor; sessions DO carry identity (name+role) so fix = read `session_from_request` in the ack + stamp `approved_by` (cheap, safe, additive — NEXT concrete step after the auth soak). (3) **No trust dial / auto-graduation** — grepped whole tree, does NOT exist anywhere; spec'd only as inbox-assistant P4. See [[project_inbox_assistant]].
